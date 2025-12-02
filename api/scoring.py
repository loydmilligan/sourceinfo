"""Weighted scoring logic for source credibility and evidence quality."""

from typing import Optional, Literal
from .models import ScoringBreakdown


def get_credibility_tier(score: Optional[float]) -> str:
    """
    Classify source by credibility tier.

    Args:
        score: NewsGuard score (0-100)

    Returns:
        Tier: "high", "medium", "low", or "unknown"
    """
    if score is None:
        return "unknown"
    if score >= 80:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def calculate_type_bonus(
    source_type: Optional[str],
    claim_type: str = "general"
) -> float:
    """
    Calculate bonus points based on source type and claim type.

    Args:
        source_type: Type of source (fact_check, think_tank, news_media, etc.)
        claim_type: Type of claim being evaluated

    Returns:
        Bonus points (0-10)
    """
    if not source_type:
        return 0

    # Fact-checkers get universal bonus
    if source_type == "fact_check":
        return 10

    # Think tanks bonus for policy/economic claims
    if source_type in ("think_tank", "think_tank___policy_group"):
        if claim_type in ("political", "economic", "foreign_policy"):
            return 5
        return 2

    # Wire services bonus for factual reporting
    if source_type == "wire_service":
        return 5

    # Trade publications bonus for industry-specific claims
    if source_type == "trade_publication":
        return 3

    return 0


def calculate_bias_penalty(
    political_lean: Optional[int],
    evidence_role: str = "neutral"
) -> float:
    """
    Calculate penalty for extreme bias based on evidence role.

    Args:
        political_lean: Political lean (-2 to 2)
        evidence_role: Role of evidence (support, refute, neutral)

    Returns:
        Penalty points (0-10, negative value)
    """
    if political_lean is None:
        return 0

    # For counternarratives, no penalty (we WANT opposite bias)
    if evidence_role == "counternarrative":
        return 0

    # For partisan evidence, no penalty (we're seeking a perspective)
    if evidence_role in ("support", "refute"):
        return 0

    # For neutral evidence, penalize extreme bias
    if evidence_role == "neutral":
        abs_lean = abs(political_lean)
        if abs_lean == 2:  # Left or Right
            return -10
        if abs_lean == 1:  # Lean Left or Lean Right
            return -5

    return 0


def calculate_weighted_score(
    base_credibility: Optional[float],
    source_type: Optional[str],
    political_lean: Optional[int],
    claim_type: str = "general",
    evidence_role: str = "neutral"
) -> tuple[float, ScoringBreakdown]:
    """
    Calculate weighted score for source based on context.

    Args:
        base_credibility: NewsGuard score (0-100)
        source_type: Type of source
        political_lean: Political lean (-2 to 2)
        claim_type: Type of claim being evaluated
        evidence_role: Role of evidence (support, refute, neutral, counternarrative)

    Returns:
        Tuple of (weighted_score, scoring_breakdown)
    """
    # Handle missing credibility score
    if base_credibility is None:
        weighted_score = 50  # Neutral score for unknown sources
        explanation = "No NewsGuard rating available; assigned neutral score"
    else:
        weighted_score = base_credibility
        explanation = f"Base credibility: {base_credibility}/100"

    # Calculate adjustments
    type_bonus = calculate_type_bonus(source_type, claim_type)
    bias_penalty = calculate_bias_penalty(political_lean, evidence_role)

    # Apply adjustments
    weighted_score += type_bonus + bias_penalty

    # Clamp to 0-100 range
    weighted_score = max(0, min(100, weighted_score))

    # Build explanation
    explanation_parts = [explanation]

    if type_bonus > 0:
        explanation_parts.append(f"+{type_bonus} type bonus ({source_type})")

    if bias_penalty < 0:
        lean_label = {-2: "Left", -1: "Lean Left", 0: "Center", 1: "Lean Right", 2: "Right"}.get(political_lean, "Unknown")
        explanation_parts.append(f"{bias_penalty} bias penalty (extreme {lean_label} for neutral evidence)")

    if evidence_role == "counternarrative":
        lean_label = {-2: "Left", -1: "Lean Left", 0: "Center", 1: "Lean Right", 2: "Right"}.get(political_lean, "Unknown")
        explanation_parts.append(f"Counternarrative perspective ({lean_label})")

    full_explanation = "; ".join(explanation_parts)

    breakdown = ScoringBreakdown(
        credibility_score=base_credibility or 50,
        bias_penalty=bias_penalty,
        type_bonus=type_bonus,
        explanation=full_explanation
    )

    return weighted_score, breakdown


def get_recommendation(
    weighted_score: float,
    credibility_tier: str
) -> Literal["strong", "acceptable", "use_with_caution", "not_recommended"]:
    """
    Get recommendation based on weighted score.

    Args:
        weighted_score: Weighted score (0-100)
        credibility_tier: Credibility tier (high, medium, low, unknown)

    Returns:
        Recommendation level
    """
    if credibility_tier == "unknown":
        return "use_with_caution"

    if weighted_score >= 80:
        return "strong"
    elif weighted_score >= 60:
        return "acceptable"
    elif weighted_score >= 40:
        return "use_with_caution"
    else:
        return "not_recommended"


def score_source_for_context(
    source: dict,
    context: Optional[dict] = None
) -> dict:
    """
    Score a source given a specific context.

    Args:
        source: Source dictionary from database
        context: Optional context dict with claim_type, evidence_role, etc.

    Returns:
        Dict with weighted_score, scoring_breakdown, and recommendation
    """
    # Extract context parameters
    claim_type = "general"
    evidence_role = "neutral"

    if context:
        claim_type = context.get("claim_type", "general")
        evidence_role = context.get("evidence_role", "neutral")

    # Calculate weighted score
    weighted_score, breakdown = calculate_weighted_score(
        base_credibility=source.get("newsguard_score"),
        source_type=source.get("source_type"),
        political_lean=source.get("political_lean"),
        claim_type=claim_type,
        evidence_role=evidence_role
    )

    # Get credibility tier and recommendation
    tier = get_credibility_tier(source.get("newsguard_score"))
    recommendation = get_recommendation(weighted_score, tier)

    return {
        "weighted_score": round(weighted_score, 1),
        "scoring_breakdown": breakdown,
        "recommendation": recommendation,
        "credibility_tier": tier
    }
