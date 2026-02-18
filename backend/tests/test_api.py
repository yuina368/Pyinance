#!/usr/bin/env python3
"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_login_success(client):
    """Test successful login"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


def test_login_failure(client):
    """Test failed login"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_get_companies(client):
    """Test get companies endpoint"""
    response = client.get("/api/companies/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_model_status(client):
    """Test model status endpoint"""
    response = client.get("/api/model/status")
    assert response.status_code == 200
    data = response.json()
    assert "loaded" in data
    assert "model" in data
    assert "status" in data


def test_protected_endpoint_without_token(client):
    """Test protected endpoint without token"""
    response = client.get("/api/auth/me")
    assert response.status_code == 403


def test_protected_endpoint_with_token(client):
    """Test protected endpoint with valid token"""
    # First, login to get token
    login_response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # Then, access protected endpoint
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"


def test_sentiments_daily_invalid_date(client):
    """Test sentiments daily endpoint with invalid date"""
    response = client.get("/api/sentiments/daily?target_date=invalid-date")
    assert response.status_code == 400


def test_sentiments_ticker_not_found(client):
    """Test sentiments ticker endpoint with non-existent ticker"""
    response = client.get("/api/sentiments/NONEXISTENT")
    assert response.status_code == 404


def test_sentiments_ticker_invalid_days(client):
    """Test sentiments ticker endpoint with invalid days parameter"""
    response = client.get("/api/sentiments/AAPL?days=0")
    assert response.status_code == 400
    
    response = client.get("/api/sentiments/AAPL?days=500")
    assert response.status_code == 400
