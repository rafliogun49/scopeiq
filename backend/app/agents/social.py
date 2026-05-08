"""Social agent — B-PR3."""

import pathlib

from agents import Agent, function_tool

from app.tools.hn import hn_search
from app.tools.stackexchange import stackexchange_search
from app.tools.tavily import tavily_search

# Load prompt dari file
_PROMPT = (pathlib.Path(__file__).parent.parent.parent / "prompts" / "social.md").read_text()


@function_tool
async def tool_tavily_search(
    query: str,
    max_results: int = 5,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
) -> list[dict]:
    """Cari artikel, review, dan thread dari domain tertentu."""
    return await tavily_search(query, max_results, include_domains, exclude_domains)


@function_tool
async def tool_hn_search(query: str, limit: int = 10) -> list[dict]:
    """Cari thread di Hacker News via Algolia."""
    return await hn_search(query, limit)


@function_tool
async def tool_stackexchange_search(
    query: str,
    sites: list[str] | None = None,
    limit: int = 10,
) -> list[dict]:
    """Cari pertanyaan di Stack Exchange (softwarerecs, workplace, startups, stackoverflow)."""
    return await stackexchange_search(query, sites, limit)


social_agent = Agent(
    name="SocialAgent",
    model="gpt-4o-mini",
    instructions=_PROMPT,
    tools=[tool_tavily_search, tool_hn_search, tool_stackexchange_search],
)
