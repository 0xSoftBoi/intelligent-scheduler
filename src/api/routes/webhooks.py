"""Webhook API routes."""

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional
from src.webhooks.webhook_handler import WebhookHandler, WebhookRegistry
from src.core.config import get_settings
from src.core.security import require_api_key

router = APIRouter(dependencies=[Depends(require_api_key)])
settings = get_settings()
handler = WebhookHandler(settings.WEBHOOK_SECRET_KEY)
registry = WebhookRegistry()


class WebhookRegistration(BaseModel):
    user_id: str
    webhook_url: str
    events: list
    metadata: Optional[dict] = None


@router.post("/calendar")
async def calendar_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None)
):
    """Receive calendar update webhooks."""
    try:
        body = await request.body()

        # Enforce signature verification when WEBHOOK_SECRET_KEY is configured
        if settings.WEBHOOK_SECRET_KEY:
            if not x_signature:
                raise HTTPException(status_code=401, detail="X-Signature header required")
            if not handler.verify_signature(body, x_signature):
                raise HTTPException(status_code=403, detail="Invalid signature")

        # Parse event data
        event_data = await request.json()

        # Handle event
        result = handler.handle_calendar_event(event_data)

        return result
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/register")
async def register_webhook(registration: WebhookRegistration):
    """Register a new webhook."""
    try:
        subscription = registry.register_webhook(
            registration.user_id,
            registration.webhook_url,
            registration.events,
            registration.metadata
        )
        return subscription
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
