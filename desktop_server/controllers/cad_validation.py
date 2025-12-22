"""
CAD Validation Controller

FastAPI router for CAD validation endpoints.
Integrates ValidationOrchestrator with REST API.
"""

import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Import validation system with graceful fallback
try:
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    from agents.cad_agent.validators import (
        ValidationOrchestrator,
        ValidationRequest,
        ValidationReport,
        ValidationStatus,
    )
    VALIDATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Validation system not available: {e}")
    VALIDATION_AVAILABLE = False
    ValidationOrchestrator = None

router = APIRouter(prefix="/cad/validate", tags=["CAD Validation"])

# Global orchestrator instance
_orchestrator: Optional[ValidationOrchestrator] = None


def get_orchestrator() -> ValidationOrchestrator:
    """Get or create the global validation orchestrator."""
    global _orchestrator
    
    if not VALIDATION_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Validation system not available - install required dependencies"
        )
    
    if _orchestrator is None:
        _orchestrator = ValidationOrchestrator()
        logger.info("ValidationOrchestrator initialized")
    
    return _orchestrator


class ValidateDrawingRequest(BaseModel):
    """Request to validate a drawing."""
    
    file_id: Optional[str] = None
    checks: list[str] = ["all"]
    severity: str = "all"
    user_id: str = "anonymous"
    project_id: Optional[str] = None


class ValidateDrawingResponse(BaseModel):
    """Response from drawing validation."""
    
    request_id: str
    status: str
    report: Optional[dict] = None
    duration_ms: int = 0
    message: str = ""


@router.post("/drawing")
async def validate_drawing(
    file: Optional[UploadFile] = File(None),
    file_id: Optional[str] = Form(None),
    checks: str = Form('["all"]'),
    severity: str = Form("all"),
    user_id: str = Form("anonymous"),
    project_id: Optional[str] = Form(None),
) -> ValidateDrawingResponse:
    """
    Validate a CAD drawing.
    
    Accepts either:
    - file: Upload PDF/DXF drawing
    - file_id: Reference to existing file
    
    Returns comprehensive validation report.
    """
    orchestrator = get_orchestrator()
    
    # Parse checks JSON
    import json
    try:
        checks_list = json.loads(checks)
    except:
        checks_list = ["all"]
    
    # Handle file upload
    file_path = None
    if file:
        # Save uploaded file temporarily
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "vulcan_validations"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = temp_dir / f"{uuid.uuid4()}_{file.filename}"
        
        try:
            content = await file.read()
            temp_file.write_bytes(content)
            file_path = str(temp_file)
            logger.info(f"Uploaded file saved to {file_path}")
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")
    
    elif file_id:
        # Use existing file
        file_path = file_id
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'file' or 'file_id' must be provided"
        )
    
    # Create validation request
    request = ValidationRequest(
        type="drawing",
        file_path=file_path,
        checks=checks_list,
        severity=severity,
        user_id=user_id,
        project_id=project_id,
    )
    
    try:
        # Run validation
        logger.info(f"Starting validation for {file_path}")
        report = await orchestrator.validate(request)
        
        # Convert to response
        return ValidateDrawingResponse(
            request_id=report.request_id,
            status=report.status.value,
            report=report.dict(),
            duration_ms=report.duration_ms,
            message=f"Validation complete: {report.pass_rate:.1f}% pass rate",
        )
    
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/ache")
async def validate_ache(
    file: Optional[UploadFile] = File(None),
    file_id: Optional[str] = Form(None),
    user_id: str = Form("anonymous"),
    project_id: Optional[str] = Form(None),
) -> ValidateDrawingResponse:
    """
    Run full 130-point ACHE validation.
    
    Comprehensive validation including:
    - GD&T compliance
    - Welding standards (AWS D1.1)
    - Material specifications
    - ACHE master checklist
    """
    orchestrator = get_orchestrator()
    
    # Handle file upload (same logic as validate_drawing)
    file_path = None
    if file:
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "vulcan_validations"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = temp_dir / f"{uuid.uuid4()}_{file.filename}"
        
        try:
            content = await file.read()
            temp_file.write_bytes(content)
            file_path = str(temp_file)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")
    
    elif file_id:
        file_path = file_id
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'file' or 'file_id' must be provided"
        )
    
    # Create ACHE validation request
    request = ValidationRequest(
        type="ache",
        file_path=file_path,
        checks=["ache"],  # ACHE includes all checks
        user_id=user_id,
        project_id=project_id,
    )
    
    try:
        # Run validation
        logger.info(f"Starting ACHE validation for {file_path}")
        report = await orchestrator.validate(request)
        
        return ValidateDrawingResponse(
            request_id=report.request_id,
            status=report.status.value,
            report=report.dict(),
            duration_ms=report.duration_ms,
            message=f"ACHE validation complete: {report.ache_results.passed}/130 checks passed" if report.ache_results else "ACHE validation complete",
        )
    
    except Exception as e:
        logger.error(f"ACHE validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"ACHE validation failed: {str(e)}"
        )


@router.get("/status")
async def validation_status():
    """Get validation system status."""
    if not VALIDATION_AVAILABLE:
        return {
            "available": False,
            "message": "Validation system not installed"
        }
    
    orchestrator = get_orchestrator()
    
    return {
        "available": True,
        "validators": {
            "gdt_parser": orchestrator.gdt_parser is not None,
            "welding_validator": orchestrator.welding_validator is not None,
            "material_validator": orchestrator.material_validator is not None,
            "ache_validator": orchestrator.ache_validator is not None,
        },
        "message": "Validation system ready"
    }


# Export router
__all__ = ["router"]
