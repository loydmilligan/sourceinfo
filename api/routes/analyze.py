"""Routes for analyzing article URLs and extracting source information."""

from fastapi import APIRouter, HTTPException
from typing import List

from ..models import (
    AnalyzeRequest,
    AnalyzeResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    SourceWithScore
)
from ..utils.url_parser import extract_domain, is_valid_url
from ..database import lookup_source, find_counternarratives
from ..scoring import score_source_for_context
from ..config import settings

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_url(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze an article URL and return source information with counternarratives.

    This endpoint:
    1. Extracts the domain from the article URL
    2. Looks up the source in the database
    3. Returns detailed source information (NewsGuard score, political lean, etc.)
    4. Optionally finds credible counternarrative sources from opposing viewpoints

    Use Cases:
    - Trump Admin Tracker: Get bias info + counternarrative recommendations
    - Claim Analysis Tool: Assess source credibility for evidence
    - Research: Understand source background and find balanced perspectives
    """
    # Validate URL
    if not is_valid_url(request.url):
        return AnalyzeResponse(
            url=request.url,
            domain="",
            source=None,
            source_found=False,
            counternarratives=None,
            error="Invalid URL format"
        )

    # Extract domain
    try:
        domain = extract_domain(request.url)
    except Exception as e:
        return AnalyzeResponse(
            url=request.url,
            domain="",
            source=None,
            source_found=False,
            counternarratives=None,
            error=f"Failed to extract domain: {str(e)}"
        )

    # Lookup source
    source = lookup_source(domain)

    if not source:
        return AnalyzeResponse(
            url=request.url,
            domain=domain,
            source=None,
            source_found=False,
            counternarratives=None,
            error=f"Source not found in database: {domain}"
        )

    # Find counternarratives if requested
    counternarratives = None
    if request.include_counternarratives:
        counter_results = find_counternarratives(
            domain=domain,
            min_credibility=request.min_counternarrative_credibility,
            limit=request.counternarrative_limit,
            preferred_leans=request.preferred_leans
        )

        # Add weighted scores to counternarratives
        counternarratives = []
        for counter in counter_results:
            scoring = score_source_for_context(
                source=counter,
                context={"evidence_role": "counternarrative"}
            )
            counter_with_score = SourceWithScore(
                **counter,
                weighted_score=scoring["weighted_score"]
            )
            counternarratives.append(counter_with_score)

    return AnalyzeResponse(
        url=request.url,
        domain=domain,
        source=source,
        source_found=True,
        counternarratives=counternarratives,
        error=None
    )


@router.post("/batch", response_model=BatchAnalyzeResponse)
async def analyze_batch(request: BatchAnalyzeRequest) -> BatchAnalyzeResponse:
    """
    Analyze multiple article URLs in a single request.

    Useful for:
    - Processing timeline events with multiple sources
    - Bulk evidence collection for claim analysis
    - Batch validation of source credibility
    """
    if not request.urls:
        raise HTTPException(status_code=400, detail="URLs list cannot be empty")

    if len(request.urls) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 URLs per batch request")

    # Use default options if not provided
    options = request.options or AnalyzeRequest(url="")

    results = []
    successful = 0
    failed = 0

    for url in request.urls:
        # Create individual request
        analyze_request = AnalyzeRequest(
            url=url,
            include_counternarratives=options.include_counternarratives,
            min_counternarrative_credibility=options.min_counternarrative_credibility,
            counternarrative_limit=options.counternarrative_limit,
            preferred_leans=options.preferred_leans
        )

        # Analyze
        result = await analyze_url(analyze_request)
        results.append(result)

        if result.source_found and not result.error:
            successful += 1
        else:
            failed += 1

    return BatchAnalyzeResponse(
        results=results,
        total=len(request.urls),
        successful=successful,
        failed=failed
    )
