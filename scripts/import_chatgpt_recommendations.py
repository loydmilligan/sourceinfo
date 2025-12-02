#!/usr/bin/env python3
"""
Import ChatGPT recommendations into the SourceInfo database.
Maps estimated_lean to our political_lean integer scale.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path("/home/mmariani/Projects/SourceInfo/data/sources.db")
RECOMMENDATIONS_PATH = Path("/home/mmariani/Projects/SourceInfo/data/chatgpt_recommendations.json")


def map_lean_to_integer(estimated_lean: str) -> tuple[int | None, str | None]:
    """
    Map ChatGPT's estimated_lean strings to our integer scale.

    Returns: (political_lean_int, political_lean_label)
    """
    # Mapping dictionary
    lean_mapping = {
        "Left": (-2, "Left"),
        "Lean Left": (-1, "Lean Left"),
        "Center-Left": (-1, "Lean Left"),
        "Center": (0, "Center"),
        "Center-Right": (1, "Lean Right"),
        "Lean Right": (1, "Lean Right"),
        "Right": (2, "Right"),
        "Libertarian": (0, "Center"),  # Treating as center for now
        "Center-Right (Anti-Trump)": (1, "Lean Right"),
        "N/A": (None, None),
    }

    return lean_mapping.get(estimated_lean, (None, None))


def determine_source_type(category: str, notes: str = "") -> str:
    """Determine source_type based on category and notes."""
    type_mapping = {
        "international": "news_media",
        "technology": "news_media",
        "business": "news_media",
        "science_health": "news_media",
        "entertainment": "news_media",
        "sports": "news_media",
        "alternative_independent": "news_media",
    }

    # Special cases
    if "fact" in notes.lower() or "factcheck" in notes.lower():
        return "fact_check"
    if "think tank" in notes.lower():
        return "think_tank"
    if "newsletter" in notes.lower() or "substack" in notes.lower():
        return "author"
    if "wire service" in notes.lower() or "wire-service" in notes.lower():
        return "wire_service"

    return type_mapping.get(category, "news_media")


def import_recommendations():
    """Import all recommendations into the database."""

    # Load recommendations
    with open(RECOMMENDATIONS_PATH) as f:
        data = json.load(f)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {
        "total": 0,
        "new": 0,
        "updated": 0,
        "skipped": 0,
        "by_category": {},
    }

    # Process each category
    for category, sources in data.items():
        stats["by_category"][category] = 0

        for source in sources:
            domain = source["domain"]
            name = source["name"]
            description = source.get("description", "")
            notes = source.get("notes", "")

            # Map political lean
            estimated_lean = source.get("estimated_lean", "N/A")
            political_lean, political_lean_label = map_lean_to_integer(estimated_lean)

            # Determine source type
            source_type = determine_source_type(category, notes)

            # Check if source already exists
            cursor.execute("SELECT domain, name FROM sources WHERE domain = ?", (domain,))
            existing = cursor.fetchone()

            if existing:
                # Update only if we have new information
                # For now, skip if already exists to preserve NewsGuard data
                print(f"  SKIP (exists): {domain} - {name}")
                stats["skipped"] += 1
                stats["total"] += 1
                continue

            # Build full description including notes and country
            full_description = description
            if source.get("country"):
                full_description = f"[{source['country']}] {description}"
            if notes:
                full_description = f"{full_description} | {notes}"

            # Insert new source
            cursor.execute("""
                INSERT INTO sources (
                    domain, name, political_lean, political_lean_label,
                    source_type, description, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                domain,
                name,
                political_lean,
                political_lean_label,
                source_type,
                full_description,
                datetime.now().isoformat()
            ))

            print(f"  ADD: {domain} - {name} ({political_lean_label or 'N/A'}, {source_type})")
            stats["new"] += 1
            stats["total"] += 1
            stats["by_category"][category] += 1

    conn.commit()
    conn.close()

    # Print summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Total sources processed: {stats['total']}")
    print(f"  New sources added: {stats['new']}")
    print(f"  Existing (skipped): {stats['skipped']}")
    print(f"  Updated: {stats['updated']}")
    print("\nBy Category:")
    for category, count in stats["by_category"].items():
        print(f"  {category}: {count} new")

    # Show updated database stats
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM sources")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sources WHERE newsguard_score IS NOT NULL")
    with_ng = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM sources WHERE political_lean IS NOT NULL")
    with_lean = cursor.fetchone()[0]

    cursor.execute("SELECT political_lean_label, COUNT(*) FROM sources WHERE political_lean IS NOT NULL GROUP BY political_lean_label ORDER BY political_lean")
    lean_dist = cursor.fetchall()

    print("\n" + "=" * 60)
    print("UPDATED DATABASE STATS")
    print("=" * 60)
    print(f"Total sources: {total}")
    print(f"With NewsGuard data: {with_ng}")
    print(f"With political lean data: {with_lean}")
    print("\nPolitical lean distribution:")
    for label, count in lean_dist:
        print(f"  {label}: {count}")

    conn.close()


if __name__ == "__main__":
    print("Importing ChatGPT recommendations into SourceInfo database...")
    print("=" * 60)
    import_recommendations()
