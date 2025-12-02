#!/usr/bin/env python3
"""
Build the unified SourceInfo SQLite database from NewsGuard and AllSides data.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime


def load_newsguard_data(filepath: str) -> dict:
    """Load NewsGuard extracted data."""
    with open(filepath) as f:
        data = json.load(f)
    # Convert to dict keyed by domain
    return {s["domain"]: s for s in data["sources"]}


def load_allsides_data(filepath: str) -> dict:
    """Load AllSides ratings data."""
    with open(filepath) as f:
        data = json.load(f)

    # Convert to dict keyed by domain
    # Handle multiple entries per domain (news vs opinion) by taking primary
    result = {}
    for entry in data["ratings"]:
        domain = entry.get("domain")
        if not domain:
            continue

        # If domain already exists, prefer News over Opinion entries
        if domain in result:
            if "Opinion" in entry.get("name", ""):
                continue  # Skip opinion variants if we have news

        result[domain] = {
            "name": entry["name"],
            "political_lean": entry["lean"],
            "political_lean_label": {
                -2: "Left",
                -1: "Lean Left",
                0: "Center",
                1: "Lean Right",
                2: "Right"
            }.get(entry["lean"], "Unknown"),
            "source_type": entry.get("type", "News Media").lower().replace(" ", "_").replace("/", "_")
        }

    return result


def create_database(db_path: str, newsguard_data: dict, allsides_data: dict):
    """Create SQLite database with merged data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            domain TEXT PRIMARY KEY,
            name TEXT,

            -- NewsGuard data
            newsguard_score REAL,
            newsguard_rating TEXT,

            -- 9 NewsGuard criteria (JSON)
            criteria_json TEXT,

            -- AllSides data
            political_lean INTEGER,
            political_lean_label TEXT,

            -- Source classification
            source_type TEXT,

            -- Descriptive content
            description TEXT,
            ownership_summary TEXT,

            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_political_lean ON sources(political_lean)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_newsguard_score ON sources(newsguard_score)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source_type ON sources(source_type)")

    # Get all unique domains from both sources
    all_domains = set(newsguard_data.keys()) | set(allsides_data.keys())

    print(f"NewsGuard sources: {len(newsguard_data)}")
    print(f"AllSides sources: {len(allsides_data)}")
    print(f"Total unique domains: {len(all_domains)}")

    # Insert/merge data
    for domain in sorted(all_domains):
        ng = newsguard_data.get(domain, {})
        als = allsides_data.get(domain, {})

        # Determine name - prefer AllSides name as it's cleaner
        name = als.get("name") or ng.get("name") or domain

        cursor.execute("""
            INSERT OR REPLACE INTO sources (
                domain, name, newsguard_score, newsguard_rating,
                criteria_json, political_lean, political_lean_label,
                source_type, description, ownership_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            domain,
            name,
            ng.get("newsguard_score"),
            ng.get("newsguard_rating"),
            json.dumps(ng.get("criteria")) if ng.get("criteria") else None,
            als.get("political_lean"),
            als.get("political_lean_label"),
            als.get("source_type") or ng.get("source_type") or "news_media",
            ng.get("description"),
            ng.get("ownership_summary")
        ))

    conn.commit()

    # Print summary
    cursor.execute("SELECT COUNT(*) FROM sources")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sources WHERE newsguard_score IS NOT NULL")
    with_ng = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sources WHERE political_lean IS NOT NULL")
    with_als = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sources WHERE newsguard_score IS NOT NULL AND political_lean IS NOT NULL")
    with_both = cursor.fetchone()[0]

    print(f"\nDatabase created: {db_path}")
    print(f"Total sources: {total}")
    print(f"With NewsGuard data: {with_ng}")
    print(f"With AllSides data: {with_als}")
    print(f"With both: {with_both}")

    # Show sample of sources with both
    print("\nSample sources with both NewsGuard and AllSides data:")
    cursor.execute("""
        SELECT domain, name, newsguard_score, political_lean_label
        FROM sources
        WHERE newsguard_score IS NOT NULL AND political_lean IS NOT NULL
        ORDER BY domain
        LIMIT 15
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[2]}/100, {row[3]}")

    conn.close()
    return total


def create_counternarrative_view(db_path: str):
    """Create a view for finding counternarrative sources."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop and recreate view
    cursor.execute("DROP VIEW IF EXISTS counternarrative_pairs")
    cursor.execute("""
        CREATE VIEW counternarrative_pairs AS
        SELECT
            s1.domain as source_domain,
            s1.name as source_name,
            s1.political_lean as source_lean,
            s1.political_lean_label as source_lean_label,
            s1.newsguard_score as source_credibility,
            s2.domain as counter_domain,
            s2.name as counter_name,
            s2.political_lean as counter_lean,
            s2.political_lean_label as counter_lean_label,
            s2.newsguard_score as counter_credibility
        FROM sources s1
        CROSS JOIN sources s2
        WHERE s1.political_lean IS NOT NULL
          AND s2.political_lean IS NOT NULL
          AND s1.political_lean != 0
          AND s2.political_lean != 0
          AND s1.political_lean * s2.political_lean < 0  -- opposite sides
          AND s2.newsguard_score >= 60  -- minimum credibility threshold
        ORDER BY s1.domain, s2.newsguard_score DESC
    """)

    conn.commit()

    # Test the view
    print("\nCounternarrative view created. Sample queries:")

    cursor.execute("""
        SELECT source_domain, source_lean_label, counter_domain, counter_lean_label, counter_credibility
        FROM counternarrative_pairs
        WHERE source_domain = 'nytimes.com'
        LIMIT 5
    """)
    print("\nCounternarratives for nytimes.com (Lean Left):")
    for row in cursor.fetchall():
        print(f"  -> {row[2]} ({row[3]}, score: {row[4]})")

    cursor.execute("""
        SELECT source_domain, source_lean_label, counter_domain, counter_lean_label, counter_credibility
        FROM counternarrative_pairs
        WHERE source_domain = 'foxnews.com'
        LIMIT 5
    """)
    print("\nCounternarratives for foxnews.com (Lean Right / Right):")
    for row in cursor.fetchall():
        print(f"  -> {row[2]} ({row[3]}, score: {row[4]})")

    conn.close()


if __name__ == "__main__":
    base_dir = Path("/home/mmariani/Projects/SourceInfo")

    # Load data
    newsguard = load_newsguard_data(base_dir / "data" / "newsguard_extracted.json")
    allsides = load_allsides_data(base_dir / "data" / "allsides_ratings.json")

    # Build database
    db_path = base_dir / "data" / "sources.db"
    create_database(str(db_path), newsguard, allsides)

    # Create counternarrative view
    create_counternarrative_view(str(db_path))
