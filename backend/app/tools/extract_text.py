"""extract_text tool — A-PR4.

Uses trafilatura for clean article extraction; lxml for link enumeration.
See PRD §10.3.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import trafilatura
from lxml import html as lxml_html

from app.workers.run_events import emit_event


def extract_text(html: str, base_url: str | None = None) -> dict[str, Any]:
    """Extract title, body text, and outbound links from an HTML document.

    Returns ``{title, text, links}``. Links are absolute when ``base_url`` is provided.
    """
    if not html:
        emit_event(
            "tool_called",
            agent="scraper",
            payload={"tool": "extract_text", "base_url": base_url, "chars": 0},
        )
        return {"title": "", "text": "", "links": []}

    text = trafilatura.extract(html, include_links=False, include_comments=False) or ""

    title = ""
    metadata = trafilatura.extract_metadata(html)
    if metadata is not None and metadata.title:
        title = metadata.title

    links: list[str] = []
    seen: set[str] = set()
    try:
        tree = lxml_html.fromstring(html)
    except (ValueError, lxml_html.etree.ParserError):
        tree = None
    if tree is not None:
        for a in tree.iter("a"):
            href = a.get("href")
            if not href:
                continue
            href = href.strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            absolute = urljoin(base_url, href) if base_url else href
            if absolute in seen:
                continue
            seen.add(absolute)
            links.append(absolute)

    emit_event(
        "tool_called",
        agent="scraper",
        payload={
            "tool": "extract_text",
            "base_url": base_url,
            "chars": len(text),
            "links": len(links),
        },
    )
    return {"title": title, "text": text, "links": links}
