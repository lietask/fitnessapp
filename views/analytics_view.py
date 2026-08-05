import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from services.db_service import fetch_workouts

WORKOUTS_CSV = 'data/workouts.csv'

def render_analytics(current_user):
    st.title("Workout Analytics & Consistency")

    df_w = fetch_workouts(current_user)
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
                output_df = ex_df.groupby(['date', 'user_name'])['e1RM'].max().reset_index()
                output_df['date'] = pd.to_datetime(output_df['date'])

                fig, ax = plt.subplots(figsize=(10, 4))
                for u in output_df['user_name'].unique():
                    u_data = output_df[output_df['user_name'] == u].sort_values('date')
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
                selected_year = st.selectbox("Select Year:",
                                             available_years if available_years else [dt.datetime.now().year])
            with col2:
                all_u = ['All Users'] + sorted(df_w['user_name'].dropna().astype(str).unique().tolist())
                selected_user_hm = st.selectbox("Filter User:", all_u,
                                                index=all_u.index(current_user) if current_user in all_u else 0)

            heatmap_df = df_w[df_w['date_dt'].dt.year == selected_year].copy()
            if selected_user_hm != 'All Users':
                heatmap_df = heatmap_df[heatmap_df['user_name'] == selected_user_hm]

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

            ax.set_title(f"Workout Consistency ({selected_user_hm}) - {selected_year}", fontsize=13, pad=12)
            fig.tight_layout()
            st.pyplot(fig)