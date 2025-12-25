"""
Tests for the core API endpoints.
"""

import pytest
import os
from fastapi.testclient import TestClient

# Set API key before importing app
os.environ["API_KEY"] = "test-api-key"

from core.api import app


class TestTradingJournalAPI:
    """Tests for Trading Journal API endpoints."""

    def test_create_trade(self):
        """Test POST /api/trading/journal endpoint."""
        client = TestClient(app)

        trade_data = {
            "pair": "EURUSD",
            "bias": "long",
            "setup": "test setup",
            "entry": 1.1,
            "target": 1.2,
            "stop": 1.0,
            "rr": 2.0,
        }
        response = client.post(
            "/api/trading/journal",
            json=trade_data,
            headers={"X-API-Key": "test-api-key"},
        )
        assert response.status_code == 200
        assert "id" in response.json()

    def test_get_trades(self):
        """Test GET /api/trading/journal endpoint."""
        client = TestClient(app)

        response = client.get(
            "/api/trading/journal", headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestValidationHistoryAPI:
    """Tests for Validation History API endpoints."""

    def test_get_recent_validations(self):
        """Test GET /api/cad/validations/recent endpoint."""
        client = TestClient(app)

        response = client.get(
            "/api/cad/validations/recent", headers={"X-API-Key": "test-api-key"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_validation_not_found(self):
        """Test GET /api/cad/validations/{id} for non-existent validation."""
        client = TestClient(app)

        response = client.get(
            "/api/cad/validations/nonexistent-id",
            headers={"X-API-Key": "test-api-key"},
        )
        assert response.status_code == 404


class TestHealthEndpoint:
    """Tests for health endpoint."""

    def test_health_returns_ok(self):
        """Test GET /health endpoint."""
        client = TestClient(app)

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
