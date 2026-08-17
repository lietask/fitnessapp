import numpy as np
import pandas as pd
import streamlit as st
import datetime as dt
import os

from views.workout_view import render_log_workout, render_view_workout
from views.nutrition_view import render_nutrition
from views.analytics_view import render_analytics


st.set_page_config(page_title="Gym Tracker", layout="wide")

import streamlit.components.v1 as components

def load_css(file_name: str = "style.css"):
    css_path = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def inject_js():
    # Injects client-side keyboard shortcuts and micro-interactions
    components.html("""
        <script>
        const doc = window.parent.document;
        doc.addEventListener('keydown', function(e) {
            // Cmd+Enter or Ctrl+Enter to quickly submit active forms
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                const submitBtn = doc.querySelector('div[data-testid="stFormSubmitButton"] button');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        });
        </script>
    """, height=0)

load_css("style.css")
inject_js()

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
    if st.sidebar.button("Switch User / Logout", use_container_width=True):
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
