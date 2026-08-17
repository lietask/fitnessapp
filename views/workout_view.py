import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from services.db_service import fetch_workouts, insert_workout


def sync_set_1():
    s1_w = st.session_state.get("weight_s1", 0.0)
    s1_r = st.session_state.get("reps_s1", 0)
    for i in range(2, 9):
        st.session_state[f"weight_s{i}"] = s1_w
        st.session_state[f"reps_s{i}"] = s1_r


def render_log_workout(current_user):
    st.title("Log a Workout")
    st.write(f"Logging as **{current_user}**")

    for i in range(1, 9):
        if f"weight_s{i}" not in st.session_state:
            st.session_state[f"weight_s{i}"] = 0.0
        if f"reps_s{i}" not in st.session_state:
            st.session_state[f"reps_s{i}"] = 0

    sets = st.selectbox("Number of sets", [1, 2, 3, 4, 5, 6, 7, 8], index=2)
    
    with st.container():
        ex_name = st.text_input("Exercise name", placeholder="e.g. Bench press", key="ex_name_input")
        workout_date = st.date_input("Date of exercise", value=dt.date.today(), key="workout_date_input")

        collection_sets = []
        for i in range(sets):
            st.write(f"**Set {i + 1}**")
            col_w, col_r = st.columns(2)
            
            if i == 0:
                with col_w:
                    w = st.number_input(
                        "Weight (kg)", 
                        min_value=0.0, 
                        format="%.1f", 
                        step=0.5, 
                        key="weight_s1",
                        on_change=sync_set_1
                    )
                with col_r:
                    r = st.number_input(
                        "Reps", 
                        min_value=0, 
                        format="%d", 
                        step=1, 
                        key="reps_s1",
                        on_change=sync_set_1
                    )
            else:
                with col_w:
                    w = st.number_input(
                        "Weight (kg)", 
                        min_value=0.0, 
                        format="%.1f", 
                        step=0.5, 
                        key=f"weight_s{i + 1}"
                    )
                with col_r:
                    r = st.number_input(
                        "Reps", 
                        min_value=0, 
                        format="%d", 
                        step=1, 
                        key=f"reps_s{i + 1}"
                    )
            collection_sets.append([w, r])

        submitted = st.button("Submit Workout Log", type="primary", use_container_width=True)

        if submitted:
            if not ex_name.strip():
                st.error("Please enter an exercise name.")
            else:
                new_rows = []
                for i in range(sets):
                    new_rows.append({
                        'date': str(workout_date),
                        'ex_name': ex_name.strip(),
                        'set_number': i + 1,
                        'reps': collection_sets[i][1],
                        'weight': collection_sets[i][0],
                        'user_name': current_user
                    })

                insert_workout(new_rows)

                st.success(f"Logged {sets} sets of {ex_name} for {current_user} on {workout_date}!")
                st.dataframe(pd.DataFrame(new_rows), use_container_width=True)

def render_view_workout(current_user):
    st.title("Workout History")

    df_w = fetch_workouts(current_user)
    if df_w.empty:
        st.info("No workout data logged yet.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            all_users = ['All'] + sorted(df_w['user_name'].dropna().astype(str).unique().tolist())
            user_filter = st.selectbox("Filter by User:", all_users,
                                       index=all_users.index(current_user) if current_user in all_users else 0)
        with col2:
            unique_ex = ['All'] + sorted(df_w['ex_name'].dropna().unique().tolist())
            ex_filter = st.selectbox("Filter by Exercise:", unique_ex)
        with col3:
            date_range = st.date_input("Date Range:", value=[])

        filtered_df = df_w.copy()
        if user_filter != 'All':
            filtered_df = filtered_df[filtered_df['user_name'] == user_filter]
        if ex_filter != 'All':
            filtered_df = filtered_df[filtered_df['ex_name'] == ex_filter]
        if date_range and len(date_range) == 2:
            start_d, end_d = date_range
            filtered_df['date_dt'] = pd.to_datetime(filtered_df['date']).dt.date
            filtered_df = filtered_df[(filtered_df['date_dt'] >= start_d) & (filtered_df['date_dt'] <= end_d)].drop(
                columns=['date_dt'])

        st.write(f"Showing **{len(filtered_df)}** records:")
        st.dataframe(filtered_df, use_container_width=True)