from typing import Dict, List

from db.connection import run_query


def get_tensions_for_system(system_name: str) -> List[Dict]:
    return run_query(
        """
        MATCH (s:Individual {name: $system_name})-[:HAS_ETHICAL_TENSION]->(t:Individual)
        RETURN t.name AS tension
        ORDER BY tension
        """,
        {"system_name": system_name},
    )


def get_all_principle_conflicts() -> List[Dict]:
    return run_query(
        """
        MATCH (a:Individual)-[:CONFLICTS_WITH]->(b:Individual)
        RETURN a.name AS principle_1, b.name AS principle_2
        ORDER BY principle_1, principle_2
        """
    )
