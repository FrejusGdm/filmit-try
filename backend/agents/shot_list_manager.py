"""
Shot List Manager - Dynamically create, modify, and manage shot lists.
Handles user requests to add/remove/modify shots based on feedback.
"""

from typing import Dict, Any, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage


class ShotListManager:
    """
    Manages shot list modifications dynamically.
    Can add new shots, remove shots, modify scripts, adjust durations, etc.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def modify_shot_list(
        self,
        current_shot_list: List[Dict[str, Any]],
        user_request: str,
        format_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Modify shot list based on user request.
        
        Args:
            current_shot_list: Current list of shots
            user_request: User's modification request
            format_context: Viral format being followed (optional)
        
        Returns:
            Updated shot list and explanation
        """
        
        llm = LlmChat(
            api_key=self.api_key,
            session_id="shot_list_modifier",
            system_message=self._get_modifier_prompt()
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        # Build current state summary
        current_summary = self._format_shot_list_summary(current_shot_list)
        
        modification_request = f"""Modify this shot list based on user request:

**Current Shot List:**
{current_summary}

**User Request:**
{user_request}

{f"**Format Context:** {format_context['name']}" if format_context else ""}

Respond with:
1. What specific changes to make
2. Why these changes improve the video
3. Updated shot list in JSON format

Format each shot as:
{{
  "segment_name": "name",
  "duration": seconds,
  "script": "script text",
  "visual_guide": "filming guide",
  "required": true/false,
  "uploaded": false
}}"""

        response = await llm.send_message(UserMessage(text=modification_request))
        
        # Parse response to extract updated shot list
        # For now, return response - in production, would parse JSON properly
        return {
            "original_count": len(current_shot_list),
            "modification_explanation": response,
            "updated_shot_list": current_shot_list,  # Would be parsed from LLM response
            "changes_made": self._detect_changes(current_shot_list, current_shot_list)
        }
    
    async def add_shot(
        self,
        shot_list: List[Dict[str, Any]],
        segment_name: str,
        duration: int,
        script: str,
        visual_guide: str,
        position: Optional[int] = None,
        required: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Add a new shot to the list.
        
        Args:
            shot_list: Current shot list
            segment_name: Name for new segment
            duration: Duration in seconds
            script: Script text
            visual_guide: Filming instructions
            position: Where to insert (None = end)
            required: Whether shot is required
        
        Returns:
            Updated shot list
        """
        new_shot = {
            "segment_name": segment_name,
            "duration": duration,
            "script": script,
            "visual_guide": visual_guide,
            "required": required,
            "uploaded": False
        }
        
        if position is None:
            shot_list.append(new_shot)
        else:
            shot_list.insert(position, new_shot)
        
        return shot_list
    
    async def remove_shot(
        self,
        shot_list: List[Dict[str, Any]],
        segment_name: str
    ) -> List[Dict[str, Any]]:
        """
        Remove a shot from the list.
        
        Args:
            shot_list: Current shot list
            segment_name: Name of segment to remove
        
        Returns:
            Updated shot list
        """
        return [shot for shot in shot_list if shot["segment_name"] != segment_name]
    
    async def update_shot_script(
        self,
        shot_list: List[Dict[str, Any]],
        segment_name: str,
        new_script: str
    ) -> List[Dict[str, Any]]:
        """
        Update script for a specific shot.
        
        Args:
            shot_list: Current shot list
            segment_name: Segment to update
            new_script: New script text
        
        Returns:
            Updated shot list
        """
        for shot in shot_list:
            if shot["segment_name"] == segment_name:
                shot["script"] = new_script
        
        return shot_list
    
    async def reorder_shots(
        self,
        shot_list: List[Dict[str, Any]],
        new_order: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Reorder shots based on segment names.
        
        Args:
            shot_list: Current shot list
            new_order: List of segment names in desired order
        
        Returns:
            Reordered shot list
        """
        shot_dict = {shot["segment_name"]: shot for shot in shot_list}
        reordered = []
        
        for name in new_order:
            if name in shot_dict:
                reordered.append(shot_dict[name])
        
        # Add any shots not in new_order at the end
        for shot in shot_list:
            if shot["segment_name"] not in new_order:
                reordered.append(shot)
        
        return reordered
    
    def _format_shot_list_summary(self, shot_list: List[Dict[str, Any]]) -> str:
        """Format shot list for display"""
        summary = []
        for i, shot in enumerate(shot_list, 1):
            status = "✅" if shot.get("uploaded") else "⏳"
            required = "Required" if shot.get("required") else "Optional"
            summary.append(
                f"{i}. {status} {shot['segment_name'].replace('_', ' ').title()} "
                f"({shot['duration']}s, {required})\n"
                f"   Script: {shot['script'][:60]}...\n"
                f"   Visual: {shot['visual_guide'][:60]}..."
            )
        return "\n".join(summary)
    
    def _detect_changes(
        self,
        old_list: List[Dict[str, Any]],
        new_list: List[Dict[str, Any]]
    ) -> List[str]:
        """Detect what changed between two shot lists"""
        changes = []
        
        if len(old_list) != len(new_list):
            changes.append(f"Shot count changed: {len(old_list)} → {len(new_list)}")
        
        # More detailed change detection would go here
        
        return changes
    
    def _get_modifier_prompt(self) -> str:
        """System prompt for shot list modifier"""
        return """You are a shot list expert for viral videos. Your job is to:

1. **Understand user intent** - What do they want to change and why?
2. **Make smart modifications** - Adjust the shot list to improve the video
3. **Maintain format integrity** - Keep the viral format structure intact
4. **Explain your reasoning** - Help user understand why changes work

When modifying:
- Add shots if they enhance the story
- Remove shots if they're redundant or hurt pacing
- Adjust durations to match viral video best practices
- Rewrite scripts to be more engaging and hook-focused
- Ensure visual guides are clear and actionable

Always preserve the core viral format structure while being flexible to user needs."""


async def suggest_shot_improvements(
    api_key: str,
    shot: Dict[str, Any],
    user_concern: str
) -> str:
    """
    Suggest improvements for a specific shot based on user concern.
    
    Args:
        api_key: LLM API key
        shot: The shot to improve
        user_concern: User's concern or feedback
    
    Returns:
        Improvement suggestions
    """
    
    llm = LlmChat(
        api_key=api_key,
        session_id="shot_improvement",
        system_message="You are a shot improvement expert."
    ).with_model("anthropic", "claude-3-7-sonnet-20250219")
    
    request = f"""The user has concerns about this shot:

**Shot:** {shot['segment_name'].replace('_', ' ').title()}
**Current Script:** {shot['script']}
**Visual Guide:** {shot['visual_guide']}
**Duration:** {shot['duration']}s

**User's Concern:**
{user_concern}

Provide:
1. Alternative script options (2-3 variants)
2. Visual filming tips to address concern
3. Duration adjustment recommendations if needed
4. Why these changes will work better

Be specific and actionable."""

    response = await llm.send_message(UserMessage(text=request))
    return response
