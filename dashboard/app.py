import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Set up the page
st.set_page_config(page_title="SURS 2026 Dashboard", page_icon="📊", layout="wide")
st.title("SURS 2026 Live Attendance")

# Function to fetch data directly via Supabase REST API
def fetch_attendance():
    # The endpoint to select all records from the attendance table
    url = f"{SUPABASE_URL}/rest/v1/attendance?select=*"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Check for errors
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return []

# Fetch the data
data = fetch_attendance()

if not data:
    st.info("No attendance records found yet.")
else:
    # Convert the JSON data into a Pandas DataFrame for easy viewing
    df = pd.DataFrame(data)
    
    # Optional: Format the scanned_at column to be more readable
    if 'scanned_at' in df.columns:
        df['scanned_at'] = pd.to_datetime(df['scanned_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # Display Metrics
    total_scans = len(df)
    unique_students = df['surs_mail'].nunique() if 'surs_mail' in df.columns else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Check-ins", value=total_scans)
    with col2:
        st.metric(label="Unique Students", value=unique_students)

    st.divider()

    # Display the actual data table
    st.subheader("Recent Activity")
    
    # Sort by newest first, if the column exists
    if 'scanned_at' in df.columns:
        df = df.sort_values(by='scanned_at', ascending=False)
        
    st.dataframe(df, use_container_width=True)

    # Add a refresh button
    if st.button("Refresh Data"):
        st.rerun()