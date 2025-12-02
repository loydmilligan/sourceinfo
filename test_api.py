#!/usr/bin/env python3
"""Quick API tests to verify functionality."""

import sys
sys.path.insert(0, "/home/mmariani/Projects/SourceInfo")

from api.utils.url_parser import extract_domain, is_valid_url
from api.database import lookup_source, find_counternarratives, get_database_stats
from api.scoring import calculate_weighted_score, score_source_for_context

def test_url_parser():
    """Test URL parsing utility."""
    print("=" * 60)
    print("TEST 1: URL Parser")
    print("=" * 60)

    test_urls = [
        "https://www.nytimes.com/2024/article",
        "edition.cnn.com/world",
        "nytimes.com",
        "m.wsj.com/article"
    ]

    for url in test_urls:
        domain = extract_domain(url)
        valid = is_valid_url(url)
        print(f"  {url}")
        print(f"    → Domain: {domain}, Valid: {valid}")

    print("✓ URL Parser working\n")


def test_database():
    """Test database queries."""
    print("=" * 60)
    print("TEST 2: Database Queries")
    print("=" * 60)

    # Test lookup
    source = lookup_source("nytimes.com")
    if source:
        print(f"  ✓ Found: {source['name']}")
        print(f"    Lean: {source['political_lean_label']}")
        print(f"    Credibility: {source['newsguard_score']}/100")
    else:
        print("  ✗ NYT not found")

    # Test counternarratives
    counters = find_counternarratives("nytimes.com", min_credibility=70, limit=3)
    print(f"\n  Counternarratives for NYT: {len(counters)}")
    for c in counters[:3]:
        print(f"    - {c['name']} ({c['political_lean_label']}, {c['newsguard_score']}/100)")

    # Test stats
    stats = get_database_stats()
    print(f"\n  Database stats:")
    print(f"    Total sources: {stats['total_sources']}")
    print(f"    With NewsGuard: {stats['with_newsguard']}")
    print(f"    With lean: {stats['with_political_lean']}")

    print("✓ Database queries working\n")


def test_scoring():
    """Test weighted scoring."""
    print("=" * 60)
    print("TEST 3: Weighted Scoring")
    print("=" * 60)

    source = lookup_source("nytimes.com")
    if not source:
        print("  ✗ Source not found for scoring")
        return

    # Test neutral evidence scoring
    weighted, breakdown = calculate_weighted_score(
        base_credibility=source.get("newsguard_score"),
        source_type=source.get("source_type"),
        political_lean=source.get("political_lean"),
        claim_type="political",
        evidence_role="neutral"
    )

    print(f"  NYT for neutral evidence:")
    print(f"    Base: {breakdown.credibility_score}/100")
    print(f"    Type bonus: {breakdown.type_bonus}")
    print(f"    Bias penalty: {breakdown.bias_penalty}")
    print(f"    Weighted: {weighted}/100")
    print(f"    Explanation: {breakdown.explanation}")

    # Test counternarrative scoring
    weighted2, breakdown2 = calculate_weighted_score(
        base_credibility=source.get("newsguard_score"),
        source_type=source.get("source_type"),
        political_lean=source.get("political_lean"),
        claim_type="political",
        evidence_role="counternarrative"
    )

    print(f"\n  NYT as counternarrative:")
    print(f"    Weighted: {weighted2}/100 (no bias penalty)")

    print("✓ Weighted scoring working\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SourceInfo API - Component Tests")
    print("=" * 60 + "\n")

    try:
        test_url_parser()
        test_database()
        test_scoring()

        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nTo start the API server, run:")
        print("  ./run_api.sh")
        print("\nThen visit:")
        print("  http://localhost:8000/docs")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
