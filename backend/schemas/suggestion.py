from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class SuggestionItem(BaseModel):
    """Individual suggestion item."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # 'script', 'text_overlay', 'shot', 'timestamp', 'format'
    title: str
    description: str
    content: str
    reasoning: str  # Why this suggestion was made
    confidence_score: float = Field(ge=0.0, le=1.0)
    status: str = "pending"  # pending, accepted, rejected
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class VideoSuggestions(BaseModel):
    """Complete set of suggestions for a video."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    session_id: str
    trending_format_used: str
    format_description: str
    suggestions: List[SuggestionItem]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class SuggestionActionRequest(BaseModel):
    """Request to accept/reject a suggestion."""
    suggestion_id: str
    action: str  # 'accept' or 'reject'
    feedback: Optional[str] = None

class SuggestionResponse(BaseModel):
    """Response after suggestion action."""
    success: bool
    message: str
    updated_suggestion: Optional[SuggestionItem] = None