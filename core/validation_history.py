from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from core.database_adapter import get_db_adapter

logger = logging.getLogger("core.cad")
router = APIRouter()


class Validation(BaseModel):
    id: Optional[str] = None
    drawing: str
    status: str
    result: Dict


@router.get("/cad/validations/recent", response_model=List[Validation])
async def get_recent_validations():
    db = get_db_adapter()
    try:
        # For now, using a simple query in DatabaseAdapter or implementing a specific one
        # Let's assume DatabaseAdapter has a general query or we add get_recent_validations
        session = db.get_session()
        from core.database_adapter import ValidationModel

        validations = (
            session.query(ValidationModel)
            .order_by(ValidationModel.created_at.desc())
            .limit(10)
            .all()
        )

        results = []
        for v in validations:
            results.append(
                Validation(
                    id=v.id, drawing=v.file_path, status=v.status, result=v.errors or {}
                )
            )
        session.close()
        return results
    except Exception as e:
        logger.error(f"API Error fetching validations: {e}")
        return []


@router.get("/cad/validations/{validation_id}", response_model=Validation)
async def get_validation(validation_id: str):
    db = get_db_adapter()
    session = db.get_session()
    from core.database_adapter import ValidationModel

    v = (
        session.query(ValidationModel)
        .filter(ValidationModel.id == validation_id)
        .first()
    )
    if not v:
        session.close()
        raise HTTPException(status_code=404, detail="Validation not found")

    result = Validation(
        id=v.id, drawing=v.file_path, status=v.status, result=v.errors or {}
    )
    session.close()
    return result
