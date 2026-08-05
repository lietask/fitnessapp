import numpy as np
import pandas as pd
import streamlit as st
import datetime as dt
import os

from views.workout_view import render_log_workout, render_view_workout
from views.nutrition_view import render_nutrition
from views.analytics_view import render_analytics

WORKOUTS_CSV = 'data/workouts.csv'
DAILY_CSV = 'data/daily_logs.csv'

if os.path.exists(WORKOUTS_CSV):
    df_workouts = pd.read_csv(WORKOUTS_CSV)
    if 'user' not in df_workouts.columns:
        df_workouts['user'] = 'Default'
        df_workouts.to_csv(WORKOUTS_CSV, index=False)
else:
    df_workouts = pd.DataFrame(columns=['index', 'date', 'ex_name', 'SiaR', 'reps', 'weight', 'user'])
    df_workouts.to_csv(WORKOUTS_CSV, index=False)

if os.path.exists(DAILY_CSV):
    df_daily = pd.read_csv(DAILY_CSV)
    if 'User' not in df_daily.columns:
        df_daily['User'] = 'Default'
        df_daily.to_csv(DAILY_CSV, index=False)
else:
    df_daily = pd.DataFrame(columns=['Date', 'User', 'Calories', 'Protein', 'Carbs', 'Fats',
                                     'Time_asleep', 'Awake', 'REM', 'Core', 'Deep', 'Sleep_score'])
    df_daily.to_csv(DAILY_CSV, index=False)



st.set_page_config(page_title="Gym Tracker", layout="wide")

if 'user_name' not in st.session_state or not st.session_state['user_name']:

    st.title("Gym tracker")
    st.subheader("Enter your Name. And keep it the same each time you log in.")
    
    with st.form('login_form'):
        user_input = st.text_input("Name", placeholder="e.g. Alex etc.")
        submitted = st.form_submit_button("Start Tracking", type="primary")
        if submitted:
            if user_input.strip():
                st.session_state['user_name'] = user_input.strip()
                st.rerun()
            else:
                st.error("Please enter a valid name before proceeding.")
    st.stop()

else:
    current_user = st.session_state['user_name']

    st.sidebar.markdown(f"### 👤 User: **{current_user}**")
    if st.sidebar.button("Switch User / Logout"):
        st.session_state['user_name'] = None
        st.rerun()

    st.sidebar.divider()
    page = st.sidebar.radio(
        "Navigation",
        ["Log Workout", "View Workouts", "Nutrition & Sleep", "Analytics & Heatmap"]
    )

    if page == "Log Workout":
        render_log_workout(current_user)

    elif page == "View Workouts":
        render_view_workout(current_user)

    elif page == "Nutrition & Sleep":
        render_nutrition(current_user)

    elif page == "Analytics & Heatmap":
        render_analytics(current_user)

