from datetime import datetime, timedelta
from random import random, randint
from .habit import Habit
from .habit_manager import HabitManager

def initialize_default_habits(db):
    """
    Initialize default habits with 4 weeks of sample completion data.
    Includes random missing days to simulate realistic usage.
    
    Daily habits have ~70% completion rate
    Weekly habits have ~80% completion rate
    """
    habit_manager = HabitManager(db)
    
    defaults = [
        ("Walk the cat", "daily", "30 minutes"),
        ("Read Book", "daily", "Read 20 pages"),
        ("Yoga", "weekly", "1.5 h yoga"),
        ("Meditation", "daily", "15 minutes mindfulness"),
        ("feeding stray cats", "weekly", "feeding cats in the neighborhood")
    ]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=28)
    
    completion_rates = {
        "daily": 0.7,  # 70% completion rate
        "weekly": 0.8  # 80% completion rate
    }
    
    for name, periodicity, description in defaults:
        habit = habit_manager.create_habit(name, periodicity, description)
        if not habit:
            print(f"Failed to create habit: {name}")
            continue
            
        current_date = start_date
        while current_date <= end_date:
            # Randomly skip some days/weeks based on periodicity
            should_complete = random() < completion_rates[periodicity]
            
            if periodicity == "daily":
                if should_complete:
                    # Add some variety to completion times
                    hour = randint(7, 22)  # Between 7 AM and 10 PM
                    completion_time = datetime.combine(
                        current_date.date(),
                        datetime.strptime(f"{hour:02d}:00", "%H:%M").time()
                    )
                    habit_manager.complete_habit(habit.id, completion_time)
                current_date += timedelta(days=1)
                
            elif periodicity == "weekly" and current_date.weekday() == 6:  # Sunday
                if should_complete:
                    # Weekly habits completed sometime on Sunday
                    hour = randint(10, 20)  # Between 10 AM and 8 PM
                    completion_time = datetime.combine(
                        current_date.date(),
                        datetime.strptime(f"{hour:02d}:00", "%H:%M").time()
                    )
                    habit_manager.complete_habit(habit.id, completion_time)
                current_date += timedelta(days=1)
            else:
                current_date += timedelta(days=1)
    
    return habit_manager