"""Energy pattern analysis algorithms."""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger


class EnergyAnalyzer:
    """Analyzes user energy patterns throughout the day."""

    def __init__(self):
        self.energy_data = pd.DataFrame()
        self.pattern_cache = {}

    def analyze_historical_patterns(self, user_id: str, days: int = 30) -> Dict:
        """Analyze historical energy patterns for a user.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Dictionary containing energy patterns and insights
        """
        logger.info(f"Analyzing {days} days of energy patterns for user {user_id}")
        
        # Load historical data (would query from database in production)
        energy_logs = self._load_energy_logs(user_id, days)
        
        if energy_logs.empty:
            return self._default_energy_pattern()
        
        # Calculate hourly averages
        hourly_energy = energy_logs.groupby('hour')['energy_level'].agg([
            'mean', 'std', 'count'
        ]).to_dict('index')
        
        # Identify peak hours
        peak_hours = self._identify_peak_hours(hourly_energy)
        
        # Identify low-energy periods
        low_energy_periods = self._identify_low_energy_periods(hourly_energy)
        
        # Day of week patterns
        dow_patterns = self._analyze_day_of_week_patterns(energy_logs)
        
        return {
            'user_id': user_id,
            'analysis_period_days': days,
            'hourly_energy': hourly_energy,
            'peak_hours': peak_hours,
            'low_energy_periods': low_energy_periods,
            'day_of_week_patterns': dow_patterns,
            'recommendations': self._generate_recommendations(peak_hours, low_energy_periods)
        }

    def predict_energy_level(self, user_id: str, target_datetime: datetime) -> float:
        """Predict energy level at a specific time.
        
        Args:
            user_id: User identifier
            target_datetime: Target datetime to predict
            
        Returns:
            Predicted energy level (0-100)
        """
        hour = target_datetime.hour
        day_of_week = target_datetime.weekday()
        
        # Get historical pattern for this hour and day
        pattern = self.pattern_cache.get(user_id, {})
        
        if not pattern:
            pattern = self.analyze_historical_patterns(user_id)
            self.pattern_cache[user_id] = pattern
        
        # Base prediction from hourly average
        hourly_data = pattern['hourly_energy'].get(hour, {'mean': 50})
        base_energy = hourly_data['mean']
        
        # Adjust for day of week
        dow_factor = pattern['day_of_week_patterns'].get(day_of_week, 1.0)
        
        predicted_energy = base_energy * dow_factor
        
        return np.clip(predicted_energy, 0, 100)

    def calculate_energy_score(self, time_slot: datetime, meeting_type: str, 
                              user_id: str) -> float:
        """Calculate suitability score for a meeting at a specific time.
        
        Args:
            time_slot: Proposed meeting time
            meeting_type: Type of meeting (deep_work, collaborative, routine)
            user_id: User identifier
            
        Returns:
            Suitability score (0-100)
        """
        energy_level = self.predict_energy_level(user_id, time_slot)
        
        # Meeting type energy requirements
        energy_requirements = {
            'deep_work': 80,
            'collaborative': 60,
            'routine': 40,
            'administrative': 30
        }
        
        required_energy = energy_requirements.get(meeting_type, 50)
        
        # Calculate score based on how well energy matches requirement
        if energy_level >= required_energy:
            score = 100 - ((energy_level - required_energy) / 2)
        else:
            # Penalize heavily if energy is below requirement
            score = (energy_level / required_energy) * 70
        
        return np.clip(score, 0, 100)

    def _load_energy_logs(self, user_id: str, days: int) -> pd.DataFrame:
        """Load energy logs from database (mock implementation)."""
        # Mock data generation for demonstration
        date_range = pd.date_range(end=datetime.now(), periods=days, freq='D')
        data = []
        
        for date in date_range:
            for hour in range(24):
                # Simulate typical energy pattern: high morning, dip after lunch, recovery
                if 6 <= hour < 10:
                    base_energy = np.random.normal(75, 10)
                elif 10 <= hour < 13:
                    base_energy = np.random.normal(80, 8)
                elif 13 <= hour < 15:
                    base_energy = np.random.normal(55, 12)
                elif 15 <= hour < 18:
                    base_energy = np.random.normal(65, 10)
                else:
                    base_energy = np.random.normal(40, 15)
                
                data.append({
                    'timestamp': datetime.combine(date.date(), datetime.min.time()) + timedelta(hours=hour),
                    'hour': hour,
                    'day_of_week': date.weekday(),
                    'energy_level': np.clip(base_energy, 0, 100)
                })
        
        return pd.DataFrame(data)

    def _identify_peak_hours(self, hourly_energy: Dict) -> List[int]:
        """Identify peak energy hours."""
        sorted_hours = sorted(hourly_energy.items(), 
                            key=lambda x: x[1]['mean'], reverse=True)
        return [hour for hour, _ in sorted_hours[:3]]

    def _identify_low_energy_periods(self, hourly_energy: Dict) -> List[int]:
        """Identify low energy periods."""
        sorted_hours = sorted(hourly_energy.items(), 
                            key=lambda x: x[1]['mean'])
        return [hour for hour, _ in sorted_hours[:3]]

    def _analyze_day_of_week_patterns(self, energy_logs: pd.DataFrame) -> Dict:
        """Analyze energy patterns by day of week."""
        dow_avg = energy_logs.groupby('day_of_week')['energy_level'].mean()
        overall_avg = energy_logs['energy_level'].mean()
        
        return {day: avg / overall_avg for day, avg in dow_avg.items()}

    def _generate_recommendations(self, peak_hours: List[int], 
                                 low_energy_periods: List[int]) -> List[str]:
        """Generate scheduling recommendations."""
        recommendations = []
        
        recommendations.append(
            f"Schedule deep work and important meetings during peak hours: "
            f"{', '.join([f'{h}:00' for h in sorted(peak_hours)])}"
        )
        
        recommendations.append(
            f"Avoid demanding tasks during low-energy periods: "
            f"{', '.join([f'{h}:00' for h in sorted(low_energy_periods)])}"
        )
        
        recommendations.append(
            "Consider scheduling routine tasks and administrative work during mid-energy periods"
        )
        
        return recommendations

    def _default_energy_pattern(self) -> Dict:
        """Return default energy pattern when no data available."""
        return {
            'hourly_energy': {},
            'peak_hours': [9, 10, 11],
            'low_energy_periods': [13, 14, 22],
            'day_of_week_patterns': {i: 1.0 for i in range(7)},
            'recommendations': ['Collect more data for personalized insights']
        }
