"""Video and clip suggestion models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class VideoStatus(str, Enum):
    """Video processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImpactType(str, Enum):
    """Types of impactful moments."""
    HOOK = "hook"
    INSIGHT = "insight"
    EMOTIONAL = "emotional"
    ACTIONABLE = "actionable"
    SURPRISING = "surprising"


class VideoUploadRequest(BaseModel):
    """Video upload request."""
    
    filename: str
    content_type: str = Field(..., regex="^(video/.+)$")
    size: int = Field(..., gt=0, le=2_147_483_648)  # 2GB limit


class UploadResult(BaseModel):
    """Video upload result."""
    
    video_id: str
    upload_url: str
    status: VideoStatus
    expires_in: int  # URL expiration in seconds


class ClipSuggestion(BaseModel):
    """AI-generated clip suggestion."""
    
    clip_id: str
    video_id: str
    start_time: float  # seconds
    end_time: float  # seconds
    duration: float  # seconds
    confidence: int = Field(..., ge=0, le=100)
    reason: str
    transcript: str
    impact_type: ImpactType


class Video(BaseModel):
    """Video entity."""
    
    video_id: str
    project_id: str
    filename: str
    storage_key: str
    status: VideoStatus
    size: int
    duration: Optional[float] = None
    transcript: Optional[str] = None
    clip_suggestions: List[ClipSuggestion] = []
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # DynamoDB specific fields
    pk: str = Field(default="", exclude=True)  # Will be set as PROJECT#{project_id}
    sk: str = Field(default="", exclude=True)  # Will be set as VIDEO#{video_id}


class ClipInsights(BaseModel):
    """Clip insights for dashboard."""
    
    total_suggestions: int
    top_clip: Optional[ClipSuggestion] = None
    insight: str
