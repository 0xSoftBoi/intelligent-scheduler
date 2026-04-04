"""API key authentication dependency."""

import os
from fastapi import Header, HTTPException
from typing import Optional


async def require_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    """FastAPI dependency that enforces API key authentication.

    If SCHEDULER_API_KEY is not set (dev mode), all requests are allowed.
    When set, the X-API-Key header must match exactly.
    """
    api_key = os.environ.get("SCHEDULER_API_KEY")
    if not api_key:
        return  # dev mode: no key configured, allow all
    if not x_api_key or x_api_key != api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
