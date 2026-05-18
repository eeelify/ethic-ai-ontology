from typing import Any, Dict
import logging

from fastapi import APIRouter, Body, HTTPException
from google.api_core import exceptions as google_api_exceptions

from services.graphrag import NoGeminiModelAvailable, run_graphrag_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/report")
def generate_report(req: Dict[str, Any] = Body(...)):
    system_name = req.get("system_name")
    text = req.get("text", "")
    
    if not system_name and not text:
        raise HTTPException(status_code=422, detail="Either system_name or text is required")

    logger.info(f"POST /report called for system: {system_name or 'Raw Text'}")

    try:
        result = run_graphrag_pipeline(system_name, text)
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
