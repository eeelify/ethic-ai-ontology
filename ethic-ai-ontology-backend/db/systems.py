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
          RETURN coalesce(s.name, s.label, s.keyword) AS name
          UNION
          MATCH (ind:Individual)-[:type]->(cls)
          WHERE cls.uri CONTAINS 'AiSystem'
          RETURN coalesce(ind.label, split(ind.uri, '/')[-1]) AS name
        }
        WITH name WHERE name IS NOT NULL
        RETURN DISTINCT name
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