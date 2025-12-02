"""Pydantic models for API requests and responses."""

from typing import Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


# ============================================================================
# Source Models
# ============================================================================

class SourceBase(BaseModel):
    """Base source information."""
    domain: str
    name: str
    political_lean: Optional[int] = None
    political_lean_label: Optional[str] = None
    newsguard_score: Optional[float] = None
    newsguard_rating: Optional[str] = None
    source_type: Optional[str] = None
    description: Optional[str] = None


class SourceDetailed(SourceBase):
    """Detailed source information including criteria."""
    ownership_summary: Optional[str] = None
    criteria: Optional[dict] = None
    created_at: Optional[str] = None


class SourceWithScore(SourceBase):
    """Source with weighted scoring."""
    weighted_score: Optional[float] = None


# ============================================================================
# Request Models
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request to analyze an article URL."""
    url: str = Field(..., description="Article URL to analyze")
    include_counternarratives: bool = Field(True, description="Include counternarrative sources")
    min_counternarrative_credibility: int = Field(60, ge=0, le=100, description="Minimum NewsGuard score for counternarratives")
    counternarrative_limit: int = Field(10, ge=1, le=50, description="Maximum number of counternarratives")
    preferred_leans: Optional[list[int]] = Field(None, description="Specific political leans to target (e.g., [1, 2] for right-leaning)")


class BatchAnalyzeRequest(BaseModel):
    """Request to analyze multiple URLs."""
    urls: list[str] = Field(..., description="List of article URLs to analyze")
    options: Optional[AnalyzeRequest] = Field(None, description="Analysis options (applied to all URLs)")


class ScoreRequest(BaseModel):
    """Request to score a source for evidence quality."""
    domain: str = Field(..., description="Source domain to score")
    context: Optional[dict] = Field(None, description="Context for scoring")

    class Context(BaseModel):
        """Scoring context."""
        claim_type: Optional[Literal["political", "economic", "foreign_policy", "scientific", "general"]] = "general"
        evidence_role: Optional[Literal["support", "refute", "neutral"]] = "neutral"
        preferred_credibility: Optional[Literal["high", "medium", "any"]] = "high"


# ============================================================================
# Response Models
# ============================================================================

class AnalyzeResponse(BaseModel):
    """Response from analyze endpoint."""
    url: str
    domain: str
    source: Optional[SourceDetailed] = None
    source_found: bool
    counternarratives: Optional[list[SourceWithScore]] = None
    error: Optional[str] = None


class BatchAnalyzeResponse(BaseModel):
    """Response from batch analyze endpoint."""
    results: list[AnalyzeResponse]
    total: int
    successful: int
    failed: int


class ScoringBreakdown(BaseModel):
    """Breakdown of weighted scoring."""
    credibility_score: float = Field(..., description="Base NewsGuard score")
    bias_penalty: float = Field(0, description="Penalty for extreme bias (if applicable)")
    type_bonus: float = Field(0, description="Bonus for source type (fact-checker, etc.)")
    explanation: str = Field(..., description="Human-readable explanation")


class ScoreResponse(BaseModel):
    """Response from score endpoint."""
    source: Optional[SourceBase] = None
    weighted_score: Optional[float] = None
    scoring_breakdown: Optional[ScoringBreakdown] = None
    recommendation: Optional[Literal["strong", "acceptable", "use_with_caution", "not_recommended"]] = None
    error: Optional[str] = None


class SourceListResponse(BaseModel):
    """Response from source list endpoint."""
    sources: list[SourceBase]
    total: int
    limit: int
    offset: int
    filters_applied: dict


class CounternarrativeResponse(BaseModel):
    """Response from counternarrative endpoint."""
    source_domain: str
    source_name: Optional[str] = None
    source_lean: Optional[str] = None
    counternarratives: list[SourceWithScore]
    total: int


class StatsResponse(BaseModel):
    """Response from stats endpoint."""
    total_sources: int
    with_newsguard: int
    with_political_lean: int
    lean_distribution: dict[str, int]
    type_distribution: dict[str, int]
    credibility_tiers: dict[str, int]


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    status_code: int
