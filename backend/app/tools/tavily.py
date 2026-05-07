"""tavily_search tool — implemented in B-PR3.

Three call patterns:
1. Review snippets — include_domains=["g2.com","trustpilot.com","capterra.com"]
2. Indie Hackers threads — include_domains=["indiehackers.com"]
3. General market signal — exclude_domains=["reddit.com"]
See PRD §10.3 and TEAM_SPLIT §4 (B-PR3).
"""
# TODO (B-PR3)


async def tavily_search(
    query: str,
    max_results: int = 5,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
) -> list[dict]:
    """Returns [{title, url, snippet}]."""
    raise NotImplementedError
