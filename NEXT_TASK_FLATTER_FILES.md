# NEXT TASK FOR CLI: CAD Performance Manager + PDM + Flatter Files Integration

**From**: Claude Chat  
**Priority**: HIGH  
**Type**: New Feature - Complete CAD Automation System  
**Estimated Files**: 9 new adapters  

---

## 🎯 OBJECTIVE

Build a complete CAD automation system that:
1. Manages SolidWorks PDM check-out/check-in
2. Handles 20,000+ part assemblies efficiently
3. Monitors system resources and auto-adjusts settings
4. Queues and processes batch jobs with resume capability
5. Validates changes via Inspector Agent
6. Shows notifications in Web UI
7. **Access Flatter Files for drawing search, BOMs, revisions**

---

## 📁 FILES TO CREATE

### 1-8: See Previous Sections (PDM, Job Queue, Performance Manager, etc.)

---

### 9. Flatter Files Adapter (NEW - Drawing Access)
**File**: `agents/cad_agent/adapters/flatter_files_adapter.py`  
**Lines**: ~350

```python
"""
Flatter Files API Adapter
Access drawings, BOMs, revisions from Flatter Files cloud.

API Docs: https://www.flatterfiles.com/site/docs/api/

Setup:
    1. Login as Admin to Flatter Files
    2. Dashboard > Settings > Company > Misc Settings
    3. Enable "API Access"
    4. Manage API Keys > New
    5. Copy the API key
"""

import logging
import requests
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger("cad.flatter-files")


@dataclass
class FlatItem:
    """Drawing/document item from Flatter Files."""
    ident: str
    part_number: str
    description: str
    revision: str
    state: str
    pdf_url: Optional[str]
    step_url: Optional[str]
    dxf_url: Optional[str]
    native_url: Optional[str]
    properties: Dict[str, Any]
    checked_out: bool = False
    checked_out_by: Optional[str] = None
    

@dataclass
class AssemblyView:
    """Assembly with BOM structure."""
    ident: str
    name: str
    part_number: str
    components: List['FlatItem']
    total_parts: int
    

@dataclass
class Markup:
    """Drawing markup/annotation."""
    ident: str
    created_by: str
    created_at: str
    content: str
    drawing_ident: str
    status: str  # "open", "resolved", etc.
    

class FlatterFilesAdapter:
    """
    Access Flatter Files drawings and documents via API.
    
    Usage:
        ff = FlatterFilesAdapter(api_key="your-key")
        
        # Search for drawings
        items = ff.search("bracket")
        
        # Get specific item by part number
        item = ff.get_item_by_part_number("12345")
        
        # Get assembly BOM
        bom = ff.get_assembly_bom("assembly-ident")
        
        # Get file URLs
        pdf_url = ff.get_pdf_url(item.ident)
        step_url = ff.get_step_url(item.ident)
        
        # Get markups/annotations
        markups = ff.get_markups(item.ident)
    """
    
    BASE_URL = "https://www.flatterfiles.com/api"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        
    def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request."""
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}
        params["key"] = self.api_key
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("error"):
                logger.error(f"API error: {data.get('result')}")
                return {"error": True, "result": data.get("result")}
                
            return data
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": True, "result": str(e)}
            
    def _parse_item(self, obj: Dict) -> FlatItem:
        """Parse API response into FlatItem."""
        return FlatItem(
            ident=obj.get("ident", ""),
            part_number=obj.get("partNumber", ""),
            description=obj.get("description", ""),
            revision=obj.get("revision", ""),
            state=obj.get("state", ""),
            pdf_url=obj.get("pdfUrl"),
            step_url=obj.get("stepUrl"),
            dxf_url=obj.get("dxfUrl"),
            native_url=obj.get("nativeUrl"),
            properties=obj.get("properties", {}),
            checked_out=obj.get("checkedOut", False),
            checked_out_by=obj.get("checkedOutBy")
        )
        
    def get_all_items(self, limit: int = 500) -> List[FlatItem]:
        """Get all items (paginated, 500 per request)."""
        items = []
        cursor = None
        
        while len(items) < limit:
            endpoint = "items"
            params = {"cursor": cursor} if cursor else {}
            data = self._request(endpoint, params)
            
            if data.get("error"):
                break
                
            for obj in data.get("objects", []):
                items.append(self._parse_item(obj))
                    
            cursor = data.get("cursor")
            if not cursor:
                break
                
        return items
        
    def search(self, query: str, limit: int = 50) -> List[FlatItem]:
        """Search items by part number or description."""
        all_items = self.get_all_items(limit=1000)
        query_lower = query.lower()
        
        return [
            item for item in all_items
            if query_lower in item.part_number.lower() or
               query_lower in item.description.lower()
        ][:limit]
        
    def get_item_by_ident(self, ident: str) -> Optional[FlatItem]:
        """Get item by Flatter Files ident."""
        endpoint = f"items/ident/{ident}"
        data = self._request(endpoint)
        obj = data.get("object")
        return self._parse_item(obj) if obj else None
        
    def get_item_by_part_number(self, part_number: str) -> Optional[FlatItem]:
        """Get item by part number."""
        endpoint = f"items/partNumber/{part_number}"
        data = self._request(endpoint)
        obj = data.get("object")
        return self._parse_item(obj) if obj else None
        
    def get_pdf_url(self, ident: str) -> str:
        """Get PDF download URL."""
        return f"{self.BASE_URL}/pdf/ident/{ident}?key={self.api_key}"
        
    def get_step_url(self, ident: str) -> str:
        """Get STEP file download URL."""
        return f"{self.BASE_URL}/step/ident/{ident}?key={self.api_key}"
        
    def get_dxf_url(self, ident: str) -> str:
        """Get DXF file download URL."""
        return f"{self.BASE_URL}/dxf/ident/{ident}?key={self.api_key}"
        
    def get_assembly_bom(self, ident: str) -> Optional[AssemblyView]:
        """Get assembly view with BOM."""
        item = self.get_item_by_ident(ident)
        if not item:
            return None
            
        endpoint = f"assemblyView/ident/{ident}"
        data = self._request(endpoint)
        
        if data.get("error"):
            return None
            
        obj = data.get("object", {})
        components = [self._parse_item(comp) for comp in obj.get("components", [])]
        
        return AssemblyView(
            ident=ident,
            name=item.description,
            part_number=item.part_number,
            components=components,
            total_parts=len(components)
        )
        
    def get_revision_history(self, ident: str) -> List[Dict]:
        """Get revision history for an item."""
        endpoint = f"revisions/ident/{ident}"
        data = self._request(endpoint)
        return data.get("objects", []) if not data.get("error") else []
        
    def get_markups(self, ident: str) -> List[Markup]:
        """Get markup annotations for a drawing."""
        endpoint = f"markups/ident/{ident}"
        data = self._request(endpoint)
        
        if data.get("error"):
            return []
            
        return [
            Markup(
                ident=obj.get("ident", ""),
                created_by=obj.get("createdBy", ""),
                created_at=obj.get("createdAt", ""),
                content=obj.get("content", ""),
                drawing_ident=ident,
                status=obj.get("status", "open")
            )
            for obj in data.get("objects", [])
        ]
        
    def get_checked_out_items(self) -> List[FlatItem]:
        """Get items currently checked out."""
        all_items = self.get_all_items()
        return [item for item in all_items if item.checked_out]


# Singleton
_ff: Optional[FlatterFilesAdapter] = None

def get_flatter_files_adapter(api_key: str = None) -> FlatterFilesAdapter:
    global _ff
    if _ff is None:
        import os
        key = api_key or os.environ.get("FLATTER_FILES_API_KEY")
        if not key:
            raise ValueError("Flatter Files API key required")
        _ff = FlatterFilesAdapter(key)
    return _ff
```

---

## 📋 ENVIRONMENT VARIABLES

Add to `.env`:
```
FLATTER_FILES_API_KEY=your-api-key-here
```

---

## ✅ ACCEPTANCE CRITERIA

### 6. Flatter Files Integration (NEW)
- [ ] Search drawings by part number
- [ ] Search drawings by description
- [ ] Get PDF download URL
- [ ] Get STEP/DXF download URLs
- [ ] Get assembly BOM structure
- [ ] Get revision history
- [ ] Get markup annotations
- [ ] Filter by checked-out status

---

## 💬 EXAMPLE CHATBOT CONVERSATIONS

**User:** "Find the drawing for bracket 12345"
**Bot:** Found: Bracket Assembly 12345 - Rev C - [PDF Link] [STEP Link]

**User:** "What parts are in assembly XYZ-100?"
**Bot:** Assembly XYZ-100 contains 45 parts: Bracket-001 (x4), Plate-002 (x2)...

**User:** "Any markups on drawing ABC-500?"
**Bot:** Found 2 markups: John Smith: "Tolerance needs review"...

---

## 🗑️ DELETE THIS FILE AFTER COMPLETING
