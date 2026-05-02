from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from db.connection import run_query

router = APIRouter()


class CypherQueryRequest(BaseModel):
    cypher: str = Field(min_length=1, alias="query")
    params: Optional[Dict[str, Any]] = None

    model_config = {"populate_by_name": True}


class CypherQueryResponse(BaseModel):
    results: List[Dict[str, Any]]


@router.post("", response_model=CypherQueryResponse)
def execute_query(req: CypherQueryRequest):
    results = run_query(req.cypher, req.params or {})
    return CypherQueryResponse(results=results)

