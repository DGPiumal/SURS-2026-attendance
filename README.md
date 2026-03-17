# SURS 2026 Attendance

This repository contains a simple attendance scanning system with three main components:

- **backend/**: FastAPI service that records scans into Supabase.
- **dashboard/**: Streamlit dashboard to visualize attendance data live.
- **scanner/**: Flutter mobile app that scans QR codes and hits the backend.
- **qr_generator/**: A small script to generate QR codes for test student emails.

## Quick Start

### 1) Backend (FastAPI)

1. Create a `.env` file in `backend/` with the following keys:

```env
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-service-key>
```

2. Install dependencies and run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2) Dashboard (Streamlit)

Make sure the `.env` file from the backend is also available here (or copy it).

```powershell
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

### 3) Scanner App (Flutter)

Update the backend URL in `scanner/lib/main.dart` (the `apiUrl` constant). Use the host machine’s LAN IP (not `localhost`).

```dart
final String apiUrl = 'http://<YOUR_PC_IP>:8000/scan';
```

Then run:

```powershell
cd scanner
flutter run
```

### 4) Generate QR Codes (for testing)

```powershell
cd qr_generator
python generator.py
```

---

## Notes

- The backend prevents duplicate check-ins per student per day.
- The scanner app shows a dialog after each scan, providing clear feedback.
- The dashboard includes a live data feed, a leaderboard, and daily trends.
