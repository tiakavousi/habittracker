# Habit Tracker
A command-line habit tracking application built with Python.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/habit_tracker.git
   cd habit_tracker
```

2.Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
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
```
