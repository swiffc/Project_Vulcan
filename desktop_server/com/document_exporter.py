"""
Document Exporter - COM Adapter
Export CAD documents to various formats (PDF, STEP, IGES, DXF, etc.).

Priority 2 API - Document Management (0% coverage)
Enables:
- "Export this to PDF"
- "Save as STEP file"
- "Batch export all parts to neutral formats"
"""

import logging
import os
from typing import List, Dict, Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("com.document_exporter")

router = APIRouter(prefix="/com/export", tags=["Document Export"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ExportRequest(BaseModel):
    """Request to export document."""
    format: str  # "pdf", "step", "iges", "dxf", "dwg", "stl", "parasolid"
    output_path: str
    options: Optional[Dict] = None


class BatchExportRequest(BaseModel):
    """Request to batch export multiple documents."""
    documents: List[str]  # List of file paths
    format: str
    output_directory: str
    options: Optional[Dict] = None


class ExportResponse(BaseModel):
    """Response from export operation."""
    success: bool
    output_file: str
    message: Optional[str] = None


class BatchExportResponse(BaseModel):
    """Response from batch export."""
    success: bool
    total: int
    succeeded: int
    failed: int
    results: List[Dict]


# ============================================================================
# SOLIDWORKS DOCUMENT EXPORTER
# ============================================================================

class SolidWorksExporter:
    """Export SolidWorks documents to various formats."""
    
    def __init__(self, sw_app=None):
        self.app = sw_app
        
        # SolidWorks export constants
        self.format_constants = {
            "pdf": 0,  # swSaveAsPDF
            "step": 650,  # swSaveAsSTEP
            "iges": 625,  # swSaveAsIGES
            "dxf": 620,  # swSaveAsDXF
            "dwg": 621,  # swSaveAsDWG
            "stl": 651,  # swSaveAsSTL
            "parasolid": 627,  # swSaveAsParasolid
            "acis": 623,  # swSaveAsACIS
        }
    
    def export_to_pdf(self, output_path: str, options: Optional[Dict] = None) -> str:
        """
        Export active document to PDF.
        
        Args:
            output_path: Output PDF file path
            options: PDF export options (e.g., {"include_3d": True})
        
        Returns:
            Path to exported PDF
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Get ModelDocExtension
        ext = model.Extension
        
        # Setup PDF export data
        export_data = self.app.GetExportFileData(0)  # PDF type
        
        # Apply options if provided
        if options:
            if options.get("include_3d"):
                export_data.SetSheets(0, -1)  # Export all sheets
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Export
        errors = 0
        warnings = 0
        success = model.Extension.SaveAs(
            output_path,
            0,  # swSaveAsCurrentVersion
            0,  # swSaveAsOptions_Silent
            export_data,
            errors,
            warnings
        )
        
        if not success:
            raise RuntimeError(f"PDF export failed (errors: {errors}, warnings: {warnings})")
        
        logger.info(f"Exported to PDF: {output_path}")
        return output_path
    
    def export_to_step(self, output_path: str, options: Optional[Dict] = None) -> str:
        """
        Export active document to STEP format.
        
        Args:
            output_path: Output STEP file path
            options: STEP export options
        
        Returns:
            Path to exported STEP file
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Export
        errors = 0
        warnings = 0
        success = model.SaveAs2(
            output_path,
            0,  # swSaveAsCurrentVersion
            True,  # Silent mode
            errors,
            warnings
        )
        
        if not success:
            raise RuntimeError(f"STEP export failed (errors: {errors}, warnings: {warnings})")
        
        logger.info(f"Exported to STEP: {output_path}")
        return output_path
    
    def export_to_iges(self, output_path: str, options: Optional[Dict] = None) -> str:
        """
        Export active document to IGES format.
        
        Args:
            output_path: Output IGES file path
            options: IGES export options
        
        Returns:
            Path to exported IGES file
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Export
        errors = 0
        warnings = 0
        success = model.SaveAs2(
            output_path,
            0,
            True,
            errors,
            warnings
        )
        
        if not success:
            raise RuntimeError(f"IGES export failed (errors: {errors}, warnings: {warnings})")
        
        logger.info(f"Exported to IGES: {output_path}")
        return output_path
    
    def export_to_dxf(self, output_path: str, options: Optional[Dict] = None) -> str:
        """Export drawing to DXF format."""
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        model = self.app.ActiveDoc
        if not model:
            raise ValueError("No active document")
        
        # Only works for drawings
        if model.GetType() != 3:  # swDocDRAWING
            raise ValueError("DXF export only available for drawings")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        errors = 0
        warnings = 0
        success = model.SaveAs2(output_path, 0, True, errors, warnings)
        
        if not success:
            raise RuntimeError(f"DXF export failed")
        
        logger.info(f"Exported to DXF: {output_path}")
        return output_path
    
    def batch_export(
        self,
        documents: List[str],
        format: str,
        output_dir: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Batch export multiple documents.
        
        Args:
            documents: List of document paths
            format: Export format
            output_dir: Output directory
            options: Export options
        
        Returns:
            Dictionary with export results
        """
        if not self.app:
            raise ValueError("SolidWorks not connected")
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        succeeded = 0
        failed = 0
        
        for doc_path in documents:
            try:
                # Open document
                doc_type = self._get_document_type(doc_path)
                errors = 0
                warnings = 0
                
                model = self.app.OpenDoc6(
                    doc_path,
                    doc_type,
                    0,  # swOpenDocOptions_Silent
                    "",
                    errors,
                    warnings
                )
                
                if not model:
                    raise ValueError(f"Failed to open: {doc_path}")
                
                # Generate output filename
                filename = Path(doc_path).stem
                ext = self._get_extension(format)
                output_path = os.path.join(output_dir, f"{filename}.{ext}")
                
                # Export based on format
                if format.lower() == "pdf":
                    self.export_to_pdf(output_path, options)
                elif format.lower() == "step":
                    self.export_to_step(output_path, options)
                elif format.lower() == "iges":
                    self.export_to_iges(output_path, options)
                elif format.lower() == "dxf":
                    self.export_to_dxf(output_path, options)
                else:
                    raise ValueError(f"Unsupported format: {format}")
                
                # Close document
                self.app.CloseDoc(doc_path)
                
                succeeded += 1
                results.append({
                    "input": doc_path,
                    "output": output_path,
                    "status": "success"
                })
                
            except Exception as e:
                failed += 1
                results.append({
                    "input": doc_path,
                    "output": None,
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"Failed to export {doc_path}: {e}")
        
        return {
            "total": len(documents),
            "succeeded": succeeded,
            "failed": failed,
            "results": results
        }
    
    def _get_document_type(self, filepath: str) -> int:
        """Get SolidWorks document type constant from file extension."""
        ext = Path(filepath).suffix.lower()
        if ext == ".sldprt":
            return 1  # swDocPART
        elif ext == ".sldasm":
            return 2  # swDocASSEMBLY
        elif ext == ".slddrw":
            return 3  # swDocDRAWING
        else:
            raise ValueError(f"Unknown document type: {ext}")
    
    def _get_extension(self, format: str) -> str:
        """Get file extension for export format."""
        extensions = {
            "pdf": "pdf",
            "step": "step",
            "iges": "iges",
            "dxf": "dxf",
            "dwg": "dwg",
            "stl": "stl",
            "parasolid": "x_t",
        }
        return extensions.get(format.lower(), format.lower())


# ============================================================================
# INVENTOR DOCUMENT EXPORTER
# ============================================================================

class InventorExporter:
    """Export Inventor documents to various formats."""
    
    def __init__(self, inv_app=None):
        self.app = inv_app
    
    def export_to_pdf(self, output_path: str, options: Optional[Dict] = None) -> str:
        """Export active document to PDF."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # SaveAs with PDF translator
        doc.SaveAs(output_path, True)  # SaveCopyAs
        
        logger.info(f"Exported to PDF: {output_path}")
        return output_path
    
    def export_to_step(self, output_path: str, options: Optional[Dict] = None) -> str:
        """Export active document to STEP."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as STEP
        doc.SaveAs(output_path, True)
        
        logger.info(f"Exported to STEP: {output_path}")
        return output_path
    
    def export_to_iges(self, output_path: str, options: Optional[Dict] = None) -> str:
        """Export active document to IGES."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        doc = self.app.ActiveDocument
        if not doc:
            raise ValueError("No active document")
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as IGES
        doc.SaveAs(output_path, True)
        
        logger.info(f"Exported to IGES: {output_path}")
        return output_path
    
    def batch_export(
        self,
        documents: List[str],
        format: str,
        output_dir: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """Batch export multiple documents."""
        if not self.app:
            raise ValueError("Inventor not connected")
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        succeeded = 0
        failed = 0
        
        for doc_path in documents:
            try:
                # Open document
                doc = self.app.Documents.Open(doc_path, True)  # Visible=True
                
                # Generate output filename
                filename = Path(doc_path).stem
                ext = self._get_extension(format)
                output_path = os.path.join(output_dir, f"{filename}.{ext}")
                
                # Export
                if format.lower() == "pdf":
                    self.export_to_pdf(output_path, options)
                elif format.lower() == "step":
                    self.export_to_step(output_path, options)
                elif format.lower() == "iges":
                    self.export_to_iges(output_path, options)
                else:
                    raise ValueError(f"Unsupported format: {format}")
                
                # Close document
                doc.Close(True)  # SkipSave=True
                
                succeeded += 1
                results.append({
                    "input": doc_path,
                    "output": output_path,
                    "status": "success"
                })
                
            except Exception as e:
                failed += 1
                results.append({
                    "input": doc_path,
                    "output": None,
                    "status": "failed",
                    "error": str(e)
                })
                logger.error(f"Failed to export {doc_path}: {e}")
        
        return {
            "total": len(documents),
            "succeeded": succeeded,
            "failed": failed,
            "results": results
        }
    
    def _get_extension(self, format: str) -> str:
        """Get file extension for export format."""
        extensions = {
            "pdf": "pdf",
            "step": "step",
            "iges": "iges",
            "dwg": "dwg",
            "dxf": "dxf",
        }
        return extensions.get(format.lower(), format.lower())


# ============================================================================
# FASTAPI ENDPOINTS
# ============================================================================

_sw_exporter: Optional[SolidWorksExporter] = None
_inv_exporter: Optional[InventorExporter] = None


def set_solidworks_app(sw_app):
    """Set SolidWorks application instance."""
    global _sw_exporter
    _sw_exporter = SolidWorksExporter(sw_app)


def set_inventor_app(inv_app):
    """Set Inventor application instance."""
    global _inv_exporter
    _inv_exporter = InventorExporter(inv_app)


@router.post("/pdf")
async def export_to_pdf(request: ExportRequest):
    """
    Export active document to PDF.
    
    Args:
        request: Export request with output path and options
    
    Returns:
        Export response with output file path
    """
    try:
        cad_system = request.options.get("cad_system", "solidworks") if request.options else "solidworks"
        
        if cad_system.lower() == "solidworks":
            if not _sw_exporter:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            output_file = _sw_exporter.export_to_pdf(request.output_path, request.options)
        else:
            if not _inv_exporter:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            output_file = _inv_exporter.export_to_pdf(request.output_path, request.options)
        
        return {
            "success": True,
            "output_file": output_file,
            "message": "Exported to PDF successfully"
        }
    
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/step")
async def export_to_step(request: ExportRequest):
    """Export active document to STEP format."""
    try:
        cad_system = request.options.get("cad_system", "solidworks") if request.options else "solidworks"
        
        if cad_system.lower() == "solidworks":
            if not _sw_exporter:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            output_file = _sw_exporter.export_to_step(request.output_path, request.options)
        else:
            if not _inv_exporter:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            output_file = _inv_exporter.export_to_step(request.output_path, request.options)
        
        return {
            "success": True,
            "output_file": output_file,
            "message": "Exported to STEP successfully"
        }
    
    except Exception as e:
        logger.error(f"STEP export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/iges")
async def export_to_iges(request: ExportRequest):
    """Export active document to IGES format."""
    try:
        cad_system = request.options.get("cad_system", "solidworks") if request.options else "solidworks"
        
        if cad_system.lower() == "solidworks":
            if not _sw_exporter:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            output_file = _sw_exporter.export_to_iges(request.output_path, request.options)
        else:
            if not _inv_exporter:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            output_file = _inv_exporter.export_to_iges(request.output_path, request.options)
        
        return {
            "success": True,
            "output_file": output_file,
            "message": "Exported to IGES successfully"
        }
    
    except Exception as e:
        logger.error(f"IGES export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_export(request: BatchExportRequest):
    """
    Batch export multiple documents to specified format.
    
    Args:
        request: Batch export request
    
    Returns:
        Batch export results
    """
    try:
        cad_system = request.options.get("cad_system", "solidworks") if request.options else "solidworks"
        
        if cad_system.lower() == "solidworks":
            if not _sw_exporter:
                raise HTTPException(status_code=503, detail="SolidWorks not connected")
            results = _sw_exporter.batch_export(
                request.documents,
                request.format,
                request.output_directory,
                request.options
            )
        else:
            if not _inv_exporter:
                raise HTTPException(status_code=503, detail="Inventor not connected")
            results = _inv_exporter.batch_export(
                request.documents,
                request.format,
                request.output_directory,
                request.options
            )
        
        return {
            "success": True,
            **results
        }
    
    except Exception as e:
        logger.error(f"Batch export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
