"""Notes endpoint tests."""
import pytest
from fastapi.testclient import TestClient


class TestNotes:
    def test_create_note(self, client: TestClient, auth_headers):
        response = client.post("/api/v1/notes", json={
            "title": "Monsoon Notes",
            "content": "The Indian monsoon is driven by differential heating...",
            "note_type": "manual",
            "tags": ["geography", "climate"],
            "color": "#6366f1",
            "is_pinned": False,
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Monsoon Notes"
        assert data["note_type"] == "manual"

    def test_list_notes_empty(self, client: TestClient, auth_headers):
        response = client.get("/api/v1/notes", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_notes_with_search(self, client: TestClient, auth_headers):
        client.post("/api/v1/notes", json={
            "title": "Federalism Notes",
            "content": "Federalism in India...",
            "note_type": "manual",
            "tags": [],
            "color": "#ffffff",
            "is_pinned": False,
        }, headers=auth_headers)

        response = client.get("/api/v1/notes?search=Federalism", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_update_note(self, client: TestClient, auth_headers):
        create_resp = client.post("/api/v1/notes", json={
            "title": "Old Title",
            "content": "Content",
            "note_type": "manual",
            "tags": [],
            "color": "#ffffff",
            "is_pinned": False,
        }, headers=auth_headers)
        note_id = create_resp.json()["id"]

        response = client.put(f"/api/v1/notes/{note_id}", json={
            "title": "New Title",
        }, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "New Title"

    def test_toggle_pin(self, client: TestClient, auth_headers):
        create_resp = client.post("/api/v1/notes", json={
            "title": "Pin Test",
            "content": "Content",
            "note_type": "manual",
            "tags": [],
            "color": "#ffffff",
            "is_pinned": False,
        }, headers=auth_headers)
        note_id = create_resp.json()["id"]

        response = client.post(f"/api/v1/notes/{note_id}/pin", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["is_pinned"] is True

        # Toggle again
        response = client.post(f"/api/v1/notes/{note_id}/pin", headers=auth_headers)
        assert response.json()["is_pinned"] is False

    def test_delete_note(self, client: TestClient, auth_headers):
        create_resp = client.post("/api/v1/notes", json={
            "title": "To Delete",
            "content": "Content",
            "note_type": "manual",
            "tags": [],
            "color": "#ffffff",
            "is_pinned": False,
        }, headers=auth_headers)
        note_id = create_resp.json()["id"]

        response = client.delete(f"/api/v1/notes/{note_id}", headers=auth_headers)
        assert response.status_code == 200

        # Should not appear in list
        list_resp = client.get("/api/v1/notes", headers=auth_headers)
        assert list_resp.json()["total"] == 0

    def test_pagination(self, client: TestClient, auth_headers):
        # Create 5 notes
        for i in range(5):
            client.post("/api/v1/notes", json={
                "title": f"Note {i}",
                "content": f"Content {i}",
                "note_type": "manual",
                "tags": [],
                "color": "#ffffff",
                "is_pinned": False,
            }, headers=auth_headers)

        response = client.get("/api/v1/notes?page=1&page_size=3", headers=auth_headers)
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3
        assert data["has_next"] is True
        assert data["total_pages"] == 2
