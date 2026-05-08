"""hn_search tool — B-PR3. Algolia HN API, free no auth."""

import httpx

_BASE = "https://hn.algolia.com/api/v1/search"


async def hn_search(query: str, limit: int = 10) -> list[dict]:
    """Returns [{title, url, points, comments_count, story_text}]."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            _BASE,
            params={
                "query": query,
                "tags": "story",
                "hitsPerPage": limit,
            },
        )
        resp.raise_for_status()
        hits = resp.json().get("hits", [])

    return [
        {
            "title": h.get("title", ""),
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
            "points": h.get("points", 0),
            "comments_count": h.get("num_comments", 0),
            "story_text": (h.get("story_text") or "")[:500],
        }
        for h in hits
    ]
