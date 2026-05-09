from uuid import uuid4

from fastapi.testclient import TestClient


def _make_project(client: TestClient, headers: dict[str, str]) -> str:
    r = client.post(
        "/api/v1/projects",
        json={"name": "p", "idea": "i", "known_competitors": []},
        headers=headers,
    )
    assert r.status_code == 201
    return r.json()["id"]


def test_create_run_dispatches_task_and_completes(client: TestClient, auth_headers):
    headers = auth_headers()
    project_id = _make_project(client, headers)

    r = client.post(f"/api/v1/projects/{project_id}/runs", headers=headers)
    assert r.status_code == 201, r.text
    body = r.json()
    run_id = body["run_id"]

    # With Celery eager mode, the stub task already ran synchronously.
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


def test_events_returns_three_stub_events(client: TestClient, auth_headers):
    headers = auth_headers()
    project_id = _make_project(client, headers)
    run_id = client.post(
        f"/api/v1/projects/{project_id}/runs", headers=headers
    ).json()["run_id"]

    r = client.get(f"/api/v1/runs/{run_id}/events", headers=headers)
    assert r.status_code == 200
    events = r.json()
    assert [e["type"] for e in events] == ["plan", "agent_started", "agent_finished"]
    assert events[1]["agent"] == "orchestrator"


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
    assert body[0]["type"] == "agent_started"


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
