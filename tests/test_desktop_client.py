"""
Test Desktop Client Integration
Verifies that orchestrator can communicate with desktop server.
"""

import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path setup
from core.desktop_client import DesktopClient, get_desktop_client, check_desktop_connectivity


class TestDesktopClient:
    """Test desktop client functionality."""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initializes with correct URL."""
        client = DesktopClient("http://test:8000")
        assert client.base_url == "http://test:8000"
        assert client.timeout == 30
        await client.close()

    @pytest.mark.asyncio
    async def test_client_from_env(self):
        """Test client reads URL from environment."""
        with patch.dict("os.environ", {"DESKTOP_SERVER_URL": "http://env:9000"}):
            client = DesktopClient()
            assert client.base_url == "http://env:9000"
            await client.close()

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        client = DesktopClient("http://test:8000")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        
        with patch.object(client._client, "get", return_value=mock_response) as mock_get:
            result = await client.health_check()
            
            assert result["status"] == "healthy"
            mock_get.assert_called_once_with("http://test:8000/health")
        
        await client.close()

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check handles errors."""
        client = DesktopClient("http://test:8000")
        
        with patch.object(client._client, "get", side_effect=Exception("Connection failed")):
            result = await client.health_check()
            
            assert result["status"] == "unreachable"
            assert "error" in result
        
        await client.close()

    @pytest.mark.asyncio
    async def test_get_cad_status(self):
        """Test CAD status retrieval."""
        client = DesktopClient("http://test:8000")
        
        mock_sw = Mock(status_code=200)
        mock_sw.json.return_value = {"connected": True, "version": "2024"}
        
        mock_inv = Mock(status_code=200)
        mock_inv.json.return_value = {"connected": False}
        
        async def mock_get(url):
            if "solidworks" in url:
                return mock_sw
            return mock_inv
        
        with patch.object(client._client, "get", side_effect=mock_get):
            result = await client.get_cad_status()
            
            assert result["solidworks"]["connected"] is True
            assert result["inventor"]["connected"] is False
        
        await client.close()

    @pytest.mark.asyncio
    async def test_validate_model(self):
        """Test model validation request."""
        client = DesktopClient("http://test:8000")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "issues": [],
            "passed": 10
        }
        
        with patch.object(client._client, "post", return_value=mock_response) as mock_post:
            result = await client.validate_model("test.SLDPRT", "full")
            
            assert result["success"] is True
            assert result["passed"] == 10
            mock_post.assert_called_once()
        
        await client.close()

    @pytest.mark.asyncio
    async def test_get_bom(self):
        """Test BOM retrieval."""
        client = DesktopClient("http://test:8000")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "bom": [{"part": "Part1", "qty": 1}]
        }
        
        with patch.object(client._client, "get", return_value=mock_response) as mock_get:
            result = await client.get_bom(format="structured")
            
            assert result["success"] is True
            assert len(result["bom"]) == 1
            assert "structured" in mock_get.call_args[0][0]
        
        await client.close()

    @pytest.mark.asyncio
    async def test_export_document(self):
        """Test document export."""
        client = DesktopClient("http://test:8000")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "output_file": "output.pdf"
        }
        
        with patch.object(client._client, "post", return_value=mock_response) as mock_post:
            result = await client.export_document("pdf", "/output/test.pdf")
            
            assert result["success"] is True
            assert result["output_file"] == "output.pdf"
            mock_post.assert_called_once()
        
        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client works as context manager."""
        async with DesktopClient("http://test:8000") as client:
            assert client.base_url == "http://test:8000"

    def test_singleton(self):
        """Test get_desktop_client returns singleton."""
        client1 = get_desktop_client()
        client2 = get_desktop_client()
        assert client1 is client2

    @pytest.mark.asyncio
    async def test_connectivity_check(self):
        """Test quick connectivity check."""
        with patch("core.desktop_client.get_desktop_client") as mock_get:
            mock_client = Mock()
            mock_client.health_check = AsyncMock(return_value={"status": "healthy"})
            mock_get.return_value = mock_client
            
            result = await check_desktop_connectivity()
            assert result is True

    @pytest.mark.asyncio
    async def test_control_mouse(self):
        """Test mouse control."""
        client = DesktopClient("http://test:8000")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch.object(client._client, "post", return_value=mock_response) as mock_post:
            result = await client.control_mouse(100, 200, "click")
            
            assert result["success"] is True
            assert "click" in mock_post.call_args[0][0]
        
        await client.close()

    @pytest.mark.asyncio
    async def test_type_text(self):
        """Test text typing."""
        client = DesktopClient("http://test:8000")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        with patch.object(client._client, "post", return_value=mock_response) as mock_post:
            result = await client.type_text("Hello World")
            
            assert result["success"] is True
            call_json = mock_post.call_args[1]["json"]
            assert call_json["text"] == "Hello World"
        
        await client.close()


class TestIntegration:
    """Test integration with other components."""

    def test_orchestrator_imports_client(self):
        """Test orchestrator can import desktop client."""
        from core.orchestrator_adapter import get_desktop_client as orch_client
        assert orch_client is not None

    def test_health_dashboard_imports_client(self):
        """Test health dashboard can import desktop client."""
        from core.health_dashboard import get_desktop_client as health_client
        assert health_client is not None

    @pytest.mark.asyncio
    async def test_health_dashboard_uses_client(self):
        """Test health dashboard uses desktop client for checks."""
        from core.health_dashboard import HealthDashboard
        
        dashboard = HealthDashboard()
        
        with patch("core.health_dashboard.get_desktop_client") as mock_get:
            mock_client = Mock()
            mock_client.health_check = AsyncMock(return_value={"status": "healthy"})
            mock_get.return_value = mock_client
            
            status = await dashboard._check_service("desktop", "http://localhost:8000")
            
            assert status.status == "healthy"
            mock_client.health_check.assert_called_once()


class TestErrorHandling:
    """Test error handling in desktop client."""

    @pytest.mark.asyncio
    async def test_network_timeout(self):
        """Test client handles network timeouts."""
        client = DesktopClient("http://test:8000", timeout=1)
        
        with patch.object(client._client, "get", side_effect=asyncio.TimeoutError()):
            result = await client.health_check()
            assert result["status"] == "unreachable"
        
        await client.close()

    @pytest.mark.asyncio
    async def test_invalid_response(self):
        """Test client handles invalid JSON responses."""
        client = DesktopClient("http://test:8000")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with patch.object(client._client, "get", return_value=mock_response):
            result = await client.health_check()
            assert result["status"] == "unreachable"
        
        await client.close()

    @pytest.mark.asyncio
    async def test_http_error(self):
        """Test client handles HTTP errors."""
        client = DesktopClient("http://test:8000")
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server Error")
        
        with patch.object(client._client, "get", return_value=mock_response):
            result = await client.health_check()
            assert result["status"] == "unreachable"
        
        await client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
