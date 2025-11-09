from fastapi import APIRouter, HTTPException
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

from schemas.suggestion import (
    SuggestionActionRequest,
    SuggestionResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Get DB from environment
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.get("/{video_id}")
async def get_suggestions(video_id: str):
    """Get all suggestions for a video."""
    try:
        suggestions = await db.suggestions.find(
            {"video_id": video_id},
            {"_id": 0}
        ).to_list(100)
        
        if not suggestions:
            raise HTTPException(status_code=404, detail="No suggestions found for this video")
        
        return {"suggestions": suggestions, "count": len(suggestions)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/action")
async def handle_suggestion_action(request: SuggestionActionRequest):
    """Accept or reject a suggestion."""
    try:
        # Find the suggestions document containing this suggestion
        suggestions_doc = await db.suggestions.find_one(
            {"suggestions.id": request.suggestion_id},
            {"_id": 0}
        )
        
        if not suggestions_doc:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        # Update the specific suggestion's status
        result = await db.suggestions.update_one(
            {"suggestions.id": request.suggestion_id},
            {
                "$set": {
                    "suggestions.$[elem].status": request.action + "ed",  # 'accepted' or 'rejected'
                    "suggestions.$[elem].feedback": request.feedback,
                    "suggestions.$[elem].updated_at": datetime.utcnow().isoformat()
                }
            },
            array_filters=[{"elem.id": request.suggestion_id}]
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update suggestion")
        
        # Get updated suggestion
        updated_doc = await db.suggestions.find_one(
            {"suggestions.id": request.suggestion_id},
            {"_id": 0}
        )
        
        updated_suggestion = next(
            (s for s in updated_doc["suggestions"] if s["id"] == request.suggestion_id),
            None
        )
        
        logger.info(f"Suggestion {request.suggestion_id} {request.action}ed")
        
        return {
            "success": True,
            "message": f"Suggestion {request.action}ed successfully",
            "updated_suggestion": updated_suggestion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling suggestion action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{video_id}")
async def get_suggestions_status(video_id: str):
    """Get status summary of all suggestions for a video."""
    try:
        suggestions_docs = await db.suggestions.find(
            {"video_id": video_id},
            {"_id": 0}
        ).to_list(100)
        
        if not suggestions_docs:
            raise HTTPException(status_code=404, detail="No suggestions found")
        
        # Aggregate status
        status_summary = {
            "pending": 0,
            "accepted": 0,
            "rejected": 0
        }
        
        all_suggestions = []
        for doc in suggestions_docs:
            for suggestion in doc["suggestions"]:
                all_suggestions.append(suggestion)
                status = suggestion.get("status", "pending")
                if status in status_summary:
                    status_summary[status] += 1
        
        return {
            "video_id": video_id,
            "total_suggestions": len(all_suggestions),
            "status_summary": status_summary,
            "suggestions": all_suggestions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting suggestions status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))