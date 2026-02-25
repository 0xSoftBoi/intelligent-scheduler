"""Settings API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.enforcement.no_meeting_enforcer import NoMeetingEnforcer, BlockType
from datetime import datetime

router = APIRouter()
enforcer = NoMeetingEnforcer()


class NoMeetingDayConfig(BaseModel):
    user_id: str
    day_of_week: int
    recurring: bool = True


class BlockTimeRequest(BaseModel):
    user_id: str
    start: datetime
    end: datetime
    block_type: str
    reason: str


@router.put("/no-meeting-days")
async def configure_no_meeting_day(config: NoMeetingDayConfig):
    """Configure no-meeting day."""
    try:
        result = enforcer.configure_no_meeting_day(
            config.user_id,
            config.day_of_week,
            config.recurring
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/block-time")
async def block_time(request: BlockTimeRequest):
    """Block time on calendar."""
    try:
        block_type = BlockType(request.block_type)
        
        result = enforcer.block_time_slot(
            request.user_id,
            request.start,
            request.end,
            block_type,
            request.reason
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
