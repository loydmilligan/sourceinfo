"""Routes for API usage statistics and cost tracking."""

from fastapi import APIRouter, Query

from ..models import UsageStatsResponse
from ..usage_tracker import get_usage_stats

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/stats", response_model=UsageStatsResponse)
async def get_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in stats")
) -> UsageStatsResponse:
    """
    Get API usage statistics and cost breakdown.

    Returns:
    - Total API calls, tokens, and costs
    - Breakdown by API (OpenRouter, Jina)
    - Breakdown by model
    - Daily usage trends
    - Most expensive analyses

    Use Cases:
    - Monitor API costs over time
    - Identify expensive operations
    - Track usage patterns
    - Budget planning
    """
    stats = get_usage_stats(days=days)

    return UsageStatsResponse(**stats)
