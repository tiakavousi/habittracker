import uuid
from datetime import datetime
from typing import List, Optional

VALID_PERIODICITIES = ["daily", "weekly"]


class Habit:
    """
    Represents a trackable habit with completion history and metadata.
    Supports daily or weekly periodicities and maintains completion timestamps.
    """
    def __init__(
        self,
        name: str,
        periodicity: str,
        description: str = "",
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a new habit with unique ID and given attributes.
        Raises ValueError if periodicity is invalid.
        """
        if periodicity not in VALID_PERIODICITIES:
            raise ValueError(
                f"Invalid periodicity. Must be one of: {', '.join(VALID_PERIODICITIES)}"
            )

        self.id = str(uuid.uuid4())
        self.name = name
        self.periodicity = periodicity
        self.description = description
        self.created_at = created_at or datetime.now()
        self._completions: List[datetime] = []

    def add_completion(self, completion_time: datetime = None) -> None:
        """
        Records a completion of the habit at specified time or current time.
        Adds completion timestamp to the habit's history.
        """
        if completion_time is None:
            completion_time = datetime.now()
        self._completions.append(completion_time)

    def get_completions(self) -> List[datetime]:
        """
        Returns a sorted list of all completion timestamps.
        Timestamps are ordered from earliest to latest.
        """
        return sorted(self._completions)

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the habit for database storage.
        Includes id, name, periodicity, description, and creation time.
        """
        return {
            "id": self.id,
            "name": self.name,
            "periodicity": self.periodicity,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }
