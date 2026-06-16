from typing import List

from fastapi import APIRouter

from db.systems import get_all_systems
from models.schemas import SystemResponse

router = APIRouter()


@router.get("", response_model=List[SystemResponse])
def list_systems():
    rows = get_all_systems()
    return [
        SystemResponse(
            name=row["name"],
            composite_risk_score=row.get("composite_risk_score"),
            risk_level=row.get("risk_level")
        )
        for row in rows
    ]

