"""Schedule optimization API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
from src.optimization.meeting_optimizer import MeetingOptimizer, Meeting

router = APIRouter()
optimizer = MeetingOptimizer()


class OptimizeScheduleRequest(BaseModel):
    user_id: str
    meetings: List[dict]
    start_date: datetime
    end_date: datetime


@router.post("/optimize")
async def optimize_schedule(request: OptimizeScheduleRequest):
    """Optimize meeting schedule."""
    try:
        # Convert dict meetings to Meeting objects
        meetings = [
            Meeting(
                id=m['id'],
                title=m['title'],
                duration_minutes=m['duration_minutes'],
                meeting_type=m['meeting_type'],
                participants=m.get('participants', []),
                priority=m.get('priority', 5),
                flexibility=m.get('flexibility', 'medium'),
                preferred_time=m.get('preferred_time')
            )
            for m in request.meetings
        ]
        
        result = optimizer.optimize_schedule(
            meetings,
            request.user_id,
            request.start_date,
            request.end_date
        )
        
        # Serialize result for JSON response
        serialized_result = {
            'scheduled_meetings': {
                k: {
                    'meeting': {
                        'id': v['meeting'].id,
                        'title': v['meeting'].title,
                        'duration_minutes': v['meeting'].duration_minutes,
                        'meeting_type': v['meeting'].meeting_type
                    },
                    'slot': {
                        'start': v['slot'].start.isoformat(),
                        'end': v['slot'].end.isoformat(),
                        'score': v['slot'].score
                    },
                    'score': v['score']
                }
                for k, v in result['scheduled_meetings'].items()
            },
            'unscheduled_meetings': [
                {
                    'id': m.id,
                    'title': m.title,
                    'meeting_type': m.meeting_type
                }
                for m in result['unscheduled_meetings']
            ],
            'metrics': result['metrics'],
            'recommendations': result['recommendations']
        }
        
        return serialized_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
