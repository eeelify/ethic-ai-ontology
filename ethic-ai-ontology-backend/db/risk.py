from typing import Dict, Optional

from db.connection import run_query


def get_risk_by_system(system_name: str) -> Optional[Dict]:
    rows = run_query(
        """
        MATCH (s:Individual)-[:HAS_RISK_LEVEL]->(r:Individual)
        WHERE s.name = $system_name
        RETURN s.name AS system, r.name AS risk_level
        LIMIT 1
        """,
        {"system_name": system_name},
    )
    return rows[0] if rows else None
