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
    def get_week_year(dt: datetime) -> tuple:
        """Get ISO week and year for proper week boundary handling."""
        # Using ISO calendar to handle week boundaries correctly
        return dt.isocalendar()[:2]  # (year, week)

    week1_year, week1 = get_week_year(date1)
    week2_year, week2 = get_week_year(date2)

    # Handle same week completions
    if week1_year == week2_year and week1 == week2:
        return True
    
    # Handle year boundary
    if week1_year != week2_year:
        # Check last week of one year and first week of next year
        if abs(week1_year - week2_year) == 1:
            max_week = datetime(week1_year, 12, 28).isocalendar()[1]
            if (week1 == max_week and week2 == 1) or (week2 == max_week and week1 == 1):
                return True
        return False
    
    # Regular case: check if weeks are consecutive
    return abs(week1 - week2) == 1

    # if is_same_week(date1, date2):
    #     return False
    # # Check if weeks are adjacent by comparing week numbers
    # week1 = int(date1.strftime("%W"))
    # week2 = int(date2.strftime("%W"))
    # return abs(week1 - week2) == 1


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
    """Calculate current and longest streaks for a set of completion dates."""
    if not dates:
        return {"current": 0, "longest": 0}
    
    # Sort dates in ascending order for longest streak calculation
    sorted_dates = sorted(dates)
    longest_streak = current_sequence = 1
    
    # Calculate longest streak
    for i in range(1, len(sorted_dates)):
        if is_consecutive_fn(sorted_dates[i-1], sorted_dates[i]):
            current_sequence += 1
            longest_streak = max(longest_streak, current_sequence)
        else:
            current_sequence = 1
    
    # Calculate current streak from most recent dates
    current_streak = 1
    today = datetime.now()
    most_recent = max(dates)
    
    # Check if the most recent completion is within the valid period
    if (today.date() - most_recent.date()).days > (1 if "daily" in str(is_consecutive_fn) else 7):
        current_streak = 0
    else:
        reversed_dates = sorted(dates, reverse=True)
        for i in range(1, len(reversed_dates)):
            if is_consecutive_fn(reversed_dates[i], reversed_dates[i-1]):
                current_streak += 1
            else:
                break
    
    return {
        "current": current_streak,
        "longest": longest_streak
    }


    # groups = group_by_period(dates, is_consecutive_fn)

    # if not groups:
    #     return {"current": 0, "longest": 0}

    # lengths = list(map(len, groups))
    # return {"current": lengths[-1], "longest": max(lengths)}


def calculate_completion_rate(
    dates: List[datetime], start_date: datetime, periodicity: str
) -> float:
    """Calculate completion rate as percentage."""
    if not dates:
        return 0.0

    end_date = datetime.now()
    total_periods = 0

    unique_periods = len(
        set(
            map(
                lambda d: d.date() if periodicity == "daily" else d.strftime("%Y-%W"),
                dates,
            )
        )
    )

    if periodicity == "daily":
        total_periods = (end_date.date() - start_date.date()).days + 1
    else:  # weekly
        total_periods = ((end_date.date() - start_date.date()).days // 7) + 1

    return (unique_periods / total_periods * 100) if total_periods > 0 else 0

def calculate_breaks(dates: List[datetime], is_consecutive_fn: Callable) -> int:
    """Calculate number of breaks in habit completion."""
    if len(dates) < 2:
        return 0

    pairs = zip(dates, dates[1:])
    return len(list(filter(lambda pair: not is_consecutive_fn(*pair), pairs)))


def analyze_habit(habit: Any) -> Stats:
    """Analyze a single habit and generate comprehensive statistics."""
    dates = get_completion_dates(habit)
    is_consecutive = (
        is_consecutive_daily if habit.periodicity == "daily" 
        else is_consecutive_weekly
    )

    streak_data = calculate_streaks(dates, is_consecutive)
    
    return {
        "total_completions": len(dates),
        "current": streak_data["current"],
        "longest": streak_data["longest"],
        "completion_rate": calculate_completion_rate(
            dates, habit.created_at, habit.periodicity
        ),
        "break_count": calculate_breaks(dates, is_consecutive),
        "last_completed": max(dates) if dates else None,
        "periodicity": habit.periodicity
    }

def is_consecutive_weekly(date1: datetime, date2: datetime) -> bool:
    """Check if two dates are in consecutive or same weeks."""
    def get_week_year(dt: datetime) -> tuple:
        """Get ISO week and year for proper week boundary handling."""
        return dt.isocalendar()[:2]  # (year, week)
    
    week1_year, week1 = get_week_year(date1)
    week2_year, week2 = get_week_year(date2)
    
    # If dates are in same week
    if week1_year == week2_year and week1 == week2:
        return True
    
    # If dates span year boundary
    if abs(week1_year - week2_year) == 1:
        max_week = datetime(min(week1_year, week2_year), 12, 28).isocalendar()[1]
        if (week1 == max_week and week2 == 1) or (week2 == max_week and week1 == 1):
            return True
        return False
    
    # Regular case: same year, different weeks
    return week1_year == week2_year and abs(week1 - week2) == 1

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

    period_text = "weeks" if stats.get("periodicity") == "weekly" else "days"
    suggestion_rules = [
        # Rule format: (condition_fn, message_fn)
        (
            lambda s: s["completion_rate"] < 30,
            lambda _: "Consider making this habit easier or breaking it into smaller steps",
        ),
        (
            lambda s: s["completion_rate"] < 70,
            lambda _: "You're making progress! Try setting specific times for this habit",
        ),
        (
            lambda s: s["current"] < s["longest"] / 2,
            lambda s: f"You've had a longer streak ({s['longest']} {period_text})! Try to beat your record",
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
