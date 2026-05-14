"""Integration tests: budget-exceeded forces run to failed — A-PR5."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

_FAKE_HTML = """
<html><head><title>Acme</title></head><body>
  <p>Acme charges $19/month.</p>
  <a href="/pricing">Pricing</a>
</body></html>
"""


@pytest.fixture(autouse=True)
def _stub_runner_and_fetch(monkeypatch):
    from app.agents import runner as runner_module
    from app.tools import discover_urls as discover_module
    from app.tools import http_fetch as http_fetch_module

    runner_module.use_stub_runner()

    async def _fake_fetch(url, render_js=False):
        return {"status": 200, "html": _FAKE_HTML, "text": ""}

    monkeypatch.setattr(http_fetch_module, "http_fetch", _fake_fetch)
    monkeypatch.setattr(runner_module, "http_fetch", _fake_fetch)
    monkeypatch.setattr(discover_module, "http_fetch", _fake_fetch)

    async def _fake_index(run_id, docs):
        return len(docs)

    from app.rag import index as index_module
    from app.workers import tasks as tasks_module

    monkeypatch.setattr(index_module, "index_chunks", _fake_index)
    monkeypatch.setattr(tasks_module, "index_chunks", _fake_index, raising=False)
    yield
    runner_module.use_real_runner()


def _make_project(client: TestClient, headers: dict) -> str:
    r = client.post(
        "/api/v1/projects",
        json={"name": "p", "idea": "Notion alternatives", "known_competitors": ["acme.test"]},
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_budget_exceeded_marks_run_failed(client: TestClient, auth_headers, monkeypatch):
    """A run that exceeds the input token cap must land in 'failed' with reason."""
    from app.core import config as config_module

    # Set an impossibly small token budget so any real text overflows it.
    monkeypatch.setattr(config_module.settings, "BUDGET_INPUT_TOKENS", 1)

    headers = auth_headers()
    project_id = _make_project(client, headers)

    r = client.post(f"/api/v1/projects/{project_id}/runs", headers=headers)
    assert r.status_code == 201
    run_id = r.json()["run_id"]

    run = client.get(f"/api/v1/runs/{run_id}", headers=headers).json()
    assert run["status"] == "failed", f"expected failed, got {run['status']}"
    assert run["error"] is not None
    assert "budget_exceeded" in run["error"]

    # Partial token counters must be persisted even on failure.
    assert run["token_input"] > 0

    # A budget_exceeded error event must be in the event log.
    events = client.get(f"/api/v1/runs/{run_id}/events", headers=headers).json()
    error_events = [e for e in events if e["type"] == "error"]
    assert any(
        e["payload"].get("reason") == "budget_exceeded" for e in error_events
    ), f"no budget_exceeded error event in {error_events}"


def test_normal_run_cost_is_positive(client: TestClient, auth_headers):
    """Sanity: a normal run with generous caps must report positive cost."""
    headers = auth_headers()
    project_id = _make_project(client, headers)

    r = client.post(f"/api/v1/projects/{project_id}/runs", headers=headers)
    run_id = r.json()["run_id"]

    run = client.get(f"/api/v1/runs/{run_id}", headers=headers).json()
    assert run["status"] == "completed"
    assert run["cost_usd"] > 0
    assert run["token_input"] > 0
    assert run["token_output"] > 0
