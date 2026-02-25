"""Webhook API routes."""

from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional
from src.webhooks.webhook_handler import WebhookHandler, WebhookRegistry
from src.core.config import get_settings

router = APIRouter()
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
        
        # Verify signature if provided
        if x_signature and not handler.verify_signature(body, x_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse event data
        event_data = await request.json()
        
        # Handle event
        result = handler.handle_calendar_event(event_data)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
