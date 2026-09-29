import database
from fastapi.testclient import TestClient

from main import app


def test_create_and_list_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test_tasks.db")

    with TestClient(app) as client:
        create_response = client.post("/tasks", json={"title": "Estudar FastAPI"})

        assert create_response.status_code == 201
        created_task = create_response.json()
        assert created_task["id"] == 1
        assert created_task["title"] == "Estudar FastAPI"
        assert created_task["completed"] is False
        assert "created_at" in created_task

        list_response = client.get("/tasks")

        assert list_response.status_code == 200
        assert list_response.json() == [created_task]


def test_create_task_rejects_title_over_120_characters(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test_tasks.db")

    with TestClient(app) as client:
        response = client.post("/tasks", json={"title": "a" * 121})

    assert response.status_code == 422


def test_create_task_requires_title(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test_tasks.db")

    with TestClient(app) as client:
        response = client.post("/tasks", json={})

    assert response.status_code == 422


def test_update_task_completed(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test_tasks.db")

    with TestClient(app) as client:
        created = client.post("/tasks", json={"title": "Estudar FastAPI"}).json()
        response = client.patch(f"/tasks/{created['id']}", json={"completed": True})

        assert response.status_code == 200
        assert response.json()["completed"] is True
        assert client.get("/tasks").json()[0]["completed"] is True


def test_update_task_returns_404_for_missing_id(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test_tasks.db")

    with TestClient(app) as client:
        response = client.patch("/tasks/999", json={"completed": True})

    assert response.status_code == 404


def test_delete_task(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test_tasks.db")

    with TestClient(app) as client:
        created = client.post("/tasks", json={"title": "Estudar FastAPI"}).json()
        response = client.delete(f"/tasks/{created['id']}")

        assert response.status_code == 204
        assert client.get("/tasks").json() == []


def test_delete_task_returns_404_for_missing_id(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test_tasks.db")

    with TestClient(app) as client:
        response = client.delete("/tasks/999")

    assert response.status_code == 404
