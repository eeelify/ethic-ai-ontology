import logging
from fastapi import APIRouter, HTTPException
from models.schemas import OntologyHealthResponse, ReloadOntologyResponse
from services.ontology_health_service import get_ontology_health
from services.analysis_service import refresh_ontology_cache

logger = logging.getLogger(__name__)
router = APIRouter()

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
