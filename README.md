# Habit Tracker
A command-line habit tracking application built with Python.

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

## Usage
Basic commands:
```bash
# Create a new habit
habit-tracker create "Read books" daily --description "Read for 30 minutes"

# Complete a habit
habit-tracker complete <habit_id>

# List all habits
habit-tracker list

# View habit details
habit-tracker view <habit_id>

# View all stats
habit-tracker stats all

# View daily stats
habit-tracker stats periodicity daily

# View specific stats habit
habit-tracker stats habit <habit_id>
```



