from typing import Dict, List, Optional

from db.connection import run_query


def get_all_systems() -> List[Dict]:
    """
    Returns all AI systems.

    Supports both:
    - (:AI_System {name})
    - OWL import style (:Individual)-[:type]->(cls) where cls.uri contains AiSystem
    """
    return run_query(
        """
        CALL {
          MATCH (s:AI_System)
          RETURN coalesce(s.name, s.label, s.keyword) AS name, s.hasCompositeRiskScore AS composite_risk_score, s.hasRiskLevel AS risk_level
          UNION
          MATCH (ind:Individual)-[:type]->(cls)
          WHERE cls.uri CONTAINS 'AiSystem'
          RETURN coalesce(ind.label, split(ind.uri, '/')[-1]) AS name, ind.hasCompositeRiskScore AS composite_risk_score, ind.hasRiskLevel AS risk_level
          UNION
          MATCH (a:AiSystem)
          RETURN a.name AS name, a.hasCompositeRiskScore AS composite_risk_score, a.hasRiskLevel AS risk_level
        }
        WITH name, composite_risk_score, risk_level WHERE name IS NOT NULL
        RETURN DISTINCT name, composite_risk_score, risk_level
        ORDER BY name
        """
    )


def get_system_by_name(name: str) -> Optional[Dict]:
    """
    Return a system by (partial) name match.
    """
    rows = run_query(
        """
        CALL {
          MATCH (s:AI_System)
          WHERE toLower(coalesce(s.name, s.label, s.keyword)) CONTAINS toLower($name)
          RETURN coalesce(s.name, s.label, s.keyword) AS name
          LIMIT 1
          UNION
          MATCH (ind:Individual)-[:type]->(cls)
          WHERE cls.uri CONTAINS 'AiSystem'
            AND toLower(coalesce(ind.label, split(ind.uri, '/')[-1])) CONTAINS toLower($name)
          RETURN coalesce(ind.label, split(ind.uri, '/')[-1]) AS name
          LIMIT 1
        }
        RETURN name
        LIMIT 1
        """,
        {"name": name},
    )
    return rows[0] if rows else None

import json

def save_system_report_to_db(system_name: str, report: dict):
    """
    Upsert the system and save its newly generated risk scores and full JSON from the LLM report.
    """
    query = """
    MERGE (s:AI_System {name: $name})
    SET 
        s.hasCompositeRiskScore = toFloat($composite_risk_score),
        s.hasRiskLevel = $risk_level,
        s.hasEthicalImpactScore = toFloat($ethical_score),
        s.hasLegalComplianceScore = toFloat($legal_score),
        s.hasDataSensitivityScore = toFloat($data_score),
        s.hasTechnicalRobustnessScore = toFloat($technical_score),
        s.hasHumanOversightScore = toFloat($oversight_score),
        s.lastReportJson = $last_report_json
    RETURN s
    """
    score_components = report.get("score_components", {})
    
    run_query(query, {
        "name": system_name,
        "composite_risk_score": report.get("composite_risk_score"),
        "risk_level": report.get("risk_level"),
        "ethical_score": score_components.get("ethical_score"),
        "legal_score": score_components.get("legal_score"),
        "data_score": score_components.get("data_score"),
        "data_score": score_components.get("data_score"),
        "technical_score": score_components.get("technical_score"),
        "oversight_score": score_components.get("oversight_score"),
        "last_report_json": json.dumps(report, ensure_ascii=False)
    })

def get_system_saved_report(system_name: str) -> Optional[dict]:
    """
    Retrieve the previously generated full JSON report for a system, if it exists.
    """
    query = """
    MATCH (s:AI_System)
    WHERE toLower(s.name) = toLower($name) AND s.lastReportJson IS NOT NULL
    RETURN s.lastReportJson AS report_json
    """
    rows = run_query(query, {"name": system_name})
    if rows and rows[0].get("report_json"):
        try:
            return json.loads(rows[0]["report_json"])
        except Exception:
            pass
    return None