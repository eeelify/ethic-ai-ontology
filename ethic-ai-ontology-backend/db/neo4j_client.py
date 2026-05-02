from typing import Any, Dict, List

from db.connection import close_driver, get_session


def get_risk_from_graph(text: str) -> Dict[str, Any]:
    """
    Legacy helper kept for backward compatibility.
    Prefer using db.risk + db.regulations via /analyze.
    """
    with get_session() as session:
        result = session.run(
            """
            MATCH (a:AI_System)-[:HAS_RISK]->(r:Risk)-[:REGULATED_BY]->(k:Regulation)
            WHERE $text CONTAINS toLower(coalesce(a.keyword, a.name, a.label))
            RETURN coalesce(r.level, r.risk_level, r.name, r.label) AS risk_level,
                   collect(DISTINCT coalesce(k.name, k.label)) AS regulations
            LIMIT 1
            """,
            text=text.lower(),
        )
        record = result.single()

        if not record or record.get("risk_level") is None:
            return {"risk_level": None, "applicable_regulations": []}

        regulations: List[str] = [r for r in (record.get("regulations") or []) if r]
        return {"risk_level": record["risk_level"], "applicable_regulations": regulations}