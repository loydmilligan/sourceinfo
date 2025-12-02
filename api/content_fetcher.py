"""Article content fetching using Jina AI Reader API."""

import httpx
from typing import Optional
from dataclasses import dataclass

# Jina AI Reader API - converts URLs to clean markdown
JINA_READER_URL = "https://r.jina.ai/"


@dataclass
class ArticleContent:
    """Extracted article content."""
    url: str
    title: Optional[str]
    content: str
    method: str  # "jina" or "manual"
    word_count: int
    success: bool
    error: Optional[str] = None


async def fetch_article_content(
    url: str,
    timeout: float = 30.0
) -> ArticleContent:
    """
    Fetch and extract article content using Jina AI Reader.

    Args:
        url: The article URL to fetch
        timeout: Request timeout in seconds

    Returns:
        ArticleContent with extracted text or error
    """
    try:
        jina_url = f"{JINA_READER_URL}{url}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                jina_url,
                timeout=timeout,
                headers={
                    "Accept": "text/plain",
                    # Jina returns markdown by default
                }
            )

            if response.status_code != 200:
                return ArticleContent(
                    url=url,
                    title=None,
                    content="",
                    method="jina",
                    word_count=0,
                    success=False,
                    error=f"Jina AI returned status {response.status_code}"
                )

            content = response.text

            # Check if we got meaningful content
            if len(content.strip()) < 200:
                return ArticleContent(
                    url=url,
                    title=None,
                    content=content,
                    method="jina",
                    word_count=len(content.split()),
                    success=False,
                    error="Content too short - may be paywalled or blocked"
                )

            # Try to extract title from first line (usually markdown heading)
            lines = content.strip().split('\n')
            title = None
            if lines and lines[0].startswith('#'):
                title = lines[0].lstrip('#').strip()

            word_count = len(content.split())

            return ArticleContent(
                url=url,
                title=title,
                content=content,
                method="jina",
                word_count=word_count,
                success=True,
                error=None
            )

    except httpx.TimeoutException:
        return ArticleContent(
            url=url,
            title=None,
            content="",
            method="jina",
            word_count=0,
            success=False,
            error="Request timed out"
        )
    except Exception as e:
        return ArticleContent(
            url=url,
            title=None,
            content="",
            method="jina",
            word_count=0,
            success=False,
            error=f"Failed to fetch: {str(e)}"
        )


def create_manual_content(url: str, content: str, title: Optional[str] = None) -> ArticleContent:
    """
    Create ArticleContent from manually provided text.

    Use this when Jina fails and user provides content via Playwright MCP
    or copy/paste.
    """
    return ArticleContent(
        url=url,
        title=title,
        content=content,
        method="manual",
        word_count=len(content.split()),
        success=True,
        error=None
    )
