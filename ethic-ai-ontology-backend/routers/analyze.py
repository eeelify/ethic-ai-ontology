from __future__ import annotations

from fastapi import APIRouter, HTTPException

from db.regulations import get_regulations_for_system
from db.risk import get_risk_by_system
from models.schemas import AnalyzeRequest, ComplianceResponse

router = APIRouter()


def _detect_system_name(text: str) -> str | None:
    """
    Map free text to exact :Individual names in Neo4j (deterministic keywords only).
    More specific patterns are checked before generic hiring keywords.
    """
    t = text.lower()

    rules: list[tuple[tuple[str, ...], str]] = [
        (
            ("automation", "automated", "automat", "auto hiring", "automated hiring"),
            "AutoHiringSystem",
        ),
        (
            (
                "hire",
                "hiring",
                "candidate",
                "recruit",
                "recruitment",
                "job applicant",
            ),
            "AmazonHR_CVFilter",
        ),
        (
            ("face", "facial", "biometric", "surveillance", "camera"),
            "ClearviewAI_System",
        ),
        (
            ("student", "exam", "proctor", "education"),
            "StudentGradingSystem",
        ),
        (
            ("recidivism", "criminal", "justice", "defendant"),
            "COMPAS_RecidivismSystem",
        ),
    ]

    for keywords, system in rules:
        if any(k in t for k in keywords):
            return system
    return None


@router.post("/analyze", response_model=ComplianceResponse)
def analyze(req: AnalyzeRequest):
    explicit = (req.system_name or "").strip()
    if explicit:
        system_name = explicit
    else:
        system_name = _detect_system_name((req.text or ""))
        if not system_name:
            raise HTTPException(
                status_code=422,
                detail="Could not map text to a known AI system (keyword matching).",
            )

    risk_row = get_risk_by_system(system_name)
    if not risk_row or not risk_row.get("risk_level"):
        raise HTTPException(status_code=404, detail="Risk level not found in graph for detected system")

    regs_rows = get_regulations_for_system(system_name)
    regulations = [r["regulation"] for r in regs_rows if r.get("regulation")]

    return ComplianceResponse(
        system=risk_row["system"],
        risk_level=risk_row["risk_level"],
        regulations=regulations,
    )

