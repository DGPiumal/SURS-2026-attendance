from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import datetime  # ⬅️ We only need datetime now

load_dotenv()

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class ScanData(BaseModel):
    surs_mail: str
    device_id: str

@app.get("/")
def health_check():
    return {"status": "online", "message": "SURS 2026 API is ready."}

@app.post("/scan")
def scan_qr(scan_data: ScanData):
    # 1. Get midnight WITH your exact local timezone attached
    today_midnight = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    try:
        # 2. Check the database
        existing_scans = supabase.table("attendance").select("*") \
            .eq("surs_mail", scan_data.surs_mail) \
            .gte("scanned_at", today_midnight) \
            .execute()

        # 3. Block duplicates
        if len(existing_scans.data) > 0:
            return {"status": "duplicate", "message": "Student already checked in today!"}

        # 4. Save new scans
        response = supabase.table("attendance").insert({
            "surs_mail": scan_data.surs_mail,
            "device_id": scan_data.device_id
        }).execute()

        return {"status": "success", "message": "Attendance recorded successfully!"}

    except Exception as e:
        import traceback
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))