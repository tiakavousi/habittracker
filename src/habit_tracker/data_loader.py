# src/habit_tracker/data_loader.py

import yaml
from datetime import datetime, timedelta
from pathlib import Path
from random import random, randint
from typing import Dict, Any

class HabitDataLoader:
    def __init__(self, habit_manager, config_path: str = None):
        self.habit_manager = habit_manager
        self.config_path = config_path or Path(__file__).parent.parent.parent / "config" / "default_habits.yaml"

    def load_config(self) -> Dict[str, Any]:
        """Load habit configuration from YAML file."""
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)

    def initialize_habits(self, days_of_history: int = 28) -> None:
        """Initialize habits with completion history."""
        config = self.load_config()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_of_history)

        for habit_config in config['habits']:
            self._create_and_complete_habit(habit_config, start_date, end_date)

    # def _create_and_complete_habit(
    #     self,
    #     habit_config: Dict[str, Any],
    #     start_date: datetime,
    #     end_date: datetime
    # ) -> None:
    #     """Create a habit and add its completion history."""
    #     # Create the habit with the start_date
    #     habit = self.habit_manager.create_habit(
    #         name=habit_config['name'],
    #         periodicity=habit_config['periodicity'],
    #         description=habit_config['description'],
    #         created_at=start_date  # Set creation date to start_date
    #     )

    #     if not habit:
    #         print(f"Failed to create habit: {habit_config['name']}")
    #         return

    #     # Add completion history
    #     current_date = start_date
    #     days_completed = 0
    #     total_days = (end_date - start_date).days + 1

    #     while current_date <= end_date:
    #         completed = self._handle_completion(
    #             habit,
    #             current_date,
    #             habit_config['completion_rate'],
    #             habit_config['completion_time_range'],
    #             habit_config['periodicity']
    #         )
    #         if completed:
    #             days_completed += 1
    #         current_date += timedelta(days=1)

    #     # Verify completion rate
    #     actual_rate = (days_completed / total_days) * 100
    #     target_rate = habit_config['completion_rate'] * 100
    #     print(f"Habit: {habit.name}")
    #     print(f"Target completion rate: {target_rate:.1f}%")
    #     print(f"Actual completion rate: {actual_rate:.1f}%")

    def _handle_completion(
        self,
        habit,
        current_date: datetime,
        completion_rate: float,
        time_range: Dict[str, int],
        periodicity: str
    ) -> None:
        """Handle habit completion based on periodicity and randomization."""
        # For weekly habits, only attempt completion on Mondays
        if periodicity == "weekly" and current_date.weekday() != 0:
            return False

        should_complete = random() < completion_rate
        if should_complete:
            hour = randint(time_range['start_hour'], time_range['end_hour'])
            completion_time = datetime.combine(
                current_date.date(),
                datetime.strptime(f"{hour:02d}:00", "%H:%M").time()
            )
            return self.habit_manager.complete_habit(habit.id, completion_time)
        return False
    def _create_and_complete_habit(
        self,
        habit_config: Dict[str, Any],
        start_date: datetime,
        end_date: datetime
    ) -> None:
        """Create a habit and add its completion history."""
        habit = self.habit_manager.create_habit(
            name=habit_config['name'],
            periodicity=habit_config['periodicity'],
            description=habit_config['description'],
            created_at=start_date
        )

        if not habit:
            print(f"Failed to create habit: {habit_config['name']}")
            return

        completions = 0
        days_count = 0
        current_date = start_date

        while current_date <= end_date:
            days_count += 1
            if self._handle_completion(
                habit,
                current_date,
                habit_config['completion_rate'],
                habit_config['completion_time_range'],
                habit_config['periodicity']
            ):
                completions += 1
            current_date += timedelta(days=1)

        actual_rate = (completions / (days_count / 7 if habit_config['periodicity'] == 'weekly' else days_count)) * 100
        print(f"Habit: {habit.name}")
        print(f"Target completion rate: {habit_config['completion_rate'] * 100:.1f}%")
        print(f"Actual completion rate: {actual_rate:.1f}%")

def initialize_default_habits(habit_manager, config_path: str = None) -> None:
    """Initialize default habits with 4 weeks of sample completion data."""
    loader = HabitDataLoader(habit_manager, config_path)
    loader.initialize_habits()