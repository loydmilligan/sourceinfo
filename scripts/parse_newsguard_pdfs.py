#!/usr/bin/env python3
"""
Parse NewsGuard PDF "Nutrition Labels" and extract structured data.
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Try to import PDF parsing libraries
try:
    import pdfplumber
    PDF_LIBRARY = "pdfplumber"
except ImportError:
    try:
        from pypdf import PdfReader
        PDF_LIBRARY = "pypdf"
    except ImportError:
        PDF_LIBRARY = None
        print("Warning: No PDF library found. Install pdfplumber or pypdf:")
        print("  pip install pdfplumber")
        print("  # or")
        print("  pip install pypdf")


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    if PDF_LIBRARY == "pdfplumber":
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text
    elif PDF_LIBRARY == "pypdf":
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    else:
        raise RuntimeError("No PDF library available")


def parse_newsguard_text(text: str, domain: str) -> dict:
    """Parse NewsGuard label text into structured data."""
    result = {
        "domain": domain,
        "name": None,
        "newsguard_score": None,
        "newsguard_rating": None,
        "criteria": {
            "false_content": {"status": None, "points": None},
            "responsible_gathering": {"status": None, "points": None},
            "corrections": {"status": None, "points": None},
            "news_opinion_separation": {"status": None, "points": None},
            "avoids_deceptive_headlines": {"status": None, "points": None},
            "ownership_disclosure": {"status": None, "points": None},
            "labels_advertising": {"status": None, "points": None},
            "reveals_leadership": {"status": None, "points": None},
            "content_creator_info": {"status": None, "points": None},
        },
        "description": None,
        "ownership_summary": None,
        "source_type": "news_media",
    }

    # Extract score (e.g., "80 / 100" or "80/100")
    score_match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*100', text)
    if score_match:
        result["newsguard_score"] = float(score_match.group(1))

    # Extract rating category
    if "High Credibility" in text:
        result["newsguard_rating"] = "High Credibility"
    elif "Generally Credible" in text:
        result["newsguard_rating"] = "Generally Credible"
    elif "Proceed with Caution" in text or "Proceed With Caution" in text:
        result["newsguard_rating"] = "Proceed with Caution"
    elif "Low Credibility" in text:
        result["newsguard_rating"] = "Low Credibility"

    # Define criteria with their max points - if we see the max points, it's a pass
    criteria_config = [
        ("false_content", ["false", "misleading content"], 22),
        ("responsible_gathering", ["gathers", "presents information responsibly"], 18),
        ("corrections", ["correcting errors", "effective practices"], 12.5),
        ("news_opinion_separation", ["news and opinion", "opinion responsibly"], 12.5),
        ("avoids_deceptive_headlines", ["deceptive headlines"], 10),
        ("ownership_disclosure", ["ownership and financing", "discloses ownership"], 7.5),
        ("labels_advertising", ["labels advertising", "clearly labels"], 7.5),
        ("reveals_leadership", ["who's in charge", "conflicts of interest"], 5),
        ("content_creator_info", ["content creators", "biographical information"], 5),
    ]

    # Parse criteria from the text
    # The format is usually: "Criterion text 22 points" or "Criterion text 18"
    for crit_key, keywords, max_points in criteria_config:
        for keyword in keywords:
            # Find lines containing this criterion's keywords
            pattern = re.compile(
                rf'({keyword}).*?(\d+(?:\.\d+)?)\s*(?:points?)?',
                re.IGNORECASE | re.DOTALL
            )
            match = pattern.search(text)
            if match:
                points = float(match.group(2))
                result["criteria"][crit_key]["points"] = points
                # If points equal max, it's a pass. Otherwise fail.
                # (Some criteria have N/A which shows as 7.5 for advertising)
                if points >= max_points - 0.1:  # Small tolerance
                    result["criteria"][crit_key]["status"] = "pass"
                elif points == 0:
                    result["criteria"][crit_key]["status"] = "fail"
                else:
                    # Partial points - could be pass with deductions or fail
                    # We'll infer based on whether it's more than half
                    result["criteria"][crit_key]["status"] = "pass" if points > max_points / 2 else "fail"
                break

    # Extract description (first paragraph after domain name)
    desc_match = re.search(rf'{re.escape(domain)}\s*\n(.+?)(?:\d+(?:\.\d+)?\s*/\s*100)', text, re.DOTALL | re.IGNORECASE)
    if desc_match:
        desc = desc_match.group(1).strip()
        # Clean up
        desc = re.sub(r'\s+', ' ', desc)
        if len(desc) > 30:  # Only keep if it looks like a real description
            result["description"] = desc[:500]  # Truncate if too long

    # Extract ownership summary - get first 2-3 paragraphs
    ownership_match = re.search(r'Ownership and Financing\s*\n(.+?)(?:\nContent\n|\nCredibility\n)', text, re.DOTALL | re.IGNORECASE)
    if ownership_match:
        ownership = ownership_match.group(1).strip()
        ownership = re.sub(r'\s+', ' ', ownership)
        if len(ownership) > 20:
            result["ownership_summary"] = ownership[:1000]

    return result


def process_all_pdfs(pdf_dir: str, output_file: str):
    """Process all PDFs in directory and output JSON."""
    pdf_dir = Path(pdf_dir)
    results = []
    errors = []

    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")

    for pdf_path in sorted(pdf_files):
        domain = pdf_path.stem  # filename without extension
        print(f"Processing: {domain}")

        try:
            text = extract_text_from_pdf(str(pdf_path))
            data = parse_newsguard_text(text, domain)
            results.append(data)
        except Exception as e:
            print(f"  Error: {e}")
            errors.append({"domain": domain, "error": str(e)})

    # Save results
    output = {
        "metadata": {
            "source": "NewsGuard Nutrition Labels",
            "extracted_date": datetime.now().isoformat(),
            "total_processed": len(results),
            "errors": len(errors)
        },
        "sources": results,
        "errors": errors
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(results)} sources to {output_file}")
    if errors:
        print(f"Errors: {len(errors)}")

    return results


def test_single_pdf(pdf_path: str):
    """Test parsing on a single PDF and print results."""
    print(f"Testing: {pdf_path}")
    print("=" * 60)

    text = extract_text_from_pdf(pdf_path)
    print("Raw text (first 2000 chars):")
    print(text[:2000])
    print("\n" + "=" * 60)

    domain = Path(pdf_path).stem
    data = parse_newsguard_text(text, domain)

    print("\nParsed data:")
    print(json.dumps(data, indent=2))

    return data


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode - process single PDF
        if len(sys.argv) > 2:
            test_single_pdf(sys.argv[2])
        else:
            # Default test file
            test_single_pdf("/home/mmariani/Projects/SourceInfo/scraper/pdfs/nytimes.com.pdf")
    else:
        # Process all PDFs
        process_all_pdfs(
            "/home/mmariani/Projects/SourceInfo/scraper/pdfs",
            "/home/mmariani/Projects/SourceInfo/data/newsguard_extracted.json"
        )
