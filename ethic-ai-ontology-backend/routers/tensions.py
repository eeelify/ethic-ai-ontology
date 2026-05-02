from fastapi import APIRouter, HTTPException

from db.tensions import get_all_principle_conflicts, get_tensions_for_system
from db.violations import individual_exists
from models.schemas import TensionsResponse

router = APIRouter()


@router.get("/{system_name}", response_model=TensionsResponse)
def get_tensions(system_name: str):
    if not individual_exists(system_name):
        raise HTTPException(status_code=404, detail="System not found in graph")
    tension_rows = get_tensions_for_system(system_name)
    ethical = [r["tension"] for r in tension_rows if r.get("tension")]
    conflicts = get_all_principle_conflicts()
    principle_conflicts = [
        {"principle_1": r["principle_1"], "principle_2": r["principle_2"]}
        for r in conflicts
        if r.get("principle_1") is not None and r.get("principle_2") is not None
    ]
    return TensionsResponse(
        system=system_name,
        ethical_tensions=ethical,
        principle_conflicts=principle_conflicts,
    )
