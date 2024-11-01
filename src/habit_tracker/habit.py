from datetime import datetime
import uuid
from typing import List


class Habit:
    def __init__(self, name: str, periodicity: str, description: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.periodicity = periodicity
        self.description = description
        self.created_at = datetime.now()
        self._completions: List[datetime] = []

    def add_completion(self, completion_time: datetime = None) -> None:
        """Add a completion timestamp for the habit."""
        if completion_time is None:
            completion_time = datetime.now()
        self._completions.append(completion_time)

    def get_completions(self) -> List[datetime]:
        """Get all completion timestamps for the habit."""
        return sorted(self._completions)

    def to_dict(self) -> dict:
        """Convert habit to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "periodicity": self.periodicity,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }
