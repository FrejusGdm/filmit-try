from fastapi import APIRouter, HTTPException
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import uuid

from schemas.chat import ChatRequest, ChatResponse, ChatMessage
from services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Get DB from environment
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.post("/message")
async def send_chat_message(request: ChatRequest):
    """Send a chat message and get AI response."""
    try:
        # Save user message to DB
        user_message = ChatMessage(
            session_id=request.session_id,
            role="user",
            content=request.message,
            metadata=request.context
        )
        await db.chat_messages.insert_one(user_message.model_dump())
        
        # Get video context if video_id provided
        video_context = None
        if request.video_id:
            video = await db.videos.find_one({"id": request.video_id}, {"_id": 0})
            if video:
                video_context = video
        
        # Get AI response
        ai_response = await ai_service.chat_with_context(
            session_id=request.session_id,
            message=request.message,
            video_context=video_context
        )
        
        # Save assistant message to DB
        assistant_message = ChatMessage(
            session_id=request.session_id,
            role="assistant",
            content=ai_response,
            metadata={"video_id": request.video_id} if request.video_id else None
        )
        await db.chat_messages.insert_one(assistant_message.model_dump())
        
        logger.info(f"Chat message processed for session {request.session_id}")
        
        return ChatResponse(
            message_id=assistant_message.id,
            response=ai_response,
            timestamp=assistant_message.timestamp
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """Get chat history for a session."""
    try:
        messages = await db.chat_messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(limit)
        
        return {
            "session_id": session_id,
            "messages": messages,
            "count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session."""
    try:
        result = await db.chat_messages.delete_many({"session_id": session_id})
        
        return {
            "success": True,
            "message": f"Deleted {result.deleted_count} messages",
            "deleted_count": result.deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))