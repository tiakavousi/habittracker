from datetime import datetime
import pytest
from datetime import datetime, timedelta
from habit_tracker.database import Database
from habit_tracker.habit import Habit
from habit_tracker.habit_manager import HabitManager


@pytest.fixture
def test_db():
    """Fixture for test database"""
    db = Database(":memory:")
    return db


@pytest.fixture
def sample_habit():
    """Fixture for a sample habit"""
    return Habit("Read Books", "daily", "Read for 30 minutes")


@pytest.fixture
def habit_manager(test_db):
    """Fixture for habit manager"""
    return HabitManager(test_db)


@pytest.fixture
def sample_dates():
    """Fixture for sample dates"""
    base_date = datetime.now()
    return [base_date - timedelta(days=i) for i in range(5)]
