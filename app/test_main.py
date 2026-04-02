import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app

client = TestClient(app)

# Test /healthz endpoint
def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Test /readyz endpoint
def test_readyz():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

# Test /load endpoint
def test_load():
    response = client.get("/load")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "load generated"

# Test /crash endpoint
# def test_crash():
#     response = client.get("/crash")
#     assert response.status_code == 500  # Simulated crash should return 500

# Test /slow endpoint
def test_slow():
    response = client.get("/slow?delay=2")
    assert response.status_code == 200
    assert response.json() == {"status": "response delayed", "delay": 2}

# Test /random-failure endpoint
def test_random_failure():
    response = client.get("/random-failure")
    assert response.status_code in [200, 500]  # Random failure can return either

# Test /metrics endpoint
def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "prometheus" in response.text.lower()

# Test logging middleware
def test_logging_middleware(caplog):
    with caplog.at_level("INFO"):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert "request_received" in caplog.text
        assert "response_sent" in caplog.text