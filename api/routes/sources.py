"""Routes for querying and managing sources."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..models import (
    SourceDetailed,
    SourceListResponse,
    CounternarrativeResponse,
    ScoreRequest,
    ScoreResponse,
    StatsResponse,
    SourceWithScore
)
from ..database import (
    lookup_source,
    lookup_sources_bulk,
    query_sources,
    find_counternarratives,
    get_database_stats
)
from ..scoring import score_source_for_context

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/{domain}", response_model=SourceDetailed)
async def get_source(domain: str) -> SourceDetailed:
    """
    Get detailed information about a specific source by domain.

    Returns full source details including NewsGuard criteria breakdown,
    ownership information, and metadata.
    """
    source = lookup_source(domain)

    if not source:
        raise HTTPException(
            status_code=404,
            detail=f"Source not found: {domain}"
        )

    return SourceDetailed(**source)


@router.get("", response_model=SourceListResponse)
async def list_sources(
    domains: Optional[str] = Query(None, description="Comma-separated list of domains for bulk lookup"),
    lean: Optional[int] = Query(None, ge=-2, le=2, description="Political lean filter (-2=Left to 2=Right)"),
    min_credibility: Optional[int] = Query(None, ge=0, le=100, description="Minimum NewsGuard score"),
    source_type: Optional[str] = Query(None, description="Source type (news_media, fact_check, etc.)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
) -> SourceListResponse:
    """
    List or search sources with optional filters.

    Supports:
    - Bulk lookup by domains
    - Filtering by political lean, credibility, type
    - Pagination

    Use Cases:
    - Get all Center sources with high credibility for neutral evidence
    - Find all fact-checkers for claim verification
    - Browse available sources by category
    """
    # Handle bulk lookup
    if domains:
        domain_list = [d.strip() for d in domains.split(",")]
        result_dict = lookup_sources_bulk(domain_list)

        return SourceListResponse(
            sources=list(result_dict.values()),
            total=len(result_dict),
            limit=limit,
            offset=0,
            filters_applied={"domains": domain_list}
        )

    # Handle filtered query
    sources, total = query_sources(
        lean=lean,
        min_credibility=min_credibility,
        source_type=source_type,
        limit=limit,
        offset=offset
    )

    filters_applied = {}
    if lean is not None:
        filters_applied["lean"] = lean
    if min_credibility is not None:
        filters_applied["min_credibility"] = min_credibility
    if source_type:
        filters_applied["source_type"] = source_type

    return SourceListResponse(
        sources=sources,
        total=total,
        limit=limit,
        offset=offset,
        filters_applied=filters_applied
    )


@router.get("/{domain}/counternarratives", response_model=CounternarrativeResponse)
async def get_counternarratives(
    domain: str,
    min_credibility: int = Query(60, ge=0, le=100, description="Minimum NewsGuard score"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    preferred_leans: Optional[str] = Query(None, description="Comma-separated lean values (e.g., '1,2' for right-leaning)")
) -> CounternarrativeResponse:
    """
    Find counternarrative sources for a given source domain.

    Returns credible sources from the opposite political spectrum that can provide
    alternative perspectives on the same topics.

    Use Cases:
    - Trump Admin Tracker: Find right-leaning sources to balance left-leaning articles
    - Claim Analysis: Get diverse perspectives on controversial topics
    - Research: Understand multiple viewpoints on an issue
    """
    # Lookup source to get name and lean
    source = lookup_source(domain)

    if not source:
        raise HTTPException(
            status_code=404,
            detail=f"Source not found: {domain}"
        )

    # Parse preferred leans if provided
    preferred_leans_list = None
    if preferred_leans:
        try:
            preferred_leans_list = [int(l.strip()) for l in preferred_leans.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid preferred_leans format. Use comma-separated integers (e.g., '1,2')"
            )

    # Find counternarratives
    counters = find_counternarratives(
        domain=domain,
        min_credibility=min_credibility,
        limit=limit,
        preferred_leans=preferred_leans_list
    )

    # Add weighted scores
    scored_counters = []
    for counter in counters:
        scoring = score_source_for_context(
            source=counter,
            context={"evidence_role": "counternarrative"}
        )
        counter_with_score = SourceWithScore(
            **counter,
            weighted_score=scoring["weighted_score"]
        )
        scored_counters.append(counter_with_score)

    return CounternarrativeResponse(
        source_domain=domain,
        source_name=source.get("name"),
        source_lean=source.get("political_lean_label"),
        counternarratives=scored_counters,
        total=len(scored_counters)
    )


@router.post("/score", response_model=ScoreResponse)
async def score_source(request: ScoreRequest) -> ScoreResponse:
    """
    Calculate weighted evidence quality score for a source given context.

    Use Cases:
    - Claim Analysis: Assess source quality for specific evidence types
    - Prioritize sources based on evidence role (support/refute/neutral)
    - Weight fact-checkers higher for verification tasks
    """
    source = lookup_source(request.domain)

    if not source:
        return ScoreResponse(
            source=None,
            weighted_score=None,
            scoring_breakdown=None,
            recommendation=None,
            error=f"Source not found: {request.domain}"
        )

    # Score with context
    scoring = score_source_for_context(
        source=source,
        context=request.context.dict() if request.context else None
    )

    return ScoreResponse(
        source=source,
        weighted_score=scoring["weighted_score"],
        scoring_breakdown=scoring["scoring_breakdown"],
        recommendation=scoring["recommendation"],
        error=None
    )


@router.get("/stats/overview", response_model=StatsResponse)
async def get_stats() -> StatsResponse:
    """
    Get database statistics and source distribution metrics.

    Returns:
    - Total sources and coverage (NewsGuard, political lean)
    - Lean distribution (Left to Right)
    - Type distribution (news_media, fact_check, etc.)
    - Credibility tiers (high/medium/low)
    """
    stats = get_database_stats()
    return StatsResponse(**stats)
