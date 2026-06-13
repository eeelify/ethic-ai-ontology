import logging
from db.connection import run_query

logger = logging.getLogger(__name__)

def get_dynamic_profile(system_name: str) -> dict:
    logger.info(f"Fetching dynamic profile for system: {system_name}")
    
    # 1. Fetch node properties
    props_query = """
    MATCH (s:Individual {name: $name})
    RETURN properties(s) AS props
    """
    props_rows = run_query(props_query, {"name": system_name})
    properties = {}
    if props_rows:
        properties = props_rows[0].get("props") or {}

    # 2. Fetch relationships
    rel_query = """
    MATCH (s:Individual {name: $name})-[r]->(n)
    RETURN type(r) AS relation, collect(DISTINCT coalesce(n.name, n.label, split(n.uri, '/')[-1])) AS targets
    """
    rows = run_query(rel_query, {"name": system_name})
    
    relationships = {}
    for row in rows:
        relationships[row["relation"]] = row["targets"]
        
    if not relationships and not properties:
        logger.warning(f"No relationships or properties found for system: {system_name}")
        return {}
        
    profile = {
        "system": system_name,
        "properties": properties,
        "relationships": relationships
    }
    return profile

