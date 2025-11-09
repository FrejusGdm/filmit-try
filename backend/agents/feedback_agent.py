"""
Feedback Agent - Analyzes uploaded video shots and provides specific feedback.
Uses AI to evaluate shot quality, adherence to script, and viral potential.
"""

from typing import Dict, Any, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os


class FeedbackAgent:
    """
    Analyzes uploaded video shots and provides constructive feedback.
    Evaluates: script adherence, visual quality, pacing, hook effectiveness, etc.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def analyze_shot(
        self,
        segment_name: str,
        script: str,
        visual_guide: str,
        duration_target: int,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a specific shot and provide feedback.
        
        Args:
            segment_name: Name of the segment (e.g., "hook", "problem")
            script: Expected script for this segment
            visual_guide: Visual filming guide
            duration_target: Target duration in seconds
            file_path: Path to uploaded video (optional for now)
        
        Returns:
            Feedback with scores and suggestions
        """
        
        # Initialize LLM for feedback
        llm = LlmChat(
            api_key=self.api_key,
            session_id=f"feedback_{segment_name}",
            system_message=self._get_feedback_prompt()
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        # Build analysis request
        analysis_request = f"""Analyze this video shot:

**Segment:** {segment_name.replace('_', ' ').title()}
**Target Duration:** {duration_target} seconds
**Expected Script:** {script}
**Visual Guide:** {visual_guide}

{"**Video File:** " + file_path if file_path else "**Note:** Video not yet uploaded, provide guidance based on requirements"}

Provide feedback on:
1. **Script Adherence** (if video uploaded): Does it follow the script? Any deviations?
2. **Visual Quality**: Does it match the visual guide? Lighting, framing, composition?
3. **Pacing & Energy**: Is the energy level appropriate for this segment?
4. **Hook Effectiveness** (if hook segment): Does it grab attention in first 3 seconds?
5. **Duration**: Is it close to the {duration_target}s target?
6. **Improvements**: Specific suggestions to make it more viral

Respond in this format:
SCORES:
- Script: X/10
- Visual: X/10
- Pacing: X/10
- Overall: X/10

FEEDBACK:
[Your detailed feedback here]

QUICK WINS:
[3 actionable improvements]
"""
        
        response = await llm.send_message(UserMessage(text=analysis_request))
        
        # Parse response (simplified - in production would use structured output)
        return {
            "segment_name": segment_name,
            "feedback": response,
            "status": "analyzed",
            "has_video": file_path is not None
        }
    
    async def compare_to_examples(
        self,
        segment_name: str,
        user_video_description: str,
        reference_videos: list
    ) -> Dict[str, Any]:
        """
        Compare user's shot to reference viral videos.
        
        Args:
            segment_name: Name of segment
            user_video_description: Description of what user filmed
            reference_videos: List of reference video descriptions
        
        Returns:
            Comparison analysis
        """
        
        llm = LlmChat(
            api_key=self.api_key,
            session_id=f"compare_{segment_name}",
            system_message="You are a video comparison expert."
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        comparison_request = f"""Compare this shot to viral references:

**User's Shot ({segment_name}):**
{user_video_description}

**Viral References:**
{chr(10).join([f"- {ref}" for ref in reference_videos])}

What do the viral videos do that the user's shot could improve on?
Give 3 specific, actionable suggestions."""

        response = await llm.send_message(UserMessage(text=comparison_request))
        
        return {
            "segment_name": segment_name,
            "comparison": response,
            "references_used": len(reference_videos)
        }
    
    def _get_feedback_prompt(self) -> str:
        """System prompt for feedback agent"""
        return """You are a viral video coach and expert analyzer. Your job is to provide:

1. **Honest, constructive feedback** - Point out what works and what doesn't
2. **Specific, actionable suggestions** - Not vague advice, but concrete improvements
3. **Reference to viral patterns** - Compare to successful videos in the format
4. **Encouragement with realism** - Be supportive but truthful

Focus on:
- Hook effectiveness (first 3 seconds)
- Pacing and energy
- Visual quality and composition
- Script delivery and authenticity
- Adherence to proven viral formats

Your feedback should help creators improve without being discouraging."""


async def get_overall_project_feedback(
    api_key: str,
    shot_list: list,
    uploaded_count: int,
    matched_format: Dict[str, Any]
) -> str:
    """
    Provide overall project feedback - what's done, what's missing, next steps.
    
    Args:
        api_key: LLM API key
        shot_list: List of all shots
        uploaded_count: Number of shots uploaded
        matched_format: The viral format being followed
    
    Returns:
        Overall project status and guidance
    """
    
    llm = LlmChat(
        api_key=api_key,
        session_id="project_overview",
        system_message="You are a project guidance expert."
    ).with_model("anthropic", "claude-3-7-sonnet-20250219")
    
    # Build shot status summary
    shot_status = []
    for shot in shot_list:
        status = "✅ Uploaded" if shot.get("uploaded") else "⏳ Pending"
        required = "Required" if shot.get("required") else "Optional"
        shot_status.append(f"- {shot['segment_name'].replace('_', ' ').title()}: {status} ({required})")
    
    request = f"""Provide overall project guidance:

**Format:** {matched_format['name']}
**Progress:** {uploaded_count}/{len(shot_list)} shots uploaded

**Shot Status:**
{chr(10).join(shot_status)}

Give:
1. What's been completed well
2. What's still needed (prioritize required shots)
3. Next recommended action
4. Estimated time to completion

Be encouraging but keep them focused on what matters most."""

    response = await llm.send_message(UserMessage(text=request))
    return response
