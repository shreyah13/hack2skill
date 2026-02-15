"""Script-related data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from .common import BaseDBModel


class ScriptSection(str, Enum):
    """Script section types."""
    HOOK = "hook"
    INTRODUCTION = "introduction"
    MAIN = "main"
    CTA = "cta"


class SectionContent(BaseModel):
    """Content for a script section."""
    
    section: ScriptSection
    content: str
    word_count: int
    estimated_duration: int  # seconds


class ScriptRequest(BaseModel):
    """Script generation request."""
    
    topic: str
    duration: Optional[int] = Field(None, ge=1, le=30)  # target duration in minutes
    tone: Optional[str] = Field("casual", regex="^(casual|professional|energetic|educational)$")
    platform: Optional[str] = Field("youtube", regex="^(youtube|tiktok|instagram)$")


class Script(BaseDBModel):
    """Script entity."""
    
    project_id: str
    hook: SectionContent
    introduction: SectionContent
    main_content: List[SectionContent]
    call_to_action: SectionContent
    version: int = 1
    
    # DynamoDB specific fields
    pk: str = Field(default="", exclude=True)  # Will be set as PROJECT#{project_id}
    sk: str = Field(default="", exclude=True)  # Will be set as SCRIPT#{script_id}


class ScriptUpdate(BaseModel):
    """Script update request."""
    
    hook: Optional[SectionContent] = None
    introduction: Optional[SectionContent] = None
    main_content: Optional[List[SectionContent]] = None
    call_to_action: Optional[SectionContent] = None


class SectionRegenerateRequest(BaseModel):
    """Section regeneration request."""
    
    section: ScriptSection
    context: Optional[str] = None  # Additional context for regeneration


class SectionRegenerateResponse(BaseModel):
    """Section regeneration response."""
    
    section: ScriptSection
    content: SectionContent
