from typing import Dict, List

from db.connection import run_query


def get_violations_for_system(system_name: str) -> List[Dict]:
    return run_query(
        """
        CALL {
          MATCH (s:Individual {name: $system_name})-[:VIOLATES]->(p:Individual)
          RETURN p.name AS violated_principle
          UNION
          MATCH (p:Individual)-[:IS_VIOLATED_BY]->(s:Individual {name: $system_name})
          RETURN p.name AS violated_principle
        }
        WITH violated_principle WHERE violated_principle IS NOT NULL
        RETURN DISTINCT violated_principle
        ORDER BY violated_principle
        """,
        {"system_name": system_name},
    )


def individual_exists(system_name: str) -> bool:
    rows = run_query(
        """
        MATCH (s:Individual {name: $system_name})
        RETURN s.name AS name LIMIT 1
        """,
        {"system_name": system_name},
    )
    return bool(rows)
