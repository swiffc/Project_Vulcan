"""
BOM Manager - COM Adapter
Extract and manage Bill of Materials (BOM) from CAD assemblies.

Priority 2 API - BOM Operations (0% coverage)
Enables:
- "Get the BOM as structured data"
- "Export BOM to CSV"
- "Show me quantities of all parts"
"""

import logging
import csv
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("com.bom_manager")

router = APIRouter(prefix="/com/bom", tags=["BOM Operations"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class BOMItem(BaseModel):
    """Single BOM item."""
    level: int
    part_number: str
    description: str
    quantity: int
    file_path: Optional[str] = None
    configuration: Optional[str] = None
    material: Optional[str] = None
    mass: Optional[float] = None
    children: Optional[List['BOMItem']] = None


class BOMResponse(BaseModel):
    """Response with BOM data."""
    items: List[BOMItem]
    total_items: int
    total_unique_parts: int


class ExportBOMRequest(BaseModel):
    """Request to export BOM."""
    output_path: str
    format: str = "csv"  # csv, excel, json
    include_properties: Optional[List[str]] = None


# ============================================================================
# SOLIDWORKS BOM MANAGER
# ============================================================================

class SolidWorksBOMManager:
    """Manage BOM data from SolidWorks assemblies."""
    
    def __init__(self, sw_app=None):
        self.app = sw_app
    
    def get_structured_bom(self, configuration: Optional[str] = None) -> List[BOMItem]:
        """
        Get hierarchical BOM structure.
        
        Args:
            configuration: Configuration name (None for active)
        
        Returns:
            List of BOM items with hierarchy
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Verify it's an assembly
        if model.GetType() != 2:  # swDocASSEMBLY
            raise ValueError("Document must be an assembly")
        
        # Get configuration
        if configuration:
            config = model.GetConfigurationByName(configuration)
        else:
            config = model.GetActiveConfiguration()
        
        if not config:
            raise ValueError("Configuration not found")
        
        # Get root component
        root_comp = config.GetRootComponent3(True)
        
        # Build BOM recursively
        bom_items = []
        self._process_component(root_comp, bom_items, level=0)
        
        return bom_items
    
    def _process_component(self, component, bom_items: List, level: int):
        """Recursively process assembly component."""
        if not component:
            return
        
        # Get component info
        comp_doc = component.GetModelDoc2()
        
        part_number = ""
        description = ""
        material = ""
        mass = None
        
        if comp_doc:
            # Get custom properties
            ext = comp_doc.Extension
            cust_prop_mgr = ext.CustomPropertyManager("")
            
            # Try to get part number
            val_out = [""]
            resolved_val = [""]
            was_resolved = [False]
            link_to_prop = [False]
            
            cust_prop_mgr.Get5("PartNo", False, val_out, resolved_val, was_resolved, link_to_prop)
            part_number = resolved_val[0] if resolved_val[0] else component.Name2
            
            # Try to get description
            cust_prop_mgr.Get5("Description", False, val_out, resolved_val, was_resolved, link_to_prop)
            description = resolved_val[0] if resolved_val[0] else ""
            
            # Try to get material
            cust_prop_mgr.Get5("Material", False, val_out, resolved_val, was_resolved, link_to_prop)
            material = resolved_val[0] if resolved_val[0] else ""
            
            # Get mass properties
            try:
                mass_prop = comp_doc.Extension.CreateMassProperty()
                if mass_prop:
                    mass = mass_prop.Mass
            except:
                pass
        
        # Create BOM item
        item = BOMItem(
            level=level,
            part_number=part_number or component.Name2,
            description=description,
            quantity=1,  # Component instance count handled separately
            file_path=component.GetPathName() if component.GetPathName() else None,
            configuration=component.ReferencedConfiguration,
            material=material if material else None,
            mass=mass,
            children=[]
        )
        
        # Process children
        children = component.GetChildren()
        if children:
            for child in children:
                self._process_component(child, item.children, level + 1)
        
        bom_items.append(item)
    
    def get_flat_bom(self) -> List[Dict]:
        """
        Get flattened BOM with quantities.
        
        Returns:
            List of parts with quantities
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        if model.GetType() != 2:
            raise ValueError("Document must be an assembly")
        
        # Get BOM table feature
        config = model.GetActiveConfiguration()
        root_comp = config.GetRootComponent3(True)
        
        # Count components
        quantity_map = {}
        self._count_components(root_comp, quantity_map)
        
        # Convert to list
        flat_bom = []
        for part_path, quantity in quantity_map.items():
            # Get part info
            part_name = part_path.split("\\")[-1] if part_path else "Unknown"
            
            flat_bom.append({
                "part_number": part_name,
                "quantity": quantity,
                "file_path": part_path
            })
        
        return flat_bom
    
    def _count_components(self, component, quantity_map: Dict):
        """Count component instances recursively."""
        if not component:
            return
        
        path = component.GetPathName()
        if path:
            quantity_map[path] = quantity_map.get(path, 0) + 1
        
        # Process children
        children = component.GetChildren()
        if children:
            for child in children:
                self._count_components(child, quantity_map)
    
    def export_bom_to_csv(self, output_path: str, include_properties: Optional[List[str]] = None) -> str:
        """
        Export BOM to CSV file.
        
        Args:
            output_path: Output CSV file path
            include_properties: List of custom properties to include
        
        Returns:
            Path to exported CSV
        """
        # Get flat BOM
        bom_data = self.get_flat_bom()
        
        # Write to CSV
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = ['part_number', 'quantity', 'file_path']
            if include_properties:
                fieldnames.extend(include_properties)
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in bom_data:
                writer.writerow(item)
        
        logger.info(f"Exported BOM to CSV: {output_path}")
        return output_path


# ============================================================================
# INVENTOR BOM MANAGER
# ============================================================================

class InventorBOMManager:
    """Manage BOM data from Inventor assemblies."""
    
    def __init__(self, inv_app=None):
        self.app = inv_app
    
    def get_structured_bom(self, configuration: Optional[str] = None) -> List[BOMItem]:
        """Get hierarchical BOM structure."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        # Check if assembly
        if doc.DocumentType != 12292:  # kAssemblyDocumentObject
            raise ValueError("Document must be an assembly")
        
        # Get BOM
        bom = doc.ComponentDefinition.BOM
        bom.StructuredViewEnabled = True
        bom_view = bom.BOMViews.Item("Structured")
        
        # Process BOM rows
        bom_items = []
        for i in range(1, bom_view.BOMRows.Count + 1):
            row = bom_view.BOMRows.Item(i)
            item = self._process_bom_row(row, level=0)
            bom_items.append(item)
        
        return bom_items
    
    def _process_bom_row(self, row, level: int) -> BOMItem:
        """Process a single BOM row."""
        # Get component definition
        comp_def = row.ComponentDefinitions.Item(1)
        
        # Get properties
        part_number = ""
        description = ""
        
        try:
            # Try to get from iProperties
            prop_sets = comp_def.Document.PropertySets
            design_props = prop_sets.Item("Design Tracking Properties")
            part_number = design_props.Item("Part Number").Value
        except:
            part_number = row.ItemNumber
        
        try:
            sum_info = comp_def.Document.PropertySets.Item("Inventor Summary Information")
            description = sum_info.Item("Title").Value
        except:
            description = ""
        
        # Create BOM item
        item = BOMItem(
            level=level,
            part_number=part_number,
            description=description,
            quantity=row.ItemQuantity,
            file_path=comp_def.Document.FullFileName if comp_def.Document else None,
            children=[]
        )
        
        # Process child rows
        if row.ChildRows:
            for i in range(1, row.ChildRows.Count + 1):
                child_row = row.ChildRows.Item(i)
                child_item = self._process_bom_row(child_row, level + 1)
                item.children.append(child_item)
        
        return item
    
    def get_flat_bom(self) -> List[Dict]:
        """Get flattened BOM with quantities."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        if doc.DocumentType != 12292:
            raise ValueError("Document must be an assembly")
        
        # Get parts-only BOM
        bom = doc.ComponentDefinition.BOM
        bom.PartsOnlyViewEnabled = True
        bom_view = bom.BOMViews.Item("Parts Only")
        
        flat_bom = []
        for i in range(1, bom_view.BOMRows.Count + 1):
            row = bom_view.BOMRows.Item(i)
            comp_def = row.ComponentDefinitions.Item(1)
            
            flat_bom.append({
                "part_number": row.ItemNumber,
                "quantity": row.ItemQuantity,
                "file_path": comp_def.Document.FullFileName if comp_def.Document else None
            })
        
        return flat_bom
    
    def export_bom_to_csv(self, output_path: str, include_properties: Optional[List[str]] = None) -> str:
        """Export BOM to CSV file."""
        bom_data = self.get_flat_bom()
        
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = ['part_number', 'quantity', 'file_path']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in bom_data:
                writer.writerow(item)
        
        logger.info(f"Exported BOM to CSV: {output_path}")
        return output_path


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

_sw_bom: Optional[SolidWorksBOMManager] = None
_inv_bom: Optional[InventorBOMManager] = None


def set_solidworks_app(sw_app):
    """Set SolidWorks application instance."""
    global _sw_bom
    _sw_bom = SolidWorksBOMManager(sw_app)


def set_inventor_app(inv_app):
    """Set Inventor application instance."""
    global _inv_bom
    _inv_bom = InventorBOMManager(inv_app)


@router.get("/structured")
async def get_structured_bom(cad_system: str = "solidworks", configuration: Optional[str] = None):
    """
    Get hierarchical BOM structure.
    
    Args:
        cad_system: "solidworks" or "inventor"
        configuration: Configuration name (optional)
    
    Returns:
        Structured BOM with hierarchy
    """
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_bom:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            items = _sw_bom.get_structured_bom(configuration)
        else:
            if not _inv_bom:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            items = _inv_bom.get_structured_bom(configuration)
        
        return {
            "success": True,
            "items": [item.dict() for item in items],
            "total_items": len(items),
            "total_unique_parts": len(items)
        }
    
    except Exception as e:
        logger.error(f"Get structured BOM failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flat")
async def get_flat_bom(cad_system: str = "solidworks"):
    """
    Get flattened BOM with quantities.
    
    Args:
        cad_system: "solidworks" or "inventor"
    
    Returns:
        Flat BOM with part quantities
    """
    try:
        if cad_system.lower() == "solidworks":
            if not _sw_bom:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            items = _sw_bom.get_flat_bom()
        else:
            if not _inv_bom:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            items = _inv_bom.get_flat_bom()
        
        return {
            "success": True,
            "items": items,
            "total_unique_parts": len(items)
        }
    
    except Exception as e:
        logger.error(f"Get flat BOM failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export-csv")
async def export_bom_to_csv(request: ExportBOMRequest):
    """
    Export BOM to CSV file.
    
    Args:
        request: Export request
    
    Returns:
        Export response with file path
    """
    try:
        cad_system = "solidworks"  # Default, can be added to request model
        
        if cad_system.lower() == "solidworks":
            if not _sw_bom:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            output_file = _sw_bom.export_bom_to_csv(request.output_path, request.include_properties)
        else:
            if not _inv_bom:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            output_file = _inv_bom.export_bom_to_csv(request.output_path, request.include_properties)
        
        return {
            "success": True,
            "output_file": output_file,
            "message": "BOM exported to CSV successfully"
        }
    
    except Exception as e:
        logger.error(f"Export BOM to CSV failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
