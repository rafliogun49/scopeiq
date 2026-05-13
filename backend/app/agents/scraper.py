"""Scraper agent — A-PR4.

Fetches competitor landing/pricing/about pages. Uses gpt-4o-mini.
Tools: http_fetch, discover_urls. See PRD §10 and TEAM_SPLIT §3 (A-PR4).

Why http_fetch_tool returns metadata instead of full HTML/text:
the openai-agents SDK accumulates every tool result into conversation history,
so returning raw HTML (~50–200KB/page) blew the context window after a few
fetches. The full extracted text is still captured in raw_docs_var for the
downstream index_chunks() call; the LLM only needs to know fetches succeeded.
"""
from __future__ import annotations

from contextvars import ContextVar
from pathlib import Path
from typing import Any, Literal

from agents import Agent, function_tool

from app.schemas.rag import RawDoc
from app.tools.discover_urls import discover_urls as _discover_urls
from app.tools.extract_text import extract_text as _extract_text
from app.tools.http_fetch import http_fetch as _http_fetch

SourceType = Literal["landing", "pricing", "review_snippet", "community", "hn", "stackexchange"]

# Per-run accumulator for RawDocs produced by the scraper. The runner sets
# this contextvar before invoking the agent and reads it after the run.
raw_docs_var: ContextVar[list[RawDoc] | None] = ContextVar("scopeiq_raw_docs", default=None)
# Tracks the competitor whose URLs we are currently scraping so RawDocs can be
# attributed correctly without the LLM passing it through.
current_competitor_var: ContextVar[str | None] = ContextVar("scopeiq_current_competitor", default=None)


def _classify(url: str) -> SourceType:
    path = url.lower()
    if "pricing" in path or "plans" in path:
        return "pricing"
    return "landing"


@function_tool
async def http_fetch_tool(url: str) -> dict[str, Any]:
    """Fetch a URL, store its extracted text, and return only metadata (status, char count)."""
    result = await _http_fetch(url)
    status = result.get("status", 0)
    chars = 0
    html = result.get("html", "")
    if html:
        extracted = _extract_text(html, base_url=url)
        text = extracted["text"]
        chars = len(text)
        docs = raw_docs_var.get()
        if docs is not None and text:
            docs.append(
                RawDoc(
                    url=url,
                    text=text,
                    source_type=_classify(url),
                    competitor=current_competitor_var.get(),
                )
            )
    summary: dict[str, Any] = {"url": url, "status": status, "chars": chars}
    if "skipped" in result:
        summary["skipped"] = result["skipped"]
    if "error" in result:
        summary["error"] = result["error"]
    return summary


@function_tool
async def discover_urls_tool(domain: str) -> list[str]:
    """Crawl `domain` one level and return up to 5 likely landing/pricing/about URLs."""
    return await _discover_urls(domain)


_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "scraper.md"
scraper_agent = Agent(
    name="Scraper",
    model="gpt-4o-mini",
    instructions=_PROMPT_PATH.read_text(encoding="utf-8") if _PROMPT_PATH.exists() else "",
    tools=[discover_urls_tool, http_fetch_tool],
)
