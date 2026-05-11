import logging
from db.connection import run_query

logger = logging.getLogger(__name__)

def get_dynamic_profile(system_name: str) -> dict:
    logger.info(f"Fetching dynamic profile for system: {system_name}")
    query = """
    MATCH (s:Individual {name: $name})-[r]->(n)
    RETURN type(r) AS relation, collect(DISTINCT n.name) AS targets
    """
    rows = run_query(query, {"name": system_name})
    
    relationships = {}
    for row in rows:
        relationships[row["relation"]] = row["targets"]
        
    if not relationships:
        logger.warning(f"No relationships found for system: {system_name}")
        return {}
        
    profile = {
        "system": system_name,
        "relationships": relationships
    }
    return profile
