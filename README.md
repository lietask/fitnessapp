# Gym Tracker

Gym Tracker is a Streamlit app for logging workouts, nutrition, and sleep. It uses Supabase (PostgreSQL) for storage and turns workout logs into strength trends and a training calendar with pandas, NumPy, and Matplotlib.

## Logging and history

- Log one to eight sets per exercise. The first set can prefill weight and reps for the remaining sets. Filter workout history by user, exercise, and date range.
- Record daily calories, protein, carbohydrates, and fat, as well as sleep duration, stages, and quality score. Nutrition and sleep entries use the date and username as the upsert key, so saving again updates that day's entry.

## Workout analytics

- **Strength over time.** For an exercise, the app estimates one-rep max for each set as `weight × (1 + reps / 30)`, then plots the highest estimate for each user and date.
- **Training consistency.** A calendar heatmap marks days with at least one logged workout. Filter it by year and user.
- **Working-weight suggestions.** For the selected exercise, the app averages estimated one-rep max across up to five set records from the end of the filtered workout data. It uses that average to suggest a weight for eight reps (hypertrophy), four reps (strength), or the rounded average rep count for the exercise (For me). Multiple sets from the same day can contribute to the average.

## Project structure

| File | Purpose |
| --- | --- |
| [main.py](main.py) | Streamlit entry point and navigation |
| [services/db_service.py](services/db_service.py) | Supabase queries and connection recovery |
| [views/workout_view.py](views/workout_view.py) | Workout logging and history |
| [views/nutrition_view.py](views/nutrition_view.py) | Nutrition and sleep logging |
| [views/analytics_view.py](views/analytics_view.py) | Metric calculations, weight suggestions, and charts |
| [requirements.txt](requirements.txt) | Python dependencies |
| [style.css](style.css) | Interface styling |
