from datetime import datetime

from habit_tracker.habit import Habit


def test_habit_creation():
    """Test habit initialization"""
    habit = Habit("Read Books", "daily", "Read for 30 minutes")
    assert habit.name == "Read Books"
    assert habit.periodicity == "daily"
    assert habit.description == "Read for 30 minutes"
    assert isinstance(habit.id, str)
    assert isinstance(habit.created_at, datetime)


def test_add_completion(sample_habit):
    """Test adding completion times"""
    completion_time = datetime.now()
    sample_habit.add_completion(completion_time)
    assert completion_time in sample_habit.get_completions()


def test_get_completions_sorted(sample_habit, sample_dates):
    """Test completions are returned sorted"""
    for date in sample_dates:
        sample_habit.add_completion(date)
    completions = sample_habit.get_completions()
    assert completions == sorted(completions)


def test_to_dict(sample_habit):
    """Test conversion to dictionary"""
    habit_dict = sample_habit.to_dict()
    assert all(
        key in habit_dict
        for key in ["id", "name", "periodicity", "description", "created_at"]
    )
    assert habit_dict["name"] == "Read Books"
