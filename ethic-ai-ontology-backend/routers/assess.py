from fastapi import APIRouter, HTTPException

from db.profile import get_full_profile
from db.regulations import get_regulations_for_system
from models.schemas import AssessRequest, AssessResponse, ERCLevel

router = APIRouter()


def _erc_level(score: int) -> ERCLevel:
    if score >= 10:
        return ERCLevel.CRITICAL
    if score >= 6:
        return ERCLevel.HIGH
    if score >= 3:
        return ERCLevel.MEDIUM
    return ERCLevel.LOW


@router.post("", response_model=AssessResponse)
def assess(body: AssessRequest):
    system_name = (body.system_name or "").strip()
    if not system_name:
        raise HTTPException(status_code=422, detail="system_name is required")

    profile = get_full_profile(system_name)
    if not profile or not profile.get("system"):
        raise HTTPException(status_code=404, detail="System not found in graph")

    violated_principles = profile.get("violated_principles") or []
    ethical_tensions = profile.get("ethical_tensions") or []
    requirements = profile.get("requirements") or []

    v_count = len(violated_principles)
    t_count = len(ethical_tensions)
    r_count = len(requirements)
    erc_score = v_count * 3 + t_count * 2 + r_count * 1
    erc_lvl = _erc_level(erc_score)

    reg_rows = get_regulations_for_system(system_name)
    regulations = [row["regulation"] for row in reg_rows if row.get("regulation")]

    sector = profile.get("sector") or "unspecified-sector"
    risk_level = profile.get("risk_level") or "unknown"

    summary = (
        f"{profile['system']} is a {sector} AI system with {risk_level} risk. "
        f"It violates {v_count} ethical principles and has {t_count} ethical tensions. "
        f"{r_count} compliance obligations identified."
    )

    return AssessResponse(
        system=profile["system"],
        risk_level=profile.get("risk_level"),
        erc_score=erc_score,
        erc_level=erc_lvl,
        sector=profile.get("sector"),
        decision_type=profile.get("decision_type"),
        violated_principles=violated_principles,
        ethical_tensions=ethical_tensions,
        requirements=requirements,
        regulations=regulations,
        summary=summary,
    )
