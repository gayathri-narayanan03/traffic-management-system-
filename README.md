# AI-Powered Traffic Management System — Backend

FastAPI backend for a camera-based traffic monitoring and signal-recommendation
system, built around a simulated four-way intersection.

## What it does
- Detects and counts vehicles (car / motorcycle / bus / truck) from an uploaded
  video using YOLOv8 (`app/vehicle_detector.py`)
- Estimates a weighted traffic load and congestion level per road (`app/traffic_analyzer.py`)
- Recommends green-light durations per road for each signal cycle (`app/decision_engine.py`)
- Stores every reading and recommendation in SQLite for historical analysis (`app/models.py`)
- Exposes a REST API for a dashboard frontend to consume (`app/routes/`)
- Includes a built-in simulator so you can generate demo data with no camera/video needed

## Project structure
```
traffic_backend/
├── main.py                  # FastAPI app entry point
├── requirements.txt
├── app/
│   ├── config.py             # thresholds, road names, timing rules
│   ├── database.py           # SQLAlchemy engine/session
│   ├── models.py             # DB tables
│   ├── schemas.py            # Pydantic request/response models
│   ├── vehicle_detector.py   # YOLOv8 vehicle counting
│   ├── traffic_analyzer.py   # weighted load + congestion classification
│   ├── decision_engine.py    # green-light time allocation
│   ├── simulator.py          # synthetic traffic generator
│   └── routes/
│       ├── traffic.py        # ingest counts / video / run simulation
│       ├── dashboard.py      # live status for the dashboard
│       ├── history.py        # historical analytics
│       └── incidents.py      # alerts / incident log
```

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
uvicorn main:app --reload
```
API docs (interactive): http://127.0.0.1:8000/docs

## Try it without a camera or video
```bash
curl -X POST "http://127.0.0.1:8000/api/traffic/simulate?peak=true"
curl "http://127.0.0.1:8000/api/dashboard/current-status"
```

## Key endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/traffic/simulate` | Generate a synthetic reading + signal plan |
| POST | `/api/traffic/cycle` | Submit manual/pre-counted vehicle numbers |
| POST | `/api/traffic/upload/{road_name}` | Upload a video; runs YOLO vehicle counting |
| GET  | `/api/dashboard/current-status` | Latest status per road |
| GET  | `/api/dashboard/summary` | Dashboard summary cards |
| GET  | `/api/history/records` | Raw historical traffic records |
| GET  | `/api/history/peak-periods` | Avg load by hour of day |
| GET  | `/api/history/road-comparison` | Compare roads against each other |
| GET/POST | `/api/incidents/` | List / log incidents |
| PATCH | `/api/incidents/{id}/resolve` | Mark an incident resolved |

## Notes
- The database is SQLite (`traffic_system.db`), created automatically on first run — no separate DB setup needed.
- The YOLOv8 model (`yolov8n.pt`) downloads automatically the first time you call the video-upload endpoint.
- `opencv-python` and `ultralytics` are only needed for the video-upload endpoint — every other endpoint (simulate, manual cycle, dashboard, history) works without them.
