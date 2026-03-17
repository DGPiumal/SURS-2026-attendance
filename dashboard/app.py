"""Streamlit dashboard for the SURS 2026 attendance tracking system.

This dashboard queries the Supabase "attendance" table and provides live insights
including total scans, top attendees, daily trends, and a live data feed.
"""

import datetime
import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv

# Load configuration from .env (Supabase credentials)
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Configure Streamlit layout and theme
st.set_page_config(page_title="SURS 2026 | UoP", page_icon="🦁", layout="wide")

# UoP official brand colors
UOP_MAROON = "#800000"
UOP_GOLD = "#FFD700"

# Apply custom styling for metric cards and banner.
st.markdown(
    f"""
<style>
    div[data-testid="metric-container"] {{
        border: 1px solid rgba(255, 215, 0, 0.3);
        padding: 5% 5% 5% 10%;
        border-radius: 8px;
        border-left: 8px solid {UOP_GOLD};
        background-color: rgba(128, 0, 0, 0.05);
    }}

    .mvp-banner {{
        background: linear-gradient(90deg, {UOP_MAROON} 0%, rgba(128,0,0,0.8) 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        border-bottom: 5px solid {UOP_GOLD};
        margin-bottom: 20px;
        text-align: center;
    }}

    .mvp-title {{ font-size: 1.2rem; font-weight: bold; color: {UOP_GOLD}; margin-bottom: 5px; }}
    .mvp-emails {{ font-size: 1.5rem; font-weight: 900; }}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(ttl=5)
def fetch_attendance():
    url = f"{SUPABASE_URL}/rest/v1/attendance?select=*"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return []


# Fetch the live data
data = fetch_attendance()

# --- SIDEBAR ---
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/University_of_Peradeniya_crest.png/220px-University_of_Peradeniya_crest.png",
        width=100,
    )
    st.title("SURS 2026")
    st.markdown("**Event Control Panel**")
    if st.button("🔄 Refresh Live Data", use_container_width=True):
        st.rerun()
    st.divider()
    st.markdown("### 🔍 Search Student")
    search_email = st.text_input("Enter Email Address (e.g., s22001)")

# --- MAIN DASHBOARD ---
st.title("🦁 SURS 2026 Live Command Center")

if not data:
    st.info("No attendance records found yet. Waiting for the first scan...")
else:
    # 1. Clean and Prepare the Data
    df = pd.DataFrame(data)

    if "scanned_at" in df.columns:
        df["scanned_at"] = pd.to_datetime(df["scanned_at"])
        df["Date"] = df["scanned_at"].dt.date
        df["Time"] = df["scanned_at"].dt.strftime("%I:%M %p")
        df["Hour"] = df["scanned_at"].dt.hour

    # 2. Calculate Top-Level Metrics
    total_scans = len(df)
    unique_students = df["surs_mail"].nunique() if "surs_mail" in df.columns else 0
    today = datetime.datetime.now().date()
    scans_today = len(df[df["Date"] == today]) if "Date" in df.columns else 0

    # Calculate Busiest Day
    busiest_day_count = 0
    busiest_day_date = "N/A"
    if "Date" in df.columns and not df.empty:
        daily_counts = df["Date"].value_counts()
        busiest_day_date = daily_counts.idxmax().strftime("%b %d")
        busiest_day_count = daily_counts.max()

    # --- THE MVP BANNER ---
    if "surs_mail" in df.columns:
        student_counts = df["surs_mail"].value_counts().reset_index()
        student_counts.columns = ["Student Email", "Total Check-ins"]

        max_checkins = student_counts["Total Check-ins"].max()
        # Find ALL students who have the exact max score (handles ties!)
        top_students = student_counts[
            student_counts["Total Check-ins"] == max_checkins
        ]["Student Email"].tolist()

        # Format the text to display
        if len(top_students) <= 3:
            mvp_text = " 🏆 ".join(top_students)
        else:
            mvp_text = f"🏆 {top_students[0]}, {top_students[1]} + {len(top_students)-2} others!"

        st.markdown(
            f"""
        <div class="mvp-banner">
            <div class="mvp-title">👑 MOST ACTIVE PARTICIPANTS ({max_checkins} Check-ins)</div>
            <div class="mvp-emails">{mvp_text}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # 3. Display Hero Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Total Scans", value=total_scans)
    with m2:
        st.metric(label="Unique Students", value=unique_students)
    with m3:
        st.metric(label="Today's Check-ins", value=scans_today)
    with m4:
        st.metric(
            label="Busiest Day Peak",
            value=f"{busiest_day_count} scans",
            delta=busiest_day_date,
            delta_color="off",
        )

    st.divider()

    # 4. Create Interactive Tabs
    tab1, tab2, tab3 = st.tabs(
        ["📈 Overview & Trends", "🏆 Leaderboard", "📋 Live Data Feed"]
    )

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Day-wise Attendance Flow")
            if "Date" in df.columns:
                daily_counts_df = (
                    df.groupby("Date").size().reset_index(name="Check-ins")
                )
                fig_bar = px.bar(
                    daily_counts_df,
                    x="Date",
                    y="Check-ins",
                    text="Check-ins",
                    color_discrete_sequence=[UOP_MAROON],
                )
                fig_bar.update_traces(
                    textposition="outside",
                    marker_line_color=UOP_GOLD,
                    marker_line_width=2,
                )
                fig_bar.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="",
                    yaxis_title="Total Scans",
                    height=350,
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.subheader("Peak Check-in Hours")
            if "Hour" in df.columns:
                hourly_counts = df.groupby("Hour").size().reset_index(name="Traffic")
                hourly_counts["Hour Label"] = hourly_counts["Hour"].apply(
                    lambda x: f"{x}:00"
                )
                fig_area = px.area(
                    hourly_counts,
                    x="Hour Label",
                    y="Traffic",
                    markers=True,
                    color_discrete_sequence=[UOP_GOLD],
                )
                fig_area.update_traces(
                    line_color=UOP_MAROON, marker=dict(color=UOP_MAROON, size=8)
                )
                fig_area.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis_title="Time of Day",
                    yaxis_title="Foot Traffic",
                    height=350,
                )
                st.plotly_chart(fig_area, use_container_width=True)

    with tab2:
        st.subheader("Top 10 Most Active Students")
        if "surs_mail" in df.columns:
            # Sort for the Horizontal Bar Chart (bottom to top for Plotly)
            top_10 = student_counts.head(10).sort_values(
                by="Total Check-ins", ascending=True
            )

            fig_hbar = px.bar(
                top_10,
                x="Total Check-ins",
                y="Student Email",
                orientation="h",
                text="Total Check-ins",
                color_discrete_sequence=[UOP_MAROON],
            )
            fig_hbar.update_traces(
                textposition="outside",
                marker_line_color=UOP_GOLD,
                marker_line_width=1.5,
            )
            fig_hbar.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Total Check-ins",
                yaxis_title="",
                height=450,
            )

            # Put the chart on the left, and the raw table on the right
            s1, s2 = st.columns([2, 1])
            with s1:
                st.plotly_chart(fig_hbar, use_container_width=True)
            with s2:
                st.dataframe(student_counts, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Live Raw Feed")
        display_df = df.copy()

        # Apply Search Filter from Sidebar
        if search_email:
            display_df = display_df[
                display_df["surs_mail"].str.contains(search_email, case=False, na=False)
            ]
            st.success(
                f"Showing results for: {search_email} ({len(display_df)} records found)"
            )

        if "scanned_at" in display_df.columns:
            display_df = display_df.sort_values(by="scanned_at", ascending=False)
            display_df["scanned_at"] = display_df["scanned_at"].dt.strftime(
                "%Y-%m-%d | %I:%M:%S %p"
            )

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        csv = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Secure Event Data (.CSV)",
            data=csv,
            file_name=f"SURS_2026_UoP_Attendance_{today}.csv",
            mime="text/csv",
            use_container_width=True,
        )
