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
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash-latest",
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
    inferred_data: dict = None
) -> Tuple[dict, str]:

    legal_text = "\n".join([
        f"[{doc['source']} - {doc['article']}]: {doc['text']}"
        for doc in legal_context
    ])

    inferred_str = json.dumps(inferred_data, indent=2) if inferred_data else "None"
    profile_str = json.dumps(dynamic_profile, indent=2)

    prompt = f"""You are a Z-Inspection AI ethics auditor.
Generate a structured audit report based ONLY on the provided ontology data and legal context.

ONTOLOGY DATA (Dynamic Graph Profile):
System: {system_name}
Relationships:
{profile_str}

INFERRED DATA (Keyword-based):
{inferred_str}

LEGAL CONTEXT (from ChromaDB):
{legal_text}

Generate a JSON report with these exact fields:
{{
  "executive_summary": "2-3 sentence summary citing ontology data",
  "risk_assessment": "Risk level explanation with legal article reference",
  "ethical_analysis": "Analysis of violated principles and tensions",
  "legal_compliance": "Specific legal obligations with article numbers",
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "citation_sources": ["source1", "source2"]
}}

Format: Return valid JSON only, no markdown.
"""

    report, model_used = _generate_report_with_model_fallback(prompt)
    return report, model_used

def run_graphrag_pipeline(system_name: str, text: str = "") -> dict:
    logger.info(f"Running GraphRAG pipeline for {system_name}")
    # 1. Fetch graph profile
    dynamic_profile = get_dynamic_profile(system_name)
    
    # 2. Extract keywords if text is provided
    inferred_data = analyze_text(text) if text else None
    
    # 3. Build query dynamically
    flat_profile = " ".join([f"{k}: {', '.join(v)}" for k, v in dynamic_profile.get("relationships", {}).items()])
    query = f"AI system ethics audit: {system_name} {flat_profile}"
    
    if inferred_data:
        query += " " + " ".join(inferred_data.get("inferred_regulations", []))
        
    # 4. Retrieve legal documents
    legal_context = retrieve_legal_context(query, n_results=5)
    
    # 5. Generate report
    report, gemini_model = generate_zinspection_report(system_name, dynamic_profile, legal_context, inferred_data)
    
    return {
        "system": system_name,
        "dynamic_profile": dynamic_profile,
        "inferred_data": inferred_data,
        "legal_sources_used": [f"{d['source']} - {d['article']}" for d in legal_context],
        "report": report,
        "gemini_model": gemini_model,
    }
