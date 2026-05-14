from fastapi.testclient import TestClient


def _create(client: TestClient, headers: dict[str, str], **overrides) -> dict:
    payload = {
        "name": "ScopeIQ",
        "idea": "Idea validation for indie founders",
        "known_competitors": ["productHunt"],
        **overrides,
    }
    r = client.post("/api/v1/projects", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_create_project_returns_full_project(client: TestClient, auth_headers):
    headers = auth_headers()
    body = _create(client, headers, name="Acme")
    assert body["name"] == "Acme"
    assert body["archived"] is False
    assert body["known_competitors"] == ["productHunt"]
    assert "id" in body and "user_id" in body and "created_at" in body


def test_create_without_auth_returns_401(client: TestClient):
    r = client.post(
        "/api/v1/projects",
        json={"name": "x", "idea": "y", "known_competitors": []},
    )
    assert r.status_code == 401


def test_list_returns_only_own_projects(client: TestClient, auth_headers):
    alice = auth_headers("alice@example.com")
    bob = auth_headers("bob@example.com")
    _create(client, alice, name="alice-proj")
    _create(client, bob, name="bob-proj-1")
    _create(client, bob, name="bob-proj-2")

    r = client.get("/api/v1/projects", headers=alice)
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body) == 1
    assert body[0]["name"] == "alice-proj"


def test_get_project_includes_last_run_summary_or_none(client: TestClient, auth_headers):
    headers = auth_headers()
    project = _create(client, headers)

    r = client.get(f"/api/v1/projects/{project['id']}", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["last_run"] is None

    run = client.post(f"/api/v1/projects/{project['id']}/runs", headers=headers).json()

    r = client.get(f"/api/v1/projects/{project['id']}", headers=headers)
    body = r.json()
    assert body["last_run"] is not None
    assert body["last_run"]["id"] == run["run_id"]
    assert body["last_run"]["status"] in {"pending", "running", "completed"}


def test_get_other_users_project_returns_404(client: TestClient, auth_headers):
    alice = auth_headers("alice@example.com")
    bob = auth_headers("bob@example.com")
    project = _create(client, bob)

    r = client.get(f"/api/v1/projects/{project['id']}", headers=alice)
    assert r.status_code == 404


def test_get_missing_project_returns_404(client: TestClient, auth_headers):
    headers = auth_headers()
    r = client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000", headers=headers)
    assert r.status_code == 404


def test_patch_updates_name_and_archived(client: TestClient, auth_headers):
    headers = auth_headers()
    project = _create(client, headers)

    r = client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"name": "renamed", "archived": True},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["name"] == "renamed"
    assert body["archived"] is True


def test_patch_other_users_project_returns_404(client: TestClient, auth_headers):
    alice = auth_headers("alice@example.com")
    bob = auth_headers("bob@example.com")
    project = _create(client, bob)

    r = client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"name": "stolen"},
        headers=alice,
    )
    assert r.status_code == 404


def test_delete_cascades_runs_and_events(client: TestClient, auth_headers):
    headers = auth_headers()
    project = _create(client, headers)
    run = client.post(f"/api/v1/projects/{project['id']}/runs", headers=headers).json()
    run_id = run["run_id"]

    r = client.delete(f"/api/v1/projects/{project['id']}", headers=headers)
    assert r.status_code == 204

    assert client.get(f"/api/v1/projects/{project['id']}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/runs/{run_id}", headers=headers).status_code == 404
    assert client.get(f"/api/v1/runs/{run_id}/events", headers=headers).status_code == 404
