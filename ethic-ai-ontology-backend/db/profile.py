from typing import Any, Dict, List, Optional

from db.connection import run_query


def _filter_names(names: List[Optional[str]]) -> List[str]:
    return sorted({n for n in names if n is not None and n != ""})


def get_full_profile(system_name: str) -> Dict[str, Any]:
    rows = run_query(
        """
        MATCH (s:Individual {name: $system_name})
        OPTIONAL MATCH (s)-[:HAS_RISK_LEVEL]->(risk:Individual)
        WITH s, collect(DISTINCT risk.name) AS _risk
        OPTIONAL MATCH (s)-[:HAS_SECTOR]->(sector:Individual)
        WITH s, _risk, collect(DISTINCT sector.name) AS _sector
        OPTIONAL MATCH (s)-[:HAS_DECISION_TYPE]->(dt:Individual)
        WITH s, _risk, _sector, collect(DISTINCT dt.name) AS _dt
        OPTIONAL MATCH (s)-[:HAS_AUTOMATION_LEVEL]->(aut:Individual)
        WITH s, _risk, _sector, _dt, collect(DISTINCT aut.name) AS _aut
        OPTIONAL MATCH (s)-[:HAS_LEGAL_BASIS]->(lb:Individual)
        WITH s, _risk, _sector, _dt, _aut, collect(DISTINCT lb.name) AS _lb
        OPTIONAL MATCH (s)-[:HAS_ETHICAL_TENSION]->(et:Individual)
        WITH s, _risk, _sector, _dt, _aut, _lb, collect(DISTINCT et.name) AS _et
        OPTIONAL MATCH (s)-[:REQUIRES]->(rq:Individual)
        WITH s, _risk, _sector, _dt, _aut, _lb, _et, collect(DISTINCT rq.name) AS _rq
        OPTIONAL MATCH (s)-[:AFFECTS]->(af:Individual)
        WITH s, _risk, _sector, _dt, _aut, _lb, _et, _rq, collect(DISTINCT af.name) AS _aff
        OPTIONAL MATCH (s)-[:VIOLATES]->(vio:Individual)
        WITH s, _risk, _sector, _dt, _aut, _lb, _et, _rq, _aff, collect(DISTINCT vio.name) AS _vio
        OPTIONAL MATCH (s)-[:HAS_USER_AREA]->(ua:Individual)
        WITH s, _risk, _sector, _dt, _aut, _lb, _et, _rq, _aff, _vio, collect(DISTINCT ua.name) AS _ua
        RETURN s.name AS system,
               head([x IN _risk WHERE x IS NOT NULL]) AS risk_level,
               head([x IN _sector WHERE x IS NOT NULL]) AS sector,
               head([x IN _dt WHERE x IS NOT NULL]) AS decision_type,
               head([x IN _aut WHERE x IS NOT NULL]) AS automation_level,
               head([x IN _lb WHERE x IS NOT NULL]) AS legal_basis,
               [x IN _et WHERE x IS NOT NULL] AS ethical_tensions,
               [x IN _rq WHERE x IS NOT NULL] AS requirements,
               [x IN _aff WHERE x IS NOT NULL] AS affected_parties,
               [x IN _vio WHERE x IS NOT NULL] AS violated_principles,
               head([x IN _ua WHERE x IS NOT NULL]) AS user_area
        """,
        {"system_name": system_name},
    )
    if not rows:
        return {}

    row = rows[0]
    return {
        "system": row.get("system"),
        "risk_level": row.get("risk_level"),
        "sector": row.get("sector"),
        "decision_type": row.get("decision_type"),
        "automation_level": row.get("automation_level"),
        "legal_basis": row.get("legal_basis"),
        "ethical_tensions": _filter_names(row.get("ethical_tensions") or []),
        "requirements": _filter_names(row.get("requirements") or []),
        "affected_parties": _filter_names(row.get("affected_parties") or []),
        "violated_principles": _filter_names(row.get("violated_principles") or []),
        "user_area": row.get("user_area"),
    }
