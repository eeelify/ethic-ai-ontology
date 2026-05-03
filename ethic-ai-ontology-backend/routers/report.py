from typing import Any, Dict

from fastapi import APIRouter, Body, HTTPException
from google.api_core import exceptions as google_api_exceptions

from db.profile import get_full_profile
from models.schemas import ReportResponse
from services.graphrag import NoGeminiModelAvailable, run_graphrag_pipeline

router = APIRouter()


def _erc_score_from_profile(profile: Dict[str, Any]) -> int:
    violated_principles = profile.get("violated_principles") or []
    ethical_tensions = profile.get("ethical_tensions") or []
    requirements = profile.get("requirements") or []
    return len(violated_principles) * 3 + len(ethical_tensions) * 2 + len(requirements) * 1


@router.post("/report", response_model=ReportResponse)
def generate_report(req: Dict[str, Any] = Body(...)):
    system_name = req.get("system_name")
    if not system_name:
        raise HTTPException(status_code=422, detail="system_name required")

    profile = get_full_profile(system_name)
    if not profile or not profile.get("system"):
        raise HTTPException(status_code=404, detail=f"System {system_name} not found")

    ontology_profile = {**profile, "erc_score": _erc_score_from_profile(profile)}
    try:
        result = run_graphrag_pipeline(system_name, ontology_profile)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except NoGeminiModelAvailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except google_api_exceptions.InvalidArgument as exc:
        err = str(exc).lower()
        if "api key" in err or "api_key" in err:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Gemini API anahtarı geçersiz veya eksik. "
                    ".env içinde GEMINI_API_KEY değerini Google AI Studio’dan aldığın geçerli bir anahtarla güncelle; "
                    "uvicorn’u durdurup yeniden başlat."
                ),
            ) from exc
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except google_api_exceptions.GoogleAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini API hatası: {exc}",
        ) from exc
    return result
