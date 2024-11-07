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


@pytest.fixture
def weekly_dates():
    """Fixture for dates in consecutive weeks"""
    base = datetime(2024, 1, 1)  # Tuesday of week 1
    return [
        base,
        base + timedelta(days=7),  # Next week
        base + timedelta(days=14),  # Week after
    ]

@pytest.fixture
def cross_year_dates():
    """Fixture for dates crossing year boundary"""
    return [
        datetime(2023, 12, 31),  # Sunday of week 52
        datetime(2024, 1, 1),    # Monday of week 1
    ]

@pytest.fixture
def sample_habits():
    """Fixture for multiple habits"""
    class MockHabit:
        def __init__(self, name, periodicity, created_at, completions):
            self.name = name
            self.periodicity = periodicity
            self.created_at = created_at
            self._completions = completions

        def get_completions(self):
            return self._completions

    base_date = datetime(2024, 1, 1)
    return [
        MockHabit(
            "Daily Habit",
            "daily",
            base_date,
            [base_date + timedelta(days=i) for i in range(5)]
        ),
        MockHabit(
            "Weekly Habit",
            "weekly",
            base_date,
            [base_date + timedelta(weeks=i) for i in range(3)]
        )
    ]


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


def test_is_consecutive_weekly():
    """Test weekly consecutive date checks"""
    # Same week
    date1 = datetime(2024, 1, 1)  # Monday
    date2 = datetime(2024, 1, 5)  # Friday
    assert analytics.is_consecutive_weekly(date1, date2)

    # Consecutive weeks
    date3 = datetime(2024, 1, 8)  # Next Monday
    assert analytics.is_consecutive_weekly(date1, date3)

    # Non-consecutive weeks
    date4 = datetime(2024, 1, 15)  # Two weeks later
    assert not analytics.is_consecutive_weekly(date1, date4)


def test_is_consecutive_weekly_year_boundary(cross_year_dates):
    """Test weekly consecutive checks across year boundary"""
    date1, date2 = cross_year_dates
    assert analytics.is_consecutive_weekly(date1, date2)

def test_calculate_breaks():
    """Test break calculation"""
    # Daily habit breaks
    dates = [
        datetime(2024, 1, 1),
        datetime(2024, 1, 2),
        datetime(2024, 1, 4),  # Break
        datetime(2024, 1, 5),
        datetime(2024, 1, 7),  # Break
    ]
    breaks = analytics.calculate_breaks(dates, analytics.is_consecutive_daily)
    assert breaks == 2

    # Weekly habit breaks
    weekly_dates = [
        datetime(2024, 1, 1),
        datetime(2024, 1, 8),
        datetime(2024, 1, 22),  # Break (skipped a week)
    ]
    breaks = analytics.calculate_breaks(weekly_dates, analytics.is_consecutive_weekly)
    assert breaks == 1

def test_calculate_streaks(consecutive_dates):
    """Test streak calculation"""
    result = analytics.calculate_streaks(
        consecutive_dates, analytics.is_consecutive_daily
    )
    assert result["current"] == 5
    assert result["longest"] == 5

def test_get_longest_streak_all_habits(sample_habits):
    """Test longest streak calculation for multiple habits"""
    result = analytics.get_longest_streak_all_habits(sample_habits)
    assert isinstance(result, dict)
    assert "Daily Habit" in result
    assert "Weekly Habit" in result
    assert result["Daily Habit"] == 5
    assert result["Weekly Habit"] == 3


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

def test_analyze_habits_by_predicate(sample_habits):
    """Test habit analysis with predicate filtering"""
    # Test filtering daily habits
    daily_habits = analytics.analyze_habits_by_predicate(
        sample_habits,
        lambda h: h.periodicity == "daily"
    )
    assert len(daily_habits) == 1
    assert daily_habits[0]["name"] == "Daily Habit"
    assert "stats" in daily_habits[0]

    # Test filtering by completion count
    active_habits = analytics.analyze_habits_by_predicate(
        sample_habits,
        lambda h: len(h.get_completions()) > 2
    )
    assert len(active_habits) == 2

# Edge cases and error handling tests
def test_calculate_streaks_empty_dates():
    """Test streak calculation with empty dates list"""
    result = analytics.calculate_streaks([], analytics.is_consecutive_daily)
    assert result["current"] == 0
    assert result["longest"] == 0


def test_completion_rate_edge_cases():
    """Test completion rate calculation edge cases"""
    start_date = datetime.now()
    
    # Empty dates
    rate = analytics.calculate_completion_rate([], start_date, "daily")
    assert rate == 0.0
    
    # Single date
    rate = analytics.calculate_completion_rate([start_date], start_date, "daily")
    assert rate == 100.0
    
    # Future start date
    future_start = datetime.now() + timedelta(days=10)
    rate = analytics.calculate_completion_rate([], future_start, "daily")
    assert rate == 0.0

def test_calculate_breaks_edge_cases():
    """Test break calculation edge cases"""
    # Empty dates
    assert analytics.calculate_breaks([], analytics.is_consecutive_daily) == 0
    
    # Single date
    assert analytics.calculate_breaks([datetime.now()], analytics.is_consecutive_daily) == 0
    
    # Two consecutive dates
    dates = [datetime.now(), datetime.now() + timedelta(days=1)]
    assert analytics.calculate_breaks(dates, analytics.is_consecutive_daily) == 0


