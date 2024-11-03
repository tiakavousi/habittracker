import sqlite3
from datetime import datetime
from typing import Dict, List


def adapt_datetime(dt):
    """Convert datetime to string for SQLite storage"""
    return dt.isoformat()


def convert_datetime(s):
    """Convert string from SQLite to datetime"""
    return datetime.fromisoformat(s)


class Database:
    def __init__(self, db_name: str = "habits.db"):
        self.db_name = db_name
        # Register adapters for datetime
        sqlite3.register_adapter(datetime, adapt_datetime)
        sqlite3.register_converter("timestamp", convert_datetime)
        self.connection = self._create_connection()
        self._create_tables()

    def _create_connection(self) -> sqlite3.Connection:
        """Create a database connection."""
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            raise Exception(f"Error connecting to database: {e}")

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            cursor = self.connection.cursor()

            # Create habits table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS habits (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    periodicity TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """
            )

            # Create completions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id TEXT NOT NULL,
                    completed_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (habit_id) REFERENCES habits (id)
                )
            """
            )

            self.connection.commit()
        except sqlite3.Error as e:
            raise Exception(f"Error creating tables: {e}")

    def save_habit(self, habit_data: Dict) -> bool:
        """Save a new habit to the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO habits (id, name, periodicity, description, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    habit_data["id"],
                    habit_data["name"],
                    habit_data["periodicity"],
                    habit_data["description"],
                    habit_data["created_at"],
                ),
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving habit: {e}")
            return False

    def save_completion(self, habit_id: str, completed_at: datetime) -> bool:
        """Save a habit completion."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO completions (habit_id, completed_at)
                VALUES (?, ?)
            """,
                (habit_id, completed_at),
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error saving completion: {e}")
            return False

    def get_all_habits(self) -> List[Dict]:
        """Retrieve all habits from the database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM habits")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error retrieving habits: {e}")
            return []

    def get_habit_completions(self, habit_id: str) -> List[datetime]:
        """Retrieve all completions for a specific habit."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT completed_at FROM completions
                WHERE habit_id = ?
                ORDER BY completed_at
            """,
                (habit_id,),
            )
            return [
                datetime.fromisoformat(row["completed_at"]) for row in cursor.fetchall()
            ]
        except sqlite3.Error as e:
            print(f"Error retrieving completions: {e}")
            return []
