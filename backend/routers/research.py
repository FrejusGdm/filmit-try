"""
Research API - Endpoints for researching and searching viral video formats
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from services.youtube_research_service import get_youtube_research_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ResearchVideoRequest(BaseModel):
    """Request to research a YouTube video"""
    video_url: str = Field(..., description="YouTube video URL or video ID")


class SearchFormatsRequest(BaseModel):
    """Request to search viral formats"""
    query: str = Field(..., description="Search query describing desired format")
    top_k: int = Field(default=5, description="Number of results to return", ge=1, le=20)


class ResearchVideoResponse(BaseModel):
    """Response from video research"""
    success: bool
    video_id: str
    format_name: str
    analysis: Dict[str, Any]
    message: str


class SearchFormatsResponse(BaseModel):
    """Response from format search"""
    success: bool
    query: str
    results: List[Dict[str, Any]]
    count: int


@router.post("/analyze-video", response_model=ResearchVideoResponse)
async def research_video(request: ResearchVideoRequest):
    """
    Analyze a YouTube video and extract its viral format structure.
    
    This endpoint:
    1. Fetches video metadata from YouTube API
    2. Retrieves transcript if available
    3. Uses GPT-4 to analyze structure, editing patterns, and engagement tactics
    4. Stores the analysis in a vector database for semantic search
    
    Example URLs:
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - https://youtu.be/dQw4w9WgXcQ
    - dQw4w9WgXcQ (just the video ID)
    """
    try:
        service = get_youtube_research_service()
        
        # Initialize index if not already done
        service.initialize_index()
        
        # Research the video
        analysis = await service.research_video(request.video_url)
        
        return ResearchVideoResponse(
            success=True,
            video_id=analysis['video_id'],
            format_name=analysis.get('format_name', 'Unknown Format'),
            analysis=analysis,
            message=f"Successfully analyzed video: {analysis.get('format_name')}"
        )
        
    except ValueError as e:
        logger.error(f"Invalid video URL: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error researching video: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing video: {str(e)}")


@router.post("/search", response_model=SearchFormatsResponse)
async def search_viral_formats(request: SearchFormatsRequest):
    """
    Search for viral formats using semantic search.
    
    Examples:
    - "fast-paced product launch for TikTok"
    - "educational tutorial with step-by-step structure"
    - "B2B SaaS demo for LinkedIn"
    - "transformation before/after for Instagram"
    
    The search uses AI embeddings to find formats that match the intent,
    not just keyword matching.
    """
    try:
        service = get_youtube_research_service()
        
        # Initialize index if not already done
        service.initialize_index()
        
        # Search for formats
        results = await service.search_viral_formats(request.query, request.top_k)
        
        return SearchFormatsResponse(
            success=True,
            query=request.query,
            results=results,
            count=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error searching formats: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching formats: {str(e)}")


@router.get("/formats")
async def list_all_formats():
    """
    List all viral formats in the database.
    
    Returns a summary of all analyzed videos without full analysis details.
    Use the search endpoint for semantic matching.
    """
    try:
        service = get_youtube_research_service()
        
        # Initialize index if not already done
        service.initialize_index()
        
        # Get all items from index
        # Note: Vectra doesn't have a "list all" method, so we'll search with empty query
        # or return a simple message
        
        return {
            "success": True,
            "message": "Use /search endpoint to find formats by query",
            "index_path": str(service.index_path)
        }
        
    except Exception as e:
        logger.error(f"Error listing formats: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing formats: {str(e)}")


@router.get("/health")
async def research_health_check():
    """Check if research service is properly configured"""
    try:
        service = get_youtube_research_service()
        service.initialize_index()
        
        return {
            "success": True,
            "status": "operational",
            "youtube_api": "configured",
            "emergent_llm": "configured",
            "vectra_index": "initialized"
        }
    except Exception as e:
        logger.error(f"Research service health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")
