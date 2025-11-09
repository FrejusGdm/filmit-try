# 🎬 Conversational Director Agent - Technical Documentation

## Overview

The Director Agent has been completely redesigned from a rigid state machine to an intelligent, conversational AI that handles free-flowing conversations and delegates tasks to specialized sub-agents based on user intent.

## Architecture Changes

### Before (Rigid State Machine)
```
Initial → Format Match → Script Plan → Recording → Editing → Export → Done
```
- Linear, fixed workflow
- No flexibility
- No conversational ability
- No feedback on uploaded content

### After (Conversational + Task Delegation)
```
User Message → Intent Detection → Route to Specialized Agent → Response
```
- Free-flowing conversation
- Intelligent task routing
- Feedback on uploads
- Dynamic shot list modifications
- Context-aware responses

## New Specialized Agents

### 1. **Feedback Agent** (`feedback_agent.py`)

Analyzes uploaded video shots and provides constructive feedback.

**Capabilities:**
- Analyze individual shots
- Evaluate script adherence
- Assess visual quality
- Check pacing and energy
- Rate hook effectiveness
- Provide improvement suggestions
- Compare to reference videos

**Methods:**
```python
async def analyze_shot(
    segment_name, script, visual_guide, 
    duration_target, file_path=None
) -> Dict[str, Any]

async def compare_to_examples(
    segment_name, user_video_description, 
    reference_videos
) -> Dict[str, Any]
```

**Response Format:**
```
SCORES:
- Script: 8/10
- Visual: 7/10
- Pacing: 9/10
- Overall: 8/10

FEEDBACK:
[Detailed analysis]

QUICK WINS:
[3 actionable improvements]
```

### 2. **Shot List Manager** (`shot_list_manager.py`)

Dynamically creates, modifies, and manages shot lists based on user requests.

**Capabilities:**
- Add new shots
- Remove shots
- Modify scripts
- Update visual guides
- Reorder shots
- Suggest improvements

**Methods:**
```python
async def modify_shot_list(
    current_shot_list, user_request, 
    format_context=None
) -> Dict[str, Any]

async def add_shot(...) -> List[Dict]
async def remove_shot(...) -> List[Dict]
async def update_shot_script(...) -> List[Dict]
async def reorder_shots(...) -> List[Dict]
```

**Use Cases:**
- "Can you add a testimonial segment?"
- "Remove the problem section, it's too long"
- "Change the hook script to be more exciting"
- "Make the demo shorter, like 10 seconds"

### 3. **Director Agent** (Updated - `director_workflow.py`)

Main orchestrator with conversational AI and intent detection.

**New Capabilities:**
- Detect user intent from natural language
- Route to appropriate specialized agent
- Maintain conversation context
- Provide contextual responses
- Handle multiple types of requests

## Intent Detection System

The Director analyzes each user message and classifies intent:

### Intent Types

1. **feedback_request**
   - Keywords: "feedback", "how does", "what do you think", "review", "analyze"
   - Routes to: Feedback Agent
   - Example: "Can you give me feedback on the hook shot?"

2. **modify_shot_list**
   - Keywords: "add", "remove", "change", "modify", "different", "instead"
   - Routes to: Shot List Manager
   - Example: "Add a customer testimonial segment"

3. **project_status**
   - Keywords: "status", "progress", "what's left", "done", "remaining"
   - Routes to: Project Overview
   - Example: "What's my project status?"

4. **recording_guidance**
   - Keywords: "how to film", "recording tips", "camera setup", "what's next"
   - Routes to: Recording Guide
   - Example: "What should I record next?"

5. **general_question**
   - Everything else
   - Routes to: Conversational Response
   - Example: "What makes a good hook?"

### Intent Detection Flow

```python
async def _detect_intent(user_message, state) -> Dict[str, Any]:
    # Use LLM to analyze message
    # Return: {"type": "intent_type", "segment": "name", "details": "..."}
```

## Conversational Flow Examples

### Example 1: Requesting Feedback

**User:** "Can you give me feedback on the hook?"

**Director Process:**
1. Detect intent: `feedback_request`
2. Find hook shot in shot list
3. Call Feedback Agent
4. Return detailed analysis with scores

**Response:**
```
🎬 Feedback on Hook:

SCORES:
- Script: 8/10
- Visual: 7/10  
- Pacing: 9/10
- Overall: 8/10

FEEDBACK:
Your hook has great energy! The first 3 seconds grab attention
well. However, the lighting could be improved - consider using
natural light or a ring light.

QUICK WINS:
1. Retake with better lighting
2. Speak 10% faster for more energy
3. Add a hand gesture in the first second

Want me to suggest improvements or analyze another shot?
```

### Example 2: Modifying Shot List

**User:** "Can you make the demo section shorter? Like 15 seconds instead of 30?"

**Director Process:**
1. Detect intent: `modify_shot_list`
2. Call Shot List Manager
3. Update demo shot duration
4. Regenerate script for 15s

**Response:**
```
✏️ Shot List Updated:

I've shortened the demo from 30s to 15s. Here's the new approach:

OLD (30s): Detailed walkthrough of all features
NEW (15s): Focus on the ONE most impressive feature

Updated script:
"Watch this - [show killer feature] - that's it. 
Simple, powerful, done."

The shot list has been updated in the left panel. 
This tighter format will actually perform better on TikTok!
```

### Example 3: Project Status

**User:** "What's my progress?"

**Director Process:**
1. Detect intent: `project_status`
2. Count uploaded vs total shots
3. Call Feedback Agent for overall assessment
4. Provide next steps

**Response:**
```
📊 Project Status:

**Progress:** 3/6 shots uploaded (50%)

**Completed:**
✅ Hook - Great energy and pacing!
✅ Problem - Clear and relatable
✅ Solution - Compelling pitch

**Still Needed:**
⏳ Demo (Required) - This is critical!
⏳ Traction (Required) - Build credibility
⏳ Call to Action (Required) - Drive conversions

**Next Step:** 
Record the Demo shot (15 seconds). This is the heart
of your video - show don't tell!

**Estimated Time:** ~30 minutes to complete all shots
```

### Example 4: Recording Guidance

**User:** "How should I film the demo?"

**Director Process:**
1. Detect intent: `recording_guidance`
2. Find demo shot in list
3. Provide detailed filming instructions

**Response:**
```
🎥 Recording Guide for Demo:

**Duration Target:** 15 seconds

**What to Say:**
"Watch this - [show killer feature] - that's it. 
Simple, powerful, done."

**How to Film:**
Screen recording of the feature in action.
Keep it fast-paced - one impressive feature only.

**Pro Tips:**
• Film in good natural light or use a ring light
• Hold phone steady or use tripod
• Speak with energy and confidence
• Do 2-3 takes and pick the best one
• Check audio levels - voice should be clear

Need help with something specific? Just ask!
```

## Frontend Integration

### Quick Action Buttons

Added to Content Studio chat interface:

```jsx
📊 Project Status
🎥 What's Next?
✨ Review Uploads (shows after uploads)
```

### "Get Feedback" Button

Added to each uploaded shot in shot list:
- Click to automatically request feedback
- Sends message: "Can you give me feedback on [shot]?"
- Director analyzes and responds

### Visual Implementation

```jsx
{shot.uploaded && (
  <button onClick={/* Auto-send feedback request */}>
    Get Feedback
  </button>
)}
```

## Key Improvements

### 1. **Natural Conversation**
- No more rigid commands
- Users can ask questions naturally
- Director understands intent

### 2. **Intelligent Delegation**
- Automatically routes to right agent
- No manual agent selection
- Context-aware responses

### 3. **Feedback System**
- Analyze uploaded shots
- Provide constructive criticism
- Suggest specific improvements
- Reference viral video best practices

### 4. **Dynamic Shot Lists**
- Add/remove shots on the fly
- Modify scripts based on feedback
- Adjust durations
- Reorder segments

### 5. **Project Tracking**
- Always knows what's done vs needed
- Prioritizes required shots
- Estimates time to completion

## Technical Details

### LLM Configuration

All agents use Claude 3.7 Sonnet via emergentintegrations:

```python
llm = LlmChat(
    api_key=self.api_key,
    session_id=unique_id,
    system_message=specialized_prompt
).with_model("anthropic", "claude-3-7-sonnet-20250219")
```

### State Management

Director maintains state:
```python
{
    "project_id": "uuid",
    "messages": [HumanMessage, AIMessage, ...],
    "shot_list": [...],
    "matched_format": {...},
    "current_step": "script_planned",
    "uploaded_segments": [...]
}
```

### Database Persistence

Project state saved to MongoDB after each interaction:
```python
await self._save_project_state(state)
```

## Example Conversations

### Natural Back-and-Forth

**User:** "Hey, I'm ready to start filming"
**Director:** "Awesome! Let's start with the hook..."

**User:** "I filmed it but not sure it's good"
**Director:** "Upload it and I'll give you feedback!"

**User:** *uploads hook*
**Director:** "Nice! The energy is great, but..."

**User:** "Should I redo it?"
**Director:** "Let's see the other shots first..."

### Asking for Help

**User:** "The demo is too long, what should I do?"
**Director:** *Modifies shot list* "I've shortened it to 15s..."

**User:** "Can you show me what to say?"
**Director:** *Provides new script*

**User:** "Perfect! What's next?"
**Director:** "Now film the traction segment..."

## System Prompts

### Director (Conversational)
```
You are an AI Director for Trendle - a conversational 
video creation coach.

Be:
- Conversational and warm
- Specific and actionable  
- Encouraging but honest
- Reference viral video best practices

You're their coach and partner in creating viral content.
```

### Feedback Agent
```
You are a viral video coach and expert analyzer.

Provide:
1. Honest, constructive feedback
2. Specific, actionable suggestions
3. Reference to viral patterns
4. Encouragement with realism

Focus on: hook effectiveness, pacing, visual quality, 
script delivery, viral format adherence.
```

### Shot List Manager
```
You are a shot list expert for viral videos.

When modifying:
- Understand user intent
- Make smart modifications
- Maintain format integrity
- Explain your reasoning
```

## Future Enhancements

### 1. **Video Analysis**
- Actually analyze uploaded video files (not just metadata)
- Use computer vision for composition analysis
- Detect pacing from video timeline

### 2. **Reference Comparison**
- Pull actual viral videos from TikTok/YouTube
- Side-by-side comparison
- Extract timing and hook patterns

### 3. **Multi-Shot Feedback**
- Analyze how shots flow together
- Check transition smoothness
- Ensure story coherence

### 4. **Learning System**
- Track what feedback leads to improvements
- Learn user's style preferences
- Adapt suggestions over time

### 5. **Collaborative Sessions**
- Multiple users in same project
- Real-time feedback from team
- Version control for shot lists

## Testing

### Test Cases

1. **Feedback Request**
```bash
curl -X POST /api/director/message \
  -d '{"project_id": "...", 
       "message": "Give me feedback on the hook"}'
```

2. **Shot List Modification**
```bash
curl -X POST /api/director/message \
  -d '{"project_id": "...", 
       "message": "Make the demo 15 seconds"}'
```

3. **Project Status**
```bash
curl -X POST /api/director/message \
  -d '{"project_id": "...", 
       "message": "What\'s my progress?"}'
```

4. **General Question**
```bash
curl -X POST /api/director/message \
  -d '{"project_id": "...", 
       "message": "What makes a good hook?"}'
```

## Files Modified

### New Files
- `/app/backend/agents/feedback_agent.py` - Feedback analysis
- `/app/backend/agents/shot_list_manager.py` - Dynamic shot list management

### Updated Files
- `/app/backend/agents/director_workflow.py` - Conversational director with intent detection
- `/app/frontend/src/components/ContentStudio.jsx` - Quick actions + feedback buttons

## Summary

The Director is now a true conversational AI partner that:
- ✅ Understands natural language
- ✅ Detects user intent
- ✅ Delegates to specialized agents
- ✅ Provides feedback on uploads
- ✅ Modifies shot lists dynamically
- ✅ Maintains conversation context
- ✅ Tracks project progress
- ✅ Offers guidance throughout

It's no longer a rigid tool - it's a creative partner! 🎬
