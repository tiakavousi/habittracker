# Create a new habit
```
habit-tracker create "Workout" daily --description "30 minutes exercise"
habit-tracker create "Reading" weekly --description "Read 20 pages"
```

# Complete a habit (mark as done)
```
habit-tracker complete <habit_id>
```

# List all habits
```
habit-tracker list
```

# List habits by periodicity
```
habit-tracker list --periodicity daily
habit-tracker list --periodicity weekly
```

# View details of a specific habit
```
habit-tracker view <habit_id>
```

# Get statistics
## All habits stats
```
habit-tracker stats all
```

## Stats by periodicity
```
habit-tracker stats periodicity daily
habit-tracker stats periodicity weekly
```

## Stats for a single habit
```
habit-tracker stats habit <habit_id>
````