import numpy as np
import pandas as pd
import streamlit as st
import datetime as dt

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
        for i in range(sets):
            df.loc[len(df)] = {"ex_name": ex_name, "date": date, "SiaR": i+1}
            df.loc[len(df)-1, 'weight'] = collection_sets[i][0]
            df.loc[len(df)-1, 'reps'] = collection_sets[i][1]
        st.dataframe(df.iloc[len(df)-sets:])
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
        dfcal = pd.read_csv('nutrition.csv', index_col='index', parse_dates=True)
        dfcal.loc[len(dfcal)] = {'Date': date, 'Calories': calories, 'Protein': protein, 'Carbs': carbs, 'Fats': fats}
        dfcal.to_csv('nutrition.csv', index=True)

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
        dfcal = pd.read_csv('nutrition.csv', index_col='index', parse_dates=True)
        dfcal.loc[date] = {'Date': date, 'Time Asleep': time_asleep, 'Awake': awake, 'REM': rem, 'Core': core, 'Deep': deep, 'Sleep Score': sleep_score}
        dfcal.to_csv('nutrition.csv', index=True)