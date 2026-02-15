"""Common data models and base classes."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class BaseDBModel(BaseModel):
    """Base model for database entities with common fields."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    
    success: bool
    data: Optional[dict] = None
    error: Optional["APIError"] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class APIError(BaseModel):
    """Standard API error format."""
    
    code: str
    message: str
    details: Optional[dict] = None


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    
    limit: int = Field(default=20, ge=1, le=100)
    next_token: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    
    items: list
    next_token: Optional[str] = None
    total_count: Optional[int] = None
