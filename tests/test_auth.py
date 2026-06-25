import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_register_login_and_me_flow(client):
    unique_email = "student.auth@example.edu"
    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Test Student",
            "email": unique_email,
            "password": "secure-pass-123",
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "secure-pass-123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["user"]["email"] == unique_email

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == unique_email

    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 200
