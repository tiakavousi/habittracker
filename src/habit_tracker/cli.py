import argparse
from typing import List, Any
from datetime import datetime
from .database import Database
from .habit_manager import HabitManager
from .data_loader import initialize_default_habits

def create_cli(habit_manager: HabitManager):
    """
    Create and configure the command-line interface for the habit tracker.
    Returns an ArgumentParser with all subcommands and arguments configured.
    """

    parser = argparse.ArgumentParser(description="Habit Tracker Application")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Create habit command
    create_parser = subparsers.add_parser("create", help="Create a new habit")
    create_parser.add_argument("name", type=str, help="Name of the habit")
    create_parser.add_argument(
        "periodicity", choices=["daily", "weekly"], help="Habit periodicity"
    )
    create_parser.add_argument("--description", type=str, help="Habit description")
    create_parser.add_argument(
        "--created_at",
        type=str,
        help="Creation date (YYYY-MM-DD format)",
        default=None
    )

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

    # Subcommands for stats to view all habits or specific habit statistics
    stats_subparsers.add_parser("all", help="View statistics for all habits")
    stats_subparsers.add_parser("longest-streaks", help="View longest streaks for all habits")

    # Subcommand to view statistics by periodicity
    periodicity_parser = stats_subparsers.add_parser(
        "periodicity", help="View statistics by periodicity"
    )
    periodicity_parser.add_argument("period", choices=["daily", "weekly"])
   
    # Subcommand for viewing stats of a single habit
    single_parser = stats_subparsers.add_parser(
        "habit", help="View statistics for a single habit"
    )
    single_parser.add_argument("habit_id", help="ID of the habit")

    return parser


# Display stats Helper function
def display_stats(habit_name: str, stats: dict, habit: Any) -> None:
    """
    Display formatted statistics for a given habit including completion history and streaks.
    Takes habit name, stats dictionary, and habit object as input.
    """
    # Performance Metrics Section
    print(f"\nHabit: {habit_name}")
    print(f"ID: {habit.id}")
    print("-" * 30)
    print(f"Total completions: {stats['total_completions']}")
    print(f"Completion rate: {stats['completion_rate']:.1f}%")
    
    # Streak Analysis
    print(f"Current streak: {stats['current']} {habit.periodicity}")
    print(f"Longest streak: {stats['longest']} {habit.periodicity}")
    print(f"Break count: {stats['break_count']}")
    

    # Complete History Section
    print("\n📅 Complete History")
    print("-" * 30)
    completions = sorted(habit.get_completions(), reverse=True)
    if completions:
        print(f"All completions ({len(completions)} total):")
        for idx, completion in enumerate(completions, 1):
            print(f"{idx}. {completion.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("No completions recorded yet")
    print("=" * 50)

# Create
def handle_create_command(args: argparse.Namespace, habit_manager: HabitManager) -> None:
    """
    Process the create habit command with provided arguments.
    Creates a new habit with specified name, periodicity, and optional description.
    """
    try:
        created_at = None
        if args.created_at:
            try:
                created_at = datetime.fromisoformat(args.created_at)
            except ValueError:
                print("Error: Invalid date format. Use YYYY-MM-DD")
                return

        habit = habit_manager.create_habit(
            args.name,
            args.periodicity,
            args.description or "",
            created_at=created_at
        )
        if habit:
            print(f"Created habit: {habit.name} (ID: {habit.id})")
        else:
            print("Failed to create habit")
    except ValueError as e:
        print(f"Error: {e}")


# List
def handle_list_command(args: argparse.Namespace, habit_manager: HabitManager) -> None:
    """
    Display a list of all habits with optional filtering by periodicity.
    Shows basic information including current and longest streaks.
    """
    if args.periodicity:
        habits = habit_manager.get_habits_by_periodicity(args.periodicity)
    else:
        habits = list(habit_manager.habits.values())

    if not habits:
        print("No habits found")
        return

    print("\n📋 Habits List")
    print("=" * 50)
    
    for habit in habits:
        stats = habit_manager.get_habit_stats(habit.id)
        
        print(f"\nHabit: {habit.name}")
        print(f"ID: {habit.id}")
        print(f"Periodicity: {habit.periodicity}")
        print(f"Current streak: {stats['current']} {habit.periodicity}")
        print(f"Longest streak: {stats['longest']} {habit.periodicity}")
        print("-" * 30)

# View
def handle_view_command(args: argparse.Namespace, habit_manager: HabitManager) -> None:
    """
    Show detailed information for a specific habit including recent activity.
    Displays habit details, current streak, and last 5 completions.
    """
    details = habit_manager.get_habit_details(args.habit_id)
    if not details:
        print("Habit not found")
        return
    
    # Basic Information Section
    print("\n📋 Habit Details")
    print("=" * 50)
    print(f"Name: {details['name']}")
    print(f"ID: {args.habit_id}")
    print(f"Periodicity: {details['periodicity']}")
    print(f"Description: {details['description']}")
    print(f"Created: {details['created_at'].strftime('%Y-%m-%d')}")
    stats = habit_manager.get_habit_stats(args.habit_id)
    print(f"\nCurrent streak: {stats['current']} {details['periodicity']}")
    
    # Recent Activity Section
    print("\n🔄 Recent Activity")
    print("_" * 20)
    completions = sorted(details['completions'], reverse=True)
    recent_completions = completions[:5]  # Show last 5 completions
    
    if recent_completions:
        print("Last completions:")
        for completion in recent_completions:
            print(f"✓ {completion.strftime('%Y-%m-%d %H:%M')}")
        if len(completions) > 5:
            print(f"... and {len(completions) - 5} more")
    else:
        print("No completions recorded yet")
    
# Stats
def handle_stats_command(args: argparse.Namespace, habit_manager: HabitManager) -> None:
    """
    Process various statistics commands including all habits, longest streaks, and periodicity analysis.
    Supports viewing stats for individual habits or grouped by different criteria.
    """
    if args.stats_command == "longest-streaks":
        longest_streaks = habit_manager.get_longest_streaks()
        print("\n🏆 Longest Streaks")
        print("_" * 20)
        for habit_name, streak in longest_streaks.items():
            habit = next((h for h in habit_manager.habits.values() 
                         if h.name == habit_name), None)
            period = 'days' if habit and habit.periodicity == 'daily' else 'weeks'
            print(f"{habit_name}: {streak} {period}")
        print("=" * 50)
    
    elif args.stats_command == "all":
        all_stats = habit_manager.get_all_habits_stats()
        print("\n📈 All Habits Analysis")
        print("\n" * 2)
        for habit_name, habit_stats in all_stats.items():
            habit = next((h for h in habit_manager.habits.values() 
                            if h.name == habit_name), None)
            if habit:
                display_stats(habit_name, habit_stats, habit)

    elif args.stats_command == "periodicity":
        period_stats = habit_manager.get_periodicity_stats(args.period)
        print(f"\n📈 {args.period.capitalize()} Habits Analysis")
        for habit_data in period_stats:
            habit = next((h for h in habit_manager.habits.values() 
                         if h.name == habit_data['name']), None)
            if habit:
                stats = habit_data["stats"]
                display_stats(habit_data["name"], stats, habit)

    elif args.stats_command == "habit":
        stats = habit_manager.get_habit_stats(args.habit_id)
        habit = habit_manager.get_habit_by_id(args.habit_id)
    
        if not stats or not habit:
            print("Habit not found")
            return

        display_stats(habit.name, stats, habit)
    else:
        print("Please specify a stats command. Use --help for options.")
        return
    

def main():
    """
    Initialize the habit tracker application and handle command-line arguments.
    Sets up the database, habit manager, and processes user commands.
    """
    db = Database()
    habit_manager = HabitManager(db)
    # Initialize default habits if the database is empty
    if not habit_manager.habits:
        print("Initializing default habits...")
        initialize_default_habits(habit_manager)
        print("Default habits initialized successfully!")

    parser = create_cli(habit_manager)
    args = parser.parse_args()

    # Create command handlers dictionary
    command_handlers = {
        "complete": lambda args, hm: print(
            "Habit completed successfully" 
            if hm.complete_habit(args.habit_id) 
            else "Failed to complete habit"
        ),
        "create": handle_create_command,
        "list": handle_list_command,
        "view": handle_view_command, 
        "stats": handle_stats_command
    }

    # Get and execute the appropriate handler
    handler = command_handlers.get(args.command)
    if handler:
        handler(args, habit_manager)

if __name__ == "__main__":
    main()