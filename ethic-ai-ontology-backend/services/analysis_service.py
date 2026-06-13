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
OPTIONAL MATCH (c)-[:HAS_REGULATION]->(reg:Regulation)
WITH k, c, collect(DISTINCT coalesce(r.name, c.risk_level)) AS risks, collect(DISTINCT reg.name) AS regulations

OPTIONAL MATCH (c)-[:MAY_CREATE_TENSION]->(t:EthicalTension)
OPTIONAL MATCH (t)-[:CONFLICTS_WITH]->(tp:EthicalPrinciple)
WITH k, c, risks, regulations, t, collect(DISTINCT tp.name) AS conflicting_principles
WITH k, c, risks, regulations, 
     collect(CASE WHEN t IS NOT NULL THEN {
         name: t.name,
         severity: t.severity,
         description: t.description,
         recommendation: t.recommendation,
         conflicting_principles: conflicting_principles
     } END) AS ethical_tensions

OPTIONAL MATCH (c)-[vr:IMPACTS_PRINCIPLE]->(p:EthicalPrinciple)
RETURN
    k.term         AS keyword,
    c.name         AS category,
    risks,
    regulations,
    ethical_tensions,
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
            
            # Calculate metrics
            principles_set = set()
            cats_with_ethics = set()
            cats_with_risks = set()
            cats_with_regs = set()
            total_risks = 0
            total_regs = 0

            for r in rows:
                cat = r.get("category")
                ea_list = [e for e in (r.get("ethical_analysis") or []) if e.get("principle")]
                risks_list = [risk for risk in (r.get("risks") or []) if risk]
                regs_list = [reg for reg in (r.get("regulations") or []) if reg]

                if cat:
                    if ea_list:
                        cats_with_ethics.add(cat)
                        for ea in ea_list:
                            principles_set.add(ea.get("principle"))
                    if risks_list:
                        cats_with_risks.add(cat)
                        total_risks += len(risks_list)
                    if regs_list:
                        cats_with_regs.add(cat)
                        total_regs += len(regs_list)
            
            principles_count = len(principles_set)
            missing_relations = categories_count - len(cats_with_ethics)
            missing_risks = categories_count - len(cats_with_risks)
            missing_regs = categories_count - len(cats_with_regs)

            logger.info(f"Successfully loaded {len(rows)} keyword mappings into ontology cache")
            logger.info(f"Loaded {principles_count} unique ethical principles.")
            logger.info(f"Categories with ethical mappings: {len(cats_with_ethics)} (Missing: {missing_relations})")
            logger.info(f"Loaded risk mappings: {total_risks} across {len(cats_with_risks)} categories (Missing: {missing_risks})")
            logger.info(f"Loaded regulation mappings: {total_regs} across {len(cats_with_regs)} categories (Missing: {missing_regs})")

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
                "risks": [str, ...],
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
                ],
                "ethical_tensions": [...]
            },
            ...
        ],
        "inferred_categories": [str, ...],
        "inferred_risks":      [str, ...],
        "inferred_regulations":[str, ...],
        "ethical_analysis":    [EthicalImpact, ...],  # deduplicated, top-level
        "ethical_tensions":    [EthicalTensionDetail, ...]
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

    # Top-level ethical tensions: deduplicate by name
    seen_tensions: set[str] = set()
    top_tensions: list[dict] = []

    for row in ontology:
        kw: str = (row.get("keyword") or "").strip()
        if not kw or kw.lower() not in t:
            continue

        category: str = row.get("category") or ""
        risks: list[str] = [r for r in (row.get("risks") or []) if r]
        regs: list[str] = [r for r in (row.get("regulations") or []) if r]
        ea: list[dict] = _clean_ethical_analysis(row.get("ethical_analysis") or [])
        et: list[dict] = row.get("ethical_tensions") or []

        matched.append({
            "keyword": kw,
            "mapped_category": category,
            "risks": sorted(risks),
            "regulations": sorted(regs),
            "ethical_analysis": ea,
            "ethical_tensions": et,
        })

        if category:
            inferred_categories.add(category)
        
        inferred_risks.update(risks)
        inferred_regulations.update(regs)

        # Deduplicate at top level for impacts
        for impact in ea:
            key = (category, impact.get("principle", ""), impact.get("harm_type", ""))
            if key not in seen_impacts:
                seen_impacts.add(key)
                top_ethical.append(impact)

        # Deduplicate at top level for tensions
        for tension in et:
            t_name = tension.get("name")
            if t_name and t_name not in seen_tensions:
                seen_tensions.add(t_name)
                top_tensions.append(tension)
                
    if not matched:
        logger.info("No known AI governance category detected.")
        return {
            "message": "No known AI governance category detected",
            "matched_keywords": [],
            "inferred_categories": [],
            "inferred_risks": [],
            "inferred_regulations": [],
            "ethical_analysis": [],
            "ethical_tensions": []
        }

    logger.info(
        f"Matched {len(matched)} keyword(s) -> "
        f"Categories: {sorted(inferred_categories)} | "
        f"Risks: {sorted(inferred_risks)} | "
        f"Regs: {len(inferred_regulations)} "
        f"(Ethical impacts: {len(top_ethical)}) "
        f"(Ethical tensions: {len(top_tensions)})"
    )

    return {
        "matched_keywords": matched,
        "inferred_categories": sorted(inferred_categories),
        "inferred_risks": sorted(inferred_risks),
        "inferred_regulations": sorted(inferred_regulations),
        "ethical_analysis": top_ethical,
        "ethical_tensions": top_tensions,
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
        risks: list[str] = [r for r in (row.get("risks") or []) if r]
        for risk in risks:
            if risk not in seen_risks:
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
