from datetime import datetime
from typing import Dict, List, Optional

from .database import Database
from .habit import Habit

VALID_PERIODICITIES = ["daily", "weekly"]


class HabitManager:
    def __init__(self, db: Database):
        self.db = db
        self.habits: Dict[str, Habit] = {}
        self._load_habits()

    def _load_habits(self):
        """Load all habits from database."""
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
        """Create a new habit and save it to database."""
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
        """Mark a habit as complete."""
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
        """Get a habit by its ID."""
        return self.habits.get(habit_id)

    def get_habits_by_periodicity(self, periodicity: str) -> List[Habit]:
        """Get all habits with specified periodicity."""
        return [
            habit for habit in self.habits.values() if habit.periodicity == periodicity
        ]