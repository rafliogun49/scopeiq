"""http_fetch tool — A-PR4.

Fetches a URL with httpx, respects robots.txt, rate-limits per host (1 req/s).
See PRD §10.3 and §20 NFR-9.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

from app.core.config import settings
from app.core.retry import async_retry
from app.workers.budget import BudgetExceeded, get_budget
from app.workers.run_events import emit_event

USER_AGENT = "ScopeIQBot/0.1 (+https://github.com/social-wiz/scopeiq)"
PER_HOST_INTERVAL_SECONDS = 1.0
REQUEST_TIMEOUT_SECONDS = 15.0

_host_locks: dict[tuple[int, str], asyncio.Lock] = {}
_last_request_at: dict[str, float] = {}
_robots_cache: dict[str, RobotFileParser] = {}


def _host_lock(host: str) -> asyncio.Lock:
    # Key locks by (running-loop id, host) — asyncio.Lock binds to the loop on
    # first acquire, so reusing a lock across asyncio.run() calls breaks.
    key = (id(asyncio.get_running_loop()), host)
    lock = _host_locks.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _host_locks[key] = lock
    return lock


async def _fetch_robots(client: httpx.AsyncClient, scheme: str, host: str) -> RobotFileParser:
    cached = _robots_cache.get(host)
    if cached is not None:
        return cached
    rp = RobotFileParser()
    try:
        r = await client.get(
            f"{scheme}://{host}/robots.txt",
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if r.status_code >= 400 or not r.text.strip():
            rp.parse([])  # treat missing/blocked robots as allow-all
        else:
            rp.parse(r.text.splitlines())
    except httpx.HTTPError:
        rp.parse([])
    _robots_cache[host] = rp
    return rp


async def http_fetch(url: str, render_js: bool = False) -> dict[str, Any]:
    """Fetch a URL respecting robots.txt and per-host rate limits.

    Returns ``{status, html, text}``. Adds ``skipped`` or ``error`` keys when
    the fetch was blocked or failed, so the caller never has to handle exceptions.
    """
    # TODO (later PR): Playwright fallback when render_js=True.
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        emit_event("tool_called", agent="scraper", payload={"tool": "http_fetch", "url": url, "status": 0, "error": "invalid_url"})
        return {"status": 0, "html": "", "text": "", "error": "invalid_url"}
    host = parsed.netloc

    async with httpx.AsyncClient(
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT_SECONDS,
    ) as client:
        rp = await _fetch_robots(client, parsed.scheme, host)
        if not rp.can_fetch(USER_AGENT, url):
            emit_event("tool_called", agent="scraper", payload={"tool": "http_fetch", "url": url, "status": 0, "skipped": "robots"})
            return {"status": 0, "html": "", "text": "", "skipped": "robots"}

        # Record this fetch against the per-run budget before making the request.
        # BudgetExceeded propagates up to the agent runner / Celery task.
        budget = get_budget()
        if budget is not None:
            budget.record_tool_call("fetch")

        async with _host_lock(host):
            wait = PER_HOST_INTERVAL_SECONDS - (time.monotonic() - _last_request_at.get(host, 0.0))
            if wait > 0:
                await asyncio.sleep(wait)
            try:
                r = await async_retry(
                    lambda: client.get(url),
                    attempts=settings.RETRY_ATTEMPTS,
                    base_seconds=settings.RETRY_BASE_SECONDS,
                )
            except BudgetExceeded:
                # Budget cap hit inside retry — propagate so the run can be marked failed.
                _last_request_at[host] = time.monotonic()
                raise
            except Exception as exc:
                # httpx.HTTPError exhausted all retries or other failure — return error dict.
                _last_request_at[host] = time.monotonic()
                emit_event("tool_called", agent="scraper", payload={"tool": "http_fetch", "url": url, "status": 0, "error": str(exc)})
                return {"status": 0, "html": "", "text": "", "error": str(exc)}
            _last_request_at[host] = time.monotonic()

        emit_event("tool_called", agent="scraper", payload={"tool": "http_fetch", "url": url, "status": r.status_code})
        if r.status_code >= 400:
            return {"status": r.status_code, "html": "", "text": ""}
        return {"status": r.status_code, "html": r.text, "text": ""}
