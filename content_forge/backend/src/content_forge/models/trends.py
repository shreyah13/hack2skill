"""Trend and topic generation models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class EngagementMetrics(BaseModel):
    """Estimated engagement metrics."""
    
    estimated_views: int
    estimated_likes: int
    estimated_comments: int
    confidence_level: int = Field(..., ge=0, le=100)


class TopicSuggestion(BaseModel):
    """AI-generated topic suggestion."""
    
    title: str
    description: str
    predicted_ctr: float = Field(..., ge=0, le=100)
    estimated_engagement: EngagementMetrics
    competitiveness: str = Field(..., regex="^(low|medium|high)$")
    trending_score: int = Field(..., ge=0, le=100)
    keywords: List[str]


class TopicRequest(BaseModel):
    """Topic generation request."""
    
    niche: str
    target_audience: str
    keywords: Optional[List[str]] = []
    competitor_urls: Optional[List[str]] = []


class TopicGenerationResponse(BaseModel):
    """Topic generation response."""
    
    suggestions: List[TopicSuggestion]
    total_suggestions: int
    processing_time_ms: Optional[int] = None


class TopicSelection(BaseModel):
    """Topic selection for project."""
    
    topic_id: Optional[str] = None  # If from suggestions
    title: str
    description: str
    keywords: List[str]
