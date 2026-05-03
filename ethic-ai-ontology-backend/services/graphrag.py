import json
import os
from typing import List, Optional, Tuple

import google.generativeai as genai
from google.api_core import exceptions as google_api_exceptions

from services.chroma_client import get_or_create_collection


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
    """Hesap / API sürümüne göre model adları değişebilir; sırayla dene."""
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
    """
    GEMINI_MODEL_CANDIDATES=gemini-2.0-flash,gemini-1.5-flash  → tüm listeyi override eder.
    Aksi halde GEMINI_MODEL varsa listenin başına alınır, sonra varsayılanlar eklenir.
    """
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
    """Yanlış/erişilemeyen model adı; sıradakine geç."""
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
    """Her istekte güncel env kullan; başta/sonda boşluk ve tırnakları temizle."""
    raw = os.getenv("GEMINI_API_KEY") or ""
    key = raw.strip().strip('"').strip("'")
    if not key:
        raise ValueError(
            "GEMINI_API_KEY boş. .env dosyasına anahtarı yaz ve sunucuyu yeniden başlat."
        )
    genai.configure(api_key=key)


def _parse_report_from_response(response) -> dict:
    raw_text = getattr(response, "text", None) or ""
    if not raw_text.strip():
        raise ValueError("Gemini yanıtı boş (içerik engellenmiş veya metin yok).")
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
    ontology_profile: dict,
    legal_context: list[dict]
) -> Tuple[dict, str]:

    legal_text = "\n".join([
        f"[{doc['source']} - {doc['article']}]: {doc['text']}"
        for doc in legal_context
    ])

    prompt = f"""You are a Z-Inspection AI ethics auditor.
Generate a structured audit report based ONLY on the provided ontology data and legal context.
Do NOT invent facts not present in the data.

ONTOLOGY DATA (from OWL ontology + Neo4j):
System: {system_name}
Risk Level: {ontology_profile.get('risk_level', 'Unknown')}
Sector: {ontology_profile.get('sector', 'Unknown')}
Decision Type: {ontology_profile.get('decision_type', 'Unknown')}
Automation Level: {ontology_profile.get('automation_level', 'Unknown')}
Legal Basis: {ontology_profile.get('legal_basis', 'Unknown')}
Violated Principles: {ontology_profile.get('violated_principles', [])}
Ethical Tensions: {ontology_profile.get('ethical_tensions', [])}
Requirements: {ontology_profile.get('requirements', [])}
ERC Score: {ontology_profile.get('erc_score', 0)}

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

IMPORTANT: Every claim must reference either an ontology node or a legal article.
Format: Return valid JSON only, no markdown.
"""

    report, model_used = _generate_report_with_model_fallback(prompt)
    return report, model_used


def run_graphrag_pipeline(system_name: str, ontology_profile: dict) -> dict:
    # Build query from ontology data
    query = f"""
    AI system ethics audit: {system_name}
    Risk: {ontology_profile.get('risk_level')}
    Violations: {ontology_profile.get('violated_principles')}
    Sector: {ontology_profile.get('sector')}
    """

    legal_context = retrieve_legal_context(query, n_results=5)
    report, gemini_model = generate_zinspection_report(
        system_name, ontology_profile, legal_context
    )

    return {
        "system": system_name,
        "ontology_profile": ontology_profile,
        "legal_sources_used": [f"{d['source']} - {d['article']}" for d in legal_context],
        "report": report,
        "gemini_model": gemini_model,
    }
