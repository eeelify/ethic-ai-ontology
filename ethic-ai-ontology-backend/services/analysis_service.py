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
from db.connection import run_query

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Fetch full ontology map in ONE round-trip.
# The WITH after the first OPTIONAL MATCH collapses regulations before the
# second OPTIONAL MATCH, preventing a Cartesian cross-product.
# ─────────────────────────────────────────────────────────────────────────────
_FETCH_ONTOLOGY_CYPHER = """
MATCH (kw:Keyword)-[:MAPS_TO]->(cat:AI_Category)
OPTIONAL MATCH (cat)-[:HAS_REGULATION]->(reg:Regulation)
WITH kw, cat, collect(DISTINCT reg.name) AS regulations
OPTIONAL MATCH (cat)-[vr:MAY_VIOLATE]->(ep:EthicalPrinciple)
RETURN
    kw.term        AS keyword,
    cat.name       AS ai_category,
    cat.risk_level AS risk_level,
    regulations,
    collect({
        principle: ep.name,
        reason:    vr.reason,
        impact:    vr.impact,
        severity:  vr.severity,
        harm_type: vr.harm_type
    }) AS ethical_analysis
"""


def _load_ontology_map() -> list[dict]:
    try:
        rows = run_query(_FETCH_ONTOLOGY_CYPHER)
        logger.info(f"Loaded {len(rows)} keyword mappings from Neo4j ontology")
        return rows
    except Exception as exc:
        logger.error(f"Failed to load ontology map from Neo4j: {exc}")
        return []


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

    ontology = _load_ontology_map()
    t = text.lower()

    matched: list[dict] = []
    inferred_categories: set[str] = set()
    inferred_risks: set[str] = set()
    inferred_regulations: set[str] = set()

    # Top-level ethical analysis: deduplicate by (category, principle) pair
    # so that multiple keywords mapping to the same category don't repeat impacts.
    seen_impacts: set[tuple] = set()
    top_ethical: list[dict] = []

    for row in ontology:
        kw: str = (row.get("keyword") or "").strip()
        if not kw or kw.lower() not in t:
            continue

        category: str = row.get("ai_category") or ""
        risk: str = row.get("risk_level") or ""
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

        # Deduplicate at top level by (category, principle)
        for impact in ea:
            key = (category, impact.get("principle", ""))
            if key not in seen_impacts:
                seen_impacts.add(key)
                top_ethical.append(impact)

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
