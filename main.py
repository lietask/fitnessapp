import numpy as np
import pandas as pd
import streamlit as st
import datetime as dt
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

WORKOUTS_CSV = 'workouts.csv'
DAILY_CSV = 'daily_logs.csv'
WORKOUT_COLUMNS = ('index', 'date', 'ex_name', 'SiaR', 'reps', 'weight', 'user')

if os.path.exists(WORKOUTS_CSV):
    df_workouts = pd.read_csv(WORKOUTS_CSV)
    if 'pr' in df_workouts.columns:
        df_workouts = df_workouts.drop(columns=['pr'])
    if 'user' not in df_workouts.columns:
        df_workouts['user'] = 'Default'
    df_workouts = df_workouts.reindex(columns=WORKOUT_COLUMNS)
    df_workouts.to_csv(WORKOUTS_CSV, index=False)
else:
    df_workouts = pd.DataFrame(columns=pd.Index(WORKOUT_COLUMNS))
    df_workouts.to_csv(WORKOUTS_CSV, index=False)

if os.path.exists(DAILY_CSV):
    df_daily = pd.read_csv(DAILY_CSV)
    if 'User' not in df_daily.columns:
        df_daily['User'] = 'Default'
        df_daily.to_csv(DAILY_CSV, index=False)
else:
    df_daily = pd.DataFrame(columns=pd.Index(['Date', 'User', 'Calories', 'Protein', 'Carbs', 'Fats',
                                              'Time_asleep', 'Awake', 'REM', 'Core', 'Deep', 'Sleep_score']))
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
        st.title("Log a Workout")
        st.write(f"Logging as **{current_user}**")
        
        sets = st.selectbox("Number of sets", [1, 2, 3, 4, 5, 6, 7, 8])
        with st.form('log_workout_form'):
            ex_name = st.text_input("Exercise name", placeholder="e.g. Bench press")
            workout_date = st.date_input("Date of exercise", value=dt.date.today())
            
            collection_sets = []
            for i in range(sets):
                st.write(f"**Set {i+1}**")
                col_w, col_r = st.columns(2)
                with col_w:
                    w = st.number_input("Weight (kg)", min_value=0.0, format="%.1f", key=f"weight_s{i+1}")
                with col_r:
                    r = st.number_input("Reps", min_value=0, format="%d", key=f"reps_s{i+1}")
                collection_sets.append([w, r])
                
            submitted = st.form_submit_button(label='Submit Workout Log', type="primary")
            
            if submitted:
                if not ex_name.strip():
                    st.error("Please enter an exercise name.")
                else:
                    df_w = pd.read_csv(WORKOUTS_CSV)
                    new_rows = []
                    for i in range(sets):
                        new_idx = len(df_w) + i
                        new_rows.append({
                            'index': new_idx,
                            'date': str(workout_date),
                            'ex_name': ex_name.strip(),
                            'SiaR': i + 1,
                            'reps': collection_sets[i][1],
                            'weight': collection_sets[i][0],
                            'user': current_user
                        })
                    df_new = pd.DataFrame(new_rows)
                    df_w = pd.concat([df_w, df_new], ignore_index=True)
                    df_w.to_csv(WORKOUTS_CSV, index=False)
                    st.success(f"Logged {sets} sets of {ex_name} for {current_user} on {workout_date}!")
                    st.dataframe(df_new)

    elif page == "View Workouts":
        st.title("Workout History")
        
        df_w = pd.read_csv(WORKOUTS_CSV)
        if df_w.empty:
            st.info("No workout data logged yet.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                all_users = ['All'] + sorted(df_w['user'].dropna().astype(str).unique().tolist())
                user_filter = st.selectbox("Filter by User:", all_users, index=all_users.index(current_user) if current_user in all_users else 0)
            with col2:
                unique_ex = ['All'] + sorted(df_w['ex_name'].dropna().unique().tolist())
                ex_filter = st.selectbox("Filter by Exercise:", unique_ex)
            with col3:
                date_range = st.date_input("Date Range:", value=[])
                
            filtered_df = df_w.copy()
            if user_filter != 'All':
                filtered_df = filtered_df[filtered_df['user'] == user_filter]
            if ex_filter != 'All':
                filtered_df = filtered_df[filtered_df['ex_name'] == ex_filter]
            if date_range and len(date_range) == 2:
                start_d, end_d = date_range
                filtered_df['date_dt'] = pd.to_datetime(filtered_df['date']).dt.date
                filtered_df = filtered_df[(filtered_df['date_dt'] >= start_d) & (filtered_df['date_dt'] <= end_d)].drop(columns=['date_dt'])
                
            st.write(f"Showing **{len(filtered_df)}** records:")
            st.dataframe(filtered_df, use_container_width=True)

    elif page == "Nutrition & Sleep":
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
                    df_d = pd.read_csv(DAILY_CSV)
                    date_str = str(n_date)
                    
                    mask = (df_d['Date'].astype(str) == date_str) & (df_d['User'] == current_user)
                    if mask.any():
                        idx = df_d[mask].index[0]
                        df_d.loc[idx, ['Calories', 'Protein', 'Carbs', 'Fats']] = [calories, protein, carbs, fats]
                    else:
                        new_row = {
                            'Date': date_str, 'User': current_user,
                            'Calories': calories, 'Protein': protein, 'Carbs': carbs, 'Fats': fats,
                            'Time_asleep': np.nan, 'Awake': np.nan, 'REM': np.nan, 'Core': np.nan, 'Deep': np.nan, 'Sleep_score': np.nan
                        }
                        df_d = pd.concat([df_d, pd.DataFrame([new_row])], ignore_index=True)
                    df_d.to_csv(DAILY_CSV, index=False)
                    st.success(f"Logged nutrition for {current_user} on {date_str}!")
                    
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
                    df_d = pd.read_csv(DAILY_CSV)
                    date_str = str(s_date)
                    
                    mask = (df_d['Date'].astype(str) == date_str) & (df_d['User'] == current_user)
                    if mask.any():
                        idx = df_d[mask].index[0]
                        df_d.loc[idx, ['Time_asleep', 'Awake', 'REM', 'Core', 'Deep', 'Sleep_score']] = [
                            time_asleep, awake, rem, core, deep, sleep_score
                        ]
                    else:
                        new_row = {
                            'Date': date_str, 'User': current_user,
                            'Calories': np.nan, 'Protein': np.nan, 'Carbs': np.nan, 'Fats': np.nan,
                            'Time_asleep': time_asleep, 'Awake': awake, 'REM': rem, 'Core': core, 'Deep': deep, 'Sleep_score': sleep_score
                        }
                        df_d = pd.concat([df_d, pd.DataFrame([new_row])], ignore_index=True)
                    df_d.to_csv(DAILY_CSV, index=False)
                    st.success(f"Logged sleep stats for {current_user} on {date_str}!")
                    
        with tab_summary:
            st.header("Daily Health Summary Table")
            df_d = pd.read_csv(DAILY_CSV)
            user_opt = st.selectbox("Show logs for:", ["Current User (" + current_user + ")", "All Users"])
            if user_opt.startswith("Current User"):
                display_df = df_d[df_d['User'] == current_user]
            else:
                display_df = df_d
            st.dataframe(display_df, use_container_width=True)

    elif page == "Analytics & Heatmap":
        st.title("Workout Analytics & Consistency")
        
        df_w = pd.read_csv(WORKOUTS_CSV)
        if df_w.empty:
            st.warning("No workout data available for analytics.")
        else:
            chart_selection = st.selectbox('Select Chart View:', ['Consistency Heatmap', 'Progression Overload Curve'])
            
            if chart_selection == 'Progression Overload Curve':
                unique_ex = sorted(df_w['ex_name'].dropna().unique().tolist())
                selected_ex = st.selectbox("Select Exercise", unique_ex)
                
                ex_df = df_w[df_w['ex_name'] == selected_ex].copy()
                if ex_df.empty:
                    st.warning(f"No records for {selected_ex}.")
                else:
                    ex_df['e1RM'] = ex_df['weight'] * (1 + (ex_df['reps'] / 30))
                    output_df = ex_df.groupby(['date', 'user'])['e1RM'].max().reset_index()
                    output_df['date'] = pd.to_datetime(output_df['date'])
                    
                    fig, ax = plt.subplots(figsize=(10, 4))
                    for u in output_df['user'].unique():
                        u_data = output_df[output_df['user'] == u].sort_values('date')
                        ax.plot(u_data['date'], u_data['e1RM'], 'o-', label=f"{u} (e1RM)")
                        
                    ax.set_title(f"Progression Overload - Estimated 1RM for {selected_ex}", fontsize=13)
                    ax.set_xlabel("Date")
                    ax.set_ylabel("e1RM (kg)")
                    ax.legend()
                    ax.grid(True, linestyle='--', alpha=0.5)
                    st.pyplot(fig)
                    
            elif chart_selection == 'Consistency Heatmap':
                df_w['date_dt'] = pd.to_datetime(df_w['date'])
                available_years = sorted(df_w['date_dt'].dt.year.unique().tolist(), reverse=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    selected_year = st.selectbox("Select Year:", available_years if available_years else [dt.datetime.now().year])
                with col2:
                    all_u = ['All Users'] + sorted(df_w['user'].dropna().astype(str).unique().tolist())
                    selected_user_hm = st.selectbox("Filter User:", all_u, index=all_u.index(current_user) if current_user in all_u else 0)
                    
                heatmap_df = df_w[df_w['date_dt'].dt.year == selected_year].copy()
                if selected_user_hm != 'All Users':
                    heatmap_df = heatmap_df[heatmap_df['user'] == selected_user_hm]
                    
                workout_days = set(heatmap_df['date_dt'].dt.normalize())
                
                start_date = pd.Timestamp(f'{selected_year}-01-01')
                end_date = pd.Timestamp(f'{selected_year}-12-31')
                year_dates = pd.date_range(start_date, end_date, freq='D')
                
                first_monday = start_date - pd.Timedelta(days=start_date.dayofweek)
                num_weeks = ((end_date - first_monday).days // 7) + 1
                
                grid = np.full((7, int(num_weeks)), np.nan)
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
                    
                ax.set_title(f"Workout Consistency ({selected_user_hm}) - {selected_year}", fontsize=13, pad=12)
                fig.tight_layout()
                st.pyplot(fig)