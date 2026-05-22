"""Authentication endpoint tests."""
import pytest
from fastapi.testclient import TestClient


class TestRegister:
    def test_register_success(self, client: TestClient):
        response = client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "NewPass123",
            "exam_target": "upsc",
        })
        assert response.status_code == 201
        data = response.json()
        assert "tokens" in data
        assert "user" in data
        assert data["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, client: TestClient, test_user):
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "anotheruser",
            "full_name": "Another User",
            "password": "AnotherPass123",
            "exam_target": "upsc",
        })
        assert response.status_code == 409

    def test_register_weak_password(self, client: TestClient):
        response = client.post("/api/v1/auth/register", json={
            "email": "weak@example.com",
            "username": "weakuser",
            "full_name": "Weak User",
            "password": "weak",
            "exam_target": "upsc",
        })
        assert response.status_code == 422

    def test_register_invalid_email(self, client: TestClient):
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "username": "user",
            "full_name": "User",
            "password": "ValidPass123",
            "exam_target": "upsc",
        })
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client: TestClient, test_user):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert data["tokens"]["access_token"]
        assert data["tokens"]["refresh_token"]

    def test_login_wrong_password(self, client: TestClient, test_user):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPass123",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "SomePass123",
        })
        assert response.status_code == 401


class TestProtectedRoutes:
    def test_get_me_authenticated(self, client: TestClient, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"

    def test_get_me_unauthenticated(self, client: TestClient):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403  # HTTPBearer returns 403 when no token

    def test_get_me_invalid_token(self, client: TestClient):
        response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert response.status_code == 401


class TestRefreshToken:
    def test_refresh_success(self, client: TestClient, test_user):
        # Login first
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })
        refresh_token = login_resp.json()["tokens"]["refresh_token"]

        response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        assert response.json()["access_token"]
