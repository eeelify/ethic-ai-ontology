from fastapi import APIRouter, Body
import logging
from services.analysis_service import analyze_text, generate_graph_trace
from models.schemas import AnalyzeTextResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze-text", response_model=AnalyzeTextResponse)
def analyze_text_endpoint(payload: dict = Body(...)):
    """
    Analyze free text against keyword mappings stored in Neo4j.

    Request body: {"text": "some description of an AI system"}

    Returns:
      - matched_keywords: per-keyword detail (keyword, mapped_category, risk_level, regulations)
      - inferred_system_types: unique AI category names
      - inferred_risks: unique risk levels
      - inferred_regulations: unique regulation identifiers
    """
    text = payload.get("text", "")
    logger.info("POST /analyze-text called")
    result = analyze_text(text)
    return result

@router.post("/graph-trace")
def graph_trace_endpoint(payload: dict = Body(...)):
    """
    Returns an explainable reasoning chain for ontology inference.
    Deterministic, no LLM.
    """
    text = payload.get("text", "")
    logger.info("POST /graph-trace called")
    return generate_graph_trace(text)
