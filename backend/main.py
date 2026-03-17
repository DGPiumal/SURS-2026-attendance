"""Backend API for the SURS 2026 attendance scanner.

This service receives scanned QR email payloads and stores attendance
records in Supabase while enforcing a single scan per student per day.
"""

from datetime import datetime
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import Client, create_client

load_dotenv()

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class ScanData(BaseModel):
    """Payload received from the scanner device."""

    surs_mail: str
    device_id: str


@app.get("/")
def health_check():
    """Basic health check endpoint."""

    return {"status": "online", "message": "SURS 2026 API is ready."}


@app.post("/scan")
def scan_qr(scan_data: ScanData):
    """Record a scan and prevent duplicate check-ins for the same day."""

    # Use local time (with timezone) to determine the current day boundary.
    today_midnight = (
        datetime.now()
        .astimezone()
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .isoformat()
    )

    try:
        # If the student has already scanned today, block the second scan.
        existing_scans = (
            supabase.table("attendance")
            .select("*")
            .eq("surs_mail", scan_data.surs_mail)
            .gte("scanned_at", today_midnight)
            .execute()
        )

        if existing_scans.data:
            return {
                "status": "duplicate",
                "message": "Student already checked in today!",
            }

        # Insert the new attendance record.
        supabase.table("attendance").insert(
            {
                "surs_mail": scan_data.surs_mail,
                "device_id": scan_data.device_id,
            }
        ).execute()

        return {"status": "success", "message": "Attendance recorded successfully!"}

    except Exception as e:
        # Preserve trace for debugging while returning a clean error response.
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
