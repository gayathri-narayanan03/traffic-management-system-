# Computer Vision - Smart Traffic Management System

This module detects vehicles in traffic video feeds using YOLO and OpenCV.

## Features
- Detects cars, motorcycles, buses, and trucks.
- Counts vehicles inside defined road regions.
- Supports traffic video input.
- Sends vehicle-count data to the FastAPI backend.
- Allows road-region polygon selection.

## Files
- `detect.py` - Detects and counts vehicles and sends results to the backend.
- `draw_polygon.py` - Helps define the road region using polygon coordinates.
- `requirements.txt` - Lists the Python dependencies for this module.

## Setup
Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the detector:

```bash
python detect.py
```

Make sure the FastAPI backend is running before enabling backend reporting.
