import secrets
from fastapi import Header, HTTPException, status
from app.config import settings


def verify_internal_api_key(
    x_internal_api_key: str = Header(..., alias="X-Internal-Api-Key"),
) -> str:
    if not secrets.compare_digest(x_internal_api_key, settings.internal_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid internal api key",
        )
    return x_internal_api_key
