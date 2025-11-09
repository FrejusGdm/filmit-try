from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class TrendingHashtag(BaseModel):
    """Trending hashtag model."""
    hashtag: str
    video_count: int
    engagement_score: float

class TrendingVideo(BaseModel):
    """Trending video data."""
    id: str
    description: str
    author: str
    stats: Dict[str, int]
    hashtags: List[str]
    music: Optional[str] = None

class ContentFormat(BaseModel):
    """Content format model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    structure: str
    examples: List[str]
    performance_metrics: Dict[str, float]
    best_practices: List[str]
    cached_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class TrendsResponse(BaseModel):
    """Response model for trends."""
    trending_hashtags: List[TrendingHashtag]
    trending_formats: List[ContentFormat]
    last_updated: str