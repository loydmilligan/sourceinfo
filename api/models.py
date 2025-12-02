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
# Content Analysis Models
# ============================================================================

class ContentAnalysisRequest(BaseModel):
    """Request to analyze article content."""
    url: str = Field(..., description="Article URL to fetch and analyze")
    content: Optional[str] = Field(None, description="Optional: provide content directly instead of fetching")
    model: Optional[str] = Field(None, description="OpenRouter model to use (default: claude-sonnet-4)")


class AnalysisScoresResponse(BaseModel):
    """Individual analysis scores (1-10 scale, except overall which is 1-100)."""
    inflammatory_language: int = Field(..., ge=1, le=10, description="1=neutral, 10=highly inflammatory")
    unsupported_claims: int = Field(..., ge=1, le=10, description="1=well-sourced, 10=many unsupported")
    emotional_manipulation: int = Field(..., ge=1, le=10, description="1=objective, 10=manipulative")
    factual_reporting: int = Field(..., ge=1, le=10, description="1=opinion, 10=factual")
    overall_quality: int = Field(..., ge=1, le=100, description="Overall quality score")
    overall_grade: str = Field(..., description="Letter grade A-F")


class UnsupportedClaim(BaseModel):
    """An unsupported claim found in the article."""
    claim: str
    issue: str


class ContentAnalysisResponse(BaseModel):
    """Response from content analysis endpoint."""
    url: str
    success: bool

    # Summary
    summary: Optional[str] = None

    # Scores
    scores: Optional[AnalysisScoresResponse] = None

    # Inflammatory language
    inflammatory_examples: list[str] = []
    inflammatory_explanation: Optional[str] = None

    # Unsupported claims
    unsupported_claims: list[UnsupportedClaim] = []
    claims_explanation: Optional[str] = None

    # Emotional manipulation
    manipulation_techniques: list[str] = []
    manipulation_explanation: Optional[str] = None

    # Factual reporting
    factual_strengths: list[str] = []
    factual_weaknesses: list[str] = []

    # Bias detection
    detected_bias: Optional[str] = None
    bias_indicators: list[str] = []
    bias_explanation: Optional[str] = None

    # Recommendation
    recommendation: Optional[str] = None

    # Metadata
    word_count: Optional[int] = None
    fetch_method: Optional[str] = None
    model_used: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# Usage Stats Models
# ============================================================================

class ApiUsageBreakdown(BaseModel):
    """Usage breakdown by API."""
    api_name: str
    calls: int
    cost: float


class ModelUsageBreakdown(BaseModel):
    """Usage breakdown by model."""
    model_used: str
    calls: int
    input_tokens: int
    output_tokens: int
    cost: float
    avg_cost_per_call: float


class DailyUsage(BaseModel):
    """Daily usage summary."""
    date: str
    calls: int
    input_tokens: int
    output_tokens: int
    cost: float


class ExpensiveAnalysis(BaseModel):
    """Info about an expensive analysis."""
    url: str
    model_used: Optional[str]
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: str


class UsageTotals(BaseModel):
    """Total usage metrics."""
    total_calls: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
    successful_calls: int
    failed_calls: int


class UsageStatsResponse(BaseModel):
    """Response from usage stats endpoint."""
    period_days: int
    totals: UsageTotals
    by_api: list[ApiUsageBreakdown]
    by_model: list[ModelUsageBreakdown]
    daily: list[DailyUsage]
    top_expensive: list[ExpensiveAnalysis]


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    status_code: int
