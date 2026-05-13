"""discover_urls tool — A-PR4.

1-level crawl on a competitor domain looking for /pricing, /features, /about.
Cap: 5 URLs per domain. See PRD §10.3.
"""
from __future__ import annotations

from urllib.parse import urlparse

from app.tools.extract_text import extract_text
from app.tools.http_fetch import http_fetch
from app.workers.run_events import emit_event

PREFERRED_PATH_TOKENS = ("pricing", "features", "about", "plans", "product")
MAX_URLS = 5


def _normalize_root(domain: str) -> str:
    domain = domain.strip()
    if not domain:
        return ""
    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain
    parsed = urlparse(domain)
    return f"{parsed.scheme}://{parsed.netloc}/"


def _registrable(host: str) -> str:
    parts = host.lower().split(":", 1)[0].split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else parts[0]


async def discover_urls(domain: str) -> list[str]:
    """Return up to 5 URLs from `domain`'s root that look like landing/pricing/about pages."""
    root = _normalize_root(domain)
    if not root:
        return []

    fetched = await http_fetch(root)
    html = fetched.get("html", "")
    extracted = extract_text(html, base_url=root)

    root_host = urlparse(root).netloc
    root_reg = _registrable(root_host)

    preferred: list[str] = []
    other: list[str] = []
    seen: set[str] = {root}
    for link in extracted["links"]:
        parsed = urlparse(link)
        if parsed.scheme not in {"http", "https"}:
            continue
        if _registrable(parsed.netloc) != root_reg:
            continue
        canonical = parsed._replace(fragment="", query="").geturl()
        if canonical in seen:
            continue
        seen.add(canonical)
        path_lower = parsed.path.lower()
        if any(token in path_lower for token in PREFERRED_PATH_TOKENS):
            preferred.append(canonical)
        else:
            other.append(canonical)

    urls = [root, *preferred, *other][:MAX_URLS]
    emit_event(
        "tool_called",
        agent="scraper",
        payload={"tool": "discover_urls", "domain": domain, "found": len(urls)},
    )
    return urls
