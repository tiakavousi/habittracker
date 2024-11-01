import argparse
from datetime import datetime
from .habit_manager import HabitManager
from .database import Database


def create_cli(habit_manager: HabitManager):
    parser = argparse.ArgumentParser(description='Habit Tracker Application')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create habit command
    create_parser = subparsers.add_parser('create', help='Create a new habit')
    create_parser.add_argument('name', type=str, help='Name of the habit')
    create_parser.add_argument('periodicity', choices=[
                               'daily', 'weekly'], help='Habit periodicity')
    create_parser.add_argument(
        '--description', type=str, help='Habit description')

    # Complete habit command
    complete_parser = subparsers.add_parser(
        'complete', help='Complete a habit')
    complete_parser.add_argument('habit_id', type=str, help='ID of the habit')

    # List habits command
    list_parser = subparsers.add_parser('list', help='List all habits')
    list_parser.add_argument(
        '--periodicity', choices=['daily', 'weekly'], help='Filter by periodicity')

    # View habit details command
    view_parser = subparsers.add_parser('view', help='View habit details')
    view_parser.add_argument('habit_id', type=str, help='ID of the habit')

    return parser


def main():
    db = Database()
    habit_manager = HabitManager(db)
    parser = create_cli(habit_manager)

    args = parser.parse_args()

    if args.command == 'create':
        habit = habit_manager.create_habit(
            args.name, args.periodicity, args.description or "")
        if habit:
            print(f"Created habit: {habit.name} (ID: {habit.id})")
        else:
            print("Failed to create habit")

    elif args.command == 'complete':
        if habit_manager.complete_habit(args.habit_id):
            print("Habit completed successfully")
        else:
            print("Failed to complete habit")

    elif args.command == 'list':
        if args.periodicity:
            habits = habit_manager.get_habits_by_periodicity(args.periodicity)
        else:
            habits = habit_manager.habits.values()

        for habit in habits:
            streak = habit_manager.calculate_streak(habit)
            longest_streak = habit_manager.get_longest_streak(habit)
            print(f"ID: {habit.id}")
            print(f"Name: {habit.name}")
            print(f"Periodicity: {habit.periodicity}")
            print(f"Current streak: {streak}")
            print(f"Longest streak: {longest_streak}")
            print("-" * 30)

    elif args.command == 'view':
        habit = habit_manager.get_habit_by_id(args.habit_id)
        if habit:
            print(f"Name: {habit.name}")
            print(f"Periodicity: {habit.periodicity}")
            print(f"Description: {habit.description}")
            print(f"Created at: {habit.created_at}")
            print("\nCompletions:")
            for completion in habit.get_completions():
                print(completion)
        else:
            print("Habit not found")


if __name__ == "__main__":
    main()
