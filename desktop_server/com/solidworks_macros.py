"""
SolidWorks Macro Execution API - ENHANCED
==========================================
Full macro capability for maximum speed and automation.

Features:
- Run VBA/VSTA macros from files (.swp, .dll)
- Execute inline VBA code directly (no file needed)
- Parameterized macros (pass arguments)
- Macro library management (store, organize, share)
- Chain multiple macros
- Macro recording control
- Generate macros from operations
- Pre-built macro templates
"""

import logging
import os
import json
import tempfile
import shutil
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


# =============================================================================
# Pydantic Models
# =============================================================================

class RunMacroRequest(BaseModel):
    """Run a macro from file."""
    macro_path: str  # Full path to .swp file
    module_name: Optional[str] = None  # VBA module name
    procedure_name: Optional[str] = "main"  # Procedure to run


class RunInlineCodeRequest(BaseModel):
    """Execute inline VBA code."""
    code: str  # VBA code to execute
    procedure_name: str = "Main"  # Entry point procedure
    module_name: str = "Module1"


class ParameterizedMacroRequest(BaseModel):
    """Run macro with parameters."""
    macro_path: str
    parameters: Dict[str, Any]  # Parameters to inject
    module_name: Optional[str] = None
    procedure_name: str = "main"


class MacroChainRequest(BaseModel):
    """Chain multiple macros together."""
    macros: List[Dict[str, Any]]  # List of macro configs
    stop_on_error: bool = True
    save_between: bool = False


class BatchMacroRequest(BaseModel):
    """Run macro on multiple files."""
    macro_path: str
    files: List[str]  # Files to process
    save_after: bool = True
    close_after: bool = False


class SaveMacroRequest(BaseModel):
    """Save macro to library."""
    name: str
    description: str
    code: str
    category: str = "General"
    parameters: Optional[List[Dict[str, str]]] = None  # [{"name": "depth", "type": "float", "default": "10"}]
    tags: Optional[List[str]] = None


class GenerateMacroRequest(BaseModel):
    """Generate macro from operations."""
    operations: List[Dict[str, Any]]
    macro_name: str = "GeneratedMacro"
    include_error_handling: bool = True


class MacroTemplateRequest(BaseModel):
    """Create part/assembly from macro template."""
    template_name: str
    parameters: Dict[str, Any]
    output_path: Optional[str] = None


router = APIRouter(prefix="/solidworks-macros", tags=["solidworks-macros"])

# Macro library storage
MACRO_LIBRARY_DIR = os.path.join(os.path.dirname(__file__), "macro_library")
os.makedirs(MACRO_LIBRARY_DIR, exist_ok=True)


# =============================================================================
# Helper Functions
# =============================================================================

def get_solidworks():
    """Get active SolidWorks application."""
    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")
    pythoncom.CoInitialize()
    try:
        return win32com.client.GetActiveObject("SldWorks.Application")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SolidWorks not running: {e}")


def create_temp_macro(code: str, module_name: str = "Module1", procedure_name: str = "Main") -> str:
    """Create a temporary .swp macro file from code."""
    # SWP file format is essentially a VBA project
    # For simplicity, we'll create a basic structure

    temp_dir = tempfile.mkdtemp()
    macro_path = os.path.join(temp_dir, "temp_macro.swp")

    # Create the VBA code with proper structure
    full_code = f'''Attribute VB_Name = "{module_name}"
Option Explicit

{code}
'''

    # Write to file
    with open(macro_path, 'w') as f:
        f.write(full_code)

    return macro_path


def inject_parameters(code: str, parameters: Dict[str, Any]) -> str:
    """Inject parameters into macro code."""
    # Replace parameter placeholders
    for name, value in parameters.items():
        placeholder = f"{{${name}}}"
        if isinstance(value, str):
            replacement = f'"{value}"'
        elif isinstance(value, bool):
            replacement = "True" if value else "False"
        else:
            replacement = str(value)
        code = code.replace(placeholder, replacement)

    # Also replace Const declarations
    for name, value in parameters.items():
        if isinstance(value, str):
            replacement = f'Const {name} As String = "{value}"'
        elif isinstance(value, bool):
            replacement = f'Const {name} As Boolean = {"True" if value else "False"}'
        elif isinstance(value, float):
            replacement = f'Const {name} As Double = {value}'
        elif isinstance(value, int):
            replacement = f'Const {name} As Long = {value}'
        else:
            replacement = f'Const {name} = {value}'

        # Replace any existing Const declaration for this name
        import re
        pattern = rf'Const\s+{name}\s+As\s+\w+\s*=\s*[^\n]+'
        code = re.sub(pattern, replacement, code)

    return code


# =============================================================================
# Macro Execution Endpoints
# =============================================================================

@router.post("/run")
async def run_macro(request: RunMacroRequest):
    """
    Run a SolidWorks macro (.swp file).
    """
    try:
        sw = get_solidworks()

        if not os.path.exists(request.macro_path):
            raise HTTPException(status_code=404, detail=f"Macro not found: {request.macro_path}")

        # Build procedure name
        if request.module_name:
            proc = f"{request.module_name}.{request.procedure_name}"
        else:
            proc = request.procedure_name

        # Run macro
        errors = 0
        result = sw.RunMacro2(
            request.macro_path,
            request.module_name or "",
            request.procedure_name,
            0,  # Options
            errors
        )

        return {
            "success": result and errors == 0,
            "macro_path": request.macro_path,
            "procedure": proc,
            "error_code": errors,
            "message": "Macro executed successfully" if result else f"Macro failed with error code {errors}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run macro failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/run-inline")
async def run_inline_code(request: RunInlineCodeRequest):
    """
    Execute inline VBA code directly - NO FILE NEEDED.

    This is the fastest way to automate SolidWorks from the chatbot.
    The code is compiled and executed in-process.

    Example:
    {
        "code": "Sub Main()\\n  Dim swApp As SldWorks.SldWorks\\n  Set swApp = Application.SldWorks\\n  MsgBox \"Hello from Vulcan!\"\\nEnd Sub",
        "procedure_name": "Main"
    }
    """
    temp_path = None
    try:
        sw = get_solidworks()

        # Create temporary macro file
        temp_path = create_temp_macro(
            request.code,
            request.module_name,
            request.procedure_name
        )

        # Run the temporary macro
        errors = 0
        result = sw.RunMacro2(
            temp_path,
            request.module_name,
            request.procedure_name,
            0,
            errors
        )

        return {
            "success": result and errors == 0,
            "error_code": errors,
            "message": "Inline code executed successfully" if result else f"Execution failed with error {errors}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run inline code failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                shutil.rmtree(os.path.dirname(temp_path))
            except:
                pass
        pythoncom.CoUninitialize()


@router.post("/run-parameterized")
async def run_parameterized_macro(request: ParameterizedMacroRequest):
    """
    Run a macro with injected parameters.

    Parameters are substituted into the macro code before execution.
    Use {$param_name} placeholders in your macro code.

    Example:
    {
        "macro_path": "C:/macros/create_box.swp",
        "parameters": {
            "width": 100,
            "height": 50,
            "depth": 25,
            "material": "Steel"
        }
    }
    """
    temp_path = None
    try:
        sw = get_solidworks()

        if not os.path.exists(request.macro_path):
            raise HTTPException(status_code=404, detail=f"Macro not found: {request.macro_path}")

        # Read original macro
        with open(request.macro_path, 'r') as f:
            original_code = f.read()

        # Inject parameters
        modified_code = inject_parameters(original_code, request.parameters)

        # Create temporary macro with modified code
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, os.path.basename(request.macro_path))

        with open(temp_path, 'w') as f:
            f.write(modified_code)

        # Run modified macro
        errors = 0
        result = sw.RunMacro2(
            temp_path,
            request.module_name or "",
            request.procedure_name,
            0,
            errors
        )

        return {
            "success": result and errors == 0,
            "parameters_injected": list(request.parameters.keys()),
            "error_code": errors,
            "message": "Parameterized macro executed" if result else f"Failed with error {errors}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run parameterized macro failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(os.path.dirname(temp_path)):
            try:
                shutil.rmtree(os.path.dirname(temp_path))
            except:
                pass
        pythoncom.CoUninitialize()


@router.post("/chain")
async def chain_macros(request: MacroChainRequest):
    """
    Chain multiple macros together for complex workflows.

    Example:
    {
        "macros": [
            {"path": "C:/macros/open_part.swp", "procedure": "Main"},
            {"path": "C:/macros/add_features.swp", "procedure": "AddHoles"},
            {"path": "C:/macros/export.swp", "procedure": "ExportSTEP"}
        ],
        "stop_on_error": true
    }
    """
    try:
        sw = get_solidworks()
        model = sw.ActiveDoc

        results = []

        for i, macro_config in enumerate(request.macros):
            macro_path = macro_config.get("path", "")
            procedure = macro_config.get("procedure", "main")
            module = macro_config.get("module", "")
            params = macro_config.get("parameters", {})

            try:
                # Handle parameterized macros
                if params:
                    with open(macro_path, 'r') as f:
                        code = f.read()
                    code = inject_parameters(code, params)

                    temp_dir = tempfile.mkdtemp()
                    temp_path = os.path.join(temp_dir, "temp.swp")
                    with open(temp_path, 'w') as f:
                        f.write(code)
                    macro_path = temp_path

                # Run macro
                errors = 0
                result = sw.RunMacro2(macro_path, module, procedure, 0, errors)

                results.append({
                    "macro": macro_config.get("path", macro_path),
                    "success": result and errors == 0,
                    "error_code": errors
                })

                # Save between if requested
                if request.save_between and model:
                    model.Save3(1, 0, 0)

                # Stop on error if requested
                if request.stop_on_error and (not result or errors != 0):
                    break

            except Exception as e:
                results.append({
                    "macro": macro_config.get("path", ""),
                    "success": False,
                    "error": str(e)
                })
                if request.stop_on_error:
                    break

        successful = sum(1 for r in results if r.get("success"))

        return {
            "total_macros": len(request.macros),
            "executed": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }

    except Exception as e:
        logger.error(f"Chain macros failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/batch")
async def batch_run_macro(request: BatchMacroRequest):
    """
    Run a macro on multiple files - PRODUCTION AUTOMATION.
    """
    try:
        sw = get_solidworks()

        if not os.path.exists(request.macro_path):
            raise HTTPException(status_code=404, detail=f"Macro not found: {request.macro_path}")

        results = []
        for file_path in request.files:
            try:
                # Determine document type
                doc_type = 1  # Part
                if file_path.lower().endswith('.sldasm'):
                    doc_type = 2  # Assembly
                elif file_path.lower().endswith('.slddrw'):
                    doc_type = 3  # Drawing

                # Open file
                errors = 0
                warnings = 0
                doc = sw.OpenDoc6(file_path, doc_type, 1, "", errors, warnings)

                if doc:
                    # Run macro
                    macro_errors = 0
                    success = sw.RunMacro2(request.macro_path, "", "main", 0, macro_errors)

                    # Save if requested
                    if request.save_after and success:
                        doc.Save3(1, errors, warnings)

                    # Close if requested
                    if request.close_after:
                        sw.CloseDoc(doc.GetTitle())

                    results.append({
                        "file": file_path,
                        "success": success and macro_errors == 0,
                        "error": None
                    })
                else:
                    results.append({
                        "file": file_path,
                        "success": False,
                        "error": f"Failed to open (error {errors})"
                    })

            except Exception as e:
                results.append({
                    "file": file_path,
                    "success": False,
                    "error": str(e)
                })

        successful = sum(1 for r in results if r["success"])

        return {
            "macro": request.macro_path,
            "total_files": len(request.files),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch macro failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Macro Library Management
# =============================================================================

@router.post("/library/save")
async def save_to_library(request: SaveMacroRequest):
    """
    Save a macro to the library for reuse.

    Example:
    {
        "name": "CreateBox",
        "description": "Creates a box with specified dimensions",
        "code": "Sub Main()\\n...",
        "category": "Parts",
        "parameters": [
            {"name": "width", "type": "float", "default": "100"},
            {"name": "height", "type": "float", "default": "50"}
        ],
        "tags": ["box", "primitive", "parametric"]
    }
    """
    # Create category directory
    category_dir = os.path.join(MACRO_LIBRARY_DIR, request.category)
    os.makedirs(category_dir, exist_ok=True)

    # Create macro entry
    macro_entry = {
        "name": request.name,
        "description": request.description,
        "category": request.category,
        "parameters": request.parameters or [],
        "tags": request.tags or [],
        "created": datetime.now().isoformat(),
        "code_file": f"{request.name}.swp"
    }

    # Save metadata
    meta_path = os.path.join(category_dir, f"{request.name}.json")
    with open(meta_path, 'w') as f:
        json.dump(macro_entry, f, indent=2)

    # Save code
    code_path = os.path.join(category_dir, f"{request.name}.swp")
    with open(code_path, 'w') as f:
        f.write(request.code)

    return {
        "status": "ok",
        "name": request.name,
        "category": request.category,
        "path": code_path,
        "message": f"Macro '{request.name}' saved to library"
    }


@router.get("/library/list")
async def list_library(category: Optional[str] = None):
    """List all macros in the library."""
    macros = []

    # Walk through library
    for cat_name in os.listdir(MACRO_LIBRARY_DIR):
        cat_path = os.path.join(MACRO_LIBRARY_DIR, cat_name)
        if not os.path.isdir(cat_path):
            continue

        if category and cat_name != category:
            continue

        for file in os.listdir(cat_path):
            if file.endswith('.json'):
                with open(os.path.join(cat_path, file)) as f:
                    macro_meta = json.load(f)
                    macros.append(macro_meta)

    # Group by category
    categories = {}
    for macro in macros:
        cat = macro.get("category", "General")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "name": macro["name"],
            "description": macro["description"],
            "parameters": macro.get("parameters", []),
            "tags": macro.get("tags", [])
        })

    return {
        "total_macros": len(macros),
        "categories": categories
    }


@router.get("/library/get/{name}")
async def get_library_macro(name: str, category: Optional[str] = None):
    """Get a macro from the library."""
    # Search for macro
    for cat_name in os.listdir(MACRO_LIBRARY_DIR):
        if category and cat_name != category:
            continue

        cat_path = os.path.join(MACRO_LIBRARY_DIR, cat_name)
        if not os.path.isdir(cat_path):
            continue

        meta_path = os.path.join(cat_path, f"{name}.json")
        code_path = os.path.join(cat_path, f"{name}.swp")

        if os.path.exists(meta_path):
            with open(meta_path) as f:
                macro_meta = json.load(f)

            code = ""
            if os.path.exists(code_path):
                with open(code_path) as f:
                    code = f.read()

            return {
                **macro_meta,
                "code": code,
                "code_path": code_path
            }

    raise HTTPException(status_code=404, detail=f"Macro '{name}' not found")


@router.post("/library/run/{name}")
async def run_library_macro(name: str, parameters: Optional[Dict[str, Any]] = None):
    """Run a macro from the library with optional parameters."""
    try:
        # Get macro from library
        macro_data = await get_library_macro(name)
        code = macro_data.get("code", "")
        code_path = macro_data.get("code_path", "")

        if not code and not code_path:
            raise HTTPException(status_code=404, detail="Macro code not found")

        sw = get_solidworks()

        # Inject parameters if provided
        if parameters and code:
            code = inject_parameters(code, parameters)

            # Create temp file with modified code
            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, f"{name}.swp")
            with open(temp_path, 'w') as f:
                f.write(code)
            code_path = temp_path

        # Run macro
        errors = 0
        result = sw.RunMacro2(code_path, "", "Main", 0, errors)

        return {
            "success": result and errors == 0,
            "macro": name,
            "parameters": parameters,
            "error_code": errors,
            "message": "Library macro executed" if result else f"Failed with error {errors}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run library macro failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.delete("/library/{name}")
async def delete_library_macro(name: str, category: Optional[str] = None):
    """Delete a macro from the library."""
    for cat_name in os.listdir(MACRO_LIBRARY_DIR):
        if category and cat_name != category:
            continue

        cat_path = os.path.join(MACRO_LIBRARY_DIR, cat_name)
        meta_path = os.path.join(cat_path, f"{name}.json")
        code_path = os.path.join(cat_path, f"{name}.swp")

        if os.path.exists(meta_path):
            os.remove(meta_path)
            if os.path.exists(code_path):
                os.remove(code_path)
            return {"status": "ok", "message": f"Macro '{name}' deleted"}

    raise HTTPException(status_code=404, detail=f"Macro '{name}' not found")


# =============================================================================
# Macro Generation
# =============================================================================

@router.post("/generate")
async def generate_macro(request: GenerateMacroRequest):
    """
    Generate VBA macro code from operations.

    Converts chatbot operations into a reusable macro.

    Example:
    {
        "operations": [
            {"type": "sketch", "plane": "Front Plane"},
            {"type": "rectangle", "x1": 0, "y1": 0, "x2": 100, "y2": 50},
            {"type": "extrude", "depth": 25}
        ],
        "macro_name": "CreateBox"
    }
    """
    # Generate VBA code from operations
    code_lines = [
        f"' {request.macro_name}",
        "' Auto-generated by Project Vulcan",
        f"' Generated: {datetime.now().isoformat()}",
        "",
        "Option Explicit",
        "",
        "Sub Main()",
        "    Dim swApp As SldWorks.SldWorks",
        "    Dim swModel As SldWorks.ModelDoc2",
        "    Dim swPart As SldWorks.PartDoc",
        "    Dim swSketchMgr As SldWorks.SketchManager",
        "    Dim swFeatMgr As SldWorks.FeatureManager",
        "    Dim swFeat As SldWorks.Feature",
        "    Dim boolstatus As Boolean",
        "",
        "    Set swApp = Application.SldWorks",
        "    Set swModel = swApp.ActiveDoc",
        "    Set swPart = swModel",
        "    Set swSketchMgr = swModel.SketchManager",
        "    Set swFeatMgr = swModel.FeatureManager",
        ""
    ]

    if request.include_error_handling:
        code_lines.append("    On Error GoTo ErrorHandler")
        code_lines.append("")

    # Convert operations to VBA
    for op in request.operations:
        op_type = op.get("type", "").lower()

        if op_type == "sketch":
            plane = op.get("plane", "Front Plane")
            code_lines.append(f'    boolstatus = swModel.Extension.SelectByID2("{plane}", "PLANE", 0, 0, 0, False, 0, Nothing, 0)')
            code_lines.append("    swSketchMgr.InsertSketch True")

        elif op_type == "end_sketch":
            code_lines.append("    swSketchMgr.InsertSketch True")

        elif op_type == "rectangle":
            x1 = op.get("x1", 0) / 1000
            y1 = op.get("y1", 0) / 1000
            x2 = op.get("x2", 100) / 1000
            y2 = op.get("y2", 100) / 1000
            code_lines.append(f"    swSketchMgr.CreateCornerRectangle {x1}, {y1}, 0, {x2}, {y2}, 0")

        elif op_type == "circle":
            cx = op.get("cx", 0) / 1000
            cy = op.get("cy", 0) / 1000
            r = op.get("radius", 10) / 1000
            code_lines.append(f"    swSketchMgr.CreateCircle {cx}, {cy}, 0, {cx + r}, {cy}, 0")

        elif op_type == "line":
            x1 = op.get("x1", 0) / 1000
            y1 = op.get("y1", 0) / 1000
            x2 = op.get("x2", 100) / 1000
            y2 = op.get("y2", 0) / 1000
            code_lines.append(f"    swSketchMgr.CreateLine {x1}, {y1}, 0, {x2}, {y2}, 0")

        elif op_type == "extrude":
            depth = op.get("depth", 10) / 1000
            code_lines.append(f"    Set swFeat = swFeatMgr.FeatureExtrusion3(True, False, False, 0, 0, {depth}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False)")

        elif op_type == "extrude_cut":
            depth = op.get("depth", 10) / 1000
            code_lines.append(f"    Set swFeat = swFeatMgr.FeatureCut4(True, False, False, 0, 0, {depth}, 0, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, 0, 0, False, False)")

        elif op_type == "fillet":
            radius = op.get("radius", 1) / 1000
            code_lines.append(f"    Set swFeat = swFeatMgr.FeatureFillet3(195, {radius}, 0, 0, 0, 0, 0, Nothing, Nothing, Nothing, Nothing, Nothing, Nothing, Nothing)")

        elif op_type == "chamfer":
            dist = op.get("distance", 1) / 1000
            code_lines.append(f"    Set swFeat = swFeatMgr.InsertFeatureChamfer(4, 1, {dist}, 0.785398163, 0, 0, 0, 0)")

        elif op_type == "rebuild":
            code_lines.append("    boolstatus = swModel.EditRebuild3()")

        elif op_type == "save":
            code_lines.append("    Dim lErrors As Long, lWarnings As Long")
            code_lines.append("    boolstatus = swModel.Save3(1, lErrors, lWarnings)")

        elif op_type == "property":
            name = op.get("name", "")
            value = op.get("value", "")
            code_lines.append(f'    swModel.Extension.CustomPropertyManager("").Set2 "{name}", "{value}"')

        code_lines.append("")

    # Add rebuild at end
    code_lines.append("    boolstatus = swModel.EditRebuild3()")
    code_lines.append("    swModel.ViewZoomtofit2")

    if request.include_error_handling:
        code_lines.extend([
            "",
            "    Exit Sub",
            "",
            "ErrorHandler:",
            '    MsgBox "Error: " & Err.Description, vbCritical',
        ])

    code_lines.extend([
        "",
        "End Sub"
    ])

    code = "\n".join(code_lines)

    return {
        "macro_name": request.macro_name,
        "code": code,
        "operations_count": len(request.operations),
        "message": "Macro code generated successfully"
    }


@router.post("/generate-and-run")
async def generate_and_run_macro(request: GenerateMacroRequest):
    """Generate macro from operations and immediately execute it."""
    # Generate the macro
    generated = await generate_macro(request)
    code = generated["code"]

    # Run it
    run_request = RunInlineCodeRequest(
        code=code,
        procedure_name="Main",
        module_name="Module1"
    )

    result = await run_inline_code(run_request)

    return {
        **result,
        "generated_code": code
    }


# =============================================================================
# Macro Recording
# =============================================================================

@router.get("/recording/status")
async def get_recording_status():
    """Check if macro recording is active."""
    try:
        sw = get_solidworks()
        is_recording = sw.GetMacroRecordingStatus() if hasattr(sw, 'GetMacroRecordingStatus') else False
        return {"is_recording": is_recording}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get recording status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/recording/start")
async def start_recording():
    """Start macro recording."""
    try:
        sw = get_solidworks()
        result = sw.StartMacroRecording() if hasattr(sw, 'StartMacroRecording') else False
        return {
            "success": result,
            "message": "Macro recording started" if result else "Failed to start recording"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start recording failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/recording/stop")
async def stop_recording(save_path: Optional[str] = None):
    """Stop macro recording and optionally save."""
    try:
        sw = get_solidworks()
        if save_path:
            result = sw.StopMacroRecording(save_path) if hasattr(sw, 'StopMacroRecording') else False
        else:
            result = sw.StopMacroRecording("") if hasattr(sw, 'StopMacroRecording') else False
        return {
            "success": result,
            "saved_to": save_path,
            "message": "Macro recording stopped"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stop recording failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Pre-built Macro Templates
# =============================================================================

@router.get("/templates")
async def list_macro_templates():
    """List available pre-built macro templates."""
    return {
        "templates": [
            {
                "name": "create_box",
                "description": "Create a parametric box",
                "parameters": ["width", "height", "depth"]
            },
            {
                "name": "create_cylinder",
                "description": "Create a parametric cylinder",
                "parameters": ["diameter", "height"]
            },
            {
                "name": "add_hole_pattern",
                "description": "Add a circular hole pattern",
                "parameters": ["hole_diameter", "pattern_diameter", "count"]
            },
            {
                "name": "export_all_configs",
                "description": "Export all configurations to separate files",
                "parameters": ["output_folder", "format"]
            },
            {
                "name": "batch_property_update",
                "description": "Update properties on multiple files",
                "parameters": ["property_name", "property_value", "files"]
            },
            {
                "name": "create_drawing",
                "description": "Create a drawing with standard views",
                "parameters": ["template", "sheet_size", "views"]
            }
        ]
    }


@router.post("/templates/run/{template_name}")
async def run_macro_template(template_name: str, parameters: Dict[str, Any]):
    """Run a pre-built macro template with parameters."""

    templates = {
        "create_box": '''
Sub Main()
    Dim swApp As SldWorks.SldWorks
    Dim swModel As SldWorks.ModelDoc2
    Dim swFeatMgr As SldWorks.FeatureManager
    Dim swSketchMgr As SldWorks.SketchManager

    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc
    Set swFeatMgr = swModel.FeatureManager
    Set swSketchMgr = swModel.SketchManager

    Const width As Double = {$width} / 1000
    Const height As Double = {$height} / 1000
    Const depth As Double = {$depth} / 1000

    swModel.Extension.SelectByID2 "Front Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    swSketchMgr.InsertSketch True
    swSketchMgr.CreateCornerRectangle -width/2, -height/2, 0, width/2, height/2, 0
    swSketchMgr.InsertSketch True

    swFeatMgr.FeatureExtrusion3 True, False, True, 0, 0, depth/2, depth/2, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False

    swModel.EditRebuild3
    swModel.ViewZoomtofit2
End Sub
''',
        "create_cylinder": '''
Sub Main()
    Dim swApp As SldWorks.SldWorks
    Dim swModel As SldWorks.ModelDoc2
    Dim swFeatMgr As SldWorks.FeatureManager
    Dim swSketchMgr As SldWorks.SketchManager

    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc
    Set swFeatMgr = swModel.FeatureManager
    Set swSketchMgr = swModel.SketchManager

    Const diameter As Double = {$diameter} / 1000
    Const height As Double = {$height} / 1000

    swModel.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    swSketchMgr.InsertSketch True
    swSketchMgr.CreateCircle 0, 0, 0, diameter/2, 0, 0
    swSketchMgr.InsertSketch True

    swFeatMgr.FeatureExtrusion3 True, False, True, 0, 0, height/2, height/2, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False

    swModel.EditRebuild3
    swModel.ViewZoomtofit2
End Sub
''',
        "add_hole_pattern": '''
Sub Main()
    Dim swApp As SldWorks.SldWorks
    Dim swModel As SldWorks.ModelDoc2
    Dim swFeatMgr As SldWorks.FeatureManager
    Dim swSketchMgr As SldWorks.SketchManager
    Dim i As Integer
    Dim angle As Double
    Dim x As Double, y As Double

    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc
    Set swFeatMgr = swModel.FeatureManager
    Set swSketchMgr = swModel.SketchManager

    Const holeDia As Double = {$hole_diameter} / 1000
    Const patternDia As Double = {$pattern_diameter} / 1000
    Const count As Integer = {$count}
    Const PI As Double = 3.14159265358979

    swModel.Extension.SelectByID2 "Top Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0
    swSketchMgr.InsertSketch True

    For i = 0 To count - 1
        angle = (2 * PI * i) / count
        x = (patternDia / 2) * Cos(angle)
        y = (patternDia / 2) * Sin(angle)
        swSketchMgr.CreateCircle x, y, 0, x + holeDia/2, y, 0
    Next i

    swSketchMgr.InsertSketch True
    swFeatMgr.FeatureCut4 True, False, False, 1, 0, 0.01, 0.01, False, False, False, False, 0, 0, False, False, False, False, False, True, True, True, True, False, 0, 0, False, False

    swModel.EditRebuild3
End Sub
'''
    }

    if template_name not in templates:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    code = templates[template_name]
    code = inject_parameters(code, parameters)

    # Run the template
    request = RunInlineCodeRequest(code=code, procedure_name="Main")
    return await run_inline_code(request)


# =============================================================================
# Command Execution
# =============================================================================

@router.post("/command/{command_id}")
async def run_command(command_id: int):
    """
    Execute a SolidWorks command by ID.
    """
    try:
        sw = get_solidworks()
        frame = sw.Frame
        if frame:
            result = frame.RunCommand(command_id, "")
            return {
                "success": True,
                "command_id": command_id,
                "message": f"Command {command_id} executed"
            }
        raise HTTPException(status_code=500, detail="Could not get SolidWorks frame")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Run command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/commands")
async def list_common_commands():
    """List common command IDs."""
    return {
        "file": {
            "new": 31031, "open": 31032, "save": 31233,
            "save_as": 31238, "close": 31034, "print": 31035
        },
        "edit": {
            "undo": 31001, "redo": 31002, "cut": 31003,
            "copy": 31004, "paste": 31005, "delete": 31006
        },
        "view": {
            "zoom_fit": 31340, "zoom_area": 31341, "zoom_in": 31342,
            "zoom_out": 31343, "rotate": 31350, "pan": 31351
        },
        "tools": {
            "rebuild": 31044, "force_rebuild": 31045,
            "measure": 24053, "check": 31212
        },
        "standard_views": {
            "front": 31324, "back": 31325, "left": 31326,
            "right": 31327, "top": 31328, "bottom": 31329, "isometric": 31330
        },
        "features": {
            "extrude": 31201, "revolve": 31202, "sweep": 31203,
            "loft": 31204, "fillet": 31205, "chamfer": 31206
        }
    }


@router.get("/info/{macro_path:path}")
async def get_macro_info(macro_path: str):
    """Get information about a macro file."""
    if not os.path.exists(macro_path):
        raise HTTPException(status_code=404, detail=f"Macro not found: {macro_path}")

    stat = os.stat(macro_path)

    # Try to read and analyze the macro
    procedures = []
    try:
        with open(macro_path, 'r', errors='ignore') as f:
            content = f.read()
            import re
            # Find Sub and Function declarations
            procs = re.findall(r'(?:Public\s+|Private\s+)?(?:Sub|Function)\s+(\w+)', content)
            procedures = list(set(procs))
    except:
        pass

    return {
        "path": macro_path,
        "filename": os.path.basename(macro_path),
        "size_bytes": stat.st_size,
        "modified": stat.st_mtime,
        "extension": os.path.splitext(macro_path)[1].lower(),
        "type": "VBA Macro" if macro_path.lower().endswith('.swp') else "VSTA Macro",
        "procedures": procedures
    }


__all__ = ["router"]
