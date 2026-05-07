"""stackexchange_search tool — implemented in B-PR3.

Uses Stack Exchange API v2.3. Default sites: softwarerecs, workplace, startups, stackoverflow.
Free tier: 300 req/day without a key; register a key for 10k/day (PRD §11, risk R8).
See PRD §10.3 and TEAM_SPLIT §4 (B-PR3).
"""
# TODO (B-PR3)

DEFAULT_SITES = ["softwarerecs", "workplace", "startups", "stackoverflow"]


async def stackexchange_search(
    query: str,
    sites: list[str] | None = None,
    limit: int = 10,
) -> list[dict]:
    """Returns [{title, url, body, score, answer_count, site}]."""
    raise NotImplementedError
