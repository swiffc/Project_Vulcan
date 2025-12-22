from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid

router = APIRouter()

class Validation(BaseModel):
    id: Optional[str] = None
    drawing: str
    status: str
    result: Dict

# In-memory database
db: Dict[str, Validation] = {}

@router.get("/cad/validations/recent", response_model=List[Validation])
async def get_recent_validations():
    return list(db.values())

@router.get("/cad/validations/{validation_id}", response_model=Validation)
async def get_validation(validation_id: str):
    if validation_id not in db:
        raise HTTPException(status_code=404, detail="Validation not found")
    return db[validation_id]
