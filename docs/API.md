# Intelligent Scheduler API Documentation

## Overview

The Intelligent Scheduler API provides endpoints for optimizing meeting schedules based on energy patterns, productivity analytics, and intelligent task batching.

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: Bearer token required for all endpoints (except health checks)

## Authentication

```bash
Authorization: Bearer YOUR_API_TOKEN
```

## Endpoints

### Energy Analysis

#### Get Energy Patterns

```http
GET /api/v1/energy/patterns
```

**Query Parameters**:
- `user_id` (required): User identifier
- `days` (optional): Number of days to analyze (default: 30)

**Response**:
```json
{
  "user_id": "user_123",
  "analysis_period_days": 30,
  "hourly_energy": {
    "9": {"mean": 75.5, "std": 10.2},
    "10": {"mean": 82.3, "std": 8.5}
  },
  "peak_hours": [9, 10, 11],
  "low_energy_periods": [13, 14, 22],
  "recommendations": ["Schedule deep work during peak hours..."]
}
```

#### Predict Energy Level

```http
POST /api/v1/energy/predict
```

**Request Body**:
```json
{
  "user_id": "user_123",
  "target_datetime": "2026-02-26T10:00:00Z"
}
```

**Response**:
```json
{
  "user_id": "user_123",
  "target_datetime": "2026-02-26T10:00:00Z",
  "predicted_energy_level": 78.5,
  "confidence": 0.85
}
```

### Meeting Optimization

#### Optimize Schedule

```http
POST /api/v1/schedule/optimize
```

**Request Body**:
```json
{
  "user_id": "user_123",
  "meetings": [
    {
      "id": "meeting_1",
      "title": "Team Sync",
      "duration_minutes": 30,
      "meeting_type": "collaborative",
      "participants": ["user_456", "user_789"],
      "priority": 7,
      "flexibility": "medium"
    }
  ],
  "start_date": "2026-02-26T00:00:00Z",
  "end_date": "2026-03-02T00:00:00Z"
}
```

**Response**:
```json
{
  "scheduled_meetings": {
    "meeting_1": {
      "meeting": {...},
      "slot": {
        "start": "2026-02-26T10:00:00Z",
        "end": "2026-02-26T10:30:00Z",
        "score": 85.5
      }
    }
  },
  "unscheduled_meetings": [],
  "metrics": {
    "success_rate": 100,
    "average_optimization_score": 85.5
  }
}
```

#### Suggest Meeting Times

```http
POST /api/v1/meetings/suggest
```

**Request Body**:
```json
{
  "user_id": "user_123",
  "meeting": {
    "title": "Project Review",
    "duration_minutes": 60,
    "meeting_type": "deep_work",
    "participants": ["user_456"]
  },
  "date_range": {
    "start": "2026-02-26T00:00:00Z",
    "end": "2026-02-28T00:00:00Z"
  }
}
```

**Response**:
```json
{
  "suggestions": [
    {
      "start": "2026-02-26T10:00:00Z",
      "end": "2026-02-26T11:00:00Z",
      "score": 92.3,
      "reason": "Peak energy period for deep work"
    }
  ]
}
```

### Communication Batching

#### Create Task Batches

```http
POST /api/v1/meetings/batch
```

**Request Body**:
```json
{
  "user_id": "user_123",
  "tasks": [
    {
      "id": "task_1",
      "type": "email",
      "topic": "project_alpha",
      "priority": 5,
      "duration": 5
    }
  ]
}
```

**Response**:
```json
{
  "batches": {
    "email": [
      {
        "batch_id": "email_batch_1",
        "tasks": [...],
        "estimated_duration": 30,
        "task_count": 15
      }
    ]
  },
  "schedule_suggestions": [
    {
      "batch_id": "email_batch_1",
      "suggested_time": "2026-02-26T09:00:00Z",
      "duration": 30
    }
  ],
  "metrics": {
    "efficiency_improvement": 75.5
  }
}
```

### No-Meeting Day Enforcement

#### Configure No-Meeting Day

```http
PUT /api/v1/settings/no-meeting-days
```

**Request Body**:
```json
{
  "user_id": "user_123",
  "day_of_week": 2,
  "recurring": true
}
```

**Response**:
```json
{
  "success": true,
  "configuration": {
    "day_of_week": 2,
    "day_name": "Wednesday",
    "recurring": true,
    "active": true
  }
}
```

#### Check Meeting Allowance

```http
POST /api/v1/meetings/check-allowed
```

**Request Body**:
```json
{
  "user_id": "user_123",
  "proposed_time": "2026-02-26T10:00:00Z",
  "meeting_type": "routine"
}
```

**Response**:
```json
{
  "allowed": false,
  "reason": "Time blocked for focus_time: Morning deep work",
  "alternative_times": [
    "2026-02-27T10:00:00Z",
    "2026-02-26T12:00:00Z"
  ]
}
```

### Calendar Integration

#### Connect Google Calendar

```http
POST /api/v1/integrations/google/connect
```

**Request Body**:
```json
{
  "user_id": "user_123",
  "auth_code": "GOOGLE_AUTH_CODE"
}
```

**Response**:
```json
{
  "success": true,
  "integration_id": "integration_123",
  "calendar_name": "primary",
  "sync_enabled": true
}
```

#### Sync Calendar Events

```http
POST /api/v1/integrations/sync
```

**Request Body**:
```json
{
  "user_id": "user_123",
  "integration_id": "integration_123",
  "start_date": "2026-02-26T00:00:00Z",
  "end_date": "2026-03-02T00:00:00Z"
}
```

### Webhooks

#### Calendar Update Webhook

```http
POST /api/v1/webhooks/calendar
```

**Request Body** (from calendar provider):
```json
{
  "event_type": "event.created",
  "event_id": "event_123",
  "calendar_id": "cal_456",
  "user_id": "user_123",
  "event_data": {
    "start": "2026-02-26T10:00:00Z",
    "end": "2026-02-26T11:00:00Z",
    "title": "New Meeting"
  }
}
```

**Response**:
```json
{
  "received": true,
  "processing_status": "queued",
  "optimization_triggered": true
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {...}
  }
}
```

**Common Error Codes**:
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error

## Rate Limiting

- **Standard**: 100 requests per minute
- **Optimization**: 10 requests per minute
- **Webhooks**: 1000 requests per minute

## Webhooks Configuration

To receive real-time updates, register webhook endpoints:

```http
POST /api/v1/webhooks/register
```

**Request Body**:
```json
{
  "user_id": "user_123",
  "webhook_url": "https://your-app.com/webhook",
  "events": ["schedule.optimized", "meeting.scheduled", "violation.detected"]
}
```

## SDK Examples

### Python

```python
import requests

API_BASE = "http://localhost:8000/api/v1"
API_TOKEN = "your_token_here"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Get energy patterns
response = requests.get(
    f"{API_BASE}/energy/patterns",
    params={"user_id": "user_123", "days": 30},
    headers=headers
)

patterns = response.json()
print(f"Peak hours: {patterns['peak_hours']}")
```

### JavaScript

```javascript
const API_BASE = 'http://localhost:8000/api/v1';
const API_TOKEN = 'your_token_here';

const headers = {
  'Authorization': `Bearer ${API_TOKEN}`,
  'Content-Type': 'application/json'
};

// Optimize schedule
fetch(`${API_BASE}/schedule/optimize`, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify({
    user_id: 'user_123',
    meetings: [...],
    start_date: '2026-02-26T00:00:00Z',
    end_date: '2026-03-02T00:00:00Z'
  })
})
.then(response => response.json())
.then(data => console.log('Optimized schedule:', data));
```

## Support

For API support:
- Email: api-support@intelligent-scheduler.com
- Documentation: https://docs.intelligent-scheduler.com
- Status: https://status.intelligent-scheduler.com
