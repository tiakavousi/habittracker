import pytest
from datetime import datetime
from habit_tracker.habit_manager import HabitManager


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
    habit_manager.complete_habit(habit.id)
    streak = habit_manager.calculate_streak(habit)
    assert streak >= 1


def test_get_longest_streak(habit_manager):
    """Test longest streak calculation"""
    habit = habit_manager.create_habit("Test Habit", "daily")
    for i in range(3):
        habit_manager.complete_habit(
            habit.id, datetime.now() - timedelta(days=i))
    longest_streak = habit_manager.get_longest_streak(habit)
    assert longest_streak >= 3
