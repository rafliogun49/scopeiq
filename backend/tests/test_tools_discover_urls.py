"""Unit tests for app.tools.discover_urls (A-PR4)."""
from __future__ import annotations

import pytest

from app.tools import discover_urls as discover_module
from app.tools.discover_urls import discover_urls


@pytest.fixture
def mock_root_html(monkeypatch):
    """Stub http_fetch so discover_urls returns a deterministic set of links."""
    html = """
    <html><body>
      <a href="/pricing">Pricing</a>
      <a href="/features">Features</a>
      <a href="/about-us">About</a>
      <a href="/blog/post-1">Blog 1</a>
      <a href="/blog/post-2">Blog 2</a>
      <a href="/blog/post-3">Blog 3</a>
      <a href="/blog/post-4">Blog 4</a>
      <a href="https://other.example/foo">External</a>
    </body></html>
    """

    async def _fake_fetch(url, render_js=False):
        return {"status": 200, "html": html, "text": ""}

    monkeypatch.setattr(discover_module, "http_fetch", _fake_fetch)


@pytest.mark.asyncio
async def test_discover_urls_prefers_pricing_features_about(mock_root_html):
    urls = await discover_urls("acme.test")
    # Root + 4 more = 5 URLs total (cap).
    assert len(urls) == 5
    assert urls[0] == "https://acme.test/"
    # Pricing/features/about must come before blog posts.
    assert "https://acme.test/pricing" in urls[:4]
    assert "https://acme.test/features" in urls[:4]
    assert "https://acme.test/about-us" in urls[:4]


@pytest.mark.asyncio
async def test_discover_urls_excludes_other_domains(mock_root_html):
    urls = await discover_urls("acme.test")
    assert all("other.example" not in u for u in urls)


@pytest.mark.asyncio
async def test_discover_urls_caps_at_five(mock_root_html):
    urls = await discover_urls("acme.test")
    assert len(urls) <= 5


@pytest.mark.asyncio
async def test_discover_urls_handles_https_input(mock_root_html):
    urls = await discover_urls("https://acme.test")
    assert urls[0] == "https://acme.test/"
