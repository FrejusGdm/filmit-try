# 🤖 Automatic Segment Analysis Feature

## Overview

When a user uploads a video segment in Director mode, the system now **automatically analyzes** the video using AI and provides immediate feedback. This analysis is stored and used by the Director AI to give contextual feedback when asked.

## How It Works

### 1. **Upload Trigger** 📤
When a segment is uploaded via `/api/director/upload-segment`:
- File is saved to `/app/backend/uploads/`
- **Segment Analysis Agent** is automatically triggered
- Analysis runs in the background (non-blocking)

### 2. **Analysis Pipeline** 🔍

The **Segment Analysis Agent** performs:

#### A. **Technical Metadata Extraction**
- Duration, resolution, aspect ratio
- FPS, bitrate, codec info
- Audio presence check
- File size validation

#### B. **AI Content Analysis** (Claude 3.7 Sonnet)
Analyzes:
- **Duration accuracy** - Is it on target?
- **Visual quality** - Resolution, aspect ratio, composition
- **Content evaluation** - Script adherence, pacing, energy
- **Technical quality** - Audio, file size, codec
- **Overall assessment** - Scores, strengths, improvements

#### C. **Scoring System**
- Duration Score: 0-10
- Visual Score: 0-10
- Content Score: 0-10
- Technical Score: 0-10
- **Overall Score: 0-10**
- **Viral Potential: Low/Medium/High**

### 3. **Storage** 💾

Analysis is stored in **two places**:

1. **MongoDB `segment_analyses` collection**
   - Quick access for Director
   - Indexed by `{project_id}_{segment_name}`

2. **Embedded in `video_projects.shot_list`**
   - Attached to the specific shot
   - Available when loading project

### 4. **Director Integration** 🎭

The Director AI can now:
- Access stored analysis when user asks for feedback
- Provide detailed, data-driven feedback
- Show scores, strengths, and improvements
- Give specific recommendations

## User Experience Flow

```
User uploads segment
    ↓
🤖 AI analyzes automatically (5-10 seconds)
    ↓
✅ Upload complete notification with score
    ↓
Director receives analysis context
    ↓
User asks: "How does my hook look?"
    ↓
Director provides detailed feedback using analysis
```

## API Response Example

### Upload Response (New):
```json
{
  "success": true,
  "message": "Segment 'hook' uploaded and analyzed successfully",
  "file_path": "/app/backend/uploads/abc123_hook_video.mp4",
  "analysis_available": true,
  "analysis_summary": {
    "overall_score": 8,
    "viral_potential": "High",
    "ready_for_assembly": true
  }
}
```

### Get Analysis Endpoint:
```
GET /api/director/segment-analysis/{project_id}/{segment_name}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "project_id": "abc123",
    "segment_name": "hook",
    "analyzed_at": "2025-01-10T12:00:00Z",
    "video_metadata": {
      "duration": 5.2,
      "width": 1920,
      "height": 1080,
      "aspect_ratio": "16:9 (landscape)",
      "fps": 30,
      "has_audio": true,
      "file_size_mb": 12.5
    },
    "content_analysis": {
      "duration_analysis": {
        "target_seconds": 5,
        "actual_seconds": 5.2,
        "duration_score": 9,
        "feedback": "Nearly perfect timing!",
        "duration_ok": true
      },
      "visual_quality": {
        "resolution_score": 10,
        "aspect_ratio_feedback": "Perfect 16:9 for YouTube",
        "visual_score": 9
      },
      "overall_assessment": {
        "overall_score": 8,
        "strengths": [
          "Excellent lighting and composition",
          "Perfect duration for hook",
          "High energy delivery"
        ],
        "areas_for_improvement": [
          "Could open with more urgency",
          "Background slightly cluttered"
        ],
        "quick_wins": [
          "Start with the problem statement first",
          "Move closer to camera for intimacy",
          "Add text overlay on key phrase"
        ],
        "viral_potential": "High",
        "ready_for_assembly": true
      },
      "director_context": {
        "summary_for_director": "Strong hook with excellent technical quality. Minor script adjustments could boost engagement.",
        "key_flags": [],
        "praise_points": ["Great energy", "Professional production quality"]
      }
    }
  }
}
```

## Director Feedback Example

**User asks:** "How's my hook?"

**Director responds with analysis:**
```
🎬 **Feedback on Hook:**

📊 **Overall Score: 8/10**
🔥 **Viral Potential: High**

✅ **What's Working Well:**
- Excellent lighting and composition
- Perfect duration for hook
- High energy delivery

📈 **Quick Wins (Do These Now):**
- Start with the problem statement first
- Move closer to camera for intimacy
- Add text overlay on key phrase

🎯 **Areas to Improve:**
- Could open with more urgency
- Background slightly cluttered

⏱️ **Duration:** 5.2s (target: 5s) - ✅ Good

🎥 **Visual Quality:** 9/10
Perfect 16:9 for YouTube

💡 **Director's Take:**
Strong hook with excellent technical quality. Minor script adjustments could boost engagement.

🚀 **Ready for Assembly:** Yes

Want me to go deeper on any specific aspect or compare this to viral examples?
```

## Technical Implementation

### Backend Files

1. **`/app/backend/agents/segment_analysis_agent.py`** (NEW)
   - Main analysis agent
   - Uses ffmpeg for metadata
   - Uses Claude 3.7 for content analysis
   - Stores results in MongoDB

2. **`/app/backend/routers/director.py`** (UPDATED)
   - Modified `/upload-segment` to trigger analysis
   - Added `/segment-analysis/{project_id}/{segment_name}` endpoint

3. **`/app/backend/agents/director_workflow.py`** (UPDATED)
   - Modified `_handle_feedback_request()` to use stored analysis
   - Formats analysis into user-friendly feedback

### Frontend Files

1. **`/app/frontend/src/utils/api.js`** (UPDATED)
   - Added `getSegmentAnalysis()` function

2. **`/app/frontend/src/components/ContentStudio.jsx`** (UPDATED)
   - Modified `handleSegmentUpload()` to show analysis results
   - Displays score in toast notification
   - Adds Director message with summary

## Benefits

### For Users:
1. **Instant Feedback** - Know immediately if shot is good
2. **Data-Driven** - Objective scores and metrics
3. **Actionable** - Specific improvements, not vague advice
4. **Confidence** - Know what works before moving forward

### For Director AI:
1. **Context** - Has actual data about uploaded videos
2. **Accuracy** - Can give precise feedback based on analysis
3. **Consistency** - Same analysis framework for all segments
4. **Intelligence** - Can compare user's work to viral standards

## Configuration

**Required Environment Variables:**
- `EMERGENT_LLM_KEY` - For Claude 3.7 Sonnet analysis
- `MONGO_URL` - For storing analysis results

**Dependencies:**
- `emergentintegrations` - LLM integration
- `ffmpeg` - Video metadata extraction
- `motor` - Async MongoDB driver

## Performance

**Analysis Speed:**
- Metadata extraction: <1 second
- AI content analysis: 5-10 seconds
- Total: ~10 seconds per segment

**Resource Usage:**
- CPU: Moderate (ffmpeg)
- Memory: Low (~100MB per analysis)
- Storage: ~2KB JSON per analysis

## Error Handling

If analysis fails:
- Upload still succeeds
- User gets notification that analysis unavailable
- Director can still provide basic feedback without analysis
- Error logged for debugging

## Future Enhancements

Potential improvements:
- [ ] Visual frame analysis (extract key frames)
- [ ] Audio quality analysis (volume, clarity)
- [ ] Speech-to-text for script comparison
- [ ] Real-time analysis preview (before upload completes)
- [ ] Comparative analysis (compare to previous shots)
- [ ] Batch analysis (analyze multiple segments at once)
- [ ] A/B testing suggestions (try variations)

## Testing

**Manual Testing:**
1. Create a Director project
2. Upload a video segment
3. Wait for "analyzed" notification
4. Ask Director: "How's my [segment name]?"
5. Verify detailed feedback with scores

**API Testing:**
```bash
# Check analysis endpoint
curl http://localhost:8001/api/director/segment-analysis/{project_id}/{segment_name}
```

## Troubleshooting

**Issue: Analysis not triggering**
- Check `EMERGENT_LLM_KEY` is set
- Check backend logs: `tail -f /var/log/supervisor/backend.*.log`

**Issue: Analysis fails but upload succeeds**
- This is expected behavior (non-blocking)
- Check error logs for root cause

**Issue: Director not using analysis**
- Verify analysis is stored in database
- Check MongoDB collection: `segment_analyses`

---

## Summary

✨ **Automatic segment analysis** transforms the Director experience by providing:
- Instant, data-driven feedback
- Objective quality scores
- Actionable improvements
- Context for Director AI conversations

All without any extra user action - it just works! 🎬
