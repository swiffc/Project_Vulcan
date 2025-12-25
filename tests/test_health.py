"""
Basic Health Check Tests for Project Vulcan
Run with: pytest tests/test_health.py -v
"""

import pytest
import httpx
import os

# Desktop server URL (local or via Tailscale)
DESKTOP_SERVER_URL = os.getenv("DESKTOP_SERVER_URL", "http://localhost:8765")

# Set API key for tests
os.environ["API_KEY"] = "test-api-key"


class TestDesktopServer:
    """Tests for the local desktop server."""

    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=DESKTOP_SERVER_URL, timeout=10.0)

    def test_health_endpoint(self, client):
        """Desktop server /health should return 200."""
        try:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
        except httpx.ConnectError:
            pytest.skip("Desktop server not running")

    def test_screen_size(self, client):
        """Screen size endpoint should return dimensions."""
        try:
            response = client.get("/screen/size")
            assert response.status_code == 200
            data = response.json()
            assert "width" in data
            assert "height" in data
            assert data["width"] > 0
            assert data["height"] > 0
        except httpx.ConnectError:
            pytest.skip("Desktop server not running")

    def test_window_list(self, client):
        """Window list should return array of windows."""
        try:
            response = client.get("/window/list")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
        except httpx.ConnectError:
            pytest.skip("Desktop server not running")

    def test_mouse_position(self, client):
        """Mouse position should return x, y coordinates."""
        try:
            response = client.get("/mouse/position")
            assert response.status_code == 200
            data = response.json()
            assert "x" in data
            assert "y" in data
        except httpx.ConnectError:
            pytest.skip("Desktop server not running")


class TestOrchestrator:
    """Tests for the cloud orchestrator API using TestClient."""

    def test_health_endpoint(self):
        """Orchestrator /health should return 200."""
        from fastapi.testclient import TestClient
        from core.api import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_chat_endpoint_requires_auth(self):
        """Chat endpoint should require API key."""
        from fastapi.testclient import TestClient
        from core.api import app

        client = TestClient(app)
        response = client.post("/chat", json={"messages": []})
        # Should fail without API key
        assert response.status_code in [401, 403, 422]

    def test_chat_endpoint_with_auth(self):
        """Chat endpoint should work with valid API key."""
        from fastapi.testclient import TestClient
        from core.api import app

        client = TestClient(app)
        response = client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            headers={"X-API-Key": "test-api-key"},
        )
        # May fail with 500 if LLM not available, but should authenticate
        assert response.status_code in [200, 400, 500]


class TestAgentDetection:
    """Tests for agent routing logic via orchestrator adapter."""

    def test_trading_keywords(self):
        """Trading keywords should route to trading agent."""
        from core.orchestrator_adapter import get_orchestrator, AgentType

        orchestrator = get_orchestrator()
        assert orchestrator.detect_agent("Analyze GBP/USD setup") == AgentType.TRADING
        assert orchestrator.detect_agent("What's the bias for forex today?") == AgentType.TRADING

    def test_cad_keywords(self):
        """CAD keywords should route to cad agent."""
        from core.orchestrator_adapter import get_orchestrator, AgentType

        orchestrator = get_orchestrator()
        assert orchestrator.detect_agent("Create a flange in SolidWorks") == AgentType.CAD
        assert orchestrator.detect_agent("Extrude this sketch") == AgentType.CAD

    def test_general_fallback(self):
        """Unknown queries should route to general agent."""
        from core.orchestrator_adapter import get_orchestrator, AgentType

        orchestrator = get_orchestrator()
        assert orchestrator.detect_agent("Hello, how are you?") == AgentType.GENERAL
        assert orchestrator.detect_agent("What's the weather?") == AgentType.GENERAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
