"""SSE stream endpoint test (A-PR4)."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

_FAKE_HTML = """
<html><head><title>Acme</title></head><body>
  <h1>Acme Pricing</h1><p>Pro plan: $19/month.</p>
  <a href="/pricing">Pricing</a>
</body></html>
"""


@pytest.fixture(autouse=True)
def _stub_runner(monkeypatch):
    from app.agents import runner as runner_module
    from app.rag import index as index_module
    from app.tools import discover_urls as discover_module
    from app.tools import http_fetch as http_fetch_module

    runner_module.use_stub_runner()

    async def _fake_fetch(url, render_js=False):
        return {"status": 200, "html": _FAKE_HTML, "text": ""}

    async def _fake_index(run_id, docs):
        return len(docs)

    monkeypatch.setattr(http_fetch_module, "http_fetch", _fake_fetch)
    monkeypatch.setattr(runner_module, "http_fetch", _fake_fetch)
    monkeypatch.setattr(discover_module, "http_fetch", _fake_fetch)
    monkeypatch.setattr(index_module, "index_chunks", _fake_index)
    yield
    runner_module.use_real_runner()


@pytest.fixture(autouse=True)
def _short_stream_poll(monkeypatch):
    from app.api import runs as runs_module

    monkeypatch.setattr(runs_module, "STREAM_POLL_SECONDS", 0.05)


def _make_project(client: TestClient, headers: dict[str, str]) -> str:
    r = client.post(
        "/api/v1/projects",
        json={"name": "p", "idea": "Notion alts", "known_competitors": ["acme.test"]},
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


def _parse_sse(text: str) -> list[tuple[str, dict]]:
    """Naively parse the SSE response body into (event_name, data_dict) tuples."""
    out: list[tuple[str, dict]] = []
    current_event: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("event:"):
            current_event = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            data = line.split(":", 1)[1].strip()
            if current_event:
                out.append((current_event, json.loads(data)))
                current_event = None
    return out


def test_stream_emits_progress_then_complete(client: TestClient, auth_headers):
    headers = auth_headers()
    project_id = _make_project(client, headers)

    run_id = client.post(f"/api/v1/projects/{project_id}/runs", headers=headers).json()["run_id"]

    # Run already completed (eager Celery). Stream should drain events + emit complete.
    with client.stream("GET", f"/api/v1/runs/{run_id}/stream", headers=headers) as r:
        assert r.status_code == 200
        assert "text/event-stream" in r.headers["content-type"]
        body = "".join(chunk for chunk in r.iter_text())

    frames = _parse_sse(body)
    assert frames, "expected at least one SSE frame"
    assert frames[-1][0] == "complete"
    assert frames[-1][1]["status"] == "completed"
    assert frames[-1][1]["run_id"] == run_id

    progress_frames = [f for f in frames if f[0] == "progress"]
    types = [f[1]["type"] for f in progress_frames]
    assert types[0] == "plan"
    assert "agent_finished" in types


def test_stream_404_for_other_user(client: TestClient, auth_headers):
    alice = auth_headers("alice@example.com")
    bob = auth_headers("bob@example.com")
    project_id = _make_project(client, bob)
    run_id = client.post(f"/api/v1/projects/{project_id}/runs", headers=bob).json()["run_id"]

    r = client.get(f"/api/v1/runs/{run_id}/stream", headers=alice)
    assert r.status_code == 404
