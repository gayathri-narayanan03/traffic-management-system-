
from ultralytics import YOLO
import cv2
import numpy as np
import json
import requests
import os

# ================ SETTINGS ================
BACKEND_URL = "http://127.0.0.1:8000/api/traffic/cycle"
SEND_TO_BACKEND = True
REPORT_INTERVAL_SEC = 5
DETECTIONS_PER_SEC = 2
SHOW_VIDEO = True
MODEL_PATH = "yolov8n.pt"

# Add the actual polygon coordinates for each road.
# Use draw_polygon.py to get coordinates for each video.
ROADS = {
    "North": {
        "polygon": [[5, 427], [1272, 406], [801, 5],
                    [520, 7], [4, 424]]
    },
    "South": {"polygon": []},
    "East":  {"polygon": []},
    "West":  {"polygon": []},
}
# =========================================

CLASS_TO_FIELD = {
    "car": "car_count",
    "motorcycle": "motorcycle_count",
    "bus": "bus_count",
    "truck": "truck_count",
}

model = YOLO(MODEL_PATH)
payload_history = []
streams = {}

# Ask for video paths instead of hardcoding one MP4.
for road_name, config in ROADS.items():
    video_path = input(
        f"Video path for {road_name} (press Enter to skip): "
    ).strip().strip('"')

    if not video_path:
        print(f"{road_name}: no video supplied; counts will be zero.")
        continue

    if not os.path.isfile(video_path):
        print(f"{road_name}: file not found. Skipping this road.")
        continue

    if len(config["polygon"]) < 3:
        print(
            f"{road_name}: polygon not configured. "
            "Use draw_polygon.py and add its points to ROADS."
        )
        continue

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Could not open video: {video_path}")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 30

    streams[road_name] = {
        "cap": cap,
        "fps": fps,
        "step": max(1, round(fps / DETECTIONS_PER_SEC)),
        "frame_idx": 0,
        "polygon": np.array(config["polygon"], np.int32),
        "samples": [],
        "finished": False,
    }

def count_vehicles(frame, polygon):
    """Count detected vehicles whose centers fall inside the polygon."""
    counts = {field: 0 for field in CLASS_TO_FIELD.values()}

    results = model.predict(frame, conf=0.35, verbose=False)

    for box in results[0].boxes:
        class_name = model.names[int(box.cls[0])]

        if class_name not in CLASS_TO_FIELD:
            continue

        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        if cv2.pointPolygonTest(
            polygon, (float(cx), float(cy)), False
        ) >= 0:
            counts[CLASS_TO_FIELD[class_name]] += 1

            if SHOW_VIDEO:
                cv2.rectangle(
                    frame, (int(x1), int(y1)),
                    (int(x2), int(y2)), (0, 255, 0), 2
                )
                cv2.putText(
                    frame, class_name,
                    (int(x1), max(20, int(y1) - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2
                )

    return counts

def build_payload():
    """Create the exact input structure expected by CycleRequest."""
    roads = []

    for road_name in ROADS:
        samples = streams[road_name]["samples"] if road_name in streams else []

        entry = {"road_name": road_name}

        for field in CLASS_TO_FIELD.values():
            entry[field] = (
                round(sum(s[field] for s in samples) / len(samples))
                if samples else 0
            )

        roads.append(entry)

        if road_name in streams:
            streams[road_name]["samples"] = []

    return {"roads": roads}

def send_payload(payload):
    payload_history.append(payload)

    # Keep a local record for debugging.
    with open("cycle_payloads.json", "w", encoding="utf-8") as file:
        json.dump(payload_history, file, indent=2)

    print("\nSending traffic reading:")
    print(json.dumps(payload, indent=2))

    if SEND_TO_BACKEND:
        try:
            response = requests.post(
                BACKEND_URL, json=payload, timeout=10
            )
            print("Backend status:", response.status_code)
            print("Backend response:", response.text)
            response.raise_for_status()
        except requests.RequestException as error:
            print("Could not send to backend:", error)

if not streams:
    print("No valid video streams loaded.")
    print("Configure a video path and its matching road polygon, then retry.")
else:
    # Track time separately for each video.
    elapsed = {name: 0.0 for name in streams}
    next_report = REPORT_INTERVAL_SEC

    try:
        while True:
            active_video = False

            for name, stream in streams.items():
                if stream["finished"]:
                    continue

                ret, frame = stream["cap"].read()

                if not ret:
                    stream["finished"] = True
                    continue

                active_video = True
                stream["frame_idx"] += 1
                elapsed[name] += 1 / stream["fps"]

                if (stream["frame_idx"] - 1) % stream["step"] == 0:
                    counts = count_vehicles(frame, stream["polygon"])
                    stream["samples"].append(counts)

                if SHOW_VIDEO:
                    cv2.polylines(
                        frame, [stream["polygon"]], True, (255, 0, 0), 2
                    )
                    cv2.putText(
                        frame, name, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 0, 255), 2
                    )
                    cv2.imshow(name, frame)

            if not active_video:
                break

            # Report according to elapsed video time.
            current_time = max(elapsed.values())

            if current_time >= next_report:
                send_payload(build_payload())
                next_report += REPORT_INTERVAL_SEC

            if SHOW_VIDEO and cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Send any remaining samples at the end.
        if any(s["samples"] for s in streams.values()):
            send_payload(build_payload())

    finally:
        for stream in streams.values():
            stream["cap"].release()

        cv2.destroyAllWindows()
        print("Detection finished.")
