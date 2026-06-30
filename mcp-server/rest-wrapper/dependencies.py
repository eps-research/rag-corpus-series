from fastapi import Header, HTTPException, status
from config import API_KEY

async def verify_api_key(x_api_key: str | None = Header(default=None)):
    if API_KEY is None:
        return
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
        )
