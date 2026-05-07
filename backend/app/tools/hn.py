"""hn_search tool — implemented in B-PR3.

Uses Algolia HN Search API (free, no auth).
See PRD §10.3 and TEAM_SPLIT §4 (B-PR3).
"""
# TODO (B-PR3)


async def hn_search(query: str, limit: int = 10) -> list[dict]:
    """Returns [{title, url, points, comments_count, story_text}]."""
    raise NotImplementedError
