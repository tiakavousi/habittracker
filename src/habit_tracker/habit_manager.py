from datetime import datetime
from typing import Dict, List, Optional, Any
from . import analytics
from .database import Database
from .habit import Habit

VALID_PERIODICITIES = ["daily", "weekly"]

class HabitManager:
    """
    Core manager class for handling habit operations and database interactions.
    Provides methods for creating, completing, and analyzing habits.
    """
    def __init__(self, db: Database):
        """
        Initialize habit manager with database connection.
        Loads existing habits from database into memory.
        """
        self.db = db
        self.habits: Dict[str, Habit] = {}
        self._load_habits()

    def _load_habits(self):
        """
        Load habits and their completion history from database.
        Populates the habits dictionary with Habit objects.
        """
        habits_data = self.db.get_all_habits()
        for habit_data in habits_data:
            habit = Habit(
                name=habit_data["name"],
                periodicity=habit_data["periodicity"],
                description=habit_data["description"],
            )
            habit.id = habit_data["id"]
            habit.created_at = datetime.fromisoformat(habit_data["created_at"])

            # Load completions
            completions = self.db.get_habit_completions(habit.id)
            for completion in completions:
                habit.add_completion(completion)

            self.habits[habit.id] = habit

    def create_habit(
        self,
        name: str,
        periodicity: str,
        description: str = "",
        created_at: Optional[datetime] = None
    ) -> Optional[Habit]:
        """
        Create a new habit with given attributes and save to database.
        Returns the created Habit object or None if creation fails.
        """
        try:
            # Validate periodicity
            if periodicity not in VALID_PERIODICITIES:
                raise ValueError(
                    f"Invalid periodicity. Must be one of: {', '.join(VALID_PERIODICITIES)}"
                )

            habit = Habit(name, periodicity, description, created_at)

            if self.db.save_habit(habit.to_dict()):
                self.habits[habit.id] = habit
                return habit
            return None
        except Exception as e:
            print(f"Error creating habit: {e}")
            raise

    def complete_habit(self, habit_id: str, completion_time: datetime = None) -> bool:
        """
        Mark a habit as complete at the specified time or current time.
        Returns True if completion was successful, False otherwise.
        """
        if habit_id not in self.habits:
            return False

        if completion_time is None:
            completion_time = datetime.now()

        habit = self.habits[habit_id]
        if self.db.save_completion(habit_id, completion_time):
            habit.add_completion(completion_time)
            return True
        return False

    def get_habit_by_id(self, habit_id: str) -> Optional[Habit]:
        """
        Retrieve a habit by its unique identifier.
        Returns the Habit object or None if not found.
        """
        return self.habits.get(habit_id)

    def get_habits_by_periodicity(self, periodicity: str) -> List[Habit]:
        """
        Get all habits matching the specified periodicity (daily/weekly).
        Returns a list of matching Habit objects.
        """
        return [
            habit for habit in self.habits.values() if habit.periodicity == periodicity
        ]

    def get_habit_stats(self, habit_id: str) -> Optional[Dict[str, Any]]:
        """
        Calculate and return statistics for a specific habit.
        Returns None if habit doesn't exist.
        """
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return None
        return analytics.analyze_habit(habit)

    def get_all_habits_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate and return statistics for all tracked habits.
        Returns a dictionary mapping habit names to their statistics.
        """
        return analytics.analyze_all_habits(list(self.habits.values()))

    def get_periodicity_stats(self, periodicity: str) -> List[Dict[str, Any]]:
        """
        Get statistics for all habits of specified periodicity.
        Returns a list of habit statistics dictionaries.
        """
        habits = list(self.habits.values())
        return analytics.get_habits_by_periodicity(habits, periodicity)

    def get_longest_streaks(self) -> Dict[str, int]:
        """
        Calculate longest completion streaks for all habits.
        Returns a dictionary mapping habit names to their longest streak counts.
        """
        return analytics.get_longest_streak_all_habits(list(self.habits.values()))

    def get_habit_details(self, habit_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific habit including stats and history.
        Returns None if habit doesn't exist.
        """
        habit = self.get_habit_by_id(habit_id)
        if not habit:
            return None
            
        stats = self.get_habit_stats(habit_id)
        return {
            "name": habit.name,
            "periodicity": habit.periodicity,
            "description": habit.description,
            "created_at": habit.created_at,
            "completions": habit.get_completions(),
            "stats": stats
        }