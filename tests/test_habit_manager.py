from datetime import datetime, timedelta

import pytest

from habit_tracker.habit_manager import VALID_PERIODICITIES


def test_create_habit(habit_manager):
    """Test habit creation through manager"""
    habit = habit_manager.create_habit("Test Habit", "daily", "Test description")
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
