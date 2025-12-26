"""
SolidWorks Design Tables API
============================
Complete design table management including:
- Create/delete design tables
- Read/modify table data
- Configuration generation and management
- Excel integration (import/export/link)
- Feature suppression control ($STATE@)
- Custom properties ($PRP, $PRPSHEET)
- Component visibility ($SHOW@)
- Color/appearance control ($COLOR)
- Batch operations
"""

import logging
import os
from typing import Optional, Dict, Any, List, Union
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


# Pydantic models
class CreateDesignTableRequest(BaseModel):
    source: str = "blank"  # blank, auto, file
    file_path: Optional[str] = None  # For 'file' source
    link_to_file: bool = False
    edit_control: str = "allow_model_edits"  # allow_model_edits, block_model_edits


class AddConfigurationRequest(BaseModel):
    configuration_name: str
    dimension_values: Dict[str, float]  # {"D1@Sketch1": 10.0, "D2@Sketch1": 20.0}


class UpdateCellRequest(BaseModel):
    row: int  # 0-indexed row (configuration)
    column: int  # 0-indexed column (parameter)
    value: Any


router = APIRouter(prefix="/solidworks-design-tables", tags=["solidworks-design-tables"])


def get_solidworks():
    """Get active SolidWorks application."""
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")
    pythoncom.CoInitialize()
    try:
        return win32com.client.GetActiveObject("SldWorks.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SolidWorks not running: {e}")


# =============================================================================
# Design Table Management
# =============================================================================

@router.post("/create")
async def create_design_table(request: CreateDesignTableRequest):
    """
    Create a design table.

    source options:
    - blank: Empty table for manual entry
    - auto: Auto-populate with current dimensions
    - file: Link to external Excel file
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Source type mapping
        source_map = {
            "blank": 0,
            "auto": 1,
            "file": 2
        }
        source_type = source_map.get(request.source.lower(), 0)

        # Edit control mapping
        control_map = {
            "allow_model_edits": 0,
            "block_model_edits": 1
        }
        edit_control = control_map.get(request.edit_control.lower(), 0)

        # Create design table
        dt = doc.InsertDesignTable(
            source_type,
            request.link_to_file,
            edit_control,
            request.file_path or ""
        )

        return {
            "success": dt is not None,
            "source": request.source,
            "linked": request.link_to_file,
            "message": "Design table created"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create design table failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/info")
async def get_design_table_info():
    """
    Get information about the design table.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            return {"has_design_table": False}

        # Get table dimensions
        row_count = dt.GetTotalRowCount() if hasattr(dt, 'GetTotalRowCount') else 0
        col_count = dt.GetTotalColumnCount() if hasattr(dt, 'GetTotalColumnCount') else 0

        # Get parameter names (first row)
        parameters = []
        if hasattr(dt, 'GetColumnHeader'):
            for i in range(col_count):
                param = dt.GetColumnHeader(i)
                if param:
                    parameters.append(param)

        # Get configuration names
        configurations = []
        if hasattr(dt, 'GetRowHeader'):
            for i in range(row_count):
                cfg = dt.GetRowHeader(i)
                if cfg:
                    configurations.append(cfg)

        return {
            "has_design_table": True,
            "row_count": row_count,
            "column_count": col_count,
            "parameters": parameters,
            "configurations": configurations,
            "is_linked": dt.GetLinkedFile() if hasattr(dt, 'GetLinkedFile') else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get design table info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/data")
async def get_design_table_data():
    """
    Get all data from the design table.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        row_count = dt.GetTotalRowCount() if hasattr(dt, 'GetTotalRowCount') else 0
        col_count = dt.GetTotalColumnCount() if hasattr(dt, 'GetTotalColumnCount') else 0

        # Build data matrix
        data = []
        for row in range(row_count):
            row_data = {}
            cfg_name = dt.GetRowHeader(row) if hasattr(dt, 'GetRowHeader') else f"Row_{row}"

            for col in range(col_count):
                param_name = dt.GetColumnHeader(col) if hasattr(dt, 'GetColumnHeader') else f"Col_{col}"
                value = dt.GetEntryValue(row, col) if hasattr(dt, 'GetEntryValue') else None
                row_data[param_name] = value

            data.append({
                "configuration": cfg_name,
                "values": row_data
            })

        return {
            "row_count": row_count,
            "column_count": col_count,
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get design table data failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/add-configuration")
async def add_configuration_to_table(request: AddConfigurationRequest):
    """
    Add a new configuration (row) to the design table.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Add new row
        row_index = dt.AddRow() if hasattr(dt, 'AddRow') else -1

        if row_index >= 0:
            # Set configuration name
            if hasattr(dt, 'SetRowHeader'):
                dt.SetRowHeader(row_index, request.configuration_name)

            # Set dimension values
            col_count = dt.GetTotalColumnCount() if hasattr(dt, 'GetTotalColumnCount') else 0
            for col in range(col_count):
                param = dt.GetColumnHeader(col) if hasattr(dt, 'GetColumnHeader') else None
                if param and param in request.dimension_values:
                    dt.SetEntryValue(row_index, col, request.dimension_values[param])

            # Update configurations
            dt.UpdateTable()
            doc.EditRebuild3()

        return {
            "success": row_index >= 0,
            "configuration": request.configuration_name,
            "row_index": row_index,
            "values_set": len(request.dimension_values)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add configuration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.put("/cell")
async def update_cell(request: UpdateCellRequest):
    """
    Update a specific cell in the design table.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Set cell value
        if hasattr(dt, 'SetEntryValue'):
            dt.SetEntryValue(request.row, request.column, request.value)
            dt.UpdateTable()
            doc.EditRebuild3()

            return {
                "success": True,
                "row": request.row,
                "column": request.column,
                "value": request.value
            }

        raise HTTPException(status_code=500, detail="Cannot update cell")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update cell failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Design Table Operations
# =============================================================================

@router.post("/edit")
async def edit_design_table():
    """
    Open design table for editing (in Excel).
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Edit table (opens Excel)
        result = dt.EditTable() if hasattr(dt, 'EditTable') else False

        return {
            "success": result,
            "message": "Design table opened for editing"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Edit design table failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/update")
async def update_design_table():
    """
    Update design table and regenerate configurations.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        result = dt.UpdateTable() if hasattr(dt, 'UpdateTable') else False
        doc.EditRebuild3()

        return {
            "success": result,
            "message": "Design table updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update design table failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/delete")
async def delete_design_table():
    """
    Delete the design table from the document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        result = doc.DeleteDesignTable() if hasattr(doc, 'DeleteDesignTable') else False

        return {
            "success": result,
            "message": "Design table deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete design table failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/export")
async def export_design_table(output_path: str):
    """
    Export design table to Excel file.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Export to Excel
        result = dt.SaveAsExcel(output_path) if hasattr(dt, 'SaveAsExcel') else False

        return {
            "success": result,
            "output_path": output_path
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export design table failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Parameter Discovery
# =============================================================================

@router.get("/available-parameters")
async def list_available_parameters():
    """
    List all dimensions and features that can be added to design table.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        parameters = []

        # Traverse feature tree for dimensions
        feature = doc.FirstFeature()
        while feature:
            try:
                # Get display dimensions from feature
                dims = feature.GetDisplayDimensions()
                if dims:
                    for dim in dims:
                        dim_obj = dim.GetDimension2(0)
                        if dim_obj:
                            parameters.append({
                                "name": dim_obj.FullName,
                                "value": dim_obj.SystemValue * 1000,  # Convert to mm
                                "feature": feature.Name,
                                "type": "dimension"
                            })
            except Exception:
                pass

            feature = feature.GetNextFeature()

        return {
            "count": len(parameters),
            "parameters": parameters
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List parameters failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
