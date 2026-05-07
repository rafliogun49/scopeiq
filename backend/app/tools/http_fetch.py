"""http_fetch tool — implemented in A-PR4.

Fetches a URL with httpx, respects robots.txt, rate-limits per host (1 req/s).
Falls back to Playwright if render_js=True.
See PRD §10.3.
"""
# TODO (A-PR4)


async def http_fetch(url: str, render_js: bool = False) -> dict:
    """Returns {status, html, text}."""
    raise NotImplementedError
