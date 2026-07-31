import numpy as np
import pandas as pd
import streamlit as st

st.title("My Gym Tracker")

with st.form('log workout'):
    df = pd.read_csv("workouts.csv")
    ex_name = st.text_input("Exercise name")
    date = st.date_input("Date of exercise")
    sets = st.selectbox("Number of sets", [0, 1, 2, 3, 4, 5])


    # collection_sets = []

    for i in range(sets):
        df['ex_name'].append(ex_name)
        df['date'].append(date)
        df['SiaR'].append(i+1)
        st.write(f"Set: {i+1}")
        weight = st.number_input("Weight in kg", min_value=0.0, format="%.1f", key=f"weight_s{i+1}")
        rep_count = st.number_input("Reps", min_value=0, format="%d", key=f"reps_s{i+1}")
        df['weight'].append(weight)
        df['reps'].append(rep_count)
        # collection_sets.append({'Weight': weight, 'Reps': rep_count})


    submitted = st.form_submit_button(label='Submit')

