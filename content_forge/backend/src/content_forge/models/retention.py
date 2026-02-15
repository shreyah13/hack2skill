"""Retention analysis models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from .script import ScriptSection


class RiskIssueType(str, Enum):
    """Types of retention risk issues."""
    PACING = "pacing"
    COMPLEXITY = "complexity"
    LENGTH = "length"
    HOOK_STRENGTH = "hook_strength"
    TRANSITION = "transition"
    CLARITY = "clarity"


class RiskSeverity(str, Enum):
    """Risk severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskIssue(BaseModel):
    """Individual retention risk issue."""
    
    type: RiskIssueType
    description: str
    severity: RiskSeverity
    suggestion: Optional[str] = None


class RiskSection(BaseModel):
    """Retention risk analysis for a script section."""
    
    section: ScriptSection
    risk_level: RiskSeverity
    risk_score: int = Field(..., ge=0, le=100)
    issues: List[RiskIssue]
    suggestions: List[str]


class RetentionAnalysis(BaseModel):
    """Complete retention analysis results."""
    
    analysis_id: str
    script_id: str
    overall_score: int = Field(..., ge=0, le=100)
    risk_sections: List[RiskSection]
    recommendations: List[str]
    analyzed_at: datetime
    
    # Analysis breakdown
    hook_strength: Optional[int] = Field(None, ge=0, le=100)
    pacing_score: Optional[int] = Field(None, ge=0, le=100)
    complexity_score: Optional[int] = Field(None, ge=0, le=100)
    clarity_score: Optional[int] = Field(None, ge=0, le=100)


class RetentionAnalysisRequest(BaseModel):
    """Retention analysis request."""
    
    script_id: str


class RetentionInsights(BaseModel):
    """Retention insights for dashboard."""
    
    overall_score: int
    high_risk_sections: int
    top_recommendation: str
    insight: str
