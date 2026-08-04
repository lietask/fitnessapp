import numpy as np
import pandas as pd
import streamlit as st
import datetime as dt
import os as os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from streamlit import success

DAILY_CSV = 'daily_logs.csv'
if os.path.exists(DAILY_CSV):
    df_daily = pd.read_csv(DAILY_CSV, index_col='Date')
else:
    # noinspection PyTypeChecker
    df_daily = pd.DataFrame(columns=['Calories', 'Protein', 'Carbs', 'Fats',
                                     'Time_asleep', 'Awake', 'REM', 'Core',
                                     'Deep', 'Sleep_score'])
    df_daily.index.name = 'Date'

df = pd.read_csv("workouts.csv", index_col='index', parse_dates=True)
st.title("My Gym Tracker")


sets = st.selectbox("Number of sets", [0, 1, 2, 3, 4, 5])
with st.form('log workout'):
    ex_name = st.text_input("Exercise name")
    date = st.date_input("Date of exercise")


    collection_sets = []

    for i in range(sets):
        st.write(f"Set: {i+1}")
        weight = st.number_input("Weight in kg", min_value=0.0, format="%.1f", key=f"weight_s{i+1}")
        rep_count = st.number_input("Reps", min_value=0, format="%d", key=f"reps_s{i+1}")
        iset = [weight, rep_count]
        collection_sets.append(iset)


    submitted = st.form_submit_button(label='Submit')

    if submitted:
        congrats = False
        for i in range(sets):
            df.loc[len(df)] = {"ex_name": ex_name, "date": date, "SiaR": i+1}
            df.loc[len(df)-1, 'weight'] = collection_sets[i][0]
            df.loc[len(df)-1, 'reps'] = collection_sets[i][1]
            if df.loc[len(df)-1, 'weight'] == df['weight'].groupby(df['ex_name']).max().loc[ex_name]:
                df.loc[len(df)-1, 'pr'] = 'PR'
                congrats = True
            else:
                df.loc[len(df)-1, 'pr'] = 'Not a PR'
        if congrats:
            st.write(f"Congratulations on hitting PR on {ex_name}!")
        st.dataframe(df.drop(columns=['pr']).iloc[len(df)-sets:])
        df.to_csv("workouts.csv", index=True)


st.header("Select an exercise to view or a date")
unique_exercises = df['ex_name'].unique().tolist()
options = ['All'] + unique_exercises
selected = st.selectbox(options[0], options)
if selected != 'All':
    filtered_df = df[df['ex_name'] == selected]
else:
    filtered_df = df
date_range = st.date_input("Date range", value=[])

if date_range and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (pd.to_datetime(filtered_df['date']).dt.date >= start_date) &
        (pd.to_datetime(filtered_df['date']).dt.date <= end_date)
    ]
    st.dataframe(filtered_df)

st.header("Caloric calc for later predictions")
with st.form('Log your caloric intake'):
    date = st.date_input("Date of your caloric intake")
    calories = st.number_input("Calories")
    protein = st.number_input("Protein")
    carbs = st.number_input("Carbohydrates")
    fats = st.number_input("Fats")

    submitted = st.form_submit_button(label='Submit')
    if submitted:
        date_str = str(date)
        df_daily.loc[date_str, ['Calories', 'Protein', 'Carbs', 'Fats']] = [
            calories, protein, carbs, fats
        ]
        df_daily.to_csv(DAILY_CSV, index=True)
        st.success(f"Logged nutrition for {date_str}!")

st.header("Sleeper stats")

with st.form('Sleep stats in minutes'):
    date = st.date_input("Date of your sleep stats")
    time_asleep = st.number_input("Time asleep")
    awake = st.number_input("Awake")
    rem = st.number_input("REM")
    core = st.number_input("Core")
    deep = st.number_input("Deep")
    sleep_score = st.number_input("Sleep score")
    submitted = st.form_submit_button(label='Submit')

    if submitted:
        date_str = str(date)
        df_daily.loc[date_str, ['Time_asleep', 'Awake', 'REM', 'Core', 'Deep', 'Sleep_score']] = [
            time_asleep, awake, rem, core, deep, sleep_score
        ]
        df_daily.to_csv(DAILY_CSV, index=True)
        st.success(f"Logged sleep for {date_str}!")

st.subheader("Daily Health Summary")
st.dataframe(df_daily)

selection = st.selectbox("Select a visualization", ['Consistency heatmap', 'Progression overload curve'])

if selection == 'Progression overload curve':
    exercise_selection = st.selectbox("Select an exercise", unique_exercises)
    exercise_df = df[df['ex_name'] == exercise_selection].copy()
    exercise_df['e1RM'] = exercise_df['weight'] * (1 + (exercise_df['reps'] / 30))
    output_df = exercise_df.groupby('date')['e1RM'].max().reset_index()
    output_df['date'] = pd.to_datetime(output_df['date'])

    x = output_df['date']
    y = output_df['e1RM']
    fig, ax = plt.subplots()
    ax.plot(x, y, 'o-', label = 'Estimated 1 rep max over time. Progression overload curve.')
    st.pyplot(fig)

elif selection == 'Consistency heatmap':
    df['date_dt'] = pd.to_datetime(df['date'])
    available_years = sorted(df['date_dt'].dt.year.unique().tolist(), reverse=True)
    
    selected_year = st.selectbox("Select Year:", available_years if available_years else [dt.datetime.now().year])

    heatmap_df = df[df['date_dt'].dt.year == selected_year]
    workout_days = set(heatmap_df['date_dt'].dt.normalize())

    start_date = pd.Timestamp(f'{selected_year}-01-01')
    end_date = pd.Timestamp(f'{selected_year}-12-31')
    year_dates = pd.date_range(start_date, end_date, freq='D')

    first_monday = start_date - pd.Timedelta(days=start_date.dayofweek)
    num_weeks = ((end_date - first_monday).days // 7) + 1

    grid = np.full((7, num_weeks), np.nan)

    for d in year_dates:
        day_of_week = d.dayofweek
        week_idx = (d - first_monday).days // 7
        grid[day_of_week, week_idx] = 1 if d in workout_days else 0

    month_ticks = []
    month_labels = []
    for month in range(1, 13):
        m_date = pd.Timestamp(f'{selected_year}-{month:02d}-01')
        w_idx = (m_date - first_monday).days // 7
        month_ticks.append(w_idx)
        month_labels.append(m_date.strftime('%b'))

    fig, ax = plt.subplots(figsize=(15, 2.5))

    cmap = mcolors.ListedColormap(['#ebedf0', '#30a14e'])
    cmap.set_bad(color='#ffffff')

    grid_masked = np.ma.masked_invalid(grid)
    im = ax.imshow(grid_masked, cmap=cmap, vmin=0, vmax=1, aspect='equal')

    ax.set_xticks(month_ticks)
    ax.set_xticklabels(month_labels, fontsize=10)
    ax.set_yticks(range(7))
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], fontsize=9)

    ax.set_xticks(np.arange(num_weeks + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(8) - 0.5, minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
    ax.tick_params(which='minor', bottom=False, left=False)
    ax.tick_params(which='major', bottom=False, left=False)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(f"Workout Consistency - {selected_year}", fontsize=13, pad=12)

    fig.tight_layout()
    st.pyplot(fig)