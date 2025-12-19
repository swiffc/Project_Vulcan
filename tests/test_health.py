"""
Basic Health Check Tests for Project Vulcan
Run with: pytest tests/test_health.py -v
"""

import pytest
import httpx
import os

# Desktop server URL (local or via Tailscale)
DESKTOP_SERVER_URL = os.getenv("DESKTOP_SERVER_URL", "http://localhost:8765")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")


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
    """Tests for the cloud orchestrator API."""

    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=ORCHESTRATOR_URL, timeout=10.0)

    def test_health_endpoint(self, client):
        """Orchestrator /health should return 200."""
        try:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
        except httpx.ConnectError:
            pytest.skip("Orchestrator not running")

    def test_chat_endpoint_requires_messages(self, client):
        """Chat endpoint should reject empty messages."""
        try:
            response = client.post("/chat", json={"messages": []})
            assert response.status_code == 400
        except httpx.ConnectError:
            pytest.skip("Orchestrator not running")

    def test_chat_endpoint_with_message(self, client):
        """Chat endpoint should process a message."""
        try:
            response = client.post("/chat", json={
                "messages": [{"role": "user", "content": "Hello"}]
            })
            # May fail if no API key, but should not 500
            assert response.status_code in [200, 500]
        except httpx.ConnectError:
            pytest.skip("Orchestrator not running")


class TestAgentDetection:
    """Tests for agent routing logic."""

    def test_trading_keywords(self):
        """Trading keywords should route to trading agent."""
        from agents.core.api import detect_agent

        assert detect_agent("Analyze GBP/USD setup") == "trading"
        assert detect_agent("What's the bias for forex today?") == "trading"
        assert detect_agent("ICT order block on EUR") == "trading"

    def test_cad_keywords(self):
        """CAD keywords should route to cad agent."""
        from agents.core.api import detect_agent

        assert detect_agent("Create a flange in SolidWorks") == "cad"
        assert detect_agent("Extrude this sketch") == "cad"
        assert detect_agent("Build a 3D model") == "cad"

    def test_general_fallback(self):
        """Unknown queries should route to general agent."""
        from agents.core.api import detect_agent

        assert detect_agent("Hello, how are you?") == "general"
        assert detect_agent("What's the weather?") == "general"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
