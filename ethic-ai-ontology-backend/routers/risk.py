from fastapi import APIRouter, HTTPException

from db.risk import get_risk_by_system
from models.schemas import RiskResponse

router = APIRouter()


@router.get("/{system_name}", response_model=RiskResponse)
def get_risk(system_name: str):
    row = get_risk_by_system(system_name)
    if not row or not row.get("risk_level"):
        raise HTTPException(status_code=404, detail="System risk not found in graph")
    return RiskResponse(system=row["system"], risk_level=row["risk_level"])

