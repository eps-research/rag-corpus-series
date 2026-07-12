from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from mcp_client import call_tool
from models.response_models import APIResponse
from dependencies import verify_api_key

router = APIRouter(prefix="/api", tags=["Search"])

@router.get("/search_metadata", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def search_metadata(corpus: str = Query(...), field: str = Query(...), value: str = Query(...)):
    try:
        data = await call_tool("search_metadata", {"corpus": corpus, "field": field, "value": value})
        return APIResponse.ok("search_metadata", data)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filter_objects", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def filter_objects(
    corpus: str = Query(...),
    field: str = Query(...),
    min: Optional[float] = Query(None),
    max: Optional[float] = Query(None),
    omega_ready_only: Optional[bool] = Query(None),
):
    try:
        data = await call_tool("filter_objects", {"corpus": corpus, "field": field, "min": min, "max": max, "omega_ready_only": omega_ready_only})
        return APIResponse.ok("filter_objects", data)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
