"""
Central configuration for the AI-Powered Traffic Management System backend.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SQLite database (swap for Postgres/MySQL URL later if needed)
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'traffic_system.db')}"

# The four roads of the simulated intersection
ROADS = ["North", "South", "East", "West"]

# Vehicle classes we care about (subset of COCO classes used by YOLO)
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

# Signal timing rules
MIN_GREEN_TIME = 10      # seconds, floor for any road even with low traffic
MAX_GREEN_TIME = 90      # seconds, ceiling to prevent starving other roads
BASE_CYCLE_TIME = 120    # total seconds to distribute across 4 roads per cycle
CONGESTION_THRESHOLDS = {
    "low": 10,       # < 10 weighted vehicles
    "medium": 25,    # 10-25
    "high": 45,      # 25-45
    "severe": 9999,  # > 45
}

# Weight different vehicle types differently when estimating "load" on a road
VEHICLE_WEIGHTS = {
    "motorcycle": 0.5,
    "car": 1.0,
    "bus": 2.5,
    "truck": 2.5,
}

# Path to YOLO model weights (nano model auto-downloads on first run if absent)
YOLO_MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")
