from fastapi import APIRouter, HTTPException, Query
import logging
from typing import Optional

from schemas.trends import TrendsResponse, TrendingHashtag, ContentFormat
from services.tiktok_service import tiktok_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/current")
async def get_current_trends(
    hashtag_limit: int = Query(20, ge=5, le=50),
    include_formats: bool = Query(True)
):
    """Get current trending hashtags and formats."""
    try:
        # Get trending hashtags
        hashtags = await tiktok_service.get_trending_hashtags(limit=hashtag_limit)
        
        # Get trending formats
        formats = []
        if include_formats:
            formats = await tiktok_service.get_trending_formats()
        
        return {
            "trending_hashtags": hashtags,
            "trending_formats": formats,
            "last_updated": tiktok_service.cache.get("last_updated", "").isoformat() if tiktok_service.cache.get("last_updated") else "never",
            "data_source": "cached" if tiktok_service._is_cache_valid() else "fresh"
        }
        
    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hashtags")
async def get_trending_hashtags(limit: int = Query(20, ge=5, le=50)):
    """Get trending hashtags only."""
    try:
        hashtags = await tiktok_service.get_trending_hashtags(limit=limit)
        
        return {
            "hashtags": hashtags,
            "count": len(hashtags)
        }
        
    except Exception as e:
        logger.error(f"Error getting trending hashtags: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/formats")
async def get_trending_formats():
    """Get trending content formats."""
    try:
        formats = await tiktok_service.get_trending_formats()
        
        return {
            "formats": formats,
            "count": len(formats)
        }
        
    except Exception as e:
        logger.error(f"Error getting trending formats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_trends_cache():
    """Force refresh trends cache."""
    try:
        # Clear cache
        tiktok_service.cache["last_updated"] = None
        
        # Fetch fresh data
        hashtags = await tiktok_service.get_trending_hashtags(limit=20)
        formats = await tiktok_service.get_trending_formats()
        
        return {
            "success": True,
            "message": "Trends cache refreshed",
            "hashtags_count": len(hashtags),
            "formats_count": len(formats)
        }
        
    except Exception as e:
        logger.error(f"Error refreshing trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))