from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _create(title: str = "Write spec", **extra) -> dict:
    r = client.post("/tasks", json={"title": title, **extra})
    assert r.status_code == 201, r.text
    return r.json()


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_create_task_defaults():
    t = _create()
    assert t["status"] == "todo" and t["priority"] == "medium" and t["id"] > 0


def test_create_task_rejects_empty_title():
    assert client.post("/tasks", json={"title": ""}).status_code == 422


def test_list_and_filter_by_status():
    t = _create("Filter me")
    client.patch(f"/tasks/{t['id']}", json={"status": "done"})
    done = client.get("/tasks", params={"status": "done"}).json()
    assert any(x["id"] == t["id"] for x in done)


def test_get_task_by_id():
    t = _create("Lookup")
    assert client.get(f"/tasks/{t['id']}").json()["title"] == "Lookup"


def test_get_unknown_task_returns_404():
    assert client.get("/tasks/999999").status_code == 404


def test_update_priority_and_status():
    t = _create("Move me")
    r = client.patch(f"/tasks/{t['id']}", json={"priority": "high", "status": "in_progress"})
    assert r.json()["priority"] == "high" and r.json()["status"] == "in_progress"


def test_delete_task():
    t = _create("Remove me")
    assert client.delete(f"/tasks/{t['id']}").status_code == 204
    assert client.get(f"/tasks/{t['id']}").status_code == 404
