from fastapi import APIRouter, Body
import logging
from services.analysis_service import analyze_text
from models.schemas import AnalyzeTextResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze-text", response_model=AnalyzeTextResponse)
def analyze_text_endpoint(payload: dict = Body(...)):
    text = payload.get("text", "")
    logger.info("POST /analyze-text called")
    result = analyze_text(text)
    return result
