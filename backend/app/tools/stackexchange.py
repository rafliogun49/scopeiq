"""stackexchange_search tool — B-PR3. Stack Exchange API v2.3."""

import asyncio

import httpx

DEFAULT_SITES = ["softwarerecs", "workplace", "startups", "stackoverflow"]
_BASE = "https://api.stackexchange.com/2.3/search/advanced"


async def _search_one(
    client: httpx.AsyncClient,
    query: str,
    site: str,
    limit: int,
) -> list[dict]:
    resp = await client.get(
        _BASE,
        params={
            "q": query,
            "site": site,
            "pagesize": limit,
            "order": "desc",
            "sort": "relevance",
            "filter": "withbody",
        },
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    return [
        {
            "title": i.get("title", ""),
            "url": i.get("link", ""),
            "body": (i.get("body") or "")[:500],
            "score": i.get("score", 0),
            "answer_count": i.get("answer_count", 0),
            "site": site,
        }
        for i in items
    ]


async def stackexchange_search(
    query: str,
    sites: list[str] | None = None,
    limit: int = 10,
) -> list[dict]:
    """Returns [{title, url, body, score, answer_count, site}]."""
    target_sites = sites or DEFAULT_SITES

    async with httpx.AsyncClient(timeout=15) as client:
        tasks = [_search_one(client, query, site, limit) for site in target_sites]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    for r in results:
        if isinstance(r, list):
            all_items.extend(r)

    # Sort by score descending
    return sorted(all_items, key=lambda x: x["score"], reverse=True)
