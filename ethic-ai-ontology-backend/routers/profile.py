from fastapi import APIRouter, HTTPException
import logging
from services.graph_service import get_dynamic_profile

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/{system_name}")
def get_profile(system_name: str):
    logger.info(f"GET /profile/{system_name} called")
    profile = get_dynamic_profile(system_name)
    if not profile:
        raise HTTPException(status_code=404, detail="System not found or has no relationships")
    return profile
