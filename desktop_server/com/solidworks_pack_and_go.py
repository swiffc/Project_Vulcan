"""
SolidWorks Pack and Go API
==========================
Pack and Go operations including:
- Create self-contained packages
- Include all references
- Flatten folder structure
- Archive creation
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
class PackAndGoRequest(BaseModel):
    output_folder: str
    flatten_to_single_folder: bool = True
    include_drawings: bool = True
    include_simulations: bool = False
    include_toolbox: bool = False
    add_prefix: Optional[str] = None
    add_suffix: Optional[str] = None


class AnalyzeReferencesRequest(BaseModel):
    file_path: Optional[str] = None  # None = active document


router = APIRouter(prefix="/solidworks-pack-and-go", tags=["solidworks-pack-and-go"])


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
# Pack and Go Operations
# =============================================================================

@router.post("/execute")
async def execute_pack_and_go(request: PackAndGoRequest):
    """
    Execute Pack and Go on the active document.
    Creates a self-contained copy with all references.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Create output folder if needed
        if not os.path.exists(request.output_folder):
            os.makedirs(request.output_folder)

        # Get Pack and Go object
        pag = doc.Extension.GetPackAndGo()
        if not pag:
            raise HTTPException(status_code=500, detail="Could not create Pack and Go")

        # Configure options
        pag.FlattenToSingleFolder = request.flatten_to_single_folder
        pag.IncludeDrawings = request.include_drawings
        pag.IncludeSimulationResults = request.include_simulations
        pag.IncludeToolboxComponents = request.include_toolbox

        if request.add_prefix:
            pag.AddPrefix = request.add_prefix

        if request.add_suffix:
            pag.AddSuffix = request.add_suffix

        # Set destination
        pag.SetSaveToName(True, request.output_folder)

        # Get document names that will be copied
        doc_names = pag.GetDocumentNames()
        save_names = pag.GetDocumentSaveToNames()

        # Execute Pack and Go
        statuses = pag.Save()

        # Check results
        success_count = 0
        failed_count = 0
        results = []

        if statuses and doc_names:
            for i in range(len(statuses)):
                if statuses[i] == 0:
                    success_count += 1
                else:
                    failed_count += 1

                results.append({
                    "source": doc_names[i] if i < len(doc_names) else None,
                    "destination": save_names[i] if save_names and i < len(save_names) else None,
                    "status": "success" if statuses[i] == 0 else f"error_{statuses[i]}"
                })

        return {
            "success": failed_count == 0,
            "output_folder": request.output_folder,
            "total_files": len(statuses) if statuses else 0,
            "successful": success_count,
            "failed": failed_count,
            "options": {
                "flatten": request.flatten_to_single_folder,
                "include_drawings": request.include_drawings,
                "prefix": request.add_prefix,
                "suffix": request.add_suffix
            },
            "files": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pack and Go failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.get("/preview")
async def preview_pack_and_go():
    """
    Preview what files will be included in Pack and Go.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        pag = doc.Extension.GetPackAndGo()
        if not pag:
            raise HTTPException(status_code=500, detail="Could not create Pack and Go")

        # Get document names
        doc_names = pag.GetDocumentNames()

        files = []
        if doc_names:
            for name in doc_names:
                file_ext = os.path.splitext(name)[1].lower()
                file_type = "part" if file_ext == ".sldprt" else (
                    "assembly" if file_ext == ".sldasm" else (
                        "drawing" if file_ext == ".slddrw" else "other"
                    )
                )
                files.append({
                    "path": name,
                    "filename": os.path.basename(name),
                    "type": file_type,
                    "exists": os.path.exists(name)
                })

        # Count by type
        type_counts = {}
        for f in files:
            t = f["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total_files": len(files),
            "by_type": type_counts,
            "files": files
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Reference Analysis
# =============================================================================

@router.get("/references")
async def analyze_references():
    """
    Analyze all references in the active document.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        references = []

        if doc.GetType() == 2:  # Assembly
            # Get all component references
            components = doc.GetComponents(False)  # Include sub-assemblies
            if components:
                for comp in components:
                    try:
                        path = comp.GetPathName()
                        references.append({
                            "name": comp.Name,
                            "path": path,
                            "exists": os.path.exists(path) if path else False,
                            "suppressed": comp.IsSuppressed(),
                            "type": "component"
                        })
                    except Exception:
                        pass

        elif doc.GetType() == 3:  # Drawing
            # Get view references
            sheets = doc.GetViews()
            if sheets:
                for sheet in sheets:
                    if sheet:
                        for view in sheet[1:]:  # Skip sheet itself
                            try:
                                ref_doc = view.ReferencedDocument
                                if ref_doc:
                                    references.append({
                                        "view": view.Name,
                                        "path": ref_doc.GetPathName(),
                                        "type": "drawing_view"
                                    })
                            except Exception:
                                pass

        # Check for missing references
        missing = [r for r in references if not r.get("exists", True)]

        return {
            "document": doc.GetTitle(),
            "document_type": ["Part", "Assembly", "Drawing"][doc.GetType() - 1],
            "total_references": len(references),
            "missing_count": len(missing),
            "references": references,
            "missing": missing
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analyze references failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


@router.post("/fix-missing")
async def fix_missing_references(search_folders: List[str]):
    """
    Attempt to fix missing references by searching in specified folders.
    """
    try:
        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        fixed = []
        not_found = []

        # Get dependencies
        deps = doc.GetDependencies2(True, True, False)

        if deps:
            for dep in deps:
                if not os.path.exists(dep):
                    filename = os.path.basename(dep)

                    # Search for file
                    found_path = None
                    for folder in search_folders:
                        potential = os.path.join(folder, filename)
                        if os.path.exists(potential):
                            found_path = potential
                            break

                        # Also check subfolders
                        for root, dirs, files in os.walk(folder):
                            if filename in files:
                                found_path = os.path.join(root, filename)
                                break

                    if found_path:
                        fixed.append({
                            "original": dep,
                            "found_at": found_path
                        })
                    else:
                        not_found.append(dep)

        return {
            "fixed_count": len(fixed),
            "not_found_count": len(not_found),
            "fixed": fixed,
            "not_found": not_found,
            "message": f"Found {len(fixed)} files, {len(not_found)} still missing"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fix references failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Archive Operations
# =============================================================================

@router.post("/create-zip")
async def create_zip_archive(output_path: str, include_drawings: bool = True):
    """
    Create a ZIP archive of the document and all references.
    """
    try:
        import zipfile
        import tempfile

        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        # Create temp folder for pack and go
        with tempfile.TemporaryDirectory() as temp_dir:
            pag = doc.Extension.GetPackAndGo()
            if not pag:
                raise HTTPException(status_code=500, detail="Could not create Pack and Go")

            pag.FlattenToSingleFolder = True
            pag.IncludeDrawings = include_drawings
            pag.SetSaveToName(True, temp_dir)

            # Execute pack and go
            statuses = pag.Save()

            # Create ZIP
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, temp_dir)
                        zf.write(file_path, arc_name)

            # Get ZIP info
            zip_size = os.path.getsize(output_path)

        return {
            "success": True,
            "output_path": output_path,
            "size_bytes": zip_size,
            "size_mb": round(zip_size / (1024 * 1024), 2)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create ZIP failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


# =============================================================================
# Copy Tree
# =============================================================================

@router.post("/copy-tree")
async def copy_tree(output_folder: str, preserve_folder_structure: bool = True):
    """
    Copy entire document tree maintaining folder structure.
    """
    try:
        import shutil

        sw = get_solidworks()
        doc = sw.ActiveDoc
        if not doc:
            raise HTTPException(status_code=404, detail="No document open")

        pag = doc.Extension.GetPackAndGo()
        if not pag:
            raise HTTPException(status_code=500, detail="Could not create Pack and Go")

        pag.FlattenToSingleFolder = not preserve_folder_structure
        pag.SetSaveToName(True, output_folder)

        # Get the source root folder
        source_folder = os.path.dirname(doc.GetPathName())

        # Execute
        statuses = pag.Save()

        success_count = sum(1 for s in statuses if s == 0) if statuses else 0

        return {
            "success": True,
            "source_folder": source_folder,
            "output_folder": output_folder,
            "preserve_structure": preserve_folder_structure,
            "files_copied": success_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Copy tree failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pythoncom.CoUninitialize()


__all__ = ["router"]
