"""URL parsing utilities for extracting domains from article URLs."""

import tldextract
from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    """
    Extract clean domain from URL.

    Handles various URL formats:
    - Full URLs: https://www.nytimes.com/2024/article-slug → nytimes.com
    - With subdomains: edition.cnn.com/world → cnn.com
    - Bare domains: nytimes.com → nytimes.com
    - Mobile sites: m.nytimes.com → nytimes.com

    Args:
        url: URL or domain string

    Returns:
        Clean domain (e.g., "nytimes.com")

    Examples:
        >>> extract_domain("https://www.nytimes.com/2024/01/15/article")
        'nytimes.com'
        >>> extract_domain("edition.cnn.com/world")
        'cnn.com'
        >>> extract_domain("nytimes.com")
        'nytimes.com'
    """
    # Add scheme if missing (required for urlparse)
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # Extract components using tldextract
    # This handles subdomains, domain, and suffix properly
    extracted = tldextract.extract(url)

    # Reconstruct as domain.suffix (e.g., nytimes.com)
    domain = f"{extracted.domain}.{extracted.suffix}"

    return domain


def is_valid_url(url: str) -> bool:
    """
    Check if string is a valid URL or domain.

    Args:
        url: String to validate

    Returns:
        True if valid URL/domain, False otherwise
    """
    try:
        # Try to extract domain
        domain = extract_domain(url)

        # Check that we got meaningful components
        if not domain or domain == "." or len(domain) < 3:
            return False

        return True
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent handling.

    - Ensures https:// scheme
    - Removes trailing slashes
    - Lowercases domain

    Args:
        url: URL to normalize

    Returns:
        Normalized URL
    """
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    parsed = urlparse(url)

    # Rebuild with normalized components
    normalized = f"{parsed.scheme}://{parsed.netloc.lower()}"

    if parsed.path and parsed.path != "/":
        normalized += parsed.path.rstrip("/")

    if parsed.query:
        normalized += f"?{parsed.query}"

    return normalized
