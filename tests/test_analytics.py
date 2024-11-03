from datetime import datetime, timedelta

import pytest

from habit_tracker import analytics


@pytest.fixture
def consecutive_dates():
    """Fixture for consecutive dates"""
    base = datetime.now()
    return [base - timedelta(days=i) for i in range(5)]


@pytest.fixture
def non_consecutive_dates():
    """Fixture for non-consecutive dates"""
    base = datetime.now()
    return [base, base - timedelta(days=2), base - timedelta(days=5)]


def test_days_between():
    """Test days between calculation"""
    date1 = datetime.now()
    date2 = date1 + timedelta(days=5)
    assert analytics.days_between(date1, date2) == 5


def test_is_consecutive_daily():
    """Test consecutive daily check"""
    date1 = datetime.now()
    date2 = date1 - timedelta(days=1)
    assert analytics.is_consecutive_daily(date1, date2)

    date3 = date1 - timedelta(days=2)
    assert not analytics.is_consecutive_daily(date1, date3)


def test_calculate_streaks(consecutive_dates):
    """Test streak calculation"""
    result = analytics.calculate_streaks(
        consecutive_dates, analytics.is_consecutive_daily
    )
    assert result["current"] == 5
    assert result["longest"] == 5


def test_completion_rate():
    """Test completion rate calculation"""
    start_date = datetime.now() - timedelta(days=10)
    dates = [datetime.now() - timedelta(days=i) for i in range(5)]
    rate = analytics.calculate_completion_rate(dates, start_date, "daily")
    assert 0 <= rate <= 100


def test_analyze_habit(sample_habit, consecutive_dates):
    """Test habit analysis"""
    for date in consecutive_dates:
        sample_habit.add_completion(date)

    result = analytics.analyze_habit(sample_habit)
    assert "total_completions" in result
    assert "current" in result
    assert "longest" in result
    assert "completion_rate" in result
    assert "break_count" in result


def test_generate_improvement_suggestions():
    """Test suggestion generation"""
    stats = {
        "completion_rate": 25,
        "current": 1,
        "longest": 5,
        "total_completions": 10,
        "break_count": 5,
    }
    suggestions = analytics.generate_improvement_suggestions(stats)
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
