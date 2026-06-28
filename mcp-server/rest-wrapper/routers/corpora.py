from fastapi import APIRouter, Depends, HTTPException, Query
from mcp_client import call_tool
from models.response_models import APIResponse
from dependencies import verify_api_key

router = APIRouter(prefix="/api", tags=["Corpora"])

@router.get("/list_corpora", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def list_corpora():
    try:
        data = await call_tool("list_corpora", {})
        return APIResponse.ok("list_corpora", data)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_corpus_schema", response_model=APIResponse, dependencies=[Depends(verify_api_key)])
async def get_corpus_schema(corpus: str = Query(...)):
    try:
        data = await call_tool("get_corpus_schema", {"corpus": corpus})
        return APIResponse.ok("get_corpus_schema", data)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
