import argparse
from typing import List

from . import analytics
from .database import Database
from .habit_manager import HabitManager


def create_cli(habit_manager: HabitManager):
    parser = argparse.ArgumentParser(description="Habit Tracker Application")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create habit command
    create_parser = subparsers.add_parser("create", help="Create a new habit")
    create_parser.add_argument("name", type=str, help="Name of the habit")
    create_parser.add_argument(
        "periodicity", choices=["daily", "weekly"], help="Habit periodicity"
    )
    create_parser.add_argument("--description", type=str, help="Habit description")

    # Complete habit command
    complete_parser = subparsers.add_parser("complete", help="Complete a habit")
    complete_parser.add_argument("habit_id", type=str, help="ID of the habit")

    # List habits command
    list_parser = subparsers.add_parser("list", help="List all habits")
    list_parser.add_argument(
        "--periodicity", choices=["daily", "weekly"], help="Filter by periodicity"
    )

    # View habit details command
    view_parser = subparsers.add_parser("view", help="View habit details")
    view_parser.add_argument("habit_id", type=str, help="ID of the habit")

    # Stats commands
    stats_parser = subparsers.add_parser("stats", help="View habit statistics")
    stats_subparsers = stats_parser.add_subparsers(dest="stats_command")

    # All habits stats
    stats_subparsers.add_parser("all", help="View statistics for all habits")

    # Stats by periodicity
    periodicity_parser = stats_subparsers.add_parser(
        "periodicity", help="View statistics by periodicity"
    )
    periodicity_parser.add_argument("period", choices=["daily", "weekly"])

    # Single habit stats
    single_parser = stats_subparsers.add_parser(
        "habit", help="View statistics for a single habit"
    )
    single_parser.add_argument("habit_id", help="ID of the habit")

    return parser


def display_habit_stats(stats: dict, habit_name: str):
    """Helper function to display habit statistics."""
    print(f"\nStatistics for {habit_name}:")
    print(f"Total completions: {stats['total_completions']}")
    print(f"Current streak: {stats['current']}")
    print(f"Longest streak: {stats['longest']}")
    print(f"Completion rate: {stats['completion_rate']:.1f}%")
    print(f"Break count: {stats['break_count']}")
    if stats["last_completed"]:
        print(f"Last completed: {stats['last_completed']}")
    print("-" * 30)


def handle_stats_command(args, habits: List):
    """Handle all stats-related commands using functional analytics."""
    if args.stats_command == "all":
        all_stats = analytics.analyze_all_habits(habits)
        for habit_name, habit_stats in all_stats.items():
            display_habit_stats(habit_stats, habit_name)

    elif args.stats_command == "periodicity":
        period_stats = analytics.get_habits_by_periodicity(habits, args.period)
        print(f"\nStatistics for {args.period} habits:")
        for habit_data in period_stats:
            print(f"\n{habit_data['name']}:")
            habit_stats = habit_data["stats"]
            print(f"Current streak: {habit_stats['current']}")
            print(f"Longest streak: {habit_stats['longest']}")
            print(f"Completion rate: {habit_stats['completion_rate']:.1f}%")
            print("-" * 30)

    elif args.stats_command == "habit":
        habit = next((h for h in habits if h.id == args.habit_id), None)
        if habit:
            stats = analytics.analyze_habit(habit)
            suggestions = analytics.generate_improvement_suggestions(stats)

            display_habit_stats(stats, habit.name)

            if suggestions:
                print("\nSuggestions for improvement:")
                for suggestion in suggestions:
                    print(f"- {suggestion}")
        else:
            print("Habit not found")


def main():
    db = Database()
    habit_manager = HabitManager(db)
    parser = create_cli(habit_manager)

    args = parser.parse_args()

    if args.command == "create":
        habit = habit_manager.create_habit(
            args.name, args.periodicity, args.description or ""
        )
        if habit:
            print(f"Created habit: {habit.name} (ID: {habit.id})")
        else:
            print("Failed to create habit")

    elif args.command == "complete":
        if habit_manager.complete_habit(args.habit_id):
            print("Habit completed successfully")
        else:
            print("Failed to complete habit")

    elif args.command == "list":
        if args.periodicity:
            habits = habit_manager.get_habits_by_periodicity(args.periodicity)
        else:
            habits = list(habit_manager.habits.values())

        for habit in habits:
            habit_stats = analytics.analyze_habit(habit)
            print(f"ID: {habit.id}")
            print(f"Name: {habit.name}")
            print(f"Periodicity: {habit.periodicity}")
            print(f"Current streak: {habit_stats['current']}")
            print(f"Longest streak: {habit_stats['longest']}")
            print("-" * 30)

    elif args.command == "view":
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

    elif args.command == "stats":
        habits = list(habit_manager.habits.values())
        handle_stats_command(args, habits)


if __name__ == "__main__":
    main()
