# Habit Tracker
A command-line habit tracking application built with Python.

## Requirements
- Python 3.9 or higher
- pip (Python package installer)
- SQLite3

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/habit_tracker.git
cd habit_tracker
```
2.Setup:
```bash
make
source .venv/bin/activate
```
3. Clean up
```
deactivate
make clean
```

## Example Usage
```bash
# Create a new habit
habit-tracker create "Workout" daily --description "30 minutes exercise"
habit-tracker create "Reading" weekly --description "Read 20 pages"

# Complete a habit (mark as done)
habit-tracker complete <habit_id>


# List all habits
habit-tracker list


# List habits by periodicity
habit-tracker list --periodicity daily
habit-tracker list --periodicity weekly


# View details of a specific habit
habit-tracker view <habit_id>


# All habits stats
habit-tracker stats all

#Longest streacks for all habits
habit-tracker stats longest-streaks

## Stats by periodicity
habit-tracker stats periodicity daily
habit-tracker stats periodicity weekly

## Stats for a single habit
habit-tracker stats habit <habit_id>
```





