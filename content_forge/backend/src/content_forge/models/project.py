"""Project-related data models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .common import BaseDBModel


class ContentTopic(BaseModel):
    """Content topic information."""
    
    title: str
    description: str
    keywords: List[str]
    selected_at: datetime


class ProjectInput(BaseModel):
    """Project creation input."""
    
    name: str = Field(..., min_length=1, max_length=200)
    niche: str = Field(..., min_length=1, max_length=100)
    target_audience: str = Field(..., min_length=1, max_length=200)


class Project(BaseDBModel):
    """Project entity."""
    
    user_id: str
    name: str
    niche: str
    target_audience: str
    topic: Optional[ContentTopic] = None
    status: str = Field(default="active", regex="^(active|archived|deleted)$")
    
    # DynamoDB specific fields
    pk: str = Field(default="", exclude=True)  # Will be set as USER#{user_id}
    sk: str = Field(default="", exclude=True)  # Will be set as PROJECT#{project_id}
    gsi1pk: Optional[str] = Field(None, exclude=True)  # Will be set as PROJECT#{project_id}
    gsi1sk: Optional[str] = Field(None, exclude=True)  # Will be set as METADATA


class ProjectUpdate(BaseModel):
    """Project update request."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    niche: Optional[str] = Field(None, min_length=1, max_length=100)
    target_audience: Optional[str] = Field(None, min_length=1, max_length=200)
    topic: Optional[ContentTopic] = None
    status: Optional[str] = Field(None, regex="^(active|archived|deleted)$")


class ProjectList(BaseModel):
    """Project list response."""
    
    projects: List[Project]
    next_token: Optional[str] = None
