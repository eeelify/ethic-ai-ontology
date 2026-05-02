from typing import List

from fastapi import APIRouter

from db.systems import get_all_systems
from models.schemas import SystemResponse

router = APIRouter()


@router.get("", response_model=List[SystemResponse])
def list_systems():
    rows = get_all_systems()
    return [SystemResponse(name=row["name"]) for row in rows]

