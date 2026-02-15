"""Dashboard data models."""

from typing import List, Optional
from pydantic import BaseModel, Field

from .project import Project
from .trends import TopicSuggestion
from .script import Script
from .retention import RetentionAnalysis, RetentionInsights
from .video import ClipInsights


class CompletionStatus(BaseModel):
    """Project completion status."""
    
    topic_selected: bool
    script_created: bool
    retention_analyzed: bool
    video_uploaded: bool
    percent_complete: float = Field(..., ge=0, le=100)


class TopicInsights(BaseModel):
    """Topic insights for dashboard."""
    
    title: str
    predicted_ctr: float
    competitiveness: str
    trending_score: int
    insight: str


class ScriptInsights(BaseModel):
    """Script insights for dashboard."""
    
    word_count: int
    estimated_duration: int  # seconds
    sections_completed: int
    total_sections: int
    insight: str


class DashboardData(BaseModel):
    """Complete dashboard data for a project."""
    
    project_id: str
    project_name: str
    topic_insights: Optional[TopicInsights] = None
    script_insights: Optional[ScriptInsights] = None
    retention_insights: Optional[RetentionInsights] = None
    clip_insights: Optional[ClipInsights] = None
    overall_score: int = Field(..., ge=0, le=100)
    recommendations: List[str]
    completion_status: CompletionStatus


class DashboardRequest(BaseModel):
    """Dashboard data request."""
    
    project_id: str
    include_cache: bool = True
