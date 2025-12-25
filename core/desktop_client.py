"""
Desktop Server Client
Connects orchestrator/agents to the desktop CAD server.
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DesktopClient:
    """
    Client for communicating with the desktop CAD server.
    
    Handles all HTTP communication between cloud orchestrator and
    physical desktop server via Tailscale VPN.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize desktop client.
        
        Args:
            base_url: Desktop server URL (defaults to env var DESKTOP_SERVER_URL)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv("DESKTOP_SERVER_URL", "http://localhost:8000")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
        logger.info(f"Desktop client initialized: {self.base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """Check if desktop server is reachable."""
        try:
            response = await self._client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Desktop health check failed: {e}")
            return {"status": "unreachable", "error": str(e)}

    async def get_cad_status(self) -> Dict[str, Any]:
        """Get SolidWorks/Inventor status."""
        try:
            sw_status = await self._client.get(f"{self.base_url}/com/solidworks/status")
            inv_status = await self._client.get(f"{self.base_url}/com/inventor/status")
            
            return {
                "solidworks": sw_status.json() if sw_status.status_code == 200 else None,
                "inventor": inv_status.json() if inv_status.status_code == 200 else None,
            }
        except Exception as e:
            logger.error(f"CAD status check failed: {e}")
            return {"solidworks": None, "inventor": None, "error": str(e)}

    async def validate_model(self, file_path: str, validation_type: str = "full") -> Dict[str, Any]:
        """
        Validate CAD model.
        
        Args:
            file_path: Path to CAD file on desktop
            validation_type: Type of validation (full, quick, holes, etc.)
        """
        try:
            response = await self._client.post(
                f"{self.base_url}/cad/validate/{validation_type}",
                json={"file_path": file_path}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_bom(self, file_path: Optional[str] = None, format: str = "structured") -> Dict[str, Any]:
        """
        Get Bill of Materials from CAD assembly.
        
        Args:
            file_path: Path to assembly file (or uses active document)
            format: BOM format (structured, flat, csv)
        """
        try:
            endpoint = f"/com/bom/{format}"
            params = {"file_path": file_path} if file_path else {}
            
            response = await self._client.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"BOM retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_properties(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get custom properties from CAD file."""
        try:
            endpoint = "/com/properties/list"
            params = {"file_path": file_path} if file_path else {}
            
            response = await self._client.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Properties retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_measurements(self, measurement_type: str = "bounding-box") -> Dict[str, Any]:
        """
        Get measurements from active CAD model.
        
        Args:
            measurement_type: Type (bounding-box, distance, angle, clearance)
        """
        try:
            response = await self._client.get(f"{self.base_url}/com/measurement/{measurement_type}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Measurement failed: {e}")
            return {"success": False, "error": str(e)}

    async def export_document(
        self, 
        format: str = "pdf", 
        output_path: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export CAD document to various formats.
        
        Args:
            format: Export format (pdf, step, iges)
            output_path: Where to save exported file
            file_path: Source CAD file (or uses active)
        """
        try:
            response = await self._client.post(
                f"{self.base_url}/com/export/{format}",
                json={
                    "output_path": output_path,
                    "file_path": file_path
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Document export failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_configurations(self) -> Dict[str, Any]:
        """List available configurations in active document."""
        try:
            response = await self._client.get(f"{self.base_url}/com/configuration/list")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Configuration list failed: {e}")
            return {"success": False, "error": str(e)}

    async def activate_configuration(self, config_name: str) -> Dict[str, Any]:
        """Activate a specific configuration."""
        try:
            response = await self._client.post(
                f"{self.base_url}/com/configuration/activate",
                json={"configuration_name": config_name}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Configuration activation failed: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_assembly(self) -> Dict[str, Any]:
        """Run comprehensive assembly analysis."""
        try:
            response = await self._client.get(f"{self.base_url}/com/assembly-analyzer/analyze")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Assembly analysis failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_features(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Get feature tree from CAD model."""
        try:
            endpoint = "/com/feature-reader/list"
            params = {"file_path": file_path} if file_path else {}
            
            response = await self._client.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Feature retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    async def execute_macro(self, macro_path: str, module: str, procedure: str) -> Dict[str, Any]:
        """Execute SolidWorks macro."""
        try:
            response = await self._client.post(
                f"{self.base_url}/com/solidworks/run_macro",
                json={
                    "macro_path": macro_path,
                    "module": module,
                    "procedure": procedure
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Macro execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def capture_screen(self) -> Dict[str, Any]:
        """Capture screenshot from desktop."""
        try:
            response = await self._client.post(f"{self.base_url}/screen/capture")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return {"success": False, "error": str(e)}

    async def control_mouse(self, x: int, y: int, action: str = "move") -> Dict[str, Any]:
        """
        Control desktop mouse.
        
        Args:
            x, y: Screen coordinates
            action: move, click, right_click, double_click
        """
        try:
            response = await self._client.post(
                f"{self.base_url}/mouse/{action}",
                json={"x": x, "y": y}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Mouse control failed: {e}")
            return {"success": False, "error": str(e)}

    async def type_text(self, text: str) -> Dict[str, Any]:
        """Type text on desktop."""
        try:
            response = await self._client.post(
                f"{self.base_url}/keyboard/type",
                json={"text": text}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Text typing failed: {e}")
            return {"success": False, "error": str(e)}

    async def close(self):
        """Close client connection."""
        await self._client.aclose()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()


# Singleton instance
_desktop_client: Optional[DesktopClient] = None


def get_desktop_client() -> DesktopClient:
    """Get or create desktop client singleton."""
    global _desktop_client
    if _desktop_client is None:
        _desktop_client = DesktopClient()
    return _desktop_client


async def check_desktop_connectivity() -> bool:
    """Quick check if desktop server is reachable."""
    client = get_desktop_client()
    result = await client.health_check()
    return result.get("status") == "healthy"
