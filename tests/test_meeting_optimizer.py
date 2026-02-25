"""Tests for meeting optimizer."""

import pytest
from datetime import datetime, timedelta
from src.optimization.meeting_optimizer import MeetingOptimizer, Meeting


@pytest.fixture
def optimizer():
    return MeetingOptimizer()


@pytest.fixture
def sample_meetings():
    return [
        Meeting(
            id="m1",
            title="Team Sync",
            duration_minutes=30,
            meeting_type="collaborative",
            participants=["user_2"],
            priority=7,
            flexibility="medium"
        ),
        Meeting(
            id="m2",
            title="Deep Work",
            duration_minutes=90,
            meeting_type="deep_work",
            participants=[],
            priority=9,
            flexibility="low"
        ),
    ]


def test_optimize_schedule(optimizer, sample_meetings):
    """Test schedule optimization."""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    result = optimizer.optimize_schedule(
        sample_meetings,
        "test_user",
        start_date,
        end_date
    )
    
    assert 'scheduled_meetings' in result
    assert 'metrics' in result
    assert result['metrics']['total_meetings'] == len(sample_meetings)


def test_suggest_meeting_time(optimizer):
    """Test meeting time suggestions."""
    meeting = Meeting(
        id="m1",
        title="Review",
        duration_minutes=60,
        meeting_type="collaborative",
        participants=["user_2"],
        priority=5,
        flexibility="high"
    )
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=3)
    
    suggestions = optimizer.suggest_meeting_time(
        meeting,
        "test_user",
        ["user_2"],
        (start_date, end_date)
    )
    
    assert len(suggestions) > 0
    assert all(hasattr(s, 'score') for s in suggestions)
    # Verify suggestions are sorted by score
    scores = [s.score for s in suggestions]
    assert scores == sorted(scores, reverse=True)
