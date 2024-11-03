import pytest
from datetime import datetime, timedelta
from habit_tracker.habit_manager import HabitManager, VALID_PERIODICITIES


def test_create_habit(habit_manager):
    """Test habit creation through manager"""
    habit = habit_manager.create_habit(
        "Test Habit", "daily", "Test description")
    assert habit is not None
    assert habit.name == "Test Habit"


def test_complete_habit(habit_manager):
    """Test habit completion"""
    habit = habit_manager.create_habit("Test Habit", "daily")
    result = habit_manager.complete_habit(habit.id)
    assert result is True


def test_get_habit_by_id(habit_manager):
    """Test retrieving habit by ID"""
    habit = habit_manager.create_habit("Test Habit", "daily")
    retrieved_habit = habit_manager.get_habit_by_id(habit.id)
    assert retrieved_habit is not None
    assert retrieved_habit.id == habit.id


def test_get_habits_by_periodicity(habit_manager):
    """Test filtering habits by periodicity"""
    habit_manager.create_habit("Daily Habit", "daily")
    habit_manager.create_habit("Weekly Habit", "weekly")
    daily_habits = habit_manager.get_habits_by_periodicity("daily")
    assert len(daily_habits) == 1
    assert daily_habits[0].periodicity == "daily"


def test_calculate_streak(habit_manager):
    """Test streak calculation"""
    habit = habit_manager.create_habit("Test Habit", "daily")
    completion_time = datetime.now()
    habit_manager.complete_habit(habit.id, completion_time)
    streak = habit_manager.calculate_streak(habit)
    assert streak >= 1


def test_get_longest_streak(habit_manager):
    """Test longest streak calculation"""
    habit = habit_manager.create_habit("Test Habit", "daily")
    base_date = datetime.now()

    # Add completions for three consecutive days
    completion_times = [
        base_date - timedelta(days=i)
        for i in range(3)
    ]

    for completion_time in completion_times:
        habit_manager.complete_habit(habit.id, completion_time)

    longest_streak = habit_manager.get_longest_streak(habit)
    assert longest_streak == 3


def test_multiple_habits_streaks(habit_manager):
    """Test streak calculation with multiple habits"""
    habit1 = habit_manager.create_habit("Habit 1", "daily")
    habit2 = habit_manager.create_habit("Habit 2", "daily")

    # Add completions to first habit
    base_date = datetime.now()
    for i in range(3):
        habit_manager.complete_habit(habit1.id, base_date - timedelta(days=i))

    # Add completions to second habit
    for i in range(2):
        habit_manager.complete_habit(habit2.id, base_date - timedelta(days=i))

    assert habit_manager.calculate_streak(habit1) == 3
    assert habit_manager.calculate_streak(habit2) == 2


def test_streak_break(habit_manager):
    """Test streak calculation with a break"""
    habit = habit_manager.create_habit("Test Habit", "daily")
    base_date = datetime.now()

    # Add completions with a break in between
    completion_times = [
        base_date,                    # Today
        base_date - timedelta(days=1),  # Yesterday
        base_date - timedelta(days=3)   # Break
    ]

    for completion_time in completion_times:
        habit_manager.complete_habit(habit.id, completion_time)

    assert habit_manager.calculate_streak(habit) == 2


def test_weekly_habit_streak(habit_manager):
    """Test streak calculation for weekly habits"""
    habit = habit_manager.create_habit("Weekly Habit", "weekly")
    base_date = datetime.now()

    # Add completions for three consecutive weeks
    completion_times = [
        base_date - timedelta(days=i*7)
        for i in range(3)
    ]

    for completion_time in completion_times:
        habit_manager.complete_habit(habit.id, completion_time)

    assert habit_manager.calculate_streak(habit) == 3


def test_habit_creation_invalid_periodicity(habit_manager):
    """Test creating habit with invalid periodicity"""
    with pytest.raises(ValueError) as exc_info:
        habit_manager.create_habit("Invalid Habit", "monthly")
    assert "Invalid periodicity" in str(exc_info.value)
    assert all(p in str(exc_info.value) for p in VALID_PERIODICITIES)


def test_complete_nonexistent_habit(habit_manager):
    """Test completing a habit that doesn't exist"""
    result = habit_manager.complete_habit("nonexistent-id")
    assert result is False


def test_get_nonexistent_habit(habit_manager):
    """Test retrieving a habit that doesn't exist"""
    habit = habit_manager.get_habit_by_id("nonexistent-id")
    assert habit is None


def test_habit_creation_valid_periodicities(habit_manager):
    """Test creating habits with all valid periodicities"""
    for periodicity in VALID_PERIODICITIES:
        habit = habit_manager.create_habit(f"Test {periodicity}", periodicity)
        assert habit is not None
        assert habit.periodicity == periodicity


def test_create_habit_empty_periodicity(habit_manager):
    """Test creating habit with empty periodicity"""
    with pytest.raises(ValueError):
        habit_manager.create_habit("Invalid Habit", "")


def test_create_habit_none_periodicity(habit_manager):
    """Test creating habit with None periodicity"""
    with pytest.raises(ValueError):
        habit_manager.create_habit("Invalid Habit", None)
