"""
SolidWorks PDM Integration
==========================
Interface to SOLIDWORKS PDM Professional (formerly Enterprise PDM)
for vault operations, version control, and workflow management.

Phase 26 - PDM/Vault Integration
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum, IntEnum
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# COM imports
try:
    import win32com.client
    import pythoncom
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False


router = APIRouter(prefix="/solidworks-pdm", tags=["solidworks-pdm"])


# =============================================================================
# Enumerations
# =============================================================================

class FileState(IntEnum):
    """PDM file states."""
    CHECKED_IN = 0
    CHECKED_OUT_BY_ME = 1
    CHECKED_OUT_BY_OTHER = 2
    NOT_IN_VAULT = 3


class LockType(IntEnum):
    """File lock types."""
    NONE = 0
    READ_ONLY = 1
    CHECKED_OUT = 2


class TransitionType(IntEnum):
    """Workflow transition types."""
    AUTOMATIC = 0
    MANUAL = 1
    PARALLEL = 2


# =============================================================================
# Request Models
# =============================================================================

class VaultLoginRequest(BaseModel):
    """Request to log into PDM vault."""
    vault_name: str
    username: Optional[str] = None  # Uses Windows auth if None
    password: Optional[str] = None


class FileOperationRequest(BaseModel):
    """Request for file operations."""
    file_path: str  # Path within vault
    comment: Optional[str] = None


class CheckOutRequest(BaseModel):
    """Request to check out files."""
    file_paths: List[str]
    get_latest: bool = True


class CheckInRequest(BaseModel):
    """Request to check in files."""
    file_paths: List[str]
    comment: str = "Checked in via API"
    keep_checked_out: bool = False


class GetVersionRequest(BaseModel):
    """Request to get specific version."""
    file_path: str
    version: Optional[int] = None  # Latest if None


class SearchRequest(BaseModel):
    """Request to search vault."""
    search_term: str
    search_in: str = "all"  # "filename", "description", "all"
    file_extension: Optional[str] = None
    folder_path: Optional[str] = None
    include_subfolders: bool = True
    max_results: int = 100


class WorkflowRequest(BaseModel):
    """Request for workflow transition."""
    file_paths: List[str]
    transition_name: str
    comment: Optional[str] = None


class VariableRequest(BaseModel):
    """Request to get/set data card variables."""
    file_path: str
    variables: Optional[Dict[str, str]] = None  # Set if provided


class BOMRequest(BaseModel):
    """Request to get BOM from PDM."""
    file_path: str
    bom_type: str = "indented"  # "flat", "indented", "top_level"
    include_purchased: bool = True


# =============================================================================
# Global State
# =============================================================================

_vault = None
_vault_name = None


def get_vault(vault_name: Optional[str] = None):
    """Get or create PDM vault connection."""
    global _vault, _vault_name

    if not COM_AVAILABLE:
        raise HTTPException(status_code=501, detail="COM not available")

    if _vault is not None and (vault_name is None or vault_name == _vault_name):
        return _vault

    try:
        pythoncom.CoInitialize()

        # Create vault interface
        vault_factory = win32com.client.Dispatch("ConisioLib.EdmVault")

        if vault_name:
            # Login to specified vault
            vault_factory.LoginAuto(vault_name, 0)  # 0 = current window
            _vault_name = vault_name
        else:
            # Get default vault
            vault_factory.LoginAuto("", 0)
            _vault_name = vault_factory.Name

        _vault = vault_factory
        return _vault

    except Exception as e:
        logger.error(f"Failed to connect to PDM vault: {e}")
        raise HTTPException(status_code=500, detail=f"PDM connection failed: {e}")


# =============================================================================
# Connection Endpoints
# =============================================================================

@router.get("/status")
async def get_pdm_status() -> Dict[str, Any]:
    """
    Check PDM availability and connection status.
    """
    try:
        pdm_available = False
        vault_name = None
        user_name = None

        try:
            pythoncom.CoInitialize()
            vault_factory = win32com.client.Dispatch("ConisioLib.EdmVault")
            pdm_available = True

            if _vault is not None:
                vault_name = _vault.Name
                user_name = _vault.CurrentUserName
        except Exception:
            pass

        return {
            "pdm_available": pdm_available,
            "connected": _vault is not None,
            "vault_name": vault_name,
            "user": user_name,
            "message": "PDM ready" if pdm_available else "Install SOLIDWORKS PDM client",
        }

    except Exception as e:
        logger.error(f"PDM status error: {e}")
        return {"pdm_available": False, "error": str(e)}


@router.post("/login")
async def login_vault(request: VaultLoginRequest) -> Dict[str, Any]:
    """
    Log into a PDM vault.
    """
    try:
        global _vault, _vault_name

        pythoncom.CoInitialize()
        vault = win32com.client.Dispatch("ConisioLib.EdmVault")

        if request.username and request.password:
            # Explicit credentials
            vault.Login(request.username, request.password, request.vault_name)
        else:
            # Windows authentication
            vault.LoginAuto(request.vault_name, 0)

        _vault = vault
        _vault_name = request.vault_name

        return {
            "success": True,
            "vault_name": vault.Name,
            "user": vault.CurrentUserName,
            "root_folder": vault.RootFolderPath,
        }

    except Exception as e:
        logger.error(f"PDM login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout_vault() -> Dict[str, Any]:
    """
    Log out of PDM vault.
    """
    global _vault, _vault_name

    if _vault:
        try:
            _vault.Logout()
        except Exception:
            pass
        _vault = None
        _vault_name = None

    return {"success": True, "message": "Logged out"}


@router.get("/vaults")
async def list_available_vaults() -> Dict[str, Any]:
    """
    List available PDM vaults on this machine.
    """
    try:
        pythoncom.CoInitialize()

        # Get vault views
        views = win32com.client.Dispatch("ConisioLib.EdmViewInfo")
        vault_list = []

        # Enumerate registered vaults
        try:
            views.GetVaultViews()
            for i in range(views.Count):
                view = views.Item(i)
                vault_list.append({
                    "name": view.VaultName,
                    "path": view.RootFolder,
                })
        except Exception:
            pass

        return {
            "success": True,
            "vaults": vault_list,
        }

    except Exception as e:
        logger.error(f"List vaults error: {e}")
        return {"success": False, "error": str(e), "vaults": []}


# =============================================================================
# File Operations
# =============================================================================

@router.post("/checkout")
async def checkout_files(request: CheckOutRequest) -> Dict[str, Any]:
    """
    Check out files from vault.
    """
    try:
        vault = get_vault()
        results = []

        for file_path in request.file_paths:
            try:
                # Get file from vault
                file = vault.GetFileFromPath(file_path)

                if file:
                    folder_id = file.ParentFolderID

                    # Get latest if requested
                    if request.get_latest:
                        file.GetFileCopy(folder_id, 0)

                    # Check out
                    file.LockFile(folder_id, 0, 0)  # EdmLock_Simple

                    results.append({
                        "path": file_path,
                        "success": True,
                        "local_path": file.GetLocalPath(folder_id),
                    })
                else:
                    results.append({
                        "path": file_path,
                        "success": False,
                        "error": "File not found in vault",
                    })

            except Exception as e:
                results.append({
                    "path": file_path,
                    "success": False,
                    "error": str(e),
                })

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count == len(request.file_paths),
            "checked_out": success_count,
            "total": len(request.file_paths),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkin")
async def checkin_files(request: CheckInRequest) -> Dict[str, Any]:
    """
    Check in files to vault.
    """
    try:
        vault = get_vault()
        results = []

        for file_path in request.file_paths:
            try:
                file = vault.GetFileFromPath(file_path)

                if file:
                    folder_id = file.ParentFolderID

                    # Determine unlock flags
                    flags = 0
                    if request.keep_checked_out:
                        flags = 2  # EdmUnlock_KeepLock

                    # Check in
                    file.UnlockFile(folder_id, request.comment, flags)

                    results.append({
                        "path": file_path,
                        "success": True,
                        "new_version": file.CurrentVersion,
                    })
                else:
                    results.append({
                        "path": file_path,
                        "success": False,
                        "error": "File not found",
                    })

            except Exception as e:
                results.append({
                    "path": file_path,
                    "success": False,
                    "error": str(e),
                })

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count == len(request.file_paths),
            "checked_in": success_count,
            "total": len(request.file_paths),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Checkin error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-latest")
async def get_latest_version(request: FileOperationRequest) -> Dict[str, Any]:
    """
    Get latest version of a file from vault.
    """
    try:
        vault = get_vault()
        file = vault.GetFileFromPath(request.file_path)

        if not file:
            return {"success": False, "error": "File not found"}

        folder_id = file.ParentFolderID

        # Get file copy
        file.GetFileCopy(folder_id, 0)

        return {
            "success": True,
            "file_path": request.file_path,
            "local_path": file.GetLocalPath(folder_id),
            "version": file.CurrentVersion,
        }

    except Exception as e:
        logger.error(f"Get latest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file-info")
async def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a file in the vault.
    """
    try:
        vault = get_vault()
        file = vault.GetFileFromPath(file_path)

        if not file:
            return {"success": False, "error": "File not found"}

        folder_id = file.ParentFolderID

        # Determine state
        state = FileState.NOT_IN_VAULT
        locked_by = None

        if file.IsLocked:
            if file.LockedByUserID == vault.CurrentUserID:
                state = FileState.CHECKED_OUT_BY_ME
            else:
                state = FileState.CHECKED_OUT_BY_OTHER
                locked_by = file.LockedByUserName
        else:
            state = FileState.CHECKED_IN

        return {
            "success": True,
            "file_path": file_path,
            "file_id": file.ID,
            "current_version": file.CurrentVersion,
            "state": state.name,
            "locked_by": locked_by,
            "local_path": file.GetLocalPath(folder_id),
            "has_local_copy": file.HasLocalCopy(folder_id),
        }

    except Exception as e:
        logger.error(f"File info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Version History
# =============================================================================

@router.get("/history")
async def get_file_history(file_path: str, limit: int = 20) -> Dict[str, Any]:
    """
    Get version history of a file.
    """
    try:
        vault = get_vault()
        file = vault.GetFileFromPath(file_path)

        if not file:
            return {"success": False, "error": "File not found"}

        history = []
        version = file.GetFirstVersion()

        count = 0
        while version and count < limit:
            history.append({
                "version": version.VersionNo,
                "comment": version.Comment,
                "created_by": version.CreateUserName,
                "created_date": str(version.CreateDate),
            })

            version = version.GetNextVersion()
            count += 1

        return {
            "success": True,
            "file_path": file_path,
            "current_version": file.CurrentVersion,
            "history_count": len(history),
            "history": history,
        }

    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-version")
async def get_specific_version(request: GetVersionRequest) -> Dict[str, Any]:
    """
    Get a specific version of a file.
    """
    try:
        vault = get_vault()
        file = vault.GetFileFromPath(request.file_path)

        if not file:
            return {"success": False, "error": "File not found"}

        folder_id = file.ParentFolderID

        if request.version:
            # Get specific version
            file.GetFileCopy(folder_id, request.version)
            version = request.version
        else:
            # Get latest
            file.GetFileCopy(folder_id, 0)
            version = file.CurrentVersion

        return {
            "success": True,
            "file_path": request.file_path,
            "version": version,
            "local_path": file.GetLocalPath(folder_id),
        }

    except Exception as e:
        logger.error(f"Get version error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Search
# =============================================================================

@router.post("/search")
async def search_vault(request: SearchRequest) -> Dict[str, Any]:
    """
    Search for files in the vault.
    """
    try:
        vault = get_vault()

        # Create search
        search = vault.CreateSearch()

        # Set search criteria
        if request.search_in == "filename":
            search.FileName = f"*{request.search_term}*"
        else:
            search.SearchTerm = request.search_term

        if request.file_extension:
            search.FileName = f"*.{request.file_extension}"

        if request.folder_path:
            folder = vault.GetFolderFromPath(request.folder_path)
            if folder:
                search.SetFolderID(folder.ID)

        search.FindSubfolders = request.include_subfolders

        # Execute search
        search.FindFiles()

        results = []
        pos = search.GetFirstPosition()

        while pos and len(results) < request.max_results:
            file = search.GetNextFile(pos)
            if file:
                results.append({
                    "name": file.Name,
                    "path": file.GetFilePath(file.ParentFolderID),
                    "version": file.CurrentVersion,
                })
            pos = search.GetNextPosition(pos)

        return {
            "success": True,
            "search_term": request.search_term,
            "result_count": len(results),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Folder Operations
# =============================================================================

@router.get("/folder/contents")
async def get_folder_contents(folder_path: str = "/") -> Dict[str, Any]:
    """
    Get contents of a vault folder.
    """
    try:
        vault = get_vault()

        if folder_path == "/":
            folder = vault.RootFolder
        else:
            folder = vault.GetFolderFromPath(folder_path)

        if not folder:
            return {"success": False, "error": "Folder not found"}

        # Get files
        files = []
        pos = folder.GetFirstFile()
        while pos:
            file = folder.GetNextFile(pos)
            if file:
                files.append({
                    "name": file.Name,
                    "version": file.CurrentVersion,
                    "is_locked": file.IsLocked,
                })
            pos = folder.GetNextFilePosition(pos)

        # Get subfolders
        subfolders = []
        pos = folder.GetFirstSubFolder()
        while pos:
            subfolder = folder.GetNextSubFolder(pos)
            if subfolder:
                subfolders.append({
                    "name": subfolder.Name,
                    "path": subfolder.LocalPath,
                })
            pos = folder.GetNextSubFolderPosition(pos)

        return {
            "success": True,
            "folder_path": folder_path,
            "file_count": len(files),
            "subfolder_count": len(subfolders),
            "files": files,
            "subfolders": subfolders,
        }

    except Exception as e:
        logger.error(f"Folder contents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Data Card Variables
# =============================================================================

@router.post("/variables")
async def manage_variables(request: VariableRequest) -> Dict[str, Any]:
    """
    Get or set data card variables for a file.
    """
    try:
        vault = get_vault()
        file = vault.GetFileFromPath(request.file_path)

        if not file:
            return {"success": False, "error": "File not found"}

        folder_id = file.ParentFolderID

        if request.variables:
            # Set variables
            for name, value in request.variables.items():
                file.SetEnvVariable(name, folder_id, value)

            return {
                "success": True,
                "operation": "set",
                "file_path": request.file_path,
                "variables_set": list(request.variables.keys()),
            }
        else:
            # Get variables
            variables = {}

            # Get all variable names
            var_mgr = vault.VariableManager
            if var_mgr:
                pos = var_mgr.GetFirstPosition()
                while pos:
                    var = var_mgr.GetNextVariable(pos)
                    if var:
                        value = file.GetEnvVariableValue(var.Name, folder_id)
                        if value:
                            variables[var.Name] = value
                    pos = var_mgr.GetNextPosition(pos)

            return {
                "success": True,
                "operation": "get",
                "file_path": request.file_path,
                "variables": variables,
            }

    except Exception as e:
        logger.error(f"Variables error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Workflow
# =============================================================================

@router.get("/workflow/state")
async def get_workflow_state(file_path: str) -> Dict[str, Any]:
    """
    Get current workflow state of a file.
    """
    try:
        vault = get_vault()
        file = vault.GetFileFromPath(file_path)

        if not file:
            return {"success": False, "error": "File not found"}

        # Get workflow state
        state_id = file.CurrentWorkflowStateID
        state = vault.GetWorkflowState(state_id)

        transitions = []
        if state:
            # Get available transitions
            trans_count = state.TransitionCount
            for i in range(trans_count):
                trans = state.GetTransition(i)
                if trans:
                    transitions.append({
                        "name": trans.Name,
                        "target_state": trans.ToStateID,
                    })

        return {
            "success": True,
            "file_path": file_path,
            "current_state": state.Name if state else "Unknown",
            "state_id": state_id,
            "available_transitions": transitions,
        }

    except Exception as e:
        logger.error(f"Workflow state error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/transition")
async def perform_transition(request: WorkflowRequest) -> Dict[str, Any]:
    """
    Perform workflow transition on files.
    """
    try:
        vault = get_vault()
        results = []

        for file_path in request.file_paths:
            try:
                file = vault.GetFileFromPath(file_path)

                if file:
                    folder_id = file.ParentFolderID

                    # Find transition by name
                    state = vault.GetWorkflowState(file.CurrentWorkflowStateID)
                    trans_id = None

                    if state:
                        for i in range(state.TransitionCount):
                            trans = state.GetTransition(i)
                            if trans and trans.Name == request.transition_name:
                                trans_id = trans.ID
                                break

                    if trans_id:
                        # Execute transition
                        file.ChangeState(trans_id, folder_id, request.comment or "", 0)

                        results.append({
                            "path": file_path,
                            "success": True,
                            "transition": request.transition_name,
                        })
                    else:
                        results.append({
                            "path": file_path,
                            "success": False,
                            "error": f"Transition '{request.transition_name}' not found",
                        })
                else:
                    results.append({
                        "path": file_path,
                        "success": False,
                        "error": "File not found",
                    })

            except Exception as e:
                results.append({
                    "path": file_path,
                    "success": False,
                    "error": str(e),
                })

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count == len(request.file_paths),
            "transitioned": success_count,
            "total": len(request.file_paths),
            "results": results,
        }

    except Exception as e:
        logger.error(f"Transition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# BOM Operations
# =============================================================================

@router.post("/bom")
async def get_pdm_bom(request: BOMRequest) -> Dict[str, Any]:
    """
    Get Bill of Materials from PDM for an assembly.
    """
    try:
        vault = get_vault()
        file = vault.GetFileFromPath(request.file_path)

        if not file:
            return {"success": False, "error": "File not found"}

        # Get BOM
        bom_mgr = file.GetBOM()

        if not bom_mgr:
            return {"success": False, "error": "Cannot get BOM - ensure file is an assembly"}

        # Set BOM type
        bom_type_map = {
            "flat": 0,
            "indented": 1,
            "top_level": 2,
        }
        bom_type = bom_type_map.get(request.bom_type, 1)

        items = []
        row = bom_mgr.GetFirstRow(bom_type)

        while row:
            item = {
                "level": row.Level,
                "part_number": row.PartNumber,
                "description": row.Description,
                "quantity": row.Quantity,
                "file_path": row.FilePath,
            }

            # Get custom variables
            for var_name in ["Material", "Weight", "Vendor"]:
                try:
                    value = row.GetVar(var_name)
                    if value:
                        item[var_name.lower()] = value
                except Exception:
                    pass

            items.append(item)
            row = bom_mgr.GetNextRow()

        return {
            "success": True,
            "file_path": request.file_path,
            "bom_type": request.bom_type,
            "item_count": len(items),
            "items": items,
        }

    except Exception as e:
        logger.error(f"BOM error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Export
# =============================================================================

PDM_AVAILABLE = COM_AVAILABLE

__all__ = [
    "router",
    "PDM_AVAILABLE",
    "FileState",
    "LockType",
]
