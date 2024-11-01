"""Test configuration and fixtures."""

import pytest
from habit_tracker.database import Database
from habit_tracker.habit_manager import HabitManager


@pytest.fixture
def test_db():
    """Create a test database."""
    db = Database("test.db")
    yield db
    # Cleanup
    import os
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
def habit_manager(test_db):
    """Create a habit manager with test database."""
    return HabitManager(test_db)
