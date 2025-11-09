from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class ChatMessage(BaseModel):
    """Chat message model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Optional[dict] = None

class ChatRequest(BaseModel):
    """Request model for chat."""
    session_id: str
    message: str
    video_id: Optional[str] = None
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    """Response model for chat."""
    message_id: str
    response: str
    suggestions: Optional[List[dict]] = None
    timestamp: str