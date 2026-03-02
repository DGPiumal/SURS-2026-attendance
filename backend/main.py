import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Load the environment variables from the .env file
load_dotenv()

# 2. Initialize the FastAPI app
app = FastAPI(
    title="SURS 2026 Attendance API",
    description="Backend for tracking student check-ins via QR codes.",
    version="1.0.0"
)

# 3. Connect to Supabase securely
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials. Check your .env file!")

# Create the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 4. Define the Data Model using Pydantic
class ScanRequest(BaseModel):
    surs_mail: str
    device_id: str = "unknown_scanner"

# 5. Define our API Endpoints
@app.get("/")
def health_check():
    """Simple health check to verify the API is running."""
    return {"status": "online", "message": "SURS 2026 API is ready."}

@app.post("/scan")
def record_scan(scan_data: ScanRequest):
    """
    Receives a scanned SURS email and logs it into the Supabase database.
    """
    try:
        # Attempt to insert the record into the 'attendance' table
        response = supabase.table("attendance").insert({
            "surs_mail": scan_data.surs_mail,
            "device_id": scan_data.device_id
        }).execute()
        
        return {
            "status": "success", 
            "message": f"Successfully checked in {scan_data.surs_mail}",
            "data": response.data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")