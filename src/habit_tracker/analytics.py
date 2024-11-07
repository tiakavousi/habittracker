"""Habit Analytics Module.

This module provides functionality for analyzing habit completion data and generating 
insights using functional programming principles.
"""

from datetime import datetime
from functools import reduce
from typing import Any, Callable, Dict, List, Tuple, Optional

# Type aliases for clarity
Stats = Dict[str, Any]

def pipe(data: Any, *functions: List[Callable]) -> Any:
    """Pipe data through multiple functions from left to right."""
    return reduce(lambda acc, fn: fn(acc), functions, data)


def days_between(date1: datetime, date2: datetime) -> int:
    """Calculate days between two dates."""
    return abs((date1.date() - date2.date()).days)


def is_consecutive_daily(date1: datetime, date2: datetime) -> bool:
    """Check if two dates are consecutive days."""
    return days_between(date1, date2) == 1


def is_consecutive_weekly(date1: datetime, date2: datetime) -> bool:
    """Check if two dates are in consecutive or same weeks using ISO calendar."""

    # Extract year and week number using ISO calendar,returns year, week, weekday
    # [:2] takes only year and week
    week1_year, week1 = date1.isocalendar()[:2]
    week2_year, week2 = date2.isocalendar()[:2]

    # Case 1: Check if dates are in the same week (both year and week match)
    if week1_year == week2_year and week1 == week2:
        return True
    
    # Case 2: Check for year boundary cases (e.g., Week 52 of 2024 -> Week 1 of 2025)
    if abs(week1_year - week2_year) == 1:
            # Get the last week number of the earlier year(28.12 always last week of the year)
            max_week = datetime(week1_year, 12, 28).isocalendar()[1]

            # Check if it's either:
            # - First date is in last week of its year and second date is in first week of next year
            # - Second date is in last week of its year and first date is in first week of next year
            return (week1 == max_week and week2 == 1) or (week2 == max_week and week1 == 1)

    # Case 3: Regular case - same year, different weeks
    # Check if weeks are consecutive (difference of 1) and in same year    
    return week1_year == week2_year and abs(week1 - week2) == 1


def calculate_streaks(
    dates: List[datetime], is_consecutive_fn: Callable
) -> Dict[str, int]:
    """Calculate current and longest streaks for a set of completion dates."""
    if not dates:
        return {"current": 0, "longest": 0}
    
    def calculate_streak(dates: List[datetime], reverse: bool = False) -> int:
        """Helper function to calculate streak length in forward or reverse order."""
        sorted_dates = sorted(dates, reverse=reverse)
        streak = 1
        
        for i in range(1, len(sorted_dates)):
            date1, date2 = sorted_dates[i-1:i+1]
            if reverse:
                date1, date2 = date2, date1
            if is_consecutive_fn(date1, date2):
                streak += 1
            else:
                break
        return streak
    
    # Calculate longest streak (forward order)
    longest_streak = calculate_streak(dates)
    
    # Calculate current streak (check grace period first)
    most_recent = max(dates)
    is_daily = "daily" in str(is_consecutive_fn)
    grace_period = 1 if is_daily else 7
    
    if (datetime.now().date() - most_recent.date()).days > grace_period:
        current_streak = 0
    else:
        current_streak = calculate_streak(dates, reverse=True)
    
    return {
        "current": current_streak,
        "longest": longest_streak
    }


def calculate_completion_rate(dates: List[datetime], start_date: datetime, periodicity: str) -> float:
    """Calculate completion rate as percentage."""
    if not dates:
        return 0.0

    end_date = datetime.now()
    # Function to convert datetime to period identifier
    # For daily habits: use date
    # For weekly habits: use year-week format (e.g., "2024-W01")
    period_key = lambda d: d.date() if periodicity == "daily" else d.strftime("%Y-%W")
    # Count unique periods with completions
    # Using set() to count each period only once
    unique_periods = len(set(map(period_key, dates)))
    # Calculate total possible periods between start and end dates
    days_diff = (end_date.date() - start_date.date()).days + 1
    total_periods = (
        days_diff if periodicity == "daily"
        else (days_diff // 7) + 1
    )
    # Calculate percentage, avoiding division by zero
    return (unique_periods / total_periods * 100) if total_periods > 0 else 0


def calculate_breaks(dates: List[datetime], is_consecutive_fn: Callable) -> int:
    """Calculate number of breaks in habit completion.
        A break is counted when two consecutive dates are not consecutive according
        to the habit's periodicity (daily/weekly).
    """
    if len(dates) < 2:
        return 0
    
    return sum(1 for d1, d2 in zip(dates, dates[1:]) 
              if not is_consecutive_fn(d1, d2))


def analyze_habit(habit: Any) -> Stats:
    """Analyze a single habit and generate comprehensive statistics."""
    dates = sorted(habit.get_completions())
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


def get_longest_streak_all_habits(habits: List[Any]) -> Dict[str, int]:
    """Return the longest streak for all habits."""
    return pipe(
        habits,
        lambda hs: map(lambda h: (h.name, analyze_habit(h)["longest"]), hs),
        dict
    )


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