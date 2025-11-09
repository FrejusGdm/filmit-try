from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class VideoUploadChunk(BaseModel):
    """Model for chunked video upload."""
    chunk_index: int
    total_chunks: int
    chunk_data: str  # Base64 encoded chunk
    session_id: str
    filename: str

class VideoMetadata(BaseModel):
    """Video metadata model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: str
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    duration: Optional[float] = None
    uploaded_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    analysis_status: str = "pending"  # pending, analyzing, completed, failed
    
class VideoResponse(BaseModel):
    """Video response model."""
    id: str
    filename: str
    file_size: int
    uploaded_at: str
    analysis_status: str

class VideoAnalysisRequest(BaseModel):
    """Request model for video analysis."""
    video_id: str
    user_context: Optional[str] = Field(None, description="User's context about their app/content")
    target_platform: str = Field(default="TikTok", description="Target platform for content")
    target_audience: Optional[str] = Field(None, description="Target audience description")