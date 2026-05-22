"""Subject and Topic endpoint tests."""
import pytest
from fastapi.testclient import TestClient


class TestSubjects:
    def test_create_subject(self, client: TestClient, auth_headers):
        response = client.post("/api/v1/subjects", json={
            "name": "Indian Geography",
            "category": "gs1",
            "color": "#6366f1",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Indian Geography"
        assert data["category"] == "gs1"
        assert data["completion_percentage"] == 0.0

    def test_list_subjects_empty(self, client: TestClient, auth_headers):
        response = client.get("/api/v1/subjects", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_subjects_with_data(self, client: TestClient, auth_headers):
        # Create a subject first
        client.post("/api/v1/subjects", json={
            "name": "Polity", "category": "gs2", "color": "#8b5cf6",
        }, headers=auth_headers)

        response = client.get("/api/v1/subjects", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_subject(self, client: TestClient, auth_headers):
        create_resp = client.post("/api/v1/subjects", json={
            "name": "Economy", "category": "gs3", "color": "#10b981",
        }, headers=auth_headers)
        subject_id = create_resp.json()["id"]

        response = client.get(f"/api/v1/subjects/{subject_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == subject_id

    def test_update_subject(self, client: TestClient, auth_headers):
        create_resp = client.post("/api/v1/subjects", json={
            "name": "History", "category": "gs1", "color": "#f59e0b",
        }, headers=auth_headers)
        subject_id = create_resp.json()["id"]

        response = client.put(f"/api/v1/subjects/{subject_id}", json={
            "name": "Modern History",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Modern History"

    def test_delete_subject(self, client: TestClient, auth_headers):
        create_resp = client.post("/api/v1/subjects", json={
            "name": "To Delete", "category": "gs4", "color": "#ef4444",
        }, headers=auth_headers)
        subject_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/subjects/{subject_id}", headers=auth_headers)
        assert response.status_code == 200

        # Should not appear in list
        list_resp = client.get("/api/v1/subjects", headers=auth_headers)
        ids = [s["id"] for s in list_resp.json()]
        assert subject_id not in ids

    def test_cannot_access_other_users_subject(self, client: TestClient, auth_headers, admin_headers):
        create_resp = client.post("/api/v1/subjects", json={
            "name": "Private Subject", "category": "gs1", "color": "#6366f1",
        }, headers=auth_headers)
        subject_id = create_resp.json()["id"]

        # Admin user should not see this subject (different user)
        response = client.get(f"/api/v1/subjects/{subject_id}", headers=admin_headers)
        assert response.status_code == 404


class TestTopics:
    def _create_subject(self, client, headers):
        resp = client.post("/api/v1/subjects", json={
            "name": "Geography", "category": "gs1", "color": "#6366f1",
        }, headers=headers)
        return resp.json()["id"]

    def test_create_topic(self, client: TestClient, auth_headers):
        subject_id = self._create_subject(client, auth_headers)
        response = client.post(f"/api/v1/subjects/{subject_id}/topics", json={
            "subject_id": subject_id,
            "name": "Monsoon",
            "importance_score": 8,
            "priority": "high",
            "tags": ["climate", "geography"],
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Monsoon"
        assert data["status"] == "not_started"

    def test_update_topic_status(self, client: TestClient, auth_headers):
        subject_id = self._create_subject(client, auth_headers)
        create_resp = client.post(f"/api/v1/subjects/{subject_id}/topics", json={
            "subject_id": subject_id,
            "name": "El Niño",
            "importance_score": 7,
            "priority": "high",
            "tags": [],
        }, headers=auth_headers)
        topic_id = create_resp.json()["id"]

        response = client.put(f"/api/v1/subjects/topics/{topic_id}", json={
            "status": "completed",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
