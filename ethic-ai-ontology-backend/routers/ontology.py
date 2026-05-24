import logging
from fastapi import APIRouter, HTTPException
from models.schemas import OntologyHealthResponse, ReloadOntologyResponse
from services.ontology_health_service import get_ontology_health
from services.analysis_service import refresh_ontology_cache
from db.connection import run_query

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/ontology-graph", tags=["ontology"])
def get_ontology_graph():
    """
    Fetch the nodes and relationships of the Neo4j ontology graph.
    """
    nodes_query = """
    MATCH (n)
    WHERE n:AI_Category OR n:RiskLevel OR n:Regulation OR n:EthicalPrinciple
    RETURN toString(id(n)) as id, labels(n)[0] as label_type, coalesce(n.name, n.term, toString(id(n))) as name
    """
    edges_query = """
    MATCH (n)-[r]->(m)
    WHERE (n:AI_Category OR n:RiskLevel OR n:Regulation OR n:EthicalPrinciple) 
      AND (m:AI_Category OR m:RiskLevel OR m:Regulation OR m:EthicalPrinciple)
    RETURN toString(id(r)) as id, toString(id(n)) as source, toString(id(m)) as target, type(r) as label
    """
    try:
        nodes = run_query(nodes_query)
        edges = run_query(edges_query)
        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        logger.error(f"Error fetching ontology graph: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch ontology graph")

@router.get("/ontology-health", response_model=OntologyHealthResponse, tags=["ontology"])
def ontology_health_endpoint():
    """
    Validate all AI_Category nodes and detect missing relationships.
    Detects incomplete structures, orphan categories, disconnected nodes, and duplicated keywords.
    """
    logger.info("GET /ontology-health called")
    return get_ontology_health()

@router.post("/reload-ontology", response_model=ReloadOntologyResponse, tags=["ontology"])
def reload_ontology_endpoint():
    """
    Reload ontology mappings from Neo4j into the application memory cache.
    Does not require server restart. Replaces cache atomically.
    """
    logger.info("POST /reload-ontology called")
    try:
        return refresh_ontology_cache()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to reload ontology: {exc}")
