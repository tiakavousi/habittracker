from datetime import datetime


def test_database_creation(test_db):
    """Test database initialization"""
    assert test_db.connection is not None


def test_save_habit(test_db, sample_habit):
    """Test saving habit to database"""
    result = test_db.save_habit(sample_habit.to_dict())
    assert result is True


def test_save_completion(test_db, sample_habit):
    """Test saving completion"""
    test_db.save_habit(sample_habit.to_dict())
    result = test_db.save_completion(sample_habit.id, datetime.now())
    assert result is True


def test_get_all_habits(test_db, sample_habit):
    """Test retrieving all habits"""
    test_db.save_habit(sample_habit.to_dict())
    habits = test_db.get_all_habits()
    assert len(habits) > 0
    assert habits[0]["name"] == sample_habit.name


def test_get_habit_completions(test_db, sample_habit):
    """Test retrieving habit completions"""
    test_db.save_habit(sample_habit.to_dict())
    completion_time = datetime.now()
    test_db.save_completion(sample_habit.id, completion_time)
    completions = test_db.get_habit_completions(sample_habit.id)
    assert len(completions) > 0
