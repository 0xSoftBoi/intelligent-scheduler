"""Tests for energy analysis module."""

import pytest
from datetime import datetime, timedelta
from src.energy_analysis.energy_analyzer import EnergyAnalyzer


@pytest.fixture
def analyzer():
    return EnergyAnalyzer()


def test_analyze_historical_patterns(analyzer):
    """Test historical pattern analysis."""
    patterns = analyzer.analyze_historical_patterns("test_user", days=30)
    
    assert 'user_id' in patterns
    assert 'hourly_energy' in patterns
    assert 'peak_hours' in patterns
    assert 'low_energy_periods' in patterns
    assert len(patterns['peak_hours']) > 0
    assert len(patterns['recommendations']) > 0


def test_predict_energy_level(analyzer):
    """Test energy level prediction."""
    target_time = datetime.now() + timedelta(hours=2)
    energy = analyzer.predict_energy_level("test_user", target_time)
    
    assert 0 <= energy <= 100
    assert isinstance(energy, (int, float))


def test_calculate_energy_score(analyzer):
    """Test energy score calculation."""
    time_slot = datetime.now().replace(hour=10, minute=0)
    score = analyzer.calculate_energy_score(
        time_slot,
        "deep_work",
        "test_user"
    )
    
    assert 0 <= score <= 100
    assert isinstance(score, (int, float))


def test_peak_hours_identification(analyzer):
    """Test peak hours are within working hours."""
    patterns = analyzer.analyze_historical_patterns("test_user", days=7)
    peak_hours = patterns['peak_hours']
    
    for hour in peak_hours:
        assert 0 <= hour <= 23
