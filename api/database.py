"""Database operations for SourceInfo API."""

import sqlite3
import json
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from .config import settings


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def lookup_source(domain: str) -> Optional[dict]:
    """
    Look up a source by domain.

    Args:
        domain: The domain to look up (e.g., "nytimes.com")

    Returns:
        Dict with source info or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Try exact match first
        cursor.execute("SELECT * FROM sources WHERE domain = ?", (domain,))
        row = cursor.fetchone()

        # If not found, try fuzzy match
        if not row:
            cursor.execute(
                "SELECT * FROM sources WHERE domain LIKE ? LIMIT 1",
                (f"%{domain}%",)
            )
            row = cursor.fetchone()

        if row:
            result = dict(row)
            # Parse JSON criteria if present
            if result.get("criteria_json"):
                try:
                    result["criteria"] = json.loads(result["criteria_json"])
                    del result["criteria_json"]
                except (json.JSONDecodeError, TypeError):
                    result["criteria"] = None
            return result
        return None


def lookup_sources_bulk(domains: list[str]) -> dict[str, dict]:
    """
    Look up multiple sources by domain.

    Args:
        domains: List of domains to look up

    Returns:
        Dict mapping domain to source info
    """
    results = {}
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Use parameterized query for bulk lookup
        placeholders = ",".join("?" * len(domains))
        cursor.execute(
            f"SELECT * FROM sources WHERE domain IN ({placeholders})",
            domains
        )

        for row in cursor.fetchall():
            source = dict(row)
            if source.get("criteria_json"):
                try:
                    source["criteria"] = json.loads(source["criteria_json"])
                    del source["criteria_json"]
                except (json.JSONDecodeError, TypeError):
                    source["criteria"] = None
            results[source["domain"]] = source

    return results


def find_counternarratives(
    domain: str,
    min_credibility: int = 60,
    limit: int = 10,
    preferred_leans: Optional[list[int]] = None
) -> list[dict]:
    """
    Find sources from the opposite political spectrum.

    Args:
        domain: The source domain to find counternarratives for
        min_credibility: Minimum NewsGuard score (default 60)
        limit: Maximum number of results
        preferred_leans: Specific lean values to target (e.g., [1, 2] for right-leaning)

    Returns:
        List of counternarrative sources
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # First get the source's political lean
        cursor.execute(
            "SELECT political_lean FROM sources WHERE domain = ? OR domain LIKE ?",
            (domain, f"%{domain}%")
        )
        row = cursor.fetchone()

        if not row or row["political_lean"] is None:
            return []

        source_lean = row["political_lean"]

        if source_lean == 0:
            # Center sources - return both left and right
            if preferred_leans:
                placeholders = ",".join("?" * len(preferred_leans))
                cursor.execute(f"""
                    SELECT domain, name, newsguard_score, political_lean, political_lean_label,
                           source_type, description
                    FROM sources
                    WHERE political_lean IN ({placeholders})
                      AND newsguard_score >= ?
                    ORDER BY newsguard_score DESC
                    LIMIT ?
                """, (*preferred_leans, min_credibility, limit))
            else:
                cursor.execute("""
                    SELECT domain, name, newsguard_score, political_lean, political_lean_label,
                           source_type, description
                    FROM sources
                    WHERE political_lean != 0
                      AND newsguard_score >= ?
                    ORDER BY newsguard_score DESC
                    LIMIT ?
                """, (min_credibility, limit))
        else:
            # Find opposite side
            if preferred_leans:
                placeholders = ",".join("?" * len(preferred_leans))
                cursor.execute(f"""
                    SELECT domain, name, newsguard_score, political_lean, political_lean_label,
                           source_type, description
                    FROM sources
                    WHERE political_lean IN ({placeholders})
                      AND political_lean * ? < 0
                      AND newsguard_score >= ?
                    ORDER BY newsguard_score DESC
                    LIMIT ?
                """, (*preferred_leans, source_lean, min_credibility, limit))
            else:
                cursor.execute("""
                    SELECT domain, name, newsguard_score, political_lean, political_lean_label,
                           source_type, description
                    FROM sources
                    WHERE political_lean IS NOT NULL
                      AND political_lean * ? < 0
                      AND newsguard_score >= ?
                    ORDER BY newsguard_score DESC
                    LIMIT ?
                """, (source_lean, min_credibility, limit))

        return [dict(row) for row in cursor.fetchall()]


def query_sources(
    lean: Optional[int] = None,
    min_credibility: Optional[int] = None,
    source_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> tuple[list[dict], int]:
    """
    Query sources with filters.

    Args:
        lean: Political lean filter (-2 to 2)
        min_credibility: Minimum NewsGuard score
        source_type: Source type filter
        limit: Max results
        offset: Pagination offset

    Returns:
        Tuple of (sources list, total count)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Build WHERE clause dynamically
        where_clauses = []
        params = []

        if lean is not None:
            where_clauses.append("political_lean = ?")
            params.append(lean)

        if min_credibility is not None:
            where_clauses.append("newsguard_score >= ?")
            params.append(min_credibility)

        if source_type:
            where_clauses.append("source_type = ?")
            params.append(source_type)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM sources WHERE {where_sql}", params)
        total = cursor.fetchone()[0]

        # Get paginated results
        cursor.execute(f"""
            SELECT domain, name, newsguard_score, political_lean, political_lean_label,
                   source_type, description
            FROM sources
            WHERE {where_sql}
            ORDER BY newsguard_score DESC, name ASC
            LIMIT ? OFFSET ?
        """, (*params, limit, offset))

        sources = [dict(row) for row in cursor.fetchall()]

        return sources, total


def get_database_stats() -> dict:
    """Get database statistics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total sources
        cursor.execute("SELECT COUNT(*) FROM sources")
        total = cursor.fetchone()[0]

        # With NewsGuard
        cursor.execute("SELECT COUNT(*) FROM sources WHERE newsguard_score IS NOT NULL")
        with_newsguard = cursor.fetchone()[0]

        # With political lean
        cursor.execute("SELECT COUNT(*) FROM sources WHERE political_lean IS NOT NULL")
        with_lean = cursor.fetchone()[0]

        # Lean distribution
        cursor.execute("""
            SELECT political_lean_label, COUNT(*) as count
            FROM sources
            WHERE political_lean IS NOT NULL
            GROUP BY political_lean_label
            ORDER BY political_lean
        """)
        lean_distribution = {row["political_lean_label"]: row["count"] for row in cursor.fetchall()}

        # Type distribution
        cursor.execute("""
            SELECT source_type, COUNT(*) as count
            FROM sources
            GROUP BY source_type
            ORDER BY count DESC
        """)
        type_distribution = {row["source_type"]: row["count"] for row in cursor.fetchall()}

        # Credibility tiers
        cursor.execute("""
            SELECT
                COUNT(CASE WHEN newsguard_score >= 80 THEN 1 END) as high,
                COUNT(CASE WHEN newsguard_score >= 60 AND newsguard_score < 80 THEN 1 END) as medium,
                COUNT(CASE WHEN newsguard_score < 60 THEN 1 END) as low
            FROM sources
            WHERE newsguard_score IS NOT NULL
        """)
        row = cursor.fetchone()
        credibility_tiers = {
            "high": row["high"],
            "medium": row["medium"],
            "low": row["low"]
        }

        return {
            "total_sources": total,
            "with_newsguard": with_newsguard,
            "with_political_lean": with_lean,
            "lean_distribution": lean_distribution,
            "type_distribution": type_distribution,
            "credibility_tiers": credibility_tiers
        }
