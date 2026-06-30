from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from mcp_client import call_tool
from models.response_models import APIResponse
from dependencies import verify_api_key

router = APIRouter(prefix="/api", tags=["Objects"])

@router.get("/list_objects", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def list_objects(
    corpus: str = Query(...),
    survey: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
):
    try:
        data = await call_tool("list_objects", {"corpus": corpus, "survey": survey, "tier": tier, "page": page, "limit": limit})
        return APIResponse.ok("list_objects", data)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_object", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def get_object(corpus: str = Query(...), object_id: str = Query(...)):
    try:
        data = await call_tool("get_object", {"corpus": corpus, "object_id": object_id})
        return APIResponse.ok("get_object", data)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
