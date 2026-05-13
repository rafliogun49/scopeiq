"""Unit tests for app.tools.extract_text (A-PR4)."""
from __future__ import annotations

from app.tools.extract_text import extract_text

_SAMPLE = """
<!doctype html>
<html><head><title>Acme — Pricing</title></head>
<body>
  <h1>Acme Plans</h1>
  <p>Our flagship plan is $19/month and supports unlimited projects.</p>
  <p>Compare it to the free tier, which covers solo founders.</p>
  <a href="/features">Features</a>
  <a href="https://other.example/post">External</a>
  <a href="javascript:void(0)">Skip</a>
  <a href="#anchor">Anchor</a>
  <a href="mailto:hi@acme.test">Mail</a>
</body></html>
"""


def test_extract_text_returns_title_text_and_links():
    result = extract_text(_SAMPLE, base_url="https://acme.test/pricing")
    assert "Acme" in result["title"]
    assert "$19/month" in result["text"]
    # Internal href resolved to absolute against base_url.
    assert "https://acme.test/features" in result["links"]
    assert "https://other.example/post" in result["links"]
    # Skip JS, anchor, and mailto.
    assert all("javascript" not in href for href in result["links"])
    assert all("mailto" not in href for href in result["links"])
    assert all(not href.startswith("#") for href in result["links"])


def test_extract_text_empty_input():
    result = extract_text("")
    assert result == {"title": "", "text": "", "links": []}


def test_extract_text_handles_garbage_html():
    result = extract_text("not really html <<<>")
    # Should not raise; text may be empty.
    assert "links" in result
    assert isinstance(result["links"], list)
