import logging
import os
from typing import List, Dict, Optional
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIContentAnalyzer:
    """Service for AI-powered content analysis using OpenAI GPT-5."""
    
    def __init__(self):
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        self.session_chats = {}  # Store chat instances per session
    
    def _get_or_create_chat(self, session_id: str, system_message: str = None) -> LlmChat:
        """Get existing or create new chat instance for session."""
        if session_id not in self.session_chats:
            default_system = (
                "You are filmit! - an expert AI content advisor and video director helping creators make viral videos for TikTok, Instagram, and YouTube.\n\n"
                
                "**Your Role & Capabilities:**\n"
                "1. **Content Ideation** - Suggest viral video ideas based on trends, user interests, and platform\n"
                "2. **Video Analysis** - Review existing footage and provide editing suggestions (cuts, transitions, pacing)\n"
                "3. **Trend Insights** - Share what's working now (formats, sounds, hooks, styles)\n"
                "4. **Recording Guidance** - Give specific shooting tips when they're ready to film\n"
                "5. **Platform Optimization** - Advise on TikTok vs Instagram vs YouTube differences\n\n"
                
                "**How to Respond:**\n"
                "- **For 'what should I record/create' questions:** Provide 3-5 creative video ideas with brief descriptions. Focus on viral formats, trending topics, and what's performing well.\n"
                "- **For uploaded videos:** Analyze for cuts (pauses, filler words), pacing, audio recommendations, and trending formats.\n"
                "- **For trend questions:** Share current viral formats, sounds, hashtags, and what's getting traction.\n"
                "- **For specific questions:** Answer directly and conversationally without over-structuring.\n\n"
                
                "**Tone & Style:**\n"
                "- Conversational, friendly, and encouraging\n"
                "- Practical and specific (not generic advice)\n"
                "- Use emojis sparingly for emphasis\n"
                "- Keep responses concise unless detailed analysis is needed\n"
                "- Think like a creative partner, not a technical manual\n\n"
                
                "**Important:**\n"
                "- Only provide JSON-structured responses when analyzing uploaded videos\n"
                "- For general chat, respond naturally in markdown-friendly text\n"
                "- Ask clarifying questions if the request is vague\n"
                "- Tailor advice to the user's skill level and platform goals"
            )
            # Use GPT-4 as fallback due to GPT-5 timeout issues in 2025
            self.session_chats[session_id] = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=system_message or default_system
            ).with_model("openai", "gpt-4")
        
        return self.session_chats[session_id]
    
    async def analyze_video_with_trends(
        self,
        session_id: str,
        video_metadata: Dict,
        user_context: str,
        trending_formats: List[Dict],
        trending_hashtags: List[Dict]
    ) -> Dict:
        """Analyze video and generate suggestions based on trends."""
        try:
            chat = self._get_or_create_chat(session_id)
            
            # Construct detailed prompt
            prompt = self._construct_analysis_prompt(
                video_metadata,
                user_context,
                trending_formats,
                trending_hashtags
            )
            
            logger.info(f"Sending analysis request for video {video_metadata.get('id')}")
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse AI response
            suggestions = self._parse_ai_response(response, trending_formats)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            raise
    
    def _construct_analysis_prompt(
        self,
        video_metadata: Dict,
        user_context: str,
        trending_formats: List[Dict],
        trending_hashtags: List[Dict]
    ) -> str:
        """Construct detailed analysis prompt."""
        
        formats_summary = "\n".join([
            f"{i+1}. {f['name']}: {f['description']}\n   Structure: {f['structure']}\n   Performance: {f['performance_metrics']}"
            for i, f in enumerate(trending_formats[:3])
        ])
        
        hashtags_summary = ", ".join([h['hashtag'] for h in trending_hashtags[:10]])
        
        prompt = f"""
You are analyzing a video for content optimization.

**USER'S CONTEXT:**
{user_context}

**VIDEO INFO:**
- Filename: {video_metadata.get('filename')}
- Duration: {video_metadata.get('duration', 'unknown')} seconds
- Upload Date: {video_metadata.get('uploaded_at')}

**TOP TRENDING FORMATS RIGHT NOW:**
{formats_summary}

**TRENDING HASHTAGS:**
{hashtags_summary}

**YOUR TASK:**
Act as their personal director and analyze this video with actionable editing guidance.

1. **Recommend the BEST trending format** this content should follow (from the list above)
2. **Generate specific suggestions** focusing on:
   
   **PRIORITY: AUTO-CUT DETECTION**
   - Identify likely pauses, awkward silences, and filler words ("um", "uh", "like", "you know")
   - Suggest exact timestamps to cut these moments
   - Mark moments where pacing drags and needs tightening
   
   **THEN:**
   - Audio/BGM recommendations (trending background music that matches the content style)
   - Example videos (similar content doing well - with titles, creators, and why they work)
   - What additional content they should film to improve this video
   - Script rewrites or voice-over improvements
   - Text overlays to add (with exact timing)
   - Shot recommendations (what to re-record or emphasize)
   - Format structure (how to reorganize content)

**IMPORTANT:** Each suggestion must:
- Be specific and actionable (not generic advice)
- Include reasoning based on current trends
- Have a confidence score (0.0-1.0)
- Be something the user can accept or reject

**FOR AUDIO/BGM SUGGESTIONS:**
- Include "type": "audio" or "bgm"
- Provide specific song names and artists when possible
- Explain why this audio is trending and fits the content
- Include genre/mood/vibe of the audio

**FOR EXAMPLE VIDEO SUGGESTIONS:**
- Include "type": "example_video"
- Provide video title and creator name
- Explain what makes it successful (hook, pacing, format)
- Include key metrics if available (views, engagement rate)
- Explain how user can apply similar techniques

**FOR TIMESTAMP/CUT SUGGESTIONS (CRITICAL - GENERATE 4-6 OF THESE):**
- Include "timestamp" field with time in seconds (e.g., 5.0, 12.5, 30.0)
- Include "action" field: "CUT" (remove this), "TRIM" (shorten), "CUT_FILLER" (remove filler word), "CUT_PAUSE" (remove awkward silence)
- Be specific: "Cut 'um' at 12.5s", "Remove 3-second pause at 28.0s", "Trim rambling section 15-18s"
- Assume there are pauses and filler words in raw footage - actively look for them

Respond in this JSON format:
{{
  "recommended_format": {{
    "id": "format-id-from-list",
    "name": "Format Name",
    "reasoning": "Why this format fits their content"
  }},
  "suggestions": [
    {{
      "type": "audio|bgm|example_video|script|text_overlay|shot|timestamp|format",
      "title": "Brief title",
      "description": "What to do",
      "content": "Exact details (song name, video title, script, etc.)",
      "reasoning": "Why this will improve performance",
      "confidence_score": 0.85,
      "timestamp": 12.5,
      "action": "CUT",
      "video_url": "https://tiktok.com/@creator/video/123",
      "creator": "Creator name",
      "metrics": "1.2M views, 8.5% engagement"
    }}
  ]
}}

Provide 10-14 diverse suggestions including:
- 4-6 timestamp-based CUT suggestions (pauses, filler words, pacing issues) - PRIORITY
- 2-3 audio/BGM recommendations (trending sounds that match the vibe)
- 2-3 example videos (similar successful content with analysis)
- 1-2 "what to film next" suggestions (additional shots/content they should capture)
- 1-2 script/voiceover improvements
"""
        return prompt
    
    def _parse_ai_response(self, response: str, trending_formats: List[Dict]) -> Dict:
        """Parse AI response and structure it."""
        try:
            # Try to extract JSON from response
            response_text = response.strip()
            
            # Find JSON in response (AI might add text before/after)
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response_text[start:end]
                parsed = json.loads(json_str)
                
                # Validate and enrich response
                if "recommended_format" in parsed and "suggestions" in parsed:
                    # Find full format details
                    format_id = parsed["recommended_format"].get("id")
                    format_details = next(
                        (f for f in trending_formats if f["id"] == format_id),
                        trending_formats[0] if trending_formats else {}
                    )
                    
                    return {
                        "recommended_format": format_details,
                        "format_reasoning": parsed["recommended_format"].get("reasoning"),
                        "suggestions": parsed["suggestions"]
                    }
            
            # Fallback if parsing fails
            logger.warning("Failed to parse AI response as JSON, using fallback")
            return self._create_fallback_suggestions(trending_formats)
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._create_fallback_suggestions(trending_formats)
    
    def _create_fallback_suggestions(self, trending_formats: List[Dict]) -> Dict:
        """Create fallback suggestions if parsing fails."""
        return {
            "recommended_format": trending_formats[0] if trending_formats else {},
            "format_reasoning": "This format has the highest engagement rates currently.",
            "suggestions": [
                {
                    "type": "script",
                    "title": "Add Hook",
                    "description": "Start with attention-grabbing statement",
                    "content": "Open with 'Stop scrolling!' or surprising fact",
                    "reasoning": "First 3 seconds determine if viewers keep watching",
                    "confidence_score": 0.85
                },
                {
                    "type": "text_overlay",
                    "title": "Add Key Points",
                    "description": "Overlay text for main message",
                    "content": "Use bold text at 0:05, 0:15, 0:25",
                    "reasoning": "80% of TikTok is watched without sound",
                    "confidence_score": 0.90
                }
            ]
        }
    
    async def chat_with_context(
        self,
        session_id: str,
        message: str,
        video_context: Optional[Dict] = None
    ) -> str:
        """Handle conversational chat with context."""
        try:
            chat = self._get_or_create_chat(session_id)
            
            # Enhance message with context
            enhanced_message = message
            
            # Add video context if provided
            if video_context:
                context_note = (
                    f"\n\n[Context: User has uploaded a video called '{video_context.get('filename')}'. "
                    f"They may be asking about this video or general content advice.]\n\n"
                )
                enhanced_message = context_note + message
            
            # Detect question type and add guidance
            message_lower = message.lower()
            
            if any(phrase in message_lower for phrase in ['what should i', 'give me ideas', 'content ideas', 'what to record', 'what to create', 'what can i']):
                guidance = (
                    "\n\n[User is asking for content ideas. Provide 3-5 creative, specific video concepts "
                    "with brief descriptions. Focus on viral formats and trending topics. Be inspiring and practical.]\n\n"
                )
                enhanced_message = guidance + enhanced_message
            
            elif any(phrase in message_lower for phrase in ['trending', 'what\'s viral', 'what\'s hot', 'popular']):
                guidance = (
                    "\n\n[User wants trend insights. Share current viral formats, trending sounds/audio, "
                    "popular hashtags, and what's performing well right now.]\n\n"
                )
                enhanced_message = guidance + enhanced_message
            
            elif any(phrase in message_lower for phrase in ['how to film', 'how do i shoot', 'recording tips', 'filming']):
                guidance = (
                    "\n\n[User needs recording/filming advice. Provide practical shooting tips, "
                    "equipment suggestions, lighting, framing, and technical guidance.]\n\n"
                )
                enhanced_message = guidance + enhanced_message
            
            user_message = UserMessage(text=enhanced_message)
            response = await chat.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise

# Global instance
ai_service = AIContentAnalyzer()