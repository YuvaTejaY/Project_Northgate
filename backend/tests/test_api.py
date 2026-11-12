import os
import uuid

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_northgate_ekyc.db")

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def test_home_page_serves_the_dashboard() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Corporate onboarding chases" in response.text


def test_healthcheck() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_registration_can_be_disabled_for_production(monkeypatch) -> None:
    monkeypatch.setattr(settings, "allow_public_registration", False)
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"blocked-{uuid.uuid4().hex[:8]}@example.com",
            "full_name": "Blocked Registration",
            "password": "StrongPass123!",
            "role": "Reviewer",
        },
    )
    assert response.status_code == 403


def test_register_login_and_customer_creation() -> None:
    email = f"analyst-{uuid.uuid4().hex[:8]}@example.com"
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Example Analyst",
            "password": "StrongPass123!",
            "role": "Analyst",
        },
    )
    assert register.status_code == 201, register.text

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "StrongPass123!"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    customer_payload = {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "phone": "+44 20 7946 0958",
        "date_of_birth": "1815-12-10",
        "address": "London, UK",
        "nationality": "British",
    }
    customer_response = client.post("/api/v1/customers/", json=customer_payload, headers=headers)
    assert customer_response.status_code == 201, customer_response.text
    customer = customer_response.json()
    assert customer["first_name"] == "Ada"

    risk_response = client.get(f"/api/v1/risk/{customer['id']}", headers=headers)
    assert risk_response.status_code == 200, risk_response.text
    assert "risk_level" in risk_response.json()
