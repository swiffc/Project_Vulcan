"""
SolidWorks Macro Execution API
==============================
Macro management and execution including:
- Run VBA/VSTA macros
- Macro recording
- Batch macro execution
- Custom command execution
"""

import logging
import os
from typing import Optional, Dict, Any, List
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
class RunMacroRequest(BaseModel):
    macro_path: str  # Full path to .swp file
    module_name: Optional[str] = None  # VBA module name
    procedure_name: Optional[str] = "main"  # Procedure to run


class RunCodeRequest(BaseModel):
    code: str  # VBA code to execute
    language: str = "vba"  # vba, vsta


class BatchMacroRequest(BaseModel):
    macro_path: str
    files: List[str]  # List of files to process
    save_after: bool = True


router = APIRouter(prefix="/solidworks-macros", tags=["solidworks-macros"])


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
# Macro Execution
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


@router.get("/recording/status")
async def get_recording_status():
    """
    Check if macro recording is active.
    """
    try:
        sw = get_solidworks()

        is_recording = sw.GetMacroRecordingStatus() if hasattr(sw, 'GetMacroRecordingStatus') else False

        return {
            "is_recording": is_recording
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get recording status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/recording/start")
async def start_recording():
    """
    Start macro recording.
    """
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
    """
    Stop macro recording and optionally save.
    """
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
# Batch Macro Execution
# =============================================================================

@router.post("/batch")
async def batch_run_macro(request: BatchMacroRequest):
    """
    Run a macro on multiple files.
    """
    try:
        sw = get_solidworks()

        if not os.path.exists(request.macro_path):
            raise HTTPException(status_code=404, detail=f"Macro not found: {request.macro_path}")

        results = []
        for file_path in request.files:
            try:
                # Open file
                doc_type = 1  # Part
                if file_path.lower().endswith('.sldasm'):
                    doc_type = 2  # Assembly
                elif file_path.lower().endswith('.slddrw'):
                    doc_type = 3  # Drawing

                errors = 0
                warnings = 0
                doc = sw.OpenDoc6(
                    file_path, doc_type,
                    1, "", errors, warnings  # Silent mode
                )

                if doc:
                    # Run macro
                    macro_errors = 0
                    success = sw.RunMacro2(
                        request.macro_path, "", "main", 0, macro_errors
                    )

                    # Save if requested
                    if request.save_after and success:
                        doc.Save3(1, errors, warnings)

                    results.append({
                        "file": file_path,
                        "success": success,
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
        failed = len(results) - successful

        return {
            "macro": request.macro_path,
            "total_files": len(request.files),
            "successful": successful,
            "failed": failed,
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
# Macro Information
# =============================================================================

@router.get("/list")
async def list_recent_macros():
    """
    List recently used macros.
    """
    try:
        sw = get_solidworks()

        # Get recent macros from registry/settings
        # This is typically stored in user preferences

        return {
            "message": "Recent macros list - check SolidWorks Tools > Macro menu",
            "tip": "Use /run endpoint with full path to execute macros"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List macros failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/info/{macro_path:path}")
async def get_macro_info(macro_path: str):
    """
    Get information about a macro file.
    """
    try:
        if not os.path.exists(macro_path):
            raise HTTPException(status_code=404, detail=f"Macro not found: {macro_path}")

        # Get file info
        stat = os.stat(macro_path)

        return {
            "path": macro_path,
            "filename": os.path.basename(macro_path),
            "size_bytes": stat.st_size,
            "modified": stat.st_mtime,
            "extension": os.path.splitext(macro_path)[1].lower(),
            "type": "VBA Macro" if macro_path.lower().endswith('.swp') else "VSTA Macro"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get macro info failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Feature API Commands
# =============================================================================

@router.post("/command/{command_id}")
async def run_command(command_id: int):
    """
    Execute a SolidWorks command by ID.

    Common command IDs:
    - 31044: Rebuild
    - 31045: Force Rebuild
    - 31233: Save
    - 31238: Save As
    - 31340: Zoom to Fit
    - 24053: Measure
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
    """
    List common command IDs.
    """
    commands = {
        "file": {
            "new": 31031,
            "open": 31032,
            "save": 31233,
            "save_as": 31238,
            "close": 31034,
            "print": 31035
        },
        "edit": {
            "undo": 31001,
            "redo": 31002,
            "cut": 31003,
            "copy": 31004,
            "paste": 31005,
            "delete": 31006
        },
        "view": {
            "zoom_fit": 31340,
            "zoom_area": 31341,
            "zoom_in": 31342,
            "zoom_out": 31343,
            "rotate": 31350,
            "pan": 31351
        },
        "tools": {
            "rebuild": 31044,
            "force_rebuild": 31045,
            "measure": 24053,
            "check": 31212
        },
        "standard_views": {
            "front": 31324,
            "back": 31325,
            "left": 31326,
            "right": 31327,
            "top": 31328,
            "bottom": 31329,
            "isometric": 31330
        }
    }

    return commands


__all__ = ["router"]
