"""Unit tests for app.tools.http_fetch (A-PR4)."""
from __future__ import annotations

import asyncio
import time

import httpx
import pytest

from app.tools import http_fetch as http_fetch_module
from app.tools.http_fetch import http_fetch


@pytest.fixture(autouse=True)
def _clear_caches(monkeypatch):
    monkeypatch.setattr(http_fetch_module, "_host_locks", {})
    monkeypatch.setattr(http_fetch_module, "_last_request_at", {})
    monkeypatch.setattr(http_fetch_module, "_robots_cache", {})
    yield


def _install_transport(monkeypatch, handler):
    transport = httpx.MockTransport(handler)
    real_async_client = httpx.AsyncClient

    def patched_client(*args, **kwargs):
        kwargs["transport"] = transport
        return real_async_client(*args, **kwargs)

    monkeypatch.setattr(http_fetch_module.httpx, "AsyncClient", patched_client)


@pytest.mark.asyncio
async def test_http_fetch_returns_html_for_200(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="")
        return httpx.Response(200, text="<html><body>hi</body></html>")

    _install_transport(monkeypatch, handler)
    res = await http_fetch("https://example.com/page")
    assert res["status"] == 200
    assert "hi" in res["html"]


@pytest.mark.asyncio
async def test_http_fetch_respects_robots_disallow(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /\n")
        return httpx.Response(200, text="should not see")

    _install_transport(monkeypatch, handler)
    res = await http_fetch("https://example.com/page")
    assert res["status"] == 0
    assert res.get("skipped") == "robots"
    assert res["html"] == ""


@pytest.mark.asyncio
async def test_http_fetch_per_host_rate_limit(monkeypatch):
    monkeypatch.setattr(http_fetch_module, "PER_HOST_INTERVAL_SECONDS", 0.2)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="")
        return httpx.Response(200, text="ok")

    _install_transport(monkeypatch, handler)
    await http_fetch("https://example.com/a")
    start = time.monotonic()
    await http_fetch("https://example.com/b")
    elapsed = time.monotonic() - start
    assert elapsed >= 0.15  # second call waited for the per-host window


@pytest.mark.asyncio
async def test_http_fetch_handles_network_error(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="")
        raise httpx.ConnectError("boom")

    _install_transport(monkeypatch, handler)
    res = await http_fetch("https://example.com/page")
    assert res["status"] == 0
    assert "boom" in res["error"]


@pytest.mark.asyncio
async def test_http_fetch_rejects_non_http_scheme():
    res = await http_fetch("file:///etc/passwd")
    assert res["status"] == 0
    assert res["error"] == "invalid_url"


def test_http_fetch_survives_fresh_event_loop(monkeypatch):
    # Locks are keyed by (loop id, host); reusing across asyncio.run() must not blow up.
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="")
        return httpx.Response(200, text="ok")

    _install_transport(monkeypatch, handler)
    asyncio.run(http_fetch("https://example.com/a"))
    asyncio.run(http_fetch("https://example.com/b"))
