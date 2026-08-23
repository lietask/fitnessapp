import httpx
import streamlit as st
import pandas as pd
from supabase import create_client, Client


def get_client() -> Client:
    url = st.secrets['SUPABASE_URL']
    key = st.secrets['SUPABASE_KEY']
    return create_client(url, key)


def get_db() -> Client:
    if 'supabase_client' not in st.session_state:
        st.session_state['supabase_client'] = get_client()
    return st.session_state['supabase_client']


def run_db_operation(operation):
    try:
        client = get_db()
        return operation(client)
    except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadTimeout, httpx.NetworkError, Exception) as e:
        st.session_state['supabase_client'] = get_client()
        client = get_db()
        return operation(client)


def fetch_workouts(current_user) -> pd.DataFrame:
    try:
        response = run_db_operation(
            lambda db: db.table('workouts').select('*').eq('user_name', current_user).execute()
        )
        if response.data is not None:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to fetch workouts: {e}")
        return pd.DataFrame()


def insert_workout(rows: list):
    run_db_operation(
        lambda db: db.table('workouts').insert(rows).execute()
    )


def fetch_daily_logs(current_user) -> pd.DataFrame:
    try:
        response = run_db_operation(
            lambda db: db.table('daily_logs').select('*').eq('user_name', current_user).execute()
        )
        data = response.data
        if not data:
            return pd.DataFrame(columns=['Date', 'User', 'Calories', 'Protein', 'Carbs', 'Fats',
                                         'Time_asleep', 'Awake', 'REM', 'Core', 'Deep', 'Sleep_score'])
        df = pd.DataFrame(data)
        df = df.rename(columns={
            'date': 'Date', 'user_name': 'User', 'calories': 'Calories',
            'protein': 'Protein', 'carbs': 'Carbs', 'fats': 'Fats',
            'time_asleep': 'Time_asleep', 'awake': 'Awake', 'rem': 'REM',
            'core': 'Core', 'deep': 'Deep', 'sleep_score': 'Sleep_score'
        })
        return df
    except Exception as e:
        st.error(f"Failed to fetch daily logs: {e}")
        return pd.DataFrame(columns=['Date', 'User', 'Calories', 'Protein', 'Carbs', 'Fats',
                                     'Time_asleep', 'Awake', 'REM', 'Core', 'Deep', 'Sleep_score'])


def upsert_daily_logs(row: dict):
    run_db_operation(
        lambda db: db.table('daily_logs').upsert(row, on_conflict='date,user_name').execute()
    )