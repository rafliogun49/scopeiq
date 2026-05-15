"""tavily_search tool — B-PR3."""

import os
import pathlib

from dotenv import load_dotenv
from tavily import AsyncTavilyClient

load_dotenv(pathlib.Path(__file__).parent.parent.parent.parent / ".env")


def _client() -> AsyncTavilyClient:
    return AsyncTavilyClient(api_key=os.environ["TAVILY_API_KEY"])


async def tavily_search(
    query: str,
    max_results: int = 5,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
) -> list[dict]:
    """Returns [{title, url, snippet}]."""
    response = await _client().search(
        query=query,
        max_results=max_results,
        include_domains=include_domains or [],
        exclude_domains=exclude_domains or [],
        search_depth="advanced",
    )
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
        }
        for r in response.get("results", [])
    ]
