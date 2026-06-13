from fastapi import APIRouter, HTTPException

from db.profile import get_full_profile
from db.regulations import get_regulations_for_system
from db.connection import get_session
from models.schemas import AssessRequest, AssessResponse, ERCLevel

router = APIRouter()

def calculate_composite_risk(
    ethical_score: float,
    legal_score: float,
    data_score: float,
    technical_score: float,
    oversight_score: float
) -> float:
    return (
        0.25 * ethical_score +
        0.25 * legal_score +
        0.20 * data_score +
        0.15 * technical_score +
        0.15 * oversight_score
    )

def classify_risk(score: float) -> str:
    if score <= 25:
        return "MinimalRisk"
    elif score <= 50:
        return "LimitedRisk"
    elif score <= 75:
        return "HighRisk"
    else:
        return "UnacceptableRisk"




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
        # If the system doesn't exist, initialize a default profile on the fly.
        # This allows assessing new/unregistered systems.
        profile = {
            "system": system_name,
            "risk_level": "MinimalRisk",
            "sector": "unspecified-sector",
            "decision_type": "unspecified",
            "automation_level": "unspecified",
            "legal_basis": "unspecified",
            "ethical_tensions": [],
            "requirements": [],
            "affected_parties": [],
            "violated_principles": [],
            "user_area": None
        }

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

    composite_score = calculate_composite_risk(
        body.ethical_score,
        body.legal_score,
        body.data_score,
        body.technical_score,
        body.oversight_score
    )

    # Note: Using the newly computed risk level directly instead of reading it from profile
    # The profile might have a pre-existing risk_level (e.g. from keyword inference), but this explicit assessment overrides it.
    risk_level = classify_risk(composite_score)

    sector = profile.get("sector") or "unspecified-sector"

    summary = (
        f"{profile['system']} is a {sector} AI system with {risk_level} risk (Score: {composite_score:.1f}). "
        f"It violates {v_count} ethical principles and has {t_count} ethical tensions. "
        f"{r_count} compliance obligations identified."
    )

    system_uri = f"http://webprotege.stanford.edu/{system_name}"

    # Write to Neo4j
    cypher = """
    MERGE (s:Individual {name: $system_name})
    ON CREATE SET s.uri = $system_uri,
                  s.classes = ["AiSystem"]
    SET s:AiSystem,
        s.hasCompositeRiskScore = $composite_score,
        s.hasEthicalImpactScore = $ethical_score,
        s.hasLegalComplianceScore = $legal_score,
        s.hasDataSensitivityScore = $data_score,
        s.hasTechnicalRobustnessScore = $technical_score,
        s.hasHumanOversightScore = $oversight_score
    WITH s
    MERGE (r:RiskLevel {name: $risk_level})
    MERGE (s)-[:HAS_RISK_LEVEL]->(r)
    """
    with get_session() as session:
        session.run(
            cypher,
            system_name=system_name,
            system_uri=system_uri,
            composite_score=composite_score,
            ethical_score=body.ethical_score,
            legal_score=body.legal_score,
            data_score=body.data_score,
            technical_score=body.technical_score,
            oversight_score=body.oversight_score,
            risk_level=risk_level
        )

    return AssessResponse(
        system=profile["system"],
        risk_level=risk_level,
        composite_risk_score=composite_score,
        erc_score=erc_score,
        erc_level=erc_lvl,
        sector=sector,
        decision_type=profile.get("decision_type"),
        violated_principles=violated_principles,
        ethical_tensions=ethical_tensions,
        requirements=requirements,
        regulations=regulations,
        summary=summary,
    )
