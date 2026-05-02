from fastapi import APIRouter, HTTPException

from db.violations import get_violations_for_system, individual_exists
from models.schemas import ViolationsResponse

router = APIRouter()


@router.get("/{system_name}", response_model=ViolationsResponse)
def get_violations(system_name: str):
    if not individual_exists(system_name):
        raise HTTPException(status_code=404, detail="System not found in graph")
    rows = get_violations_for_system(system_name)
    violated = [r["violated_principle"] for r in rows if r.get("violated_principle")]
    return ViolationsResponse(
        system=system_name,
        violated_principles=violated,
        violation_count=len(violated),
    )
