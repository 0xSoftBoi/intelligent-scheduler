"""Communication batching system that groups similar tasks."""

from datetime import datetime, timedelta
from typing import List, Dict, Set
from collections import defaultdict
from loguru import logger
from enum import Enum


class CommunicationType(Enum):
    """Types of communication tasks."""
    EMAIL = "email"
    SLACK = "slack"
    MEETING = "meeting"
    REVIEW = "review"
    ADMIN = "admin"
    CREATIVE = "creative"


class CommunicationBatcher:
    """Batches similar communication tasks to minimize context switching."""

    def __init__(self):
        self.batch_rules = {
            CommunicationType.EMAIL: {
                'max_batch_size': 50,
                'preferred_duration_minutes': 30,
                'batch_frequency_per_day': 3
            },
            CommunicationType.SLACK: {
                'max_batch_size': 100,
                'preferred_duration_minutes': 20,
                'batch_frequency_per_day': 4
            },
            CommunicationType.MEETING: {
                'max_batch_size': 4,
                'preferred_duration_minutes': 120,
                'batch_frequency_per_day': 1
            },
            CommunicationType.REVIEW: {
                'max_batch_size': 10,
                'preferred_duration_minutes': 60,
                'batch_frequency_per_day': 2
            },
            CommunicationType.ADMIN: {
                'max_batch_size': 20,
                'preferred_duration_minutes': 45,
                'batch_frequency_per_day': 1
            }
        }

    def create_batches(self, tasks: List[Dict], user_id: str) -> Dict:
        """Create batches of similar communication tasks.
        
        Args:
            tasks: List of communication tasks
            user_id: User identifier
            
        Returns:
            Batched tasks organized by type and suggested schedule
        """
        logger.info(f"Creating communication batches for {len(tasks)} tasks")
        
        # Group tasks by type
        grouped_tasks = self._group_by_type(tasks)
        
        # Create batches for each type
        batches = {}
        for comm_type, type_tasks in grouped_tasks.items():
            batches[comm_type.value] = self._batch_tasks_by_type(
                type_tasks, comm_type
            )
        
        # Suggest optimal timing for each batch
        schedule_suggestions = self._suggest_batch_schedule(batches, user_id)
        
        # Calculate efficiency metrics
        metrics = self._calculate_batching_metrics(tasks, batches)
        
        return {
            'batches': batches,
            'schedule_suggestions': schedule_suggestions,
            'metrics': metrics,
            'recommendations': self._generate_batching_recommendations(metrics)
        }

    def should_batch_now(self, task_type: CommunicationType, 
                        pending_count: int, last_batch_time: datetime) -> bool:
        """Determine if tasks should be batched now.
        
        Args:
            task_type: Type of communication
            pending_count: Number of pending tasks
            last_batch_time: When last batch was processed
            
        Returns:
            True if batching should occur now
        """
        rules = self.batch_rules.get(task_type)
        if not rules:
            return False
        
        # Batch if reached max size
        if pending_count >= rules['max_batch_size']:
            return True
        
        # Batch if enough time has passed and have some tasks
        if pending_count > 0:
            time_since_last = (datetime.now() - last_batch_time).total_seconds() / 3600
            min_interval = 24 / rules['batch_frequency_per_day']
            
            if time_since_last >= min_interval:
                return True
        
        return False

    def optimize_batch_timing(self, batch_type: CommunicationType,
                             current_schedule: List[Dict]) -> List[datetime]:
        """Suggest optimal times for batch processing.
        
        Args:
            batch_type: Type of batch
            current_schedule: Current schedule
            
        Returns:
            List of suggested batch times
        """
        rules = self.batch_rules.get(batch_type)
        frequency = rules['batch_frequency_per_day']
        
        # Suggest times based on communication type
        if batch_type == CommunicationType.EMAIL:
            # Morning, after lunch, before EOD
            return [
                datetime.now().replace(hour=9, minute=0),
                datetime.now().replace(hour=14, minute=0),
                datetime.now().replace(hour=16, minute=30)
            ]
        elif batch_type == CommunicationType.SLACK:
            # More frequent, quick checks
            return [
                datetime.now().replace(hour=10, minute=0),
                datetime.now().replace(hour=12, minute=0),
                datetime.now().replace(hour=15, minute=0),
                datetime.now().replace(hour=17, minute=0)
            ]
        elif batch_type == CommunicationType.REVIEW:
            # Deep work periods
            return [
                datetime.now().replace(hour=10, minute=0),
                datetime.now().replace(hour=15, minute=0)
            ]
        else:
            # Generic distribution throughout day
            times = []
            work_hours = 9
            interval = work_hours / frequency
            
            for i in range(frequency):
                hour = 9 + int(i * interval)
                times.append(datetime.now().replace(hour=hour, minute=0))
            
            return times

    def merge_related_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Merge related tasks that can be handled together.
        
        Args:
            tasks: List of tasks
            
        Returns:
            Merged task list
        """
        # Group by project/topic
        topic_groups = defaultdict(list)
        
        for task in tasks:
            topic = task.get('topic', 'general')
            topic_groups[topic].append(task)
        
        merged = []
        for topic, topic_tasks in topic_groups.items():
            if len(topic_tasks) > 1:
                # Merge related tasks
                merged.append({
                    'id': f"merged_{topic}",
                    'type': topic_tasks[0]['type'],
                    'topic': topic,
                    'subtasks': topic_tasks,
                    'estimated_duration': sum(
                        t.get('duration', 5) for t in topic_tasks
                    ),
                    'priority': max(t.get('priority', 1) for t in topic_tasks)
                })
            else:
                merged.extend(topic_tasks)
        
        return merged

    def _group_by_type(self, tasks: List[Dict]) -> Dict[CommunicationType, List[Dict]]:
        """Group tasks by communication type."""
        grouped = defaultdict(list)
        
        for task in tasks:
            task_type = task.get('type', 'email')
            try:
                comm_type = CommunicationType(task_type.lower())
                grouped[comm_type].append(task)
            except ValueError:
                logger.warning(f"Unknown task type: {task_type}")
                grouped[CommunicationType.ADMIN].append(task)
        
        return grouped

    def _batch_tasks_by_type(self, tasks: List[Dict],
                            comm_type: CommunicationType) -> List[Dict]:
        """Create batches for a specific communication type."""
        rules = self.batch_rules.get(comm_type, {})
        max_batch_size = rules.get('max_batch_size', 20)
        
        # Sort by priority
        sorted_tasks = sorted(tasks, key=lambda t: t.get('priority', 0), reverse=True)
        
        # Create batches
        batches = []
        current_batch = []
        
        for task in sorted_tasks:
            current_batch.append(task)
            
            if len(current_batch) >= max_batch_size:
                batches.append({
                    'batch_id': f"{comm_type.value}_batch_{len(batches) + 1}",
                    'tasks': current_batch,
                    'estimated_duration': rules.get('preferred_duration_minutes', 30),
                    'task_count': len(current_batch)
                })
                current_batch = []
        
        # Add remaining tasks
        if current_batch:
            batches.append({
                'batch_id': f"{comm_type.value}_batch_{len(batches) + 1}",
                'tasks': current_batch,
                'estimated_duration': rules.get('preferred_duration_minutes', 30),
                'task_count': len(current_batch)
            })
        
        return batches

    def _suggest_batch_schedule(self, batches: Dict, user_id: str) -> List[Dict]:
        """Suggest schedule for batch processing."""
        suggestions = []
        
        for batch_type, type_batches in batches.items():
            try:
                comm_type = CommunicationType(batch_type)
                optimal_times = self.optimize_batch_timing(comm_type, [])
                
                for i, batch in enumerate(type_batches):
                    if i < len(optimal_times):
                        suggestions.append({
                            'batch_id': batch['batch_id'],
                            'suggested_time': optimal_times[i],
                            'duration': batch['estimated_duration'],
                            'reason': f"Optimal time for {batch_type} batch processing"
                        })
            except ValueError:
                continue
        
        return suggestions

    def _calculate_batching_metrics(self, original_tasks: List[Dict],
                                   batches: Dict) -> Dict:
        """Calculate batching efficiency metrics."""
        total_batches = sum(len(b) for b in batches.values())
        total_tasks = len(original_tasks)
        
        # Calculate context switches saved
        context_switches_before = total_tasks
        context_switches_after = total_batches
        
        return {
            'total_tasks': total_tasks,
            'total_batches': total_batches,
            'avg_batch_size': total_tasks / total_batches if total_batches > 0 else 0,
            'context_switches_saved': context_switches_before - context_switches_after,
            'efficiency_improvement': (
                (context_switches_before - context_switches_after) / 
                context_switches_before * 100
            ) if context_switches_before > 0 else 0
        }

    def _generate_batching_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations for batching optimization."""
        recommendations = []
        
        efficiency = metrics.get('efficiency_improvement', 0)
        
        if efficiency > 70:
            recommendations.append(
                "Excellent batching efficiency! Continue current strategy."
            )
        elif efficiency > 50:
            recommendations.append(
                "Good batching efficiency. Consider consolidating smaller batches."
            )
        else:
            recommendations.append(
                "Batching efficiency could be improved. Review batch sizes and timing."
            )
        
        if metrics.get('avg_batch_size', 0) < 3:
            recommendations.append(
                "Small batch sizes detected. Consider increasing batch windows."
            )
        
        return recommendations
