import json
import os
import logging
from typing import List, Optional, Tuple

import google.generativeai as genai
from google.api_core import exceptions as google_api_exceptions

from services.chroma_client import get_or_create_collection
from services.graph_service import get_dynamic_profile
from services.analysis_service import analyze_text

logger = logging.getLogger(__name__)

class NoGeminiModelAvailable(RuntimeError):
    """Tüm aday modeller generateContent için reddedildiğinde."""
    def __init__(self, tried: List[str], last: Optional[BaseException]):
        self.tried = tried
        self.last = last
        super().__init__(
            "Hiçbir Gemini modeli kullanılamadı. Denenenler: "
            + ", ".join(tried)
            + (f". Son hata: {last!s}" if last else "")
        )

def _default_model_candidates() -> List[str]:
    return [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro",
        "gemini-pro",
    ]

def _model_candidates() -> List[str]:
    raw = (os.getenv("GEMINI_MODEL_CANDIDATES") or "").strip()
    if raw:
        return [m.strip() for m in raw.split(",") if m.strip()]

    preferred = (os.getenv("GEMINI_MODEL") or "").strip().strip('"').strip("'")
    out: List[str] = []
    if preferred:
        out.append(preferred)
    for m in _default_model_candidates():
        if m not in out:
            out.append(m)
    return out

def _should_try_next_model(exc: BaseException) -> bool:
    if isinstance(exc, google_api_exceptions.NotFound):
        return True
    if isinstance(exc, google_api_exceptions.InvalidArgument):
        msg = str(exc).lower()
        if "not found" in msg or "not supported for generatecontent" in msg:
            return True
        if "404" in msg and "model" in msg:
            return True
    msg = str(exc).lower()
    if "404" in msg and "models/" in msg:
        return True
    if "is not found" in msg:
        return True
    if "not supported for generatecontent" in msg:
        return True
    return False

def _configure_genai() -> None:
    raw = os.getenv("GEMINI_API_KEY") or ""
    key = raw.strip().strip('"').strip("'")
    if not key:
        raise ValueError("GEMINI_API_KEY boş.")
    genai.configure(api_key=key)

def _parse_report_from_response(response) -> dict:
    raw_text = getattr(response, "text", None) or ""
    if not raw_text.strip():
        raise ValueError("Gemini yanıtı boş.")
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        text = raw_text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())

def _generate_report_with_model_fallback(prompt: str) -> Tuple[dict, str]:
    _configure_genai()
    candidates = _model_candidates()
    last_exc: Optional[BaseException] = None
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            report = _parse_report_from_response(response)
            return report, model_name
        except (json.JSONDecodeError, ValueError):
            raise
        except Exception as exc:
            if _should_try_next_model(exc):
                last_exc = exc
                continue
            raise
    raise NoGeminiModelAvailable(candidates, last_exc)

def retrieve_legal_context(query: str, n_results: int = 4) -> list[dict]:
    collection = get_or_create_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    documents = []
    if not results["documents"] or len(results["documents"]) == 0 or len(results["documents"][0]) == 0:
        return documents

    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        documents.append({
            "text": doc,
            "source": metadata.get("source"),
            "article": metadata.get("article"),
            "category": metadata.get("category")
        })
    return documents

def generate_zinspection_report(
    system_name: str,
    dynamic_profile: dict,
    legal_context: list[dict],
    inferred_data: dict = None,
    raw_text: str = ""
) -> Tuple[dict, str]:

    legal_text = "\n".join([
        f"[{doc['source']} - {doc['article']}]: {doc['text']}"
        for doc in legal_context
    ])

    inferred_str = json.dumps(inferred_data, indent=2) if inferred_data else "None"
    profile_str = json.dumps(dynamic_profile, indent=2)
    
    raw_text_section = f"\nDOCUMENT CONTENTS (from user upload):\n{raw_text}\n" if raw_text.strip() else ""

    prompt = f"""You are a Z-Inspection AI ethics auditor.
Generate a structured audit report based ONLY on the provided ontology data, legal context, and the document contents.

ONTOLOGY DATA (Dynamic Graph Profile):
System: {system_name}
Relationships and Properties:
{profile_str}

INFERRED DATA (Keyword-based):
{inferred_str}

LEGAL CONTEXT (from ChromaDB):
{legal_text}
{raw_text_section}
Generate a JSON report with these exact fields:
{{
  "executive_summary": "2-3 sentence summary citing ontology data and document details",
  "risk_assessment": "Risk level explanation with legal article reference",
  "composite_risk_score": 75,
  "risk_level": "MinimalRisk | LimitedRisk | HighRisk | UnacceptableRisk",
  "score_components": {{
    "ethical_score": 80,
    "legal_score": 70,
    "data_score": 90,
    "technical_score": 60,
    "oversight_score": 80
  }},
  "risk_threshold_explanation": "Explanation of why the risk level was assigned based on the composite score",
  "risk_trigger_safeguard_analysis": "Detailed narrative explaining which risk triggers were found, which safeguards were detected, what safeguards are missing, what the initial risk level was, and why the final risk level changed or remained the same based on the INFERRED DATA.",
  "ethical_analysis": "Analysis of violated principles and overall ethical impact",
  "ethical_tensions": [
    {{
      "tension": "Name of the tension (e.g. Privacy vs Transparency)",
      "description": "A detailed, contextual explanation of how this specific trade-off manifests in this exact AI system's use case, rather than just a generic definition."
    }}
  ],
  "legal_compliance": "Specific legal obligations with article numbers",
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "citation_sources": ["source1", "source2"]
}}

CRITICAL INSTRUCTION 1: If the ONTOLOGY DATA properties (e.g. under the 'properties' key in the Dynamic Graph Profile JSON) contain `hasCompositeRiskScore`, `hasEthicalImpactScore`, `hasLegalComplianceScore`, `hasDataSensitivityScore`, `hasTechnicalRobustnessScore`, or `hasHumanOversightScore`, you MUST populate the corresponding fields (`composite_risk_score`, `risk_level`, and `score_components` with keys `ethical_score`, `legal_score`, `data_score`, `technical_score`, `oversight_score`) in your response JSON using those exact values. Do not recalculate, modify, or hallucinate these values. IF THEY ARE MISSING, YOU MUST GENERATE realistic integer estimates between 0 and 100 based on your ethical analysis, and calculate the `composite_risk_score` yourself (as the weighted average of the 5 vectors). Ensure all score values in the JSON are integers, not strings.
CRITICAL INSTRUCTION 2 FOR ETHICAL TENSIONS: Do not just list generic definitions. Analyze the system's specific context, use case, document contents, and provided data. Identify actual ethical trade-offs (tensions) that apply to this specific system. Provide a highly tailored explanation for *how and why* this system experiences each tension based on the uploaded document text.

Format: Return valid JSON only, no markdown.
"""

    report, model_used = _generate_report_with_model_fallback(prompt)
    return report, model_used

def run_graphrag_pipeline(system_name: Optional[str] = None, text: str = "") -> dict:
    logger.info(f"Running GraphRAG pipeline for {system_name or 'Raw Text'}")
    # 1. Fetch graph profile
    dynamic_profile = get_dynamic_profile(system_name) if system_name else {}
    
    # 2. Extract keywords if text is provided
    inferred_data = analyze_text(text) if text else None
    
    # 3. Build query dynamically
    query_parts = []
    if system_name:
        flat_profile = " ".join([f"{k}: {', '.join(v)}" for k, v in dynamic_profile.get("relationships", {}).items()])
        query_parts.append(f"AI system ethics audit: {system_name} {flat_profile}")
    else:
        query_parts.append("AI system ethics audit.")
        
    if inferred_data:
        inferred_categories = inferred_data.get("inferred_categories", [])
        if inferred_categories:
            query_parts.append(f"Categories: {', '.join(inferred_categories)}")
        query_parts.append(" ".join(inferred_data.get("inferred_regulations", [])))
        
    query = " ".join(query_parts)
    
    # 4. Retrieve legal documents
    legal_context = retrieve_legal_context(query, n_results=5)
    
    # 5. Generate report
    report, gemini_model = generate_zinspection_report(system_name or "Unknown System", dynamic_profile, legal_context, inferred_data, raw_text=text)
    
    return {
        "system": system_name or "Unknown System",
        "dynamic_profile": dynamic_profile,
        "inferred_data": inferred_data,
        "legal_sources_used": [f"{d['source']} - {d['article']}" for d in legal_context],
        "report": report,
        "gemini_model": gemini_model,
    }
