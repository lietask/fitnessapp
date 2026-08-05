import streamlit as st
import pandas as pd
from supabase import create_client, client


def get_client():
    url = st.secrets['SUPABASE_URL']
    key = st.secrets['SUPABASE_KEY']
    return create_client(url, key)

supabase = get_client()

def fetch_workouts(current_user) -> pd.DataFrame:
    response = supabase.table('workouts').select('*').eq('user_name', current_user).execute()
    if response.data is not None:
        data = response.data
        return pd.DataFrame(data)
    else:
        st.error("Failed to fetch workouts from the database.")
        return pd.DataFrame()

def insert_workout(rows: list):
    supabase.table('workouts').insert(rows).execute()

def fetch_daily_logs(current_user) -> pd.DataFrame:
    response = supabase.table('daily_logs').select('*').eq('user_name', current_user).execute()
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

def upsert_daily_logs(row: dict):
    supabase.table('daily_logs').upsert(row, on_conflict='date,user_name').execute()