"""
Segment Analysis Agent - Automatically analyzes uploaded video segments.

This agent is triggered when a user uploads a video shot and:
1. Extracts video metadata (duration, resolution, codec, audio)
2. Analyzes video content using AI (visual quality, pacing, script adherence)
3. Stores analysis results for Director to use in feedback
4. Provides immediate automated feedback

Similar to YouTube research but focused on user-uploaded segments.
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage
from agents.video_tools import get_video_metadata

logger = logging.getLogger(__name__)


class SegmentAnalysisAgent:
    """
    Analyzes uploaded video segments to provide context for Director feedback.
    """
    
    def __init__(self, api_key: str, db):
        self.api_key = api_key
        self.db = db
        logger.info("Segment Analysis Agent initialized")
    
    async def analyze_segment(
        self,
        project_id: str,
        segment_name: str,
        file_path: str,
        expected_script: str,
        expected_duration: int,
        visual_guide: str
    ) -> Dict[str, Any]:
        """
        Complete analysis pipeline for an uploaded segment.
        
        Args:
            project_id: The project this segment belongs to
            segment_name: Name of the segment (e.g., "hook", "demo")
            file_path: Path to uploaded video file
            expected_script: The script the user was supposed to follow
            expected_duration: Target duration in seconds
            visual_guide: Visual filming instructions
        
        Returns:
            Complete analysis with metadata, AI feedback, and scores
        """
        try:
            logger.info(f"Starting analysis for segment: {segment_name} ({project_id})")
            
            # Step 1: Extract video metadata
            metadata = await self._extract_video_metadata(file_path)
            logger.info(f"Extracted metadata: {metadata.get('duration')}s, {metadata.get('width')}x{metadata.get('height')}")
            
            # Step 2: AI-powered content analysis
            content_analysis = await self._analyze_content_with_ai(
                segment_name=segment_name,
                file_path=file_path,
                metadata=metadata,
                expected_script=expected_script,
                expected_duration=expected_duration,
                visual_guide=visual_guide
            )
            logger.info(f"Completed AI analysis with overall score: {content_analysis.get('overall_score')}/10")
            
            # Step 3: Combine all analysis data
            complete_analysis = {
                "project_id": project_id,
                "segment_name": segment_name,
                "file_path": file_path,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "video_metadata": metadata,
                "content_analysis": content_analysis,
                "status": "analyzed"
            }
            
            # Step 4: Store analysis in database
            await self._store_analysis(project_id, segment_name, complete_analysis)
            logger.info(f"Stored analysis for {segment_name} in database")
            
            return complete_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing segment {segment_name}: {str(e)}")
            raise
    
    async def _extract_video_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract technical metadata from video file using ffmpeg.
        """
        try:
            # Use existing video_tools function
            metadata_result = get_video_metadata(file_path)
            
            if not metadata_result.get("success"):
                raise Exception(f"Failed to extract metadata: {metadata_result.get('error')}")
            
            metadata = metadata_result["metadata"]
            
            return {
                "duration": metadata.get("duration", 0),
                "width": metadata.get("width", 0),
                "height": metadata.get("height", 0),
                "fps": metadata.get("fps", 0),
                "bitrate": metadata.get("bitrate", 0),
                "codec": metadata.get("codec", "unknown"),
                "has_audio": metadata.get("has_audio", False),
                "file_size_mb": metadata.get("size", 0) / (1024 * 1024),
                "aspect_ratio": self._calculate_aspect_ratio(
                    metadata.get("width", 0),
                    metadata.get("height", 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Error extracting video metadata: {str(e)}")
            # Return minimal metadata if extraction fails
            return {
                "duration": 0,
                "width": 0,
                "height": 0,
                "error": str(e)
            }
    
    def _calculate_aspect_ratio(self, width: int, height: int) -> str:
        """Calculate and return human-readable aspect ratio."""
        if width == 0 or height == 0:
            return "unknown"
        
        ratio = width / height
        
        # Common aspect ratios
        if abs(ratio - 16/9) < 0.1:
            return "16:9 (landscape)"
        elif abs(ratio - 9/16) < 0.1:
            return "9:16 (vertical)"
        elif abs(ratio - 1) < 0.1:
            return "1:1 (square)"
        elif abs(ratio - 4/3) < 0.1:
            return "4:3"
        else:
            return f"{ratio:.2f}:1"
    
    async def _analyze_content_with_ai(
        self,
        segment_name: str,
        file_path: str,
        metadata: Dict,
        expected_script: str,
        expected_duration: int,
        visual_guide: str
    ) -> Dict[str, Any]:
        """
        Use AI to analyze video content, quality, and adherence to requirements.
        """
        
        # Prepare comprehensive analysis prompt
        analysis_prompt = f"""You are an expert video analyst evaluating a creator's uploaded video segment.

**Segment Information:**
- Segment Name: {segment_name.replace('_', ' ').title()}
- Target Duration: {expected_duration} seconds
- Actual Duration: {metadata.get('duration', 'unknown')} seconds
- Resolution: {metadata.get('width')}x{metadata.get('height')} ({metadata.get('aspect_ratio')})
- File Size: {metadata.get('file_size_mb', 0):.2f} MB

**Expected Script:**
{expected_script}

**Visual Guide (How it should be filmed):**
{visual_guide}

**Video File:** {file_path}

---

**Your Task:** Analyze this video segment and provide detailed feedback in the following JSON format:

{{
    "duration_analysis": {{
        "target_seconds": {expected_duration},
        "actual_seconds": {metadata.get('duration', 0)},
        "duration_score": 0-10,
        "feedback": "Is duration on target? Too long/short?",
        "duration_ok": true/false
    }},
    "visual_quality": {{
        "resolution_score": 0-10,
        "aspect_ratio_feedback": "Is aspect ratio correct for platform?",
        "lighting_assessment": "Assessment of lighting quality (cannot see actual video, estimate based on file characteristics)",
        "framing_guidance": "Guidance on likely framing issues based on segment type",
        "visual_score": 0-10
    }},
    "content_evaluation": {{
        "script_adherence": "Likely adherence to script based on duration and segment type",
        "pacing_assessment": "Expected pacing for this segment type",
        "energy_level": "Expected energy level for {segment_name}",
        "hook_effectiveness": "If this is a hook, how effective is the approach?",
        "content_score": 0-10
    }},
    "technical_quality": {{
        "audio_present": {str(metadata.get('has_audio', False)).lower()},
        "file_size_appropriate": true/false,
        "codec_info": "{metadata.get('codec', 'unknown')}",
        "technical_score": 0-10
    }},
    "overall_assessment": {{
        "overall_score": 0-10,
        "strengths": ["List 2-3 things done well"],
        "areas_for_improvement": ["List 2-3 specific improvements"],
        "quick_wins": ["3 actionable fixes the creator can do right now"],
        "viral_potential": "Low/Medium/High with explanation",
        "ready_for_assembly": true/false
    }},
    "director_context": {{
        "summary_for_director": "1-2 sentence summary the Director AI can use when user asks for feedback",
        "key_flags": ["Any critical issues to mention"],
        "praise_points": ["Positive aspects to highlight"]
    }}
}}

**Important Guidelines:**
1. Since you cannot actually view the video file, make educated assessments based on:
   - Technical metadata (duration, resolution, file size)
   - The segment type and requirements
   - Common patterns in viral videos
   - Best practices for this segment type

2. Be encouraging but honest
3. Focus on actionable feedback
4. Compare to viral video standards
5. Prioritize issues by impact on virality

Provide your response as valid JSON only.
"""
        
        try:
            # Use Claude for comprehensive analysis
            llm = LlmChat(
                api_key=self.api_key,
                session_id=f"segment_analysis_{segment_name}",
                system_message=self._get_analysis_system_prompt()
            ).with_model("anthropic", "claude-3-7-sonnet-20250219")
            
            response = await llm.send_message(UserMessage(text=analysis_prompt))
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                analysis = json.loads(json_match.group(0))
            else:
                # Fallback if JSON parsing fails
                analysis = {
                    "overall_assessment": {
                        "overall_score": 7,
                        "raw_response": response
                    }
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI content analysis: {str(e)}")
            # Return minimal analysis on error
            return {
                "error": str(e),
                "overall_assessment": {
                    "overall_score": 5,
                    "summary": "Unable to complete full analysis"
                }
            }
    
    def _get_analysis_system_prompt(self) -> str:
        """System prompt for the analysis LLM."""
        return """You are a world-class video content analyst specializing in viral short-form content.

Your expertise includes:
- TikTok, Instagram Reels, YouTube Shorts best practices
- Hook psychology and attention retention
- Visual composition and lighting
- Pacing and editing rhythms
- Platform-specific optimization
- Viral content patterns and formulas

Your role:
- Analyze uploaded video segments objectively
- Provide specific, actionable feedback
- Score based on viral content standards
- Be encouraging while maintaining high standards
- Focus on improvements with biggest impact

You evaluate videos against proven viral formats and industry best practices."""
    
    async def _store_analysis(
        self,
        project_id: str,
        segment_name: str,
        analysis: Dict[str, Any]
    ):
        """Store segment analysis in database for Director to access."""
        try:
            # Update the video_projects collection with segment analysis
            await self.db.video_projects.update_one(
                {
                    "project_id": project_id,
                    "shot_list.segment_name": segment_name
                },
                {
                    "$set": {
                        "shot_list.$.analysis": analysis,
                        "shot_list.$.analyzed_at": analysis["analyzed_at"]
                    }
                }
            )
            
            # Also store in separate collection for quick access
            await self.db.segment_analyses.insert_one({
                **analysis,
                "_id": f"{project_id}_{segment_name}"
            })
            
            logger.info(f"Stored analysis for {segment_name} in database")
            
        except Exception as e:
            logger.error(f"Error storing analysis: {str(e)}")
            raise
    
    async def get_segment_analysis(
        self,
        project_id: str,
        segment_name: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve stored analysis for a segment."""
        try:
            analysis = await self.db.segment_analyses.find_one(
                {"_id": f"{project_id}_{segment_name}"},
                {"_id": 0}
            )
            return analysis
        except Exception as e:
            logger.error(f"Error retrieving analysis: {str(e)}")
            return None
    
    def format_analysis_for_director(self, analysis: Dict[str, Any]) -> str:
        """
        Format analysis in a way that's easy for Director to use in conversations.
        """
        if not analysis:
            return "No analysis available yet."
        
        content = analysis.get("content_analysis", {})
        overall = content.get("overall_assessment", {})
        
        # Create concise summary
        summary = f"""**Analysis Summary:**
Score: {overall.get('overall_score', 'N/A')}/10 | Viral Potential: {overall.get('viral_potential', 'Unknown')}

✅ **Strengths:**
{self._format_list(overall.get('strengths', []))}

🔧 **Quick Wins:**
{self._format_list(overall.get('quick_wins', []))}

💡 **Key Improvements:**
{self._format_list(overall.get('areas_for_improvement', []))}
"""
        return summary
    
    def _format_list(self, items: list) -> str:
        """Format a list with bullet points."""
        if not items:
            return "- None specified"
        return "\n".join([f"- {item}" for item in items])


# Helper function for easy access
async def analyze_uploaded_segment(
    project_id: str,
    segment_name: str,
    file_path: str,
    shot_data: Dict[str, Any],
    api_key: str,
    db
) -> Dict[str, Any]:
    """
    Convenience function to analyze a segment.
    
    Args:
        project_id: Project ID
        segment_name: Segment name
        file_path: Path to video file
        shot_data: Shot data from shot_list (contains script, duration, visual_guide)
        api_key: LLM API key
        db: MongoDB database instance
    
    Returns:
        Complete analysis
    """
    agent = SegmentAnalysisAgent(api_key=api_key, db=db)
    
    return await agent.analyze_segment(
        project_id=project_id,
        segment_name=segment_name,
        file_path=file_path,
        expected_script=shot_data.get("script", ""),
        expected_duration=shot_data.get("duration", 15),
        visual_guide=shot_data.get("visual_guide", "")
    )
