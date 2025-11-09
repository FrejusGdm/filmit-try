from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

from schemas.video import (
    VideoUploadChunk,
    VideoMetadata,
    VideoResponse,
    VideoAnalysisRequest
)
from services.video_service import video_service
from services.tiktok_service import tiktok_service
from services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Get DB from environment
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.post("/upload-chunk")
async def upload_video_chunk(chunk: VideoUploadChunk):
    """Handle chunked video upload."""
    try:
        result = await video_service.handle_chunk(
            session_id=chunk.session_id,
            filename=chunk.filename,
            chunk_index=chunk.chunk_index,
            total_chunks=chunk.total_chunks,
            chunk_data=chunk.chunk_data
        )
        
        # If upload completed, save metadata to DB
        if result["status"] == "completed":
            video_metadata = VideoMetadata(
                session_id=chunk.session_id,
                filename=chunk.filename,
                file_path=result["file_path"],
                file_size=0,  # Will update after getting file info
                mime_type="video/mp4"
            )
            
            # Get actual file info
            file_info = await video_service.get_video_info(result["file_path"])
            video_metadata.file_size = file_info["file_size"]
            
            # Save to DB
            doc = video_metadata.model_dump()
            await db.videos.insert_one(doc)
            
            logger.info(f"Video uploaded and saved: {video_metadata.id}")
            
            return {
                **result,
                "video_id": video_metadata.id,
                "video_metadata": video_metadata.model_dump()
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error uploading chunk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/{session_id}")
async def list_videos(session_id: str):
    """List all videos for a session."""
    try:
        videos = await db.videos.find(
            {"session_id": session_id},
            {"_id": 0}
        ).to_list(100)
        
        return {"videos": videos, "count": len(videos)}
        
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{video_id}")
async def get_video(video_id: str):
    """Get video by ID."""
    try:
        video = await db.videos.find_one({"id": video_id}, {"_id": 0})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return video
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_video(request: VideoAnalysisRequest):
    """Analyze video and generate AI suggestions."""
    try:
        # Get video metadata
        video = await db.videos.find_one({"id": request.video_id}, {"_id": 0})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Update status
        await db.videos.update_one(
            {"id": request.video_id},
            {"$set": {"analysis_status": "analyzing"}}
        )
        
        # Get trending data
        logger.info("Fetching trending hashtags and formats...")
        trending_hashtags = await tiktok_service.get_trending_hashtags(limit=20)
        trending_formats = await tiktok_service.get_trending_formats()
        
        # Prepare user context
        user_context = request.user_context or "Content creator looking to optimize video for TikTok"
        if request.target_audience:
            user_context += f" | Target audience: {request.target_audience}"
        
        # AI analysis
        logger.info(f"Starting AI analysis for video {request.video_id}...")
        analysis_result = await ai_service.analyze_video_with_trends(
            session_id=video["session_id"],
            video_metadata=video,
            user_context=user_context,
            trending_formats=trending_formats,
            trending_hashtags=trending_hashtags
        )
        
        # Save suggestions to DB
        from schemas.suggestion import VideoSuggestions, SuggestionItem
        import uuid
        
        # Add IDs to individual suggestions
        suggestions_with_ids = []
        for suggestion in analysis_result["suggestions"]:
            suggestion_with_id = {
                "id": str(uuid.uuid4()),
                "type": suggestion.get("type", "unknown"),
                "title": suggestion.get("title", ""),
                "description": suggestion.get("description", ""),
                "content": suggestion.get("content", ""),
                "reasoning": suggestion.get("reasoning", ""),
                "confidence_score": suggestion.get("confidence_score", 0.5),
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "timestamp": suggestion.get("timestamp"),  # For video editing
                "action": suggestion.get("action"),  # CUT, TRIM, ADD_TEXT, etc.
                "video_url": suggestion.get("video_url"),  # For example videos
                "creator": suggestion.get("creator"),  # For example videos
                "metrics": suggestion.get("metrics")  # For example videos
            }
            suggestions_with_ids.append(suggestion_with_id)
        
        suggestions_doc = {
            "id": str(uuid.uuid4()),
            "video_id": request.video_id,
            "session_id": video["session_id"],
            "trending_format_used": analysis_result["recommended_format"].get("name", "Unknown"),
            "format_description": analysis_result.get("format_reasoning", ""),
            "suggestions": suggestions_with_ids,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.suggestions.insert_one(suggestions_doc)
        
        # Update video status
        await db.videos.update_one(
            {"id": request.video_id},
            {"$set": {"analysis_status": "completed"}}
        )
        
        logger.info(f"Analysis completed for video {request.video_id}")
        
        return {
            "success": True,
            "video_id": request.video_id,
            "suggestions_id": suggestions_doc["id"],
            "recommended_format": analysis_result["recommended_format"],
            "format_reasoning": analysis_result.get("format_reasoning"),
            "suggestions": analysis_result["suggestions"],
            "trending_hashtags_used": trending_hashtags[:10]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        # Update status to failed
        await db.videos.update_one(
            {"id": request.video_id},
            {"$set": {"analysis_status": "failed"}}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """Delete a video."""
    try:
        video = await db.videos.find_one({"id": video_id}, {"_id": 0})
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Delete file
        await video_service.delete_video(video["file_path"])
        
        # Delete from DB
        await db.videos.delete_one({"id": video_id})
        await db.suggestions.delete_many({"video_id": video_id})
        
        return {"success": True, "message": "Video deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))