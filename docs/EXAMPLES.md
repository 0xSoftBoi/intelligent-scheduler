# Usage Examples

## Energy Pattern Analysis

### Analyze Your Energy Patterns

```python
from src.energy_analysis.energy_analyzer import EnergyAnalyzer

analyzer = EnergyAnalyzer()

# Analyze last 30 days
patterns = analyzer.analyze_historical_patterns("user_123", days=30)

print(f"Peak hours: {patterns['peak_hours']}")
print(f"Low energy periods: {patterns['low_energy_periods']}")
print(f"Recommendations: {patterns['recommendations']}")
```

### Predict Energy for Specific Time

```python
from datetime import datetime

# Predict energy at 2 PM tomorrow
tomorrow_2pm = datetime.now().replace(hour=14, minute=0) + timedelta(days=1)
energy_level = analyzer.predict_energy_level("user_123", tomorrow_2pm)

print(f"Predicted energy at 2 PM: {energy_level}")
```

## Meeting Optimization

### Optimize Weekly Schedule

```python
from src.optimization.meeting_optimizer import MeetingOptimizer, Meeting
from datetime import datetime, timedelta

optimizer = MeetingOptimizer()

# Define meetings
meetings = [
    Meeting(
        id="m1",
        title="Team Sync",
        duration_minutes=30,
        meeting_type="collaborative",
        participants=["user_456", "user_789"],
        priority=7,
        flexibility="medium"
    ),
    Meeting(
        id="m2",
        title="Deep Work Session",
        duration_minutes=120,
        meeting_type="deep_work",
        participants=[],
        priority=9,
        flexibility="low"
    ),
]

# Optimize
start_date = datetime.now()
end_date = start_date + timedelta(days=7)

result = optimizer.optimize_schedule(
    meetings,
    "user_123",
    start_date,
    end_date
)

for meeting_id, data in result['scheduled_meetings'].items():
    print(f"{data['meeting'].title}: {data['slot'].start} (score: {data['score']:.1f})")
```

### Get Meeting Time Suggestions

```python
meeting = Meeting(
    id="m3",
    title="Project Review",
    duration_minutes=60,
    meeting_type="deep_work",
    participants=["user_456"],
    priority=8,
    flexibility="medium"
)

suggestions = optimizer.suggest_meeting_time(
    meeting,
    "user_123",
    ["user_456"],
    (start_date, end_date)
)

for i, slot in enumerate(suggestions[:3], 1):
    print(f"{i}. {slot.start} - {slot.end} (score: {slot.score:.1f})")
```

## Communication Batching

### Batch Email Tasks

```python
from src.batching.communication_batcher import CommunicationBatcher

batcher = CommunicationBatcher()

tasks = [
    {"id": "e1", "type": "email", "topic": "project_alpha", "priority": 5},
    {"id": "e2", "type": "email", "topic": "project_beta", "priority": 7},
    {"id": "e3", "type": "email", "topic": "project_alpha", "priority": 6},
    {"id": "s1", "type": "slack", "topic": "general", "priority": 3},
]

result = batcher.create_batches(tasks, "user_123")

print(f"Created {len(result['batches'])} batches")
print(f"Efficiency improvement: {result['metrics']['efficiency_improvement']:.1f}%")

for batch_type, batches in result['batches'].items():
    for batch in batches:
        print(f"\n{batch['batch_id']}: {batch['task_count']} tasks, {batch['estimated_duration']} min")
```

## No-Meeting Day Enforcement

### Configure No-Meeting Days

```python
from src.enforcement.no_meeting_enforcer import NoMeetingEnforcer

enforcer = NoMeetingEnforcer()

# Set Wednesday as no-meeting day
result = enforcer.configure_no_meeting_day(
    "user_123",
    day_of_week=2,  # Wednesday
    recurring=True
)

print(f"Configured: {result['configuration']['day_name']}")
```

### Check if Meeting is Allowed

```python
from datetime import datetime

proposed_time = datetime(2026, 2, 26, 14, 0)  # Wednesday 2 PM

allowance = enforcer.check_meeting_allowed(
    "user_123",
    proposed_time,
    "routine"
)

if not allowance['allowed']:
    print(f"Meeting blocked: {allowance['reason']}")
    print(f"Alternatives: {allowance['alternative_times']}")
```

### Block Focus Time

```python
from src.enforcement.no_meeting_enforcer import BlockType

start = datetime.now().replace(hour=9, minute=0)
end = start + timedelta(hours=2)

block = enforcer.block_time_slot(
    "user_123",
    start,
    end,
    BlockType.FOCUS_TIME,
    "Morning deep work session"
)

print(f"Time blocked: {block['block']['start']} to {block['block']['end']}")
```

## Calendar Integration

### Google Calendar

```python
from src.integrations.google_calendar import GoogleCalendarIntegration

# Initialize
gcal = GoogleCalendarIntegration('config/google_credentials.json')

# Get authorization URL
auth_url = gcal.get_authorization_url('http://localhost:8000/callback')
print(f"Visit: {auth_url}")

# After user authorizes, exchange code for token
# auth_code = "CODE_FROM_OAUTH_FLOW"
# token_data = gcal.exchange_code_for_token(auth_code, redirect_uri)

# Initialize service with token
# gcal.initialize_service(token_data)

# Get upcoming events
# events = gcal.get_events()
# for event in events:
#     print(f"{event.get('summary')}: {event.get('start')}")
```

### Outlook Calendar

```python
from src.integrations.outlook_calendar import OutlookCalendarIntegration

# Initialize
outlook = OutlookCalendarIntegration(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)

# Authenticate
if outlook.authenticate():
    # Get events
    events = outlook.get_events()
    for event in events:
        print(f"{event['subject']}: {event['start']}")
```

## Machine Learning Models

### Energy Prediction

```python
from src.ml_models.energy_predictor import EnergyPredictor
import pandas as pd

predictor = EnergyPredictor()

# Predict energy for specific context
context = {
    'hours_since_sleep': 6,
    'meetings_today': 2,
    'energy_yesterday': 75
}

energy = predictor.predict_single(
    datetime(2026, 2, 26, 10, 0),
    context
)

print(f"Predicted energy: {energy:.1f}")
```

### Productivity Prediction

```python
from src.ml_models.productivity_predictor import ProductivityPredictor

predictor = ProductivityPredictor()

# Predict productivity
context = {
    'energy_level': 80,
    'priority': 8,
    'duration_minutes': 90,
    'meetings_before': 1,
    'context_switches': 0,
    'focus_time_available': 180
}

productivity = predictor.predict_productivity(
    datetime(2026, 2, 26, 10, 0),
    'deep_work',
    context
)

print(f"Expected productivity: {productivity:.1f}%")
```

## API Usage

### Using cURL

```bash
# Get energy patterns
curl -X GET "http://localhost:8000/api/v1/energy/patterns?user_id=user_123&days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Optimize schedule
curl -X POST "http://localhost:8000/api/v1/schedule/optimize" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "meetings": [...],
    "start_date": "2026-02-26T00:00:00Z",
    "end_date": "2026-03-02T00:00:00Z"
  }'

# Configure no-meeting day
curl -X PUT "http://localhost:8000/api/v1/settings/no-meeting-days" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "day_of_week": 2,
    "recurring": true
  }'
```

### Using Python Requests

```python
import requests

API_BASE = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# Get energy patterns
response = requests.get(
    f"{API_BASE}/energy/patterns",
    params={"user_id": "user_123", "days": 30},
    headers=headers
)
patterns = response.json()

# Batch tasks
response = requests.post(
    f"{API_BASE}/meetings/batch",
    json={
        "user_id": "user_123",
        "tasks": [...]
    },
    headers=headers
)
batch_result = response.json()
```
