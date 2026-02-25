"""Meeting management API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.batching.communication_batcher import CommunicationBatcher

router = APIRouter()
batcher = CommunicationBatcher()


class TaskBatchRequest(BaseModel):
    user_id: str
    tasks: List[dict]


class MeetingAllowanceRequest(BaseModel):
    user_id: str
    proposed_time: datetime
    meeting_type: str
    override_code: Optional[str] = None


@router.post("/batch")
async def batch_tasks(request: TaskBatchRequest):
    """Create batches of similar communication tasks."""
    try:
        result = batcher.create_batches(request.tasks, request.user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-allowed")
async def check_meeting_allowed(request: MeetingAllowanceRequest):
    """Check if a meeting can be scheduled at proposed time."""
    from src.enforcement.no_meeting_enforcer import NoMeetingEnforcer
    
    enforcer = NoMeetingEnforcer()
    
    try:
        result = enforcer.check_meeting_allowed(
            request.user_id,
            request.proposed_time,
            request.meeting_type,
            request.override_code
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
