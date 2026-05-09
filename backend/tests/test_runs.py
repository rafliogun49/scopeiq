from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

_FAKE_HTML = """
<html><head><title>Acme</title></head><body>
  <h1>Acme Pricing</h1>
  <p>Acme charges $19/month for the Pro plan, with unlimited projects.</p>
  <a href="/pricing">Pricing</a>
  <a href="/features">Features</a>
</body></html>
"""


@pytest.fixture(autouse=True)
def _use_stub_runner_with_canned_fetch(monkeypatch):
    """Run the deterministic stub runner; fake http_fetch + index_chunks."""
    from app.agents import runner as runner_module
    from app.tools import discover_urls as discover_module
    from app.tools import http_fetch as http_fetch_module
    from app.workers import tasks as tasks_module

    runner_module.use_stub_runner()

    async def _fake_fetch(url, render_js=False):
        return {"status": 200, "html": _FAKE_HTML, "text": ""}

    # Patch the symbol everywhere it's looked up.
    monkeypatch.setattr(http_fetch_module, "http_fetch", _fake_fetch)
    monkeypatch.setattr(runner_module, "http_fetch", _fake_fetch)
    monkeypatch.setattr(discover_module, "http_fetch", _fake_fetch)

    async def _fake_index(run_id, docs):
        return len(docs)

    # tasks.py imports index_chunks lazily inside the task — patch the source.
    from app.rag import index as index_module

    monkeypatch.setattr(index_module, "index_chunks", _fake_index)
    monkeypatch.setattr(tasks_module, "index_chunks", _fake_index, raising=False)
    yield
    runner_module.use_real_runner()


def _make_project(client: TestClient, headers: dict[str, str]) -> str:
    r = client.post(
        "/api/v1/projects",
        json={"name": "p", "idea": "Notion alternatives", "known_competitors": ["acme.test"]},
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_create_run_dispatches_task_and_completes(client: TestClient, auth_headers):
    headers = auth_headers()
    project_id = _make_project(client, headers)

    r = client.post(f"/api/v1/projects/{project_id}/runs", headers=headers)
    assert r.status_code == 201, r.text
    run_id = r.json()["run_id"]

    r = client.get(f"/api/v1/runs/{run_id}", headers=headers)
    assert r.status_code == 200
    run = r.json()
    assert run["status"] == "completed"
    assert run["started_at"] is not None
    assert run["finished_at"] is not None


def test_create_run_on_other_users_project_returns_404(client: TestClient, auth_headers):
    alice = auth_headers("alice@example.com")
    bob = auth_headers("bob@example.com")
    project_id = _make_project(client, bob)

    r = client.post(f"/api/v1/projects/{project_id}/runs", headers=alice)
    assert r.status_code == 404


def test_get_run_404_for_other_user(client: TestClient, auth_headers):
    alice = auth_headers("alice@example.com")
    bob = auth_headers("bob@example.com")
    project_id = _make_project(client, bob)
    run_id = client.post(
        f"/api/v1/projects/{project_id}/runs", headers=bob
    ).json()["run_id"]

    assert client.get(f"/api/v1/runs/{run_id}", headers=alice).status_code == 404


def test_cancel_completed_run_returns_409(client: TestClient, auth_headers):
    headers = auth_headers()
    project_id = _make_project(client, headers)
    run_id = client.post(
        f"/api/v1/projects/{project_id}/runs", headers=headers
    ).json()["run_id"]

    r = client.post(f"/api/v1/runs/{run_id}/cancel", headers=headers)
    assert r.status_code == 409


def test_cancel_pending_run_flips_status(client: TestClient, auth_headers, monkeypatch):
    """Suppress the eager task so the run stays in pending, then cancel."""
    from app.api import runs as runs_module

    class _Noop:
        @staticmethod
        def delay(_run_id: str) -> None:
            return None

    monkeypatch.setattr(runs_module, "run_research_task", _Noop)

    headers = auth_headers()
    project_id = _make_project(client, headers)
    run_id = client.post(
        f"/api/v1/projects/{project_id}/runs", headers=headers
    ).json()["run_id"]

    r = client.post(f"/api/v1/runs/{run_id}/cancel", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "cancelled"

    follow_up = client.get(f"/api/v1/runs/{run_id}", headers=headers).json()
    assert follow_up["status"] == "cancelled"


def test_events_emits_real_sequence(client: TestClient, auth_headers):
    headers = auth_headers()
    project_id = _make_project(client, headers)
    run_id = client.post(
        f"/api/v1/projects/{project_id}/runs", headers=headers
    ).json()["run_id"]

    r = client.get(f"/api/v1/runs/{run_id}/events", headers=headers)
    assert r.status_code == 200
    events = r.json()
    types = [e["type"] for e in events]
    agents = [e["agent"] for e in events]

    # Expected ordered milestones: plan → orchestrator started → scraper started
    # → at least one tool_called → scraper finished → orchestrator finished.
    assert types[0] == "plan"
    assert events[0]["agent"] == "orchestrator"

    def _index_of(t: str, agent: str | None = None) -> int:
        for i, e in enumerate(events):
            if e["type"] == t and (agent is None or e["agent"] == agent):
                return i
        raise AssertionError(f"missing event type={t} agent={agent} in {types}")

    plan = _index_of("plan", "orchestrator")
    orch_start = _index_of("agent_started", "orchestrator")
    scraper_start = _index_of("agent_started", "scraper")
    tool = _index_of("tool_called")
    scraper_end = _index_of("agent_finished", "scraper")
    orch_end = _index_of("agent_finished", "orchestrator")

    assert plan < orch_start < scraper_start < tool < scraper_end < orch_end
    assert any(a == "scraper" for a in agents)


def test_events_pagination_respects_limit(client: TestClient, auth_headers):
    headers = auth_headers()
    project_id = _make_project(client, headers)
    run_id = client.post(
        f"/api/v1/projects/{project_id}/runs", headers=headers
    ).json()["run_id"]

    r = client.get(
        f"/api/v1/runs/{run_id}/events?offset=1&limit=1", headers=headers
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    # Second event is the orchestrator's agent_started (after plan).
    assert body[0]["type"] == "agent_started"
    assert body[0]["agent"] == "orchestrator"


def test_events_404_for_other_user(client: TestClient, auth_headers):
    alice = auth_headers("alice@example.com")
    bob = auth_headers("bob@example.com")
    project_id = _make_project(client, bob)
    run_id = client.post(
        f"/api/v1/projects/{project_id}/runs", headers=bob
    ).json()["run_id"]

    assert client.get(f"/api/v1/runs/{run_id}/events", headers=alice).status_code == 404


def test_get_run_unknown_id_returns_404(client: TestClient, auth_headers):
    headers = auth_headers()
    assert client.get(f"/api/v1/runs/{uuid4()}", headers=headers).status_code == 404


def test_index_chunks_not_implemented_still_completes(client: TestClient, auth_headers, monkeypatch):
    """If B-PR1 hasn't landed, the run should still complete with a log warning."""
    from app.rag import index as index_module

    async def _raises(run_id, docs):
        raise NotImplementedError

    monkeypatch.setattr(index_module, "index_chunks", _raises)

    headers = auth_headers()
    project_id = _make_project(client, headers)
    run_id = client.post(
        f"/api/v1/projects/{project_id}/runs", headers=headers
    ).json()["run_id"]

    run = client.get(f"/api/v1/runs/{run_id}", headers=headers).json()
    assert run["status"] == "completed"
    events = client.get(f"/api/v1/runs/{run_id}/events", headers=headers).json()
    log_events = [e for e in events if e["type"] == "log"]
    assert any("indexing pending" in (e["payload"].get("warning") or "") for e in log_events)
