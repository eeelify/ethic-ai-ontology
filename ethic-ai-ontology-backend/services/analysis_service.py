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
                
    # If ontology didn't find much, use LLM enrichment
    if not inferred_categories and not top_ethical:
        logger.info("Ontology match weak/empty, running LLM enrichment for Analyzer.")
        try:
            import google.generativeai as genai
            import json
            import os
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise Exception("GEMINI_API_KEY not set")
                
            genai.configure(api_key=api_key)
            
            prompt = f"""
            Analyze the following text about an AI system and extract key ethical, risk, and compliance information.
            Return ONLY a valid JSON object with the following schema, with no markdown formatting:
            {{
                "inferred_categories": ["Category 1", ...],
                "inferred_regulations": ["Regulation 1", ...],
                "risk_triggers": ["BiometricFeature", "ProfilingFeature", "HiringFeature", ...],
                "data_types": ["SensitiveHealthData", "CriminalData", ...],
                "safeguards": ["ExplicitConsent", "HumanOversight", "LegalBasis", "DataMinimization", "SecurityMeasure", "TransparencyMeasure", "ExplainabilityMeasure"],
                "ethical_tensions": [{{"name": "Tension Name", "description": "Short explanation"}}],
                "ethical_analysis": [{{"principle": "Principle", "harm_type": "Harm", "reason": "Reason"}}]
            }}
            Do NOT guess the final risk level. Just extract objective facts.
            For "safeguards", ONLY include safeguards explicitly mentioned or strongly implied as being implemented.
            For "risk_triggers", include any risky features like biometric, emotion recognition, profiling, automated decision, surveillance, hiring, credit, education, health.
            Text: {text[:6000]}
            """
            
            response = None
            models_to_try = [
                os.getenv("GEMINI_MODEL"),
                "gemini-2.5-flash",
                "gemini-1.5-flash",
                "gemini-1.5-pro-latest",
                "gemini-pro"
            ]
            
            for m_name in models_to_try:
                if not m_name:
                    continue
                try:
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content(prompt)
                    if response and response.text:
                        break
                except Exception as ex:
                    logger.warning(f"Model {m_name} failed: {ex}")
                    continue
            
            if not response:
                raise Exception("All Gemini models failed for Analyzer.")
                
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3].strip()
                
            llm_data = json.loads(raw_text)
            
            inferred_categories.update(llm_data.get("inferred_categories", []))
            inferred_regulations.update(llm_data.get("inferred_regulations", []))
            
            extracted_triggers = llm_data.get("risk_triggers", [])
            extracted_safeguards = llm_data.get("safeguards", [])
            extracted_data_types = llm_data.get("data_types", [])
            for ea in llm_data.get("ethical_analysis", []):
                top_ethical.append({
                    "principle": ea.get("principle", "Unknown"),
                    "reason": ea.get("reason", ""),
                    "impact": "Inferred from document context",
                    "severity": "Medium",
                    "harm_type": ea.get("harm_type", "Potential Harm")
                })
            for et in llm_data.get("ethical_tensions", []):
                top_tensions.append({
                    "name": et.get("name", "Unknown Tension"),
                    "description": et.get("description", ""),
                    "severity": "Medium",
                    "recommendation": "Review contextually"
                })
                
            # If we used LLM, add a fake matched keyword so the UI knows it succeeded
            if not matched and inferred_categories:
                matched.append({
                    "keyword": "AI Context Analysis (LLM)",
                    "mapped_category": list(inferred_categories)[0],
                    "risks": list(inferred_risks),
                    "regulations": list(inferred_regulations),
                    "ethical_analysis": top_ethical,
                    "ethical_tensions": top_tensions
                })
        except Exception as e:
            logger.error(f"LLM Enrichment failed in analyze_text: {e}")
            inferred_categories.add(f"DEBUG_ERROR: {str(e)}")

    if not matched and not inferred_categories:
        logger.info("No AI governance category detected even after fallback.")
        return {
            "matched_keywords": [{"keyword": "NO_MATCH", "mapped_category": "Failed to analyze", "risks": [], "regulations": [], "ethical_analysis": [], "ethical_tensions": []}],
            "inferred_categories": ["Analysis Failed"],
            "inferred_risks": [],
            "inferred_regulations": [],
            "ethical_analysis": [],
            "ethical_tensions": []
        }

    logger.info(
        f"Analysis complete -> "
        f"Categories: {sorted(inferred_categories)} | "
        f"Risks: {sorted(inferred_risks)} | "
        f"Regs: {len(inferred_regulations)} "
        f"(Ethical impacts: {len(top_ethical)}) "
        f"(Ethical tensions: {len(top_tensions)})"
    )

    # --- START REASONER INTEGRATION ---
    detected_risk_triggers = []
    detected_safeguards = []
    missing_safeguards = []
    initial_risk_level = "Unknown"
    final_risk_level = "Unknown"
    reasoning_trace = []
    
    try:
        from services.reasoning_service import run_contextual_inference
        # Collect features to pass to the reasoner
        features_to_reason = list(inferred_categories)
        if 'extracted_triggers' in locals():
            features_to_reason.extend(extracted_triggers)
            
        safeguards_to_reason = []
        if 'extracted_safeguards' in locals():
            safeguards_to_reason.extend(extracted_safeguards)
            
        # Deterministic safeguard extraction fallback
        safeguard_keywords = {
            "human oversight": "HumanOversight",
            "manual review": "HumanOversight",
            "human expert": "HumanOversight",
            "human in the loop": "HumanOversight",
            "explicit consent": "ExplicitConsent",
            "anonymization": "Anonymization",
            "data minimization": "DataMinimization",
            "legal basis": "LegalBasis",
            "transparency": "TransparencyMeasure",
            "explainab": "ExplainabilityMeasure"
        }
        t_lower = text.lower()
        for kw, sg_class in safeguard_keywords.items():
            if kw in t_lower and sg_class not in safeguards_to_reason:
                safeguards_to_reason.append(sg_class)
                
        data_to_reason = []
        if 'extracted_data_types' in locals():
            data_to_reason.extend(extracted_data_types)
            
        for mk in matched:
            features_to_reason.append(mk["mapped_category"])
            features_to_reason.append(mk["keyword"])
            
        reasoning_result = run_contextual_inference(triggers=features_to_reason, safeguards=safeguards_to_reason, data_types=data_to_reason)
        
        initial_risk_level = reasoning_result.get("initial_risk_level", "Unknown")
        final_risk_level = reasoning_result.get("final_risk_level", "Unknown")
        composite_score = reasoning_result.get("composite_score", 0)
        detected_risk_triggers = reasoning_result.get("detected_risk_triggers", [])
        detected_safeguards = reasoning_result.get("detected_safeguards", [])
        missing_safeguards = reasoning_result.get("missing_safeguards", [])
        reasoning_trace = reasoning_result.get("reasoning_trace", [])
        
        trace_str = " | ".join(reasoning_trace)
        top_ethical.insert(0, {
            "principle": "Deterministik Çıkarım (SWRL)",
            "reason": trace_str,
            "impact": f"Initial Risk: {initial_risk_level} -> Final Risk: {final_risk_level} (Score: {composite_score})",
            "severity": "Critical" if final_risk_level in ["HighRisk", "ProhibitedRisk"] else "Low",
            "harm_type": "Context-Aware Inference"
        })
    except Exception as e:
        logger.error(f"Failed to run reasoner integration: {e}")
        reasoning_trace = [f"Reasoner execution failed: {str(e)}"]
        composite_score = 0
    # --- END REASONER INTEGRATION ---

    return {
        "matched_keywords": matched,
        "inferred_categories": sorted(inferred_categories),
        "inferred_regulations": sorted(inferred_regulations),
        "ethical_analysis": top_ethical,
        "ethical_tensions": top_tensions,
        "detected_risk_triggers": detected_risk_triggers,
        "detected_safeguards": detected_safeguards,
        "missing_safeguards": missing_safeguards,
        "initial_risk_level": initial_risk_level,
        "final_risk_level": final_risk_level,
        "composite_score": composite_score,
        "reasoning_trace": reasoning_trace
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
    
    explanations = []
    
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
            
            # Generate narrative for this keyword match
            narrative = f"Sistem, metinde geçen '{kw}' kelimesinden hareketle bu yapay zekayı '{category}' kategorisinde sınıflandırdı."
            risks: list[str] = [r for r in (row.get("risks") or []) if r]
            regs: list[str] = [r for r in (row.get("regulations") or []) if r]
            
            if risks and regs:
                narrative += f" Bu durum, sistemin {', '.join(risks)} gibi riskler taşımasına ve {', '.join(regs)} gibi yasal düzenlemelerin radarına girmesine neden olmaktadır."
            elif risks:
                narrative += f" Bu eşleşme, sistemin potansiyel olarak {', '.join(risks)} risklerini taşıdığı anlamına gelir."
            elif regs:
                narrative += f" Bu eşleşme, sistemin {', '.join(regs)} mevzuatlarına tabi olduğunu gösterir."
                
            explanations.append(narrative)
            
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
                    
    return {"trace": trace, "explanations": explanations}
