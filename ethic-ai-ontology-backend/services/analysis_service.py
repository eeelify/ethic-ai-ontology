"""
analysis_service.py
───────────────────
Ontology-driven text analysis with explainable ethical impact reasoning.

Architecture:
    Text
     ↓  lowercase
    Keyword Matching      (:Keyword)-[:MAPS_TO]->(:AI_Category)
     ↓
    Graph Inference       (:AI_Category)-[:HAS_REGULATION]->(:Regulation)
                          (:AI_Category)-[r:MAY_VIOLATE]->(:EthicalPrinciple)
                            r.reason, r.impact, r.severity, r.harm_type
     ↓
    Explainable Output    matched_keywords / inferred_categories /
                          inferred_risks / inferred_regulations /
                          ethical_analysis (rich, per-principle)

All vocabulary lives in Neo4j – no hardcoded dictionaries here.
"""

import logging
import threading
from db.connection import run_query

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Fetch full ontology map in ONE round-trip.
# The WITH after the first OPTIONAL MATCH collapses regulations before the
# second OPTIONAL MATCH, preventing a Cartesian cross-product.
# ─────────────────────────────────────────────────────────────────────────────
_FETCH_ONTOLOGY_CYPHER = """
MATCH (k:Keyword)-[:MAPS_TO]->(c:AI_Category)
OPTIONAL MATCH (c)-[:HAS_RISK]->(r:RiskLevel)
OPTIONAL MATCH (c)-[:RELATED_TO_REGULATION]->(reg:Regulation)
WITH k, c, r, collect(DISTINCT reg.name) AS regulations
OPTIONAL MATCH (c)-[vr:IMPACTS_PRINCIPLE]->(p:EthicalPrinciple)
RETURN
    k.term         AS keyword,
    c.name         AS category,
    r.name         AS risk,
    regulations,
    collect(DISTINCT {
        principle: p.name,
        reason:    vr.reason,
        impact:    vr.impact,
        severity:  vr.severity,
        harm_type: vr.harm_type
    }) AS ethical_analysis
"""

_ONTOLOGY_CACHE = []
_CACHE_LOCK = threading.Lock()

def refresh_ontology_cache() -> dict:
    """Reloads ontology mappings from Neo4j into memory thread-safely. Returns stats."""
    global _ONTOLOGY_CACHE
    try:
        logger.info("Attempting to reload ontology cache from Neo4j...")
        rows = run_query(_FETCH_ONTOLOGY_CYPHER)
        if rows is not None:
            with _CACHE_LOCK:
                _ONTOLOGY_CACHE = rows
            
            categories_count = len(set(r.get("category") for r in rows if r.get("category")))
            logger.info(f"Successfully loaded {len(rows)} keyword mappings into ontology cache")
            return {
                "status": "success",
                "loaded_keywords": len(rows),
                "loaded_categories": categories_count
            }
        else:
            logger.warning("Ontology query returned None, keeping old cache if exists.")
            raise ValueError("Neo4j query returned None.")
    except Exception as exc:
        logger.error(f"Failed to refresh ontology cache from Neo4j: {exc}")
        raise

def get_ontology_cache() -> list[dict]:
    global _ONTOLOGY_CACHE
    if not _ONTOLOGY_CACHE:
        refresh_ontology_cache()
    with _CACHE_LOCK:
        return _ONTOLOGY_CACHE





def _clean_ethical_analysis(raw: list[dict]) -> list[dict]:
    """
    Filter out null/empty entries that Neo4j emits when OPTIONAL MATCH
    finds no relationships (all fields will be None).
    """
    return [
        e for e in (raw or [])
        if e.get("principle")
    ]


def analyze_text(text: str) -> dict:
    """
    Analyze *text* against the Neo4j keyword ontology.

    Returns
    -------
    {
        "matched_keywords": [
            {
                "keyword": str,
                "mapped_category": str,
                "risk_level": str,
                "regulations": [str, ...],
                "ethical_analysis": [
                    {
                        "principle": str,
                        "reason":    str,
                        "impact":    str,
                        "severity":  str,
                        "harm_type": str
                    },
                    ...
                ]
            },
            ...
        ],
        "inferred_categories": [str, ...],
        "inferred_risks":      [str, ...],
        "inferred_regulations":[str, ...],
        "ethical_analysis":    [EthicalImpact, ...]  # deduplicated, top-level
    }
    """
    logger.info("POST /analyze-text: running ontology-driven analysis")

    ontology = get_ontology_cache()
    t = text.lower()

    matched: list[dict] = []
    inferred_categories: set[str] = set()
    inferred_risks: set[str] = set()
    inferred_regulations: set[str] = set()

    # Top-level ethical analysis: deduplicate by (category, principle, harm_type)
    seen_impacts: set[tuple] = set()
    top_ethical: list[dict] = []

    for row in ontology:
        kw: str = (row.get("keyword") or "").strip()
        if not kw or kw.lower() not in t:
            continue

        category: str = row.get("category") or ""
        risk: str = row.get("risk") or ""
        regs: list[str] = [r for r in (row.get("regulations") or []) if r]
        ea: list[dict] = _clean_ethical_analysis(row.get("ethical_analysis") or [])

        matched.append({
            "keyword": kw,
            "mapped_category": category,
            "risk_level": risk,
            "regulations": sorted(regs),
            "ethical_analysis": ea,
        })

        if category:
            inferred_categories.add(category)
        if risk:
            inferred_risks.add(risk)
        inferred_regulations.update(regs)

        # Deduplicate at top level
        for impact in ea:
            key = (category, impact.get("principle", ""), impact.get("harm_type", ""))
            if key not in seen_impacts:
                seen_impacts.add(key)
                top_ethical.append(impact)
                
    if not matched:
        logger.info("No known AI governance category detected.")
        return {
            "message": "No known AI governance category detected",
            "matched_keywords": [],
            "inferred_categories": [],
            "inferred_risks": [],
            "inferred_regulations": [],
            "ethical_analysis": []
        }

    logger.info(
        f"Matched {len(matched)} keyword(s) -> "
        f"{len(inferred_categories)} category/ies: {sorted(inferred_categories)}"
    )

    return {
        "matched_keywords": matched,
        "inferred_categories": sorted(inferred_categories),
        "inferred_risks": sorted(inferred_risks),
        "inferred_regulations": sorted(inferred_regulations),
        "ethical_analysis": top_ethical,
    }


def generate_graph_trace(text: str) -> dict:
    """
    Generate an explainable reasoning chain for the given text based on ontology mappings.
    Deterministic, no LLM usage.
    """
    logger.info("POST /graph-trace: running explainable graph trace")
    ontology = get_ontology_cache()
    t = text.lower()
    
    trace = []
    seen_keywords = set()
    seen_categories = set()
    seen_risks = set()
    seen_regulations = set()
    seen_principles = set()
    seen_harms = set()
    
    for row in ontology:
        kw: str = (row.get("keyword") or "").strip()
        if not kw or kw.lower() not in t:
            continue
            
        category: str = row.get("category") or ""
        if not category:
            continue
            
        # 1. Keyword mapping trace
        if kw not in seen_keywords:
            trace.append({"step": "keyword_match", "value": kw})
            seen_keywords.add(kw)
            
        # 2. Mapped category trace
        if category not in seen_categories:
            trace.append({"step": "mapped_category", "value": category})
            seen_categories.add(category)
            
        # 3. Risk inference trace
        risk: str = row.get("risk") or ""
        if risk and risk not in seen_risks:
            trace.append({"step": "risk_inference", "value": risk})
            seen_risks.add(risk)
            
        # 4. Regulation inference trace
        regs: list[str] = [r for r in (row.get("regulations") or []) if r]
        for reg in regs:
            if reg not in seen_regulations:
                trace.append({"step": "regulation_inference", "value": reg})
                seen_regulations.add(reg)
                
        # 5. Ethical principle & Harm type trace
        ea: list[dict] = _clean_ethical_analysis(row.get("ethical_analysis") or [])
        for impact in ea:
            principle = impact.get("principle")
            if principle and principle not in seen_principles:
                trace.append({"step": "ethical_principle", "value": principle})
                seen_principles.add(principle)
                
            harm_type = impact.get("harm_type")
            if harm_type and harm_type not in seen_harms:
                trace.append({"step": "harm_type", "value": harm_type})
                seen_harms.add(harm_type)
                    
    return {"trace": trace}
