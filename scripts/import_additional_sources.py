#!/usr/bin/env python3
"""
Import additional sources from research into the SourceInfo database.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path("/home/mmariani/Projects/SourceInfo/data/sources.db")
SOURCES_PATH = Path("/home/mmariani/Projects/SourceInfo/data/additional_sources_from_research.json")


def map_lean_to_integer(estimated_lean: str) -> tuple[int | None, str | None]:
    """Map estimated_lean strings to our integer scale."""
    lean_mapping = {
        "Left": (-2, "Left"),
        "Lean Left": (-1, "Lean Left"),
        "Center-Left": (-1, "Lean Left"),
        "Center": (0, "Center"),
        "Center-Right": (1, "Lean Right"),
        "Lean Right": (1, "Lean Right"),
        "Right": (2, "Right"),
        "N/A": (None, None),
    }
    return lean_mapping.get(estimated_lean, (None, None))


def determine_source_type(category: str, description: str, notes: str) -> str:
    """Determine source_type based on category and content."""
    desc_lower = description.lower()
    notes_lower = notes.lower()

    # Check for specific types
    if category == "fact_checkers" or "fact" in desc_lower or "fact-check" in notes_lower:
        return "fact_check"
    if "trade publication" in desc_lower or "industry" in desc_lower:
        return "trade_publication"
    if "think tank" in desc_lower:
        return "think_tank"

    # Default to news_media
    return "news_media"


def import_sources():
    """Import all sources into the database."""

    # Load sources
    with open(SOURCES_PATH) as f:
        data = json.load(f)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {
        "total": 0,
        "new": 0,
        "skipped": 0,
        "by_category": {},
    }

    # Process each category
    for category, sources in data.items():
        category_name = category.replace("_", " ").title()
        stats["by_category"][category_name] = 0

        print(f"\n{category_name}:")
        print("=" * 60)

        for source in sources:
            domain = source["domain"]
            name = source["name"]
            description = source.get("description", "")
            notes = source.get("notes", "")

            # Map political lean
            estimated_lean = source.get("estimated_lean", "N/A")
            political_lean, political_lean_label = map_lean_to_integer(estimated_lean)

            # Determine source type
            source_type = determine_source_type(category, description, notes)

            # Check if source already exists
            cursor.execute("SELECT domain FROM sources WHERE domain = ?", (domain,))
            existing = cursor.fetchone()

            if existing:
                print(f"  SKIP (exists): {domain}")
                stats["skipped"] += 1
                stats["total"] += 1
                continue

            # Build full description
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

            lean_str = political_lean_label or "N/A"
            print(f"  ADD: {domain} - {name} ({lean_str}, {source_type})")
            stats["new"] += 1
            stats["total"] += 1
            stats["by_category"][category_name] += 1

    conn.commit()
    conn.close()

    # Print summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Total sources processed: {stats['total']}")
    print(f"  New sources added: {stats['new']}")
    print(f"  Existing (skipped): {stats['skipped']}")
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

    cursor.execute("SELECT source_type, COUNT(*) FROM sources GROUP BY source_type ORDER BY COUNT(*) DESC")
    type_dist = cursor.fetchall()

    cursor.execute("SELECT political_lean_label, COUNT(*) FROM sources WHERE political_lean IS NOT NULL GROUP BY political_lean_label ORDER BY political_lean")
    lean_dist = cursor.fetchall()

    print("\n" + "=" * 60)
    print("UPDATED DATABASE STATS")
    print("=" * 60)
    print(f"Total sources: {total}")
    print(f"With NewsGuard data: {with_ng}")
    print(f"With political lean data: {with_lean}")

    print("\nSource type distribution:")
    for stype, count in type_dist:
        print(f"  {stype}: {count}")

    print("\nPolitical lean distribution:")
    for label, count in lean_dist:
        print(f"  {label}: {count}")

    conn.close()


if __name__ == "__main__":
    print("Importing additional sources from research...")
    print("=" * 60)
    import_sources()
