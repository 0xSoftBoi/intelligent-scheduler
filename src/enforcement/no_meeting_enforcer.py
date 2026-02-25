"""No-meeting day enforcement logic."""

from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Set
from loguru import logger
from enum import Enum


class BlockType(Enum):
    """Types of calendar blocks."""
    NO_MEETING_DAY = "no_meeting_day"
    FOCUS_TIME = "focus_time"
    PERSONAL_TIME = "personal_time"
    FLEXIBLE = "flexible"


class NoMeetingEnforcer:
    """Enforces no-meeting days and focus time blocks."""

    def __init__(self):
        self.default_rules = {
            'min_no_meeting_days_per_week': 1,
            'min_focus_blocks_per_day': 2,
            'focus_block_duration_minutes': 90,
            'enforce_exceptions': False,
            'allowed_exception_types': ['urgent', 'executive']
        }

    def enforce_no_meeting_policy(self, user_id: str, schedule: Dict,
                                 config: Optional[Dict] = None) -> Dict:
        """Enforce no-meeting day policies.
        
        Args:
            user_id: User identifier
            schedule: Current schedule to enforce
            config: Optional custom configuration
            
        Returns:
            Enforcement result with violations and corrections
        """
        logger.info(f"Enforcing no-meeting policy for user {user_id}")
        
        rules = {**self.default_rules, **(config or {})}
        violations = []
        corrections = []
        
        # Check weekly no-meeting day requirement
        no_meeting_days = self._identify_no_meeting_days(schedule)
        
        if len(no_meeting_days) < rules['min_no_meeting_days_per_week']:
            violations.append({
                'type': 'insufficient_no_meeting_days',
                'severity': 'high',
                'message': f"Only {len(no_meeting_days)} no-meeting days scheduled, "
                          f"require {rules['min_no_meeting_days_per_week']}",
                'suggested_action': 'Add more no-meeting days'
            })
            
            # Suggest days to convert
            suggested_days = self._suggest_no_meeting_days(schedule, rules)
            corrections.extend(suggested_days)
        
        # Check for violations on designated no-meeting days
        for day in no_meeting_days:
            day_violations = self._check_day_violations(schedule, day, rules)
            violations.extend(day_violations)
        
        # Check focus time blocks
        focus_violations = self._check_focus_time_blocks(schedule, rules)
        violations.extend(focus_violations)
        
        # Generate enforcement report
        return {
            'user_id': user_id,
            'enforcement_date': datetime.now(),
            'no_meeting_days_configured': no_meeting_days,
            'violations': violations,
            'corrections': corrections,
            'compliance_score': self._calculate_compliance_score(violations),
            'recommendations': self._generate_enforcement_recommendations(violations)
        }

    def block_time_slot(self, user_id: str, start: datetime, end: datetime,
                       block_type: BlockType, reason: str) -> Dict:
        """Block a time slot on the calendar.
        
        Args:
            user_id: User identifier
            start: Block start time
            end: Block end time
            block_type: Type of block
            reason: Reason for blocking
            
        Returns:
            Block confirmation
        """
        logger.info(f"Blocking time slot: {start} to {end} ({block_type.value})")
        
        block = {
            'id': f"block_{int(datetime.now().timestamp())}",
            'user_id': user_id,
            'start': start,
            'end': end,
            'type': block_type.value,
            'reason': reason,
            'is_recurring': False,
            'exceptions_allowed': block_type == BlockType.FLEXIBLE
        }
        
        # Would save to database in production
        return {
            'success': True,
            'block': block,
            'message': f"Time blocked successfully: {reason}"
        }

    def check_meeting_allowed(self, user_id: str, proposed_time: datetime,
                            meeting_type: str, override_code: Optional[str] = None) -> Dict:
        """Check if a meeting can be scheduled at proposed time.
        
        Args:
            user_id: User identifier
            proposed_time: Proposed meeting time
            meeting_type: Type of meeting
            override_code: Optional override code for exceptions
            
        Returns:
            Allowance decision with reason
        """
        # Get user's blocked times (would query from database)
        blocked_times = self._get_blocked_times(user_id, proposed_time.date())
        
        # Check if time is blocked
        for block in blocked_times:
            if block['start'] <= proposed_time < block['end']:
                # Check if exceptions allowed
                if block['exceptions_allowed'] and meeting_type in ['urgent', 'executive']:
                    return {
                        'allowed': True,
                        'reason': f"Exception granted for {meeting_type} meeting",
                        'warning': f"Conflicts with {block['type']} block"
                    }
                else:
                    return {
                        'allowed': False,
                        'reason': f"Time blocked for {block['type']}: {block['reason']}",
                        'alternative_times': self._suggest_alternative_times(
                            user_id, proposed_time
                        )
                    }
        
        return {
            'allowed': True,
            'reason': 'No conflicts detected'
        }

    def configure_no_meeting_day(self, user_id: str, day_of_week: int,
                               recurring: bool = True) -> Dict:
        """Configure a no-meeting day.
        
        Args:
            user_id: User identifier
            day_of_week: Day of week (0=Monday, 6=Sunday)
            recurring: Whether this repeats weekly
            
        Returns:
            Configuration result
        """
        if not 0 <= day_of_week <= 6:
            return {
                'success': False,
                'error': 'Invalid day_of_week. Must be 0-6.'
            }
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        config = {
            'user_id': user_id,
            'day_of_week': day_of_week,
            'day_name': day_names[day_of_week],
            'recurring': recurring,
            'exceptions_allowed': False,
            'active': True
        }
        
        logger.info(f"Configured no-meeting day: {day_names[day_of_week]} for user {user_id}")
        
        return {
            'success': True,
            'configuration': config,
            'message': f"{day_names[day_of_week]} set as no-meeting day"
        }

    def _identify_no_meeting_days(self, schedule: Dict) -> List[datetime]:
        """Identify designated no-meeting days in schedule."""
        # Would query from user configuration in production
        # For now, return mock data
        return [datetime.now() + timedelta(days=i) for i in [2, 4]]  # Wed, Fri

    def _check_day_violations(self, schedule: Dict, day: datetime,
                            rules: Dict) -> List[Dict]:
        """Check for violations on a specific no-meeting day."""
        violations = []
        
        # Would check actual schedule in production
        # Mock implementation
        day_meetings = schedule.get('scheduled_meetings', {})
        
        for meeting_id, meeting_data in day_meetings.items():
            meeting_time = meeting_data['slot'].start
            if meeting_time.date() == day.date():
                # Check if exception is allowed
                meeting = meeting_data['meeting']
                if meeting.priority < 9:  # Only allow critical meetings
                    violations.append({
                        'type': 'no_meeting_day_violation',
                        'severity': 'medium',
                        'meeting_id': meeting_id,
                        'meeting_title': meeting.title,
                        'scheduled_time': meeting_time,
                        'message': f"Meeting scheduled on no-meeting day: {day.date()}"
                    })
        
        return violations

    def _check_focus_time_blocks(self, schedule: Dict, rules: Dict) -> List[Dict]:
        """Check if minimum focus time blocks are maintained."""
        violations = []
        
        # Would analyze actual schedule for focus time
        # Mock implementation
        focus_blocks_count = 1  # Simulated
        
        if focus_blocks_count < rules['min_focus_blocks_per_day']:
            violations.append({
                'type': 'insufficient_focus_time',
                'severity': 'medium',
                'message': f"Only {focus_blocks_count} focus blocks scheduled, "
                          f"require {rules['min_focus_blocks_per_day']}"
            })
        
        return violations

    def _suggest_no_meeting_days(self, schedule: Dict, rules: Dict) -> List[Dict]:
        """Suggest days that should be converted to no-meeting days."""
        corrections = []
        
        # Suggest Wednesday and Friday as common no-meeting days
        suggested_days = [2, 4]  # Wed, Fri
        
        for day in suggested_days:
            corrections.append({
                'type': 'add_no_meeting_day',
                'day_of_week': day,
                'reason': 'Recommended for focus and deep work'
            })
        
        return corrections

    def _get_blocked_times(self, user_id: str, date: datetime.date) -> List[Dict]:
        """Get blocked times for a specific date."""
        # Would query from database in production
        # Mock implementation
        return [
            {
                'start': datetime.combine(date, time(9, 0)),
                'end': datetime.combine(date, time(11, 0)),
                'type': BlockType.FOCUS_TIME.value,
                'reason': 'Morning deep work',
                'exceptions_allowed': False
            }
        ]

    def _suggest_alternative_times(self, user_id: str,
                                  original_time: datetime) -> List[datetime]:
        """Suggest alternative meeting times."""
        alternatives = []
        
        # Suggest next day at same time
        alternatives.append(original_time + timedelta(days=1))
        
        # Suggest 2 hours later same day
        alternatives.append(original_time + timedelta(hours=2))
        
        # Suggest next available afternoon
        next_afternoon = original_time.replace(hour=14, minute=0)
        if next_afternoon <= original_time:
            next_afternoon += timedelta(days=1)
        alternatives.append(next_afternoon)
        
        return alternatives

    def _calculate_compliance_score(self, violations: List[Dict]) -> float:
        """Calculate policy compliance score."""
        if not violations:
            return 100.0
        
        # Deduct points based on violation severity
        score = 100.0
        severity_penalties = {'low': 5, 'medium': 10, 'high': 20}
        
        for violation in violations:
            penalty = severity_penalties.get(violation.get('severity', 'medium'), 10)
            score -= penalty
        
        return max(0.0, score)

    def _generate_enforcement_recommendations(self, violations: List[Dict]) -> List[str]:
        """Generate recommendations based on violations."""
        if not violations:
            return ["No violations detected. Policy compliance is excellent."]
        
        recommendations = []
        
        # Group by violation type
        violation_types = set(v['type'] for v in violations)
        
        if 'insufficient_no_meeting_days' in violation_types:
            recommendations.append(
                "Schedule at least one additional no-meeting day per week for focus time"
            )
        
        if 'no_meeting_day_violation' in violation_types:
            recommendations.append(
                "Reschedule non-critical meetings away from designated no-meeting days"
            )
        
        if 'insufficient_focus_time' in violation_types:
            recommendations.append(
                "Block additional 90-minute focus time slots in your calendar"
            )
        
        return recommendations
