"""Routes for article content analysis."""

from fastapi import APIRouter

from ..models import (
    ContentAnalysisRequest,
    ContentAnalysisResponse,
    AnalysisScoresResponse,
    UnsupportedClaim,
)
from ..content_fetcher import fetch_article_content, create_manual_content
from ..content_analyzer import analyze_content
from ..config import settings

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/analyze", response_model=ContentAnalysisResponse)
async def analyze_article(request: ContentAnalysisRequest) -> ContentAnalysisResponse:
    """
    Analyze an article for quality, bias, and reliability.

    This endpoint:
    1. Fetches the article content (or uses provided content)
    2. Analyzes it using an LLM for:
       - Inflammatory language
       - Unsupported claims
       - Emotional manipulation
       - Factual reporting quality
       - Political bias indicators
    3. Returns detailed analysis with scores and explanations

    Use Cases:
    - Verify article quality before citing as evidence
    - Identify potential bias or manipulation in news coverage
    - Compare reporting quality across sources
    """
    # Step 1: Get article content
    if request.content:
        # User provided content directly
        article = create_manual_content(request.url, request.content)
    else:
        # Fetch content using Jina AI
        article = await fetch_article_content(request.url)

        if not article.success:
            return ContentAnalysisResponse(
                url=request.url,
                success=False,
                error=f"Failed to fetch article: {article.error}",
                fetch_method=article.method
            )

    # Step 2: Analyze content with LLM
    model = request.model or settings.default_analysis_model
    analysis = await analyze_content(
        url=request.url,
        content=article.content,
        model=model
    )

    if not analysis.success:
        return ContentAnalysisResponse(
            url=request.url,
            success=False,
            word_count=article.word_count,
            fetch_method=article.method,
            model_used=model,
            error=analysis.error
        )

    # Step 3: Build response
    scores = None
    if analysis.scores:
        scores = AnalysisScoresResponse(
            inflammatory_language=analysis.scores.inflammatory_language,
            unsupported_claims=analysis.scores.unsupported_claims,
            emotional_manipulation=analysis.scores.emotional_manipulation,
            factual_reporting=analysis.scores.factual_reporting,
            overall_quality=analysis.scores.overall_quality,
            overall_grade=analysis.scores.overall_grade
        )

    # Convert unsupported claims to proper model
    unsupported_claims = [
        UnsupportedClaim(claim=c.get("claim", ""), issue=c.get("issue", ""))
        for c in analysis.unsupported_claims
        if isinstance(c, dict)
    ]

    return ContentAnalysisResponse(
        url=request.url,
        success=True,
        summary=analysis.summary,
        scores=scores,
        inflammatory_examples=analysis.inflammatory_examples,
        inflammatory_explanation=analysis.inflammatory_explanation,
        unsupported_claims=unsupported_claims,
        claims_explanation=analysis.claims_explanation,
        manipulation_techniques=analysis.manipulation_techniques,
        manipulation_explanation=analysis.manipulation_explanation,
        factual_strengths=analysis.factual_strengths,
        factual_weaknesses=analysis.factual_weaknesses,
        detected_bias=analysis.detected_bias,
        bias_indicators=analysis.bias_indicators,
        bias_explanation=analysis.bias_explanation,
        recommendation=analysis.recommendation,
        word_count=article.word_count,
        fetch_method=article.method,
        model_used=analysis.model_used,
        error=None
    )
