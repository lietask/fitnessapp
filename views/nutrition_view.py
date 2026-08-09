import pandas as pd
import numpy as np
import streamlit as st
import datetime as dt

from services.db_service import fetch_daily_logs, upsert_daily_logs

def render_nutrition(current_user):
    st.title("Daily Health Logs (Nutrition & Sleep)")

    tab_nutr, tab_sleep, tab_summary = st.tabs(["Log Nutrition", "Log Sleep", "Daily Summary"])

    with tab_nutr:
        st.header("Log Caloric & Macro Intake")
        with st.form('log_nutrition_form'):
            n_date = st.date_input("Date", value=dt.date.today(), key='n_date')
            calories = st.number_input("Calories (kcal)", min_value=0.0, format="%.0f")
            protein = st.number_input("Protein (g)", min_value=0.0, format="%.1f")
            carbs = st.number_input("Carbohydrates (g)", min_value=0.0, format="%.1f")
            fats = st.number_input("Fats (g)", min_value=0.0, format="%.1f")

            n_submitted = st.form_submit_button("Submit Nutrition", type="primary")
            if n_submitted:
                row = {
                    'date': str(n_date),
                    'user_name': current_user,
                    'calories': calories,
                    'protein': protein,
                    'carbs': carbs,
                    'fats': fats
                }
                upsert_daily_logs(row)
                st.success(f"Logged nutrition for {current_user} on {n_date}!")

    with tab_sleep:
        st.header("Log Sleep Stats")
        with st.form('log_sleep_form'):
            s_date = st.date_input("Date", value=dt.date.today(), key='s_date')
            time_asleep = st.number_input("Time Asleep (mins)", min_value=0.0)
            awake = st.number_input("Awake (mins)", min_value=0.0)
            rem = st.number_input("REM (mins)", min_value=0.0)
            core = st.number_input("Core (mins)", min_value=0.0)
            deep = st.number_input("Deep (mins)", min_value=0.0)
            sleep_score = st.number_input("Sleep Score", min_value=0.0, max_value=100.0)

            s_submitted = st.form_submit_button("Submit Sleep Stats", type="primary")
            if s_submitted:
                row = {
                    'date': str(s_date),
                    'user_name': current_user,
                    'time_asleep': time_asleep,
                    'awake': awake,
                    'rem': rem,
                    'core': core,
                    'deep': deep,
                    'sleep_score': sleep_score
                }
                upsert_daily_logs(row)
                st.success(f"Logged sleep stats for {current_user} on {s_date}!")

    with tab_summary:
        st.header("Daily Health Summary Table")
        df_d = fetch_daily_logs(current_user)
        user_opt = st.selectbox("Show logs for:", ["Current User (" + current_user + ")", "All Users"])
        if user_opt.startswith("Current User"):
            display_df = df_d[df_d['User'] == current_user]
        else:
            display_df = df_d
        st.dataframe(display_df, use_container_width=True)
