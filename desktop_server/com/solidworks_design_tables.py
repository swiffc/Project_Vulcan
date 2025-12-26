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


class AddColumnRequest(BaseModel):
    column_header: str  # e.g., "D1@Sketch1", "$STATE@Feature1", "$PRP@Description"
    default_value: Optional[Any] = None
    position: Optional[int] = None  # None = add at end


class DeleteRowRequest(BaseModel):
    row_index: int  # 0-indexed row to delete


class DeleteColumnRequest(BaseModel):
    column_index: int  # 0-indexed column to delete


class RenameConfigurationRequest(BaseModel):
    old_name: str
    new_name: str


class DuplicateConfigurationRequest(BaseModel):
    source_name: str
    new_name: str
    copy_values: bool = True


class BatchCreateConfigsRequest(BaseModel):
    configurations: List[Dict[str, Any]]  # List of {name: str, values: {param: value}}


class FeatureSuppressionRequest(BaseModel):
    configuration_name: str
    feature_name: str
    suppressed: bool  # True = suppress, False = unsuppress


class CustomPropertyRequest(BaseModel):
    configuration_name: str
    property_name: str
    property_value: str
    config_specific: bool = True  # True = $PRP, False = $PRPSHEET


class ComponentVisibilityRequest(BaseModel):
    configuration_name: str
    component_name: str
    visible: bool


class ColorControlRequest(BaseModel):
    configuration_name: str
    feature_or_face: str
    color_rgb: List[int]  # [R, G, B] 0-255


class ImportExcelRequest(BaseModel):
    excel_path: str
    sheet_name: Optional[str] = None
    create_configurations: bool = True


class LinkTableRequest(BaseModel):
    excel_path: str
    update_on_open: bool = True


class UpdateMultipleCellsRequest(BaseModel):
    updates: List[Dict[str, Any]]  # [{row: int, column: int, value: any}, ...]


class SortConfigurationsRequest(BaseModel):
    sort_by: str  # Column header name
    ascending: bool = True


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


# =============================================================================
# Column (Parameter) Management
# =============================================================================

@router.post("/add-column")
async def add_column(request: AddColumnRequest):
    """
    Add a new column (parameter) to the design table.

    column_header examples:
    - Dimension: "D1@Sketch1"
    - Feature suppression: "$STATE@Boss-Extrude1"
    - Custom property: "$PRP@Description"
    - Sheet property: "$PRPSHEET@Title"
    - Component visibility: "$SHOW@Part1-1"
    - Color: "$COLOR@Face<1>"
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Add column
        col_index = dt.AddColumn(request.column_header, request.position or -1)

        # Set default value for all rows if provided
        if request.default_value is not None and col_index >= 0:
            row_count = dt.GetTotalRowCount()
            for row in range(row_count):
                dt.SetEntryValue(row, col_index, request.default_value)

        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": col_index >= 0,
            "column_header": request.column_header,
            "column_index": col_index,
            "message": f"Column '{request.column_header}' added"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add column failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/column")
async def delete_column(request: DeleteColumnRequest):
    """Delete a column from the design table."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Get column name before deleting
        col_name = dt.GetColumnHeader(request.column_index) if hasattr(dt, 'GetColumnHeader') else None

        result = dt.DeleteColumn(request.column_index)
        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": result,
            "deleted_column": col_name,
            "column_index": request.column_index,
            "message": f"Column {request.column_index} deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete column failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Row (Configuration) Management
# =============================================================================

@router.delete("/row")
async def delete_row(request: DeleteRowRequest):
    """Delete a row (configuration) from the design table."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Get config name before deleting
        cfg_name = dt.GetRowHeader(request.row_index) if hasattr(dt, 'GetRowHeader') else None

        result = dt.DeleteRow(request.row_index)
        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": result,
            "deleted_configuration": cfg_name,
            "row_index": request.row_index,
            "message": f"Row {request.row_index} deleted"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete row failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/rename-configuration")
async def rename_configuration(request: RenameConfigurationRequest):
    """Rename a configuration in the design table."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Find row with old name
        row_count = dt.GetTotalRowCount()
        row_found = -1
        for row in range(row_count):
            if dt.GetRowHeader(row) == request.old_name:
                row_found = row
                break

        if row_found < 0:
            raise HTTPException(status_code=404, detail=f"Configuration '{request.old_name}' not found")

        # Rename
        dt.SetRowHeader(row_found, request.new_name)
        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": True,
            "old_name": request.old_name,
            "new_name": request.new_name,
            "message": f"Configuration renamed from '{request.old_name}' to '{request.new_name}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rename configuration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/duplicate-configuration")
async def duplicate_configuration(request: DuplicateConfigurationRequest):
    """Duplicate a configuration with a new name."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Find source row
        row_count = dt.GetTotalRowCount()
        col_count = dt.GetTotalColumnCount()
        source_row = -1

        for row in range(row_count):
            if dt.GetRowHeader(row) == request.source_name:
                source_row = row
                break

        if source_row < 0:
            raise HTTPException(status_code=404, detail=f"Configuration '{request.source_name}' not found")

        # Add new row
        new_row = dt.AddRow()
        if new_row >= 0:
            dt.SetRowHeader(new_row, request.new_name)

            # Copy values if requested
            if request.copy_values:
                for col in range(col_count):
                    value = dt.GetEntryValue(source_row, col)
                    dt.SetEntryValue(new_row, col, value)

            dt.UpdateTable()
            doc.EditRebuild3()

        return {
            "success": new_row >= 0,
            "source": request.source_name,
            "new_configuration": request.new_name,
            "row_index": new_row,
            "message": f"Configuration '{request.source_name}' duplicated as '{request.new_name}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Duplicate configuration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/batch-create")
async def batch_create_configurations(request: BatchCreateConfigsRequest):
    """
    Create multiple configurations at once.

    Example request:
    {
        "configurations": [
            {"name": "Small", "values": {"D1@Sketch1": 10, "D2@Sketch1": 5}},
            {"name": "Medium", "values": {"D1@Sketch1": 20, "D2@Sketch1": 10}},
            {"name": "Large", "values": {"D1@Sketch1": 30, "D2@Sketch1": 15}}
        ]
    }
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        col_count = dt.GetTotalColumnCount()
        created = []
        failed = []

        for config in request.configurations:
            try:
                name = config.get("name")
                values = config.get("values", {})

                row_index = dt.AddRow()
                if row_index >= 0:
                    dt.SetRowHeader(row_index, name)

                    # Set values
                    for col in range(col_count):
                        param = dt.GetColumnHeader(col)
                        if param in values:
                            dt.SetEntryValue(row_index, col, values[param])

                    created.append(name)
                else:
                    failed.append({"name": name, "error": "Failed to add row"})
            except Exception as e:
                failed.append({"name": config.get("name"), "error": str(e)})

        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": len(failed) == 0,
            "created_count": len(created),
            "failed_count": len(failed),
            "created": created,
            "failed": failed,
            "message": f"Created {len(created)} configurations"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch create failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Special Column Types ($STATE@, $PRP@, $SHOW@, $COLOR@)
# =============================================================================

@router.post("/feature-suppression")
async def set_feature_suppression(request: FeatureSuppressionRequest):
    """
    Control feature suppression via design table.
    Adds $STATE@<feature> column if not present.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        column_header = f"$STATE@{request.feature_name}"
        value = "S" if request.suppressed else "U"  # S=Suppressed, U=Unsuppressed

        # Find or add column
        col_count = dt.GetTotalColumnCount()
        col_index = -1
        for col in range(col_count):
            if dt.GetColumnHeader(col) == column_header:
                col_index = col
                break

        if col_index < 0:
            col_index = dt.AddColumn(column_header, -1)

        # Find configuration row
        row_count = dt.GetTotalRowCount()
        row_index = -1
        for row in range(row_count):
            if dt.GetRowHeader(row) == request.configuration_name:
                row_index = row
                break

        if row_index < 0:
            raise HTTPException(status_code=404, detail=f"Configuration '{request.configuration_name}' not found")

        # Set value
        dt.SetEntryValue(row_index, col_index, value)
        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": True,
            "configuration": request.configuration_name,
            "feature": request.feature_name,
            "suppressed": request.suppressed,
            "message": f"Feature '{request.feature_name}' {'suppressed' if request.suppressed else 'unsuppressed'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set feature suppression failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/custom-property")
async def set_custom_property(request: CustomPropertyRequest):
    """
    Control custom properties via design table.
    Adds $PRP@ or $PRPSHEET@ column if not present.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        prefix = "$PRP@" if request.config_specific else "$PRPSHEET@"
        column_header = f"{prefix}{request.property_name}"

        # Find or add column
        col_count = dt.GetTotalColumnCount()
        col_index = -1
        for col in range(col_count):
            if dt.GetColumnHeader(col) == column_header:
                col_index = col
                break

        if col_index < 0:
            col_index = dt.AddColumn(column_header, -1)

        # Find configuration row
        row_count = dt.GetTotalRowCount()
        row_index = -1
        for row in range(row_count):
            if dt.GetRowHeader(row) == request.configuration_name:
                row_index = row
                break

        if row_index < 0:
            raise HTTPException(status_code=404, detail=f"Configuration '{request.configuration_name}' not found")

        # Set value
        dt.SetEntryValue(row_index, col_index, request.property_value)
        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": True,
            "configuration": request.configuration_name,
            "property": request.property_name,
            "value": request.property_value,
            "config_specific": request.config_specific,
            "message": f"Property '{request.property_name}' set to '{request.property_value}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set custom property failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/component-visibility")
async def set_component_visibility(request: ComponentVisibilityRequest):
    """
    Control component visibility via design table (assemblies only).
    Adds $SHOW@<component> column if not present.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if doc.GetType() != 2:  # Assembly
            raise HTTPException(status_code=400, detail="Component visibility requires an assembly")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        column_header = f"$SHOW@{request.component_name}"
        value = "S" if request.visible else "H"  # S=Show, H=Hide

        # Find or add column
        col_count = dt.GetTotalColumnCount()
        col_index = -1
        for col in range(col_count):
            if dt.GetColumnHeader(col) == column_header:
                col_index = col
                break

        if col_index < 0:
            col_index = dt.AddColumn(column_header, -1)

        # Find configuration row
        row_count = dt.GetTotalRowCount()
        row_index = -1
        for row in range(row_count):
            if dt.GetRowHeader(row) == request.configuration_name:
                row_index = row
                break

        if row_index < 0:
            raise HTTPException(status_code=404, detail=f"Configuration '{request.configuration_name}' not found")

        # Set value
        dt.SetEntryValue(row_index, col_index, value)
        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": True,
            "configuration": request.configuration_name,
            "component": request.component_name,
            "visible": request.visible,
            "message": f"Component '{request.component_name}' {'shown' if request.visible else 'hidden'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set component visibility failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/color-control")
async def set_color(request: ColorControlRequest):
    """
    Control feature/face color via design table.
    Adds $COLOR@<feature_or_face> column if not present.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        column_header = f"$COLOR@{request.feature_or_face}"

        # Convert RGB to SolidWorks color format (BGR integer)
        r, g, b = request.color_rgb
        color_value = b * 65536 + g * 256 + r

        # Find or add column
        col_count = dt.GetTotalColumnCount()
        col_index = -1
        for col in range(col_count):
            if dt.GetColumnHeader(col) == column_header:
                col_index = col
                break

        if col_index < 0:
            col_index = dt.AddColumn(column_header, -1)

        # Find configuration row
        row_count = dt.GetTotalRowCount()
        row_index = -1
        for row in range(row_count):
            if dt.GetRowHeader(row) == request.configuration_name:
                row_index = row
                break

        if row_index < 0:
            raise HTTPException(status_code=404, detail=f"Configuration '{request.configuration_name}' not found")

        # Set value
        dt.SetEntryValue(row_index, col_index, color_value)
        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": True,
            "configuration": request.configuration_name,
            "feature_or_face": request.feature_or_face,
            "color_rgb": request.color_rgb,
            "message": f"Color set for '{request.feature_or_face}'"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set color failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Excel Integration
# =============================================================================

@router.post("/import-excel")
async def import_from_excel(request: ImportExcelRequest):
    """
    Import data from an Excel file into the design table.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if not os.path.exists(request.excel_path):
            raise HTTPException(status_code=404, detail=f"Excel file not found: {request.excel_path}")

        # Check if design table exists, create if not
        dt = doc.GetDesignTable()
        if not dt:
            # Create from file
            dt = doc.InsertDesignTable(2, True, 0, request.excel_path)  # 2 = from file
        else:
            # Update from file
            dt.SetLinkedFile(request.excel_path)
            dt.UpdateTable()

        doc.EditRebuild3()

        return {
            "success": dt is not None,
            "excel_path": request.excel_path,
            "create_configurations": request.create_configurations,
            "message": "Excel data imported"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Import Excel failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/link")
async def link_to_excel(request: LinkTableRequest):
    """Link the design table to an external Excel file."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if not os.path.exists(request.excel_path):
            raise HTTPException(status_code=404, detail=f"Excel file not found: {request.excel_path}")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Link to file
        result = dt.SetLinkedFile(request.excel_path)

        return {
            "success": result,
            "excel_path": request.excel_path,
            "update_on_open": request.update_on_open,
            "message": "Design table linked to Excel file"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Link to Excel failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/break-link")
async def break_excel_link():
    """Break the link to an external Excel file."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        # Break link
        result = dt.SetLinkedFile("")

        return {
            "success": result,
            "message": "Excel link broken - table is now embedded"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Break link failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/refresh-from-link")
async def refresh_from_linked_file():
    """Refresh the design table from the linked Excel file."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        linked_file = dt.GetLinkedFile() if hasattr(dt, 'GetLinkedFile') else None
        if not linked_file:
            raise HTTPException(status_code=400, detail="Design table is not linked to a file")

        # Refresh from file
        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": True,
            "linked_file": linked_file,
            "message": "Design table refreshed from linked file"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refresh from link failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Bulk Operations
# =============================================================================

@router.post("/update-multiple-cells")
async def update_multiple_cells(request: UpdateMultipleCellsRequest):
    """Update multiple cells at once for better performance."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        dt = doc.GetDesignTable()
        if not dt:
            raise HTTPException(status_code=404, detail="No design table found")

        updated = 0
        failed = []

        for update in request.updates:
            try:
                row = update.get("row")
                col = update.get("column")
                value = update.get("value")
                dt.SetEntryValue(row, col, value)
                updated += 1
            except Exception as e:
                failed.append({"row": row, "column": col, "error": str(e)})

        dt.UpdateTable()
        doc.EditRebuild3()

        return {
            "success": len(failed) == 0,
            "updated_count": updated,
            "failed_count": len(failed),
            "failed": failed,
            "message": f"Updated {updated} cells"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update multiple cells failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Utility Functions
# =============================================================================

@router.get("/column-types")
async def get_column_type_reference():
    """Get reference for special column type prefixes."""
    return {
        "column_types": {
            "dimension": {
                "format": "D#@FeatureName or DimensionName@FeatureName",
                "example": "D1@Sketch1",
                "description": "Controls dimension value"
            },
            "feature_suppression": {
                "format": "$STATE@FeatureName",
                "example": "$STATE@Boss-Extrude1",
                "values": "S=Suppressed, U=Unsuppressed",
                "description": "Controls feature suppression state"
            },
            "config_property": {
                "format": "$PRP@PropertyName",
                "example": "$PRP@Description",
                "description": "Configuration-specific custom property"
            },
            "sheet_property": {
                "format": "$PRPSHEET@PropertyName",
                "example": "$PRPSHEET@Title",
                "description": "Sheet-level custom property"
            },
            "component_visibility": {
                "format": "$SHOW@ComponentName",
                "example": "$SHOW@Part1-1",
                "values": "S=Show, H=Hide",
                "description": "Controls component visibility (assemblies)"
            },
            "color": {
                "format": "$COLOR@FeatureOrFace",
                "example": "$COLOR@Boss-Extrude1",
                "values": "BGR integer value",
                "description": "Controls feature/face color"
            },
            "configuration": {
                "format": "$CONFIGURATION@PartName",
                "example": "$CONFIGURATION@Part1-1",
                "description": "Controls which configuration of a part to use"
            },
            "description": {
                "format": "$DESCRIPTION",
                "description": "Configuration description"
            },
            "user_notes": {
                "format": "$USER_NOTES",
                "description": "User notes for configuration"
            }
        }
    }


@router.get("/features-for-suppression")
async def list_features_for_suppression():
    """List all features that can be controlled via $STATE@ columns."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        features = []
        feature = doc.FirstFeature()

        while feature:
            feat_type = feature.GetTypeName2()
            # Skip non-suppressible features
            if feat_type not in ["OriginProfileFeature", "MaterialFolder", "HistoryFolder"]:
                features.append({
                    "name": feature.Name,
                    "type": feat_type,
                    "column_header": f"$STATE@{feature.Name}",
                    "suppressed": feature.IsSuppressed2(1)[0]
                })
            feature = feature.GetNextFeature()

        return {
            "count": len(features),
            "features": features
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List features failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/components-for-visibility")
async def list_components_for_visibility():
    """List all components that can be controlled via $SHOW@ columns (assemblies)."""
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        if doc.GetType() != 2:
            raise HTTPException(status_code=400, detail="This function requires an assembly")

        components = []
        comps = doc.GetComponents(False)

        if comps:
            for comp in comps:
                components.append({
                    "name": comp.Name,
                    "column_header": f"$SHOW@{comp.Name}",
                    "visible": comp.Visible,
                    "suppressed": comp.IsSuppressed()
                })

        return {
            "count": len(components),
            "components": components
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List components failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
