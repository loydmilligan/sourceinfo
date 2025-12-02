#!/usr/bin/env python3
"""
Query utility for the SourceInfo database.
Provides functions for looking up sources and finding counternarratives.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict


DB_PATH = Path("/home/mmariani/Projects/SourceInfo/data/sources.db")


def get_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)


def lookup_source(domain: str) -> Optional[Dict]:
    """
    Look up a source by domain.

    Args:
        domain: The domain to look up (e.g., "nytimes.com")

    Returns:
        Dict with source info or None if not found
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Try exact match first
    cursor.execute("SELECT * FROM sources WHERE domain = ?", (domain,))
    row = cursor.fetchone()

    # If not found, try fuzzy match
    if not row:
        cursor.execute(
            "SELECT * FROM sources WHERE domain LIKE ?",
            (f"%{domain}%",)
        )
        row = cursor.fetchone()

    conn.close()

    if row:
        result = dict(row)
        if result.get("criteria_json"):
            result["criteria"] = json.loads(result["criteria_json"])
            del result["criteria_json"]
        return result
    return None


def find_counternarratives(domain: str, min_credibility: int = 60, limit: int = 10) -> List[Dict]:
    """
    Find sources from the opposite political spectrum.

    Args:
        domain: The source domain to find counternarratives for
        min_credibility: Minimum NewsGuard score (default 60)
        limit: Maximum number of results

    Returns:
        List of counternarrative sources
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # First get the source's political lean
    cursor.execute(
        "SELECT political_lean FROM sources WHERE domain = ? OR domain LIKE ?",
        (domain, f"%{domain}%")
    )
    row = cursor.fetchone()

    if not row or row["political_lean"] is None:
        conn.close()
        return []

    source_lean = row["political_lean"]

    if source_lean == 0:
        # Center sources - return both left and right
        cursor.execute("""
            SELECT domain, name, newsguard_score, political_lean, political_lean_label
            FROM sources
            WHERE political_lean != 0
              AND newsguard_score >= ?
            ORDER BY newsguard_score DESC
            LIMIT ?
        """, (min_credibility, limit))
    else:
        # Find opposite side
        cursor.execute("""
            SELECT domain, name, newsguard_score, political_lean, political_lean_label
            FROM sources
            WHERE political_lean IS NOT NULL
              AND political_lean * ? < 0
              AND newsguard_score >= ?
            ORDER BY newsguard_score DESC
            LIMIT ?
        """, (source_lean, min_credibility, limit))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_sources_by_lean(lean: int, min_credibility: int = 0) -> List[Dict]:
    """
    Get all sources with a specific political lean.

    Args:
        lean: Political lean (-2=Left, -1=Lean Left, 0=Center, 1=Lean Right, 2=Right)
        min_credibility: Minimum NewsGuard score

    Returns:
        List of sources
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT domain, name, newsguard_score, political_lean_label, source_type
        FROM sources
        WHERE political_lean = ?
          AND (newsguard_score >= ? OR newsguard_score IS NULL)
        ORDER BY newsguard_score DESC
    """, (lean, min_credibility))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_credible_sources(min_score: int = 80) -> List[Dict]:
    """Get all sources above a credibility threshold."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT domain, name, newsguard_score, political_lean_label, source_type
        FROM sources
        WHERE newsguard_score >= ?
        ORDER BY newsguard_score DESC
    """, (min_score,))

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def source_summary(domain: str) -> str:
    """Get a human-readable summary of a source."""
    source = lookup_source(domain)
    if not source:
        return f"Source not found: {domain}"

    lines = [
        f"=== {source.get('name') or domain} ===",
        f"Domain: {source['domain']}",
    ]

    if source.get("newsguard_score"):
        lines.append(f"Credibility: {source['newsguard_score']}/100 ({source.get('newsguard_rating', 'N/A')})")

    if source.get("political_lean_label"):
        lines.append(f"Political Lean: {source['political_lean_label']}")

    if source.get("source_type"):
        lines.append(f"Type: {source['source_type']}")

    if source.get("description"):
        lines.append(f"\nDescription: {source['description']}")

    if source.get("ownership_summary"):
        ownership = source["ownership_summary"][:300] + "..." if len(source.get("ownership_summary", "")) > 300 else source.get("ownership_summary", "")
        lines.append(f"\nOwnership: {ownership}")

    return "\n".join(lines)


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python query_sources.py lookup <domain>")
        print("  python query_sources.py counter <domain>")
        print("  python query_sources.py lean <-2|-1|0|1|2>")
        print("  python query_sources.py credible [min_score]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "lookup" and len(sys.argv) >= 3:
        print(source_summary(sys.argv[2]))

    elif cmd == "counter" and len(sys.argv) >= 3:
        domain = sys.argv[2]
        source = lookup_source(domain)
        if source:
            print(f"Counternarratives for {source.get('name', domain)} ({source.get('political_lean_label', 'Unknown')}):\n")
        counters = find_counternarratives(domain)
        if counters:
            for c in counters:
                print(f"  {c['domain']}: {c['name']} ({c['political_lean_label']}, {c['newsguard_score']}/100)")
        else:
            print("  No counternarratives found (source may be Center or not in database)")

    elif cmd == "lean" and len(sys.argv) >= 3:
        lean = int(sys.argv[2])
        lean_labels = {-2: "Left", -1: "Lean Left", 0: "Center", 1: "Lean Right", 2: "Right"}
        print(f"Sources with {lean_labels.get(lean, 'Unknown')} lean:\n")
        sources = get_sources_by_lean(lean)
        for s in sources:
            score = f"{s['newsguard_score']}/100" if s['newsguard_score'] else "N/A"
            print(f"  {s['domain']}: {s['name']} ({score})")

    elif cmd == "credible":
        min_score = int(sys.argv[2]) if len(sys.argv) >= 3 else 80
        print(f"Sources with credibility >= {min_score}:\n")
        sources = get_credible_sources(min_score)
        for s in sources:
            lean = s.get('political_lean_label') or 'Unknown'
            print(f"  {s['domain']}: {s['newsguard_score']}/100 ({lean})")

    else:
        print(f"Unknown command: {cmd}")
