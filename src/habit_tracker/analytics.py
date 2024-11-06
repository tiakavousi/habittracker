"""Habit Analytics Module.

This module provides functionality for analyzing habit completion data and generating 
insights using functional programming principles.

Key components:
    - Habit completion analysis
    - Streak calculations
    - Improvement suggestions
    - Time-based analytics
"""

from datetime import datetime
from functools import reduce
from typing import Any, Callable, Dict, List

# Type aliases for clarity
HabitData = Dict[str, Any]
Stats = Dict[str, Any]


# def compose(*functions: List[Callable]) -> Callable:
#     """Compose multiple functions from right to left.
    
#     Args:
#         *functions: Variable number of callable functions to compose.
        
#     Returns:
#         Callable: A new function that represents the composition of all input functions.
        
#     Example:
#         >>> f = lambda x: x + 1
#         >>> g = lambda x: x * 2
#         >>> h = compose(f, g)
#         >>> h(3)  # First multiplies by 2, then adds 1
#         7
#     """
#     return reduce(lambda f, g: lambda x: f(g(x)), functions)


def pipe(data: Any, *functions: List[Callable]) -> Any:
    """Pipe data through multiple functions from left to right."""
    return reduce(lambda acc, fn: fn(acc), functions, data)


def days_between(date1: datetime, date2: datetime) -> int:
    """Calculate days between two dates."""
    return abs((date1.date() - date2.date()).days)


def is_consecutive_daily(date1: datetime, date2: datetime) -> bool:
    """Check if two dates are consecutive days."""
    return days_between(date1, date2) == 1

def is_same_week(date1: datetime, date2: datetime) -> bool:
    """Check if two dates are in the same week."""
    return date1.strftime("%Y-%W") == date2.strftime("%Y-%W")  

def is_consecutive_weekly(date1: datetime, date2: datetime) -> bool:
    # """Check if two dates are in consecutive weeks."""
    # return 1 <= days_between(date1, date2) <= 7
     """Check if two dates are in consecutive weeks."""
     if is_same_week(date1, date2):
            return False
    # Check if weeks are adjacent by comparing week numbers
     week1 = int(date1.strftime("%W"))
     week2 = int(date2.strftime("%W"))
     return abs(week1 - week2) == 1


def get_completion_dates(habit: Any) -> List[datetime]:
    """Extract sorted completion dates from a habit."""
    return sorted(habit.get_completions())


def group_by_period(
    dates: List[datetime], is_consecutive_fn: Callable
) -> List[List[datetime]]:
    """Group dates into consecutive periods using the provided
    consecutive check function."""
    if not dates:
        return []

    def group_reducer(
        acc: List[List[datetime]], date: datetime
    ) -> List[List[datetime]]:
        if not acc:
            return [[date]]
        if is_consecutive_fn(date, acc[-1][-1]):
            acc[-1].append(date)
        else:
            acc.append([date])
        return acc

    return reduce(group_reducer, dates, [])


def calculate_streaks(
    dates: List[datetime], is_consecutive_fn: Callable
) -> Dict[str, int]:
    """Calculate current and longest streaks for a set of completion dates.
    
    Args:
        dates: List of datetime objects representing completion dates.
        is_consecutive_fn: Function that determines if two dates are consecutive
            according to the habit's periodicity (daily/weekly).
            
    Returns:
        Dict containing:
            - current: int (length of current streak)
            - longest: int (length of longest streak)
            
    Example:
        >>> dates = [datetime(2024, 1, 1), datetime(2024, 1, 2)]
        >>> calculate_streaks(dates, is_consecutive_daily)
        {'current': 2, 'longest': 2}
    """
    groups = group_by_period(dates, is_consecutive_fn)

    if not groups:
        return {"current": 0, "longest": 0}

    lengths = list(map(len, groups))
    return {"current": lengths[-1], "longest": max(lengths)}


def calculate_completion_rate(
    dates: List[datetime], start_date: datetime, periodicity: str
) -> float:
    """Calculate completion rate as percentage."""
    if not dates:
        return 0.0

    end_date = datetime.now()

    total_periods = (
        days_between(start_date, end_date) + 1
        if periodicity == "daily"
        else ((end_date - start_date).days // 7) + 1
    )

    unique_periods = len(
        set(
            map(
                lambda d: d.date() if periodicity == "daily" else d.strftime("%Y-%W"),
                dates,
            )
        )
    )

    return (unique_periods / total_periods * 100) if total_periods > 0 else 0

def calculate_breaks(dates: List[datetime], is_consecutive_fn: Callable) -> int:
    """Calculate number of breaks in habit completion."""
    if len(dates) < 2:
        return 0

    pairs = zip(dates, dates[1:])
    return len(list(filter(lambda pair: not is_consecutive_fn(*pair), pairs)))


def analyze_habit(habit: Any) -> Stats:
    """Analyze a single habit and generate comprehensive statistics.
    
    Performs analysis on habit completion data to generate insights including
    streaks, completion rates, and break counts.
    
    Args:
        habit: A habit object containing completion data and metadata.
            Expected to have attributes:
            - periodicity: str ("daily" or "weekly")
            - created_at: datetime
            - name: str
            
    Returns:
        Dict[str, Any]: Statistics dictionary containing:
            - total_completions: int
            - current: int (current streak)
            - longest: int (longest streak)
            - completion_rate: float (percentage)
            - break_count: int
            - last_completed: datetime or None
            
    Example:
        >>> habit = Habit(name="Exercise", periodicity="daily")
        >>> stats = analyze_habit(habit)
        >>> print(stats['current'])  # Current streak
        3
    """
    dates = get_completion_dates(habit)
    is_consecutive = (
        is_consecutive_daily if habit.periodicity == "daily" else is_consecutive_weekly
    )

    return {
        "total_completions": len(dates),
        **calculate_streaks(dates, is_consecutive),
        "completion_rate": calculate_completion_rate(
            dates, habit.created_at, habit.periodicity
        ),
        "break_count": calculate_breaks(dates, is_consecutive),
        "last_completed": max(dates) if dates else None,
    }


def analyze_habits_by_predicate(habits: List[Any], predicate: Callable) -> List[Dict]:
    """Analyze habits filtered by a predicate function."""
    return pipe(
        habits,
        lambda hs: filter(predicate, hs),
        lambda hs: map(lambda h: {"name": h.name, "stats": analyze_habit(h)}, hs),
        list,
    )


def analyze_all_habits(habits: List[Any]) -> Dict[str, Stats]:
    """Analyze all habits."""
    return pipe(habits, lambda hs: map(lambda h: (h.name, analyze_habit(h)), hs), dict)


def get_habits_by_periodicity(habits: List[Any], periodicity: str) -> List[Dict]:
    """Get analysis for habits with specified periodicity."""
    return analyze_habits_by_predicate(habits, lambda h: h.periodicity == periodicity)


def generate_improvement_suggestions(stats: Stats) -> List[str]:
    """Generate personalized improvement suggestions based on habit statistics.
    
    Analyzes habit statistics and returns relevant suggestions for improvement
    based on predefined rules.
    
    Args:
        stats: Dictionary containing habit statistics with keys:
            - completion_rate: float
            - current: int (current streak)
            - longest: int (longest streak)
            - break_count: int
            - total_completions: int
            
    Returns:
        List[str]: List of improvement suggestions based on the statistics.
        
    Example:
        >>> stats = {'completion_rate': 25, 'current': 1, 'longest': 5}
        >>> suggestions = generate_improvement_suggestions(stats)
        >>> print(suggestions[0])
        'Consider making this habit easier or breaking it into smaller steps'
    """
    suggestion_rules = [
        # Rule format: (condition_fn, message_fn)
        (
            lambda s: s["completion_rate"] < 30,
            lambda _: "Consider making this habit easier or \
              breaking it into smaller steps",
        ),
        (
            lambda s: s["completion_rate"] < 70,
            lambda _: "You're making progress! Try setting specific \
                times for this habit",
        ),
        (
            lambda s: s["current"] < s["longest"] / 2,
            lambda s: f"You've had a longer streak ({s['longest']} days)! Try to beat your record",
        ),

        (
            lambda s: s["break_count"] > s["total_completions"] / 3,
            lambda _: "Consider setting reminders to maintain consistency",
        ),
    ]

    return pipe(
        suggestion_rules,
        lambda rules: filter(lambda rule: rule[0](stats), rules),
        lambda rules: map(lambda rule: rule[1](stats), rules),
        list,
    )
