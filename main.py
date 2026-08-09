import numpy as np
import pandas as pd
import streamlit as st
import datetime as dt
import os

from views.workout_view import render_log_workout, render_view_workout
from views.nutrition_view import render_nutrition
from views.analytics_view import render_analytics


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
    nav_options = ["Log Workout", "View Workouts", "Nutrition & Sleep", "Analytics & Heatmap"]

    page = st.sidebar.radio("Navigation", nav_options)

    if page == "Log Workout":
        render_log_workout(current_user)

    elif page == "View Workouts":
        render_view_workout(current_user)

    elif page == "Nutrition & Sleep":
        render_nutrition(current_user)

    elif page == "Analytics & Heatmap":
        render_analytics(current_user)
