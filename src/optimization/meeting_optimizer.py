"""Meeting optimization engine that schedules based on energy levels and patterns."""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger
from dataclasses import dataclass

from src.energy_analysis.energy_analyzer import EnergyAnalyzer


@dataclass
class Meeting:
    """Meeting data structure."""
    id: str
    title: str
    duration_minutes: int
    meeting_type: str  # deep_work, collaborative, routine, administrative
    participants: List[str]
    priority: int  # 1-10
    flexibility: str  # high, medium, low
    preferred_time: Optional[datetime] = None
    earliest_start: Optional[datetime] = None
    latest_end: Optional[datetime] = None


@dataclass
class TimeSlot:
    """Available time slot."""
    start: datetime
    end: datetime
    score: float
    conflicts: List[str]


class MeetingOptimizer:
    """Optimizes meeting schedules based on multiple factors."""

    def __init__(self):
        self.energy_analyzer = EnergyAnalyzer()
        self.optimization_weights = {
            'energy_score': 0.35,
            'participant_availability': 0.25,
            'time_preference': 0.15,
            'priority': 0.15,
            'grouping_efficiency': 0.10
        }

    def optimize_schedule(self, meetings: List[Meeting], user_id: str,
                         start_date: datetime, end_date: datetime) -> Dict:
        """Optimize meeting schedule for a given period.
        
        Args:
            meetings: List of meetings to schedule
            user_id: User identifier
            start_date: Start of scheduling period
            end_date: End of scheduling period
            
        Returns:
            Optimized schedule with meeting assignments
        """
        logger.info(f"Optimizing schedule for {len(meetings)} meetings")
        
        # Sort meetings by priority and flexibility
        sorted_meetings = self._prioritize_meetings(meetings)
        
        # Generate available time slots
        available_slots = self._generate_time_slots(start_date, end_date, user_id)
        
        # Schedule meetings using greedy algorithm with backtracking
        scheduled = {}
        unscheduled = []
        
        for meeting in sorted_meetings:
            best_slot = self._find_best_slot(
                meeting, available_slots, user_id, scheduled
            )
            
            if best_slot:
                scheduled[meeting.id] = {
                    'meeting': meeting,
                    'slot': best_slot,
                    'score': best_slot.score
                }
                # Remove allocated time from available slots
                available_slots = self._update_available_slots(
                    available_slots, best_slot
                )
            else:
                unscheduled.append(meeting)
                logger.warning(f"Could not schedule meeting: {meeting.title}")
        
        # Calculate optimization metrics
        metrics = self._calculate_optimization_metrics(scheduled, unscheduled)
        
        return {
            'scheduled_meetings': scheduled,
            'unscheduled_meetings': unscheduled,
            'metrics': metrics,
            'recommendations': self._generate_optimization_recommendations(metrics)
        }

    def suggest_meeting_time(self, meeting: Meeting, user_id: str,
                            participants: List[str],
                            date_range: Tuple[datetime, datetime]) -> List[TimeSlot]:
        """Suggest optimal meeting times.
        
        Args:
            meeting: Meeting to schedule
            user_id: Primary user
            participants: List of participant IDs
            date_range: (start_date, end_date) tuple
            
        Returns:
            List of suggested time slots ranked by score
        """
        start_date, end_date = date_range
        available_slots = self._generate_time_slots(start_date, end_date, user_id)
        
        # Score each slot
        scored_slots = []
        for slot in available_slots:
            if slot.end - slot.start >= timedelta(minutes=meeting.duration_minutes):
                score = self._calculate_slot_score(
                    meeting, slot, user_id, participants
                )
                slot.score = score
                scored_slots.append(slot)
        
        # Sort by score and return top suggestions
        scored_slots.sort(key=lambda x: x.score, reverse=True)
        return scored_slots[:5]

    def reschedule_meeting(self, meeting_id: str, current_schedule: Dict,
                          user_id: str) -> Optional[TimeSlot]:
        """Attempt to reschedule a meeting for better optimization.
        
        Args:
            meeting_id: Meeting to reschedule
            current_schedule: Current schedule state
            user_id: User identifier
            
        Returns:
            New time slot if better option found, None otherwise
        """
        if meeting_id not in current_schedule:
            return None
        
        meeting = current_schedule[meeting_id]['meeting']
        current_slot = current_schedule[meeting_id]['slot']
        current_score = current_slot.score
        
        # Look for better slots in next 7 days
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        suggestions = self.suggest_meeting_time(
            meeting, user_id, meeting.participants, (start_date, end_date)
        )
        
        # Return if significant improvement found
        if suggestions and suggestions[0].score > current_score * 1.15:
            return suggestions[0]
        
        return None

    def _prioritize_meetings(self, meetings: List[Meeting]) -> List[Meeting]:
        """Sort meetings by priority and constraints."""
        # Sort by: low flexibility first, then high priority, then preferred time
        flexibility_order = {'low': 0, 'medium': 1, 'high': 2}
        
        return sorted(meetings, key=lambda m: (
            flexibility_order.get(m.flexibility, 1),
            -m.priority,
            0 if m.preferred_time is None else 1
        ))

    def _generate_time_slots(self, start_date: datetime, end_date: datetime,
                            user_id: str) -> List[TimeSlot]:
        """Generate available time slots."""
        slots = []
        current = start_date.replace(hour=8, minute=0, second=0, microsecond=0)
        
        while current < end_date:
            # Only generate slots during work hours (8 AM - 6 PM)
            if 8 <= current.hour < 18:
                slot_end = current + timedelta(minutes=30)
                slots.append(TimeSlot(
                    start=current,
                    end=slot_end,
                    score=0.0,
                    conflicts=[]
                ))
            
            current += timedelta(minutes=30)
            
            # Skip to next day if past work hours
            if current.hour >= 18:
                current = (current + timedelta(days=1)).replace(
                    hour=8, minute=0, second=0, microsecond=0
                )
        
        return slots

    def _find_best_slot(self, meeting: Meeting, available_slots: List[TimeSlot],
                       user_id: str, current_schedule: Dict) -> Optional[TimeSlot]:
        """Find best available slot for a meeting."""
        duration = timedelta(minutes=meeting.duration_minutes)
        best_slot = None
        best_score = -1
        
        for i, slot in enumerate(available_slots):
            # Check if slot can accommodate meeting duration
            potential_end = slot.start + duration
            
            # Verify continuous availability
            if self._is_slot_available(slot.start, potential_end, available_slots[i:]):
                score = self._calculate_slot_score(
                    meeting, slot, user_id, meeting.participants
                )
                
                if score > best_score:
                    best_score = score
                    best_slot = TimeSlot(
                        start=slot.start,
                        end=potential_end,
                        score=score,
                        conflicts=[]
                    )
        
        return best_slot

    def _calculate_slot_score(self, meeting: Meeting, slot: TimeSlot,
                             user_id: str, participants: List[str]) -> float:
        """Calculate score for a meeting in a specific slot."""
        # Energy score
        energy_score = self.energy_analyzer.calculate_energy_score(
            slot.start, meeting.meeting_type, user_id
        )
        
        # Participant availability (simplified - would check actual calendars)
        availability_score = 85.0  # Mock score
        
        # Time preference score
        if meeting.preferred_time:
            time_diff = abs((slot.start - meeting.preferred_time).total_seconds())
            pref_score = max(0, 100 - (time_diff / 3600))
        else:
            pref_score = 70.0
        
        # Priority score
        priority_score = meeting.priority * 10
        
        # Grouping efficiency (prefer grouping similar meetings)
        grouping_score = 75.0  # Would analyze adjacent meetings
        
        # Weighted combination
        total_score = (
            energy_score * self.optimization_weights['energy_score'] +
            availability_score * self.optimization_weights['participant_availability'] +
            pref_score * self.optimization_weights['time_preference'] +
            priority_score * self.optimization_weights['priority'] +
            grouping_score * self.optimization_weights['grouping_efficiency']
        )
        
        return total_score

    def _is_slot_available(self, start: datetime, end: datetime,
                          slots: List[TimeSlot]) -> bool:
        """Check if time range is continuously available."""
        current = start
        for slot in slots:
            if current >= end:
                return True
            if slot.start == current:
                current = slot.end
            else:
                return False
        return current >= end

    def _update_available_slots(self, slots: List[TimeSlot],
                               allocated: TimeSlot) -> List[TimeSlot]:
        """Remove allocated time from available slots."""
        return [
            slot for slot in slots
            if slot.end <= allocated.start or slot.start >= allocated.end
        ]

    def _calculate_optimization_metrics(self, scheduled: Dict,
                                       unscheduled: List[Meeting]) -> Dict:
        """Calculate optimization performance metrics."""
        total_meetings = len(scheduled) + len(unscheduled)
        
        if total_meetings == 0:
            return {}
        
        avg_score = np.mean([m['score'] for m in scheduled.values()]) if scheduled else 0
        
        return {
            'total_meetings': total_meetings,
            'scheduled_count': len(scheduled),
            'unscheduled_count': len(unscheduled),
            'success_rate': len(scheduled) / total_meetings * 100,
            'average_optimization_score': avg_score,
            'high_priority_scheduled': sum(
                1 for m in scheduled.values() if m['meeting'].priority >= 7
            )
        }

    def _generate_optimization_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations based on optimization results."""
        recommendations = []
        
        if metrics.get('success_rate', 0) < 80:
            recommendations.append(
                "Consider extending the scheduling window or reducing meeting count"
            )
        
        if metrics.get('average_optimization_score', 0) < 70:
            recommendations.append(
                "Some meetings may be scheduled at suboptimal times. Review and adjust."
            )
        
        return recommendations
