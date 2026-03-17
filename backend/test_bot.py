"""Simple script to populate the Supabase attendance table with realistic-looking historical data.

This is intended for local development / demo purposes only.
"""

import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Starting load test: inserting historical attendance data (past 7 days)...")

# Generate a fixed set of fake student email addresses.
all_students = [f"s22{str(i).zfill(3)}@sci.pdn.ac.lk" for i in range(1, 51)]

records_added = 0

# Insert one day's worth of attendance for each of the last 7 days.
for days_ago in range(7, 0, -1):
    target_date = datetime.now() - timedelta(days=days_ago)

    # Randomly decide how many students attended this day.
    daily_attendance_count = random.randint(30, 48)
    daily_students = random.sample(all_students, daily_attendance_count)

    daily_records = []
    for email in daily_students:
        # Generate a plausible check-in time between 08:00 and 10:59.
        random_hour = random.randint(8, 10)
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)

        scan_time = target_date.replace(
            hour=random_hour, minute=random_minute, second=random_second
        )

        daily_records.append(
            {
                "surs_mail": email,
                "device_id": "TIME_TRAVEL_BOT",
                # Supabase expects ISO 8601 timestamps.
                "scanned_at": scan_time.isoformat(),
            }
        )

    try:
        supabase.table("attendance").insert(daily_records).execute()
        print(
            f"Inserted {len(daily_records)} records for {target_date.strftime('%Y-%m-%d')}"
        )
        records_added += len(daily_records)
    except Exception as e:
        print(f"Error inserting data for {target_date.strftime('%Y-%m-%d')}: {e}")

print(f"Done. Added {records_added} historical scans to the database.")
print("Tip: Refresh the dashboard to see the new data.")
