"""
Flatter Files Adapter
Integrates with Flatter Files API for drawing management.

Phase 12: Flatter Files Integration
API Docs: https://www.flatterfiles.com/site/docs/api/

Features:
- Search drawings by part number/description
- Get PDF/STEP/DXF download URLs
- Get assembly BOM structure
- Get revision history
- Create external sharing links
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("cad_agent.flatter-files")

# API base URL
BASE_URL = "https://www.flatterfiles.com/api"


@dataclass
class FlatterItem:
    """A drawing/item from Flatter Files."""
    id: str
    part_number: str
    description: str = ""
    revision: str = ""
    status: str = ""  # released, checked_out, etc.
    file_type: str = ""  # pdf, step, dxf
    last_modified: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "part_number": self.part_number,
            "description": self.description,
            "revision": self.revision,
            "status": self.status,
            "file_type": self.file_type,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "metadata": self.metadata
        }


@dataclass
class BOMItem:
    """A BOM line item."""
    part_number: str
    description: str
    quantity: int
    level: int = 0  # Assembly hierarchy level
    parent: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "part_number": self.part_number,
            "description": self.description,
            "quantity": self.quantity,
            "level": self.level,
            "parent": self.parent
        }


class FlatterFilesAdapter:
    """
    Adapter for Flatter Files REST API.

    Requires environment variables:
    - FLATTER_FILES_COMPANY_ID
    - FLATTER_FILES_API_KEY

    Usage:
        adapter = FlatterFilesAdapter()

        # Search for drawings
        results = await adapter.search("bracket")

        # Get PDF URL
        url = await adapter.get_file_url("12345", "pdf")

        # Get BOM
        bom = await adapter.get_bom("ASSY-100")
    """

    def __init__(self, company_id: str = None, api_key: str = None):
        self._httpx = None
        self.company_id = company_id or os.getenv("FLATTER_FILES_COMPANY_ID", "")
        self.api_key = api_key or os.getenv("FLATTER_FILES_API_KEY", "")
        self._client = None

        if not self.company_id or not self.api_key:
            logger.warning("Flatter Files credentials not configured")

    def _lazy_import(self):
        """Lazy import httpx."""
        if self._httpx is None:
            try:
                import httpx
                self._httpx = httpx
            except ImportError:
                logger.error("httpx not installed: pip install httpx")

    def _get_auth_params(self) -> Dict[str, str]:
        """Get auth parameters for requests."""
        return {
            "cmpyID": self.company_id,
            "apiKey": self.api_key
        }

    async def _request(self, endpoint: str, params: Dict = None,
                       method: str = "POST") -> Dict:
        """Make authenticated API request."""
        self._lazy_import()

        if self._httpx is None:
            raise RuntimeError("httpx not available")

        url = f"{BASE_URL}/{endpoint}"
        data = {**self._get_auth_params(), **(params or {})}

        async with self._httpx.AsyncClient() as client:
            if method == "POST":
                response = await client.post(url, data=data)
            else:
                response = await client.get(url, params=data)

            response.raise_for_status()
            result = response.json()

            if result.get("error"):
                raise Exception(f"API error: {result.get('result')}")

            return result

    # === File Retrieval ===

    async def get_file_url(self, part_number: str, content_type: str = "pdf",
                          version: str = None) -> Optional[str]:
        """
        Get download URL for a file.

        Args:
            part_number: Part/drawing number
            content_type: pdf, step, preview, aslypdf (assembly view)
            version: PDM version (optional)

        Returns:
            Secure URL valid for 1 minute
        """
        endpoint = f"{content_type}/partNumber/{part_number}"

        params = {}
        if version:
            params["pdmVer"] = version

        try:
            result = await self._request(endpoint, params)
            return result.get("object", {}).get("url")
        except Exception as e:
            logger.error(f"Failed to get {content_type} URL for {part_number}: {e}")
            return None

    async def get_pdf_url(self, part_number: str, version: str = None) -> Optional[str]:
        """Get PDF download URL."""
        return await self.get_file_url(part_number, "pdf", version)

    async def get_step_url(self, part_number: str, version: str = None) -> Optional[str]:
        """Get STEP download URL."""
        return await self.get_file_url(part_number, "step", version)

    async def get_preview_url(self, part_number: str) -> Optional[str]:
        """Get preview image URL."""
        return await self.get_file_url(part_number, "preview")

    async def get_assembly_pdf_url(self, part_number: str) -> Optional[str]:
        """Get assembly view PDF URL."""
        return await self.get_file_url(part_number, "aslypdf")

    # === Items/Search ===

    async def list_items(self, page: int = 0, limit: int = 500) -> List[FlatterItem]:
        """
        List all items (paginated).

        Args:
            page: Page number (0-indexed)
            limit: Max items per page (max 500)
        """
        try:
            result = await self._request("items", {
                "page": page,
                "limit": min(limit, 500)
            })

            items = []
            for obj in result.get("objects", []):
                items.append(FlatterItem(
                    id=obj.get("id", ""),
                    part_number=obj.get("partNumber", ""),
                    description=obj.get("description", ""),
                    revision=obj.get("revision", ""),
                    status=obj.get("status", ""),
                    metadata=obj
                ))
            return items

        except Exception as e:
            logger.error(f"Failed to list items: {e}")
            return []

    async def get_item(self, part_number: str) -> Optional[FlatterItem]:
        """Get a specific item by part number."""
        try:
            result = await self._request(f"items/partNumber/{part_number}")
            obj = result.get("object", {})

            return FlatterItem(
                id=obj.get("id", ""),
                part_number=obj.get("partNumber", part_number),
                description=obj.get("description", ""),
                revision=obj.get("revision", ""),
                status=obj.get("status", ""),
                metadata=obj
            )
        except Exception as e:
            logger.error(f"Failed to get item {part_number}: {e}")
            return None

    async def search(self, query: str, limit: int = 50) -> List[FlatterItem]:
        """
        Search for items by part number or description.

        Note: Flatter Files search is done via items list filtering.
        For large libraries, use the web interface search.
        """
        items = await self.list_items(limit=limit)
        query_lower = query.lower()

        results = [
            item for item in items
            if query_lower in item.part_number.lower()
            or query_lower in item.description.lower()
        ]

        return results

    # === BOM ===

    async def get_bom(self, assembly_part_number: str) -> List[BOMItem]:
        """
        Get BOM for an assembly.

        Note: BOM extraction depends on how data is stored in Flatter Files.
        This may need customization based on your company's setup.
        """
        try:
            # Try to get assembly item with BOM metadata
            item = await self.get_item(assembly_part_number)
            if not item:
                return []

            bom_data = item.metadata.get("bom", [])
            bom_items = []

            for entry in bom_data:
                bom_items.append(BOMItem(
                    part_number=entry.get("partNumber", ""),
                    description=entry.get("description", ""),
                    quantity=entry.get("quantity", 1),
                    level=entry.get("level", 0),
                    parent=entry.get("parent")
                ))

            return bom_items

        except Exception as e:
            logger.error(f"Failed to get BOM for {assembly_part_number}: {e}")
            return []

    # === External Links ===

    async def create_external_link(
        self,
        part_numbers: List[str],
        recipient_emails: List[str],
        sender_email: str,
        password: str,
        message: str = "",
        send_email: bool = True
    ) -> Optional[str]:
        """
        Create an external sharing link.

        Args:
            part_numbers: List of part numbers to share
            recipient_emails: Email addresses for recipients
            sender_email: Your email address
            password: Link password (min 6 chars)
            message: Optional message text
            send_email: Whether to send notification email
        """
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")

        try:
            result = await self._request("link/external", {
                "senderEmail": sender_email,
                "recipientEmail": ",".join(recipient_emails),
                "password": password,
                "param": "partNumber",
                "itemValues": ",".join(part_numbers),
                "sendEmail": "true" if send_email else "false",
                "messageText": message
            })

            return result.get("object", {}).get("linkUrl")

        except Exception as e:
            logger.error(f"Failed to create external link: {e}")
            return None

    # === History/Tracking ===

    async def get_history(self, hours: int = 1) -> List[Dict]:
        """
        Get activity history (views, downloads, prints, searches).

        Args:
            hours: Hours of history to retrieve (default 1)
        """
        try:
            result = await self._request("history", {
                "hours": hours
            })
            return result.get("objects", [])
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []

    # === Item Management ===

    async def activate_item(self, part_number: str) -> bool:
        """Activate a deactivated item."""
        try:
            await self._request(f"items/activate/partNumber/{part_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to activate {part_number}: {e}")
            return False

    async def deactivate_item(self, part_number: str) -> bool:
        """Deactivate an item."""
        try:
            await self._request(f"items/deactivate/partNumber/{part_number}")
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate {part_number}: {e}")
            return False

    # === Libraries ===

    async def list_libraries(self) -> List[Dict]:
        """List all libraries."""
        try:
            result = await self._request("library/list")
            return result.get("objects", [])
        except Exception as e:
            logger.error(f"Failed to list libraries: {e}")
            return []

    # === Convenience Methods for Chatbot ===

    async def find_drawing(self, part_number: str) -> Optional[Dict]:
        """
        Find drawing and return PDF/STEP links.

        Chatbot example: "Find drawing for bracket 12345"
        """
        item = await self.get_item(part_number)
        if not item:
            return None

        pdf_url = await self.get_pdf_url(part_number)
        step_url = await self.get_step_url(part_number)
        preview_url = await self.get_preview_url(part_number)

        return {
            "part_number": item.part_number,
            "description": item.description,
            "revision": item.revision,
            "pdf_url": pdf_url,
            "step_url": step_url,
            "preview_url": preview_url
        }

    async def what_parts_in_assembly(self, assembly_pn: str) -> List[Dict]:
        """
        Get parts in an assembly.

        Chatbot example: "What parts are in assembly XYZ-100?"
        """
        bom = await self.get_bom(assembly_pn)
        return [item.to_dict() for item in bom]

    def is_configured(self) -> bool:
        """Check if credentials are configured."""
        return bool(self.company_id and self.api_key)


# Singleton
_adapter: Optional[FlatterFilesAdapter] = None

def get_flatter_files_adapter() -> FlatterFilesAdapter:
    global _adapter
    if _adapter is None:
        _adapter = FlatterFilesAdapter()
    return _adapter
