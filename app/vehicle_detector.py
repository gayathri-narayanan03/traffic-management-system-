"""
Computer-vision layer: detects and counts vehicles in an image or video frame.

Uses Ultralytics YOLOv8 (pretrained on COCO). Falls back gracefully with a
clear error if the model/dependencies aren't available, so the rest of the
API still runs (e.g. the /cycle endpoint that accepts manual counts).
"""
from typing import Dict
import numpy as np

from app.config import VEHICLE_CLASSES, YOLO_MODEL_PATH

_model = None


def _get_model():
    """Lazy-load the YOLO model on first use (keeps app startup fast)."""
    global _model
    if _model is None:
        from ultralytics import YOLO
        _model = YOLO(YOLO_MODEL_PATH if _model_exists() else "yolov8n.pt")
    return _model


def _model_exists() -> bool:
    import os
    return os.path.exists(YOLO_MODEL_PATH)


def count_vehicles_in_frame(frame: np.ndarray, conf_threshold: float = 0.35) -> Dict[str, int]:
    """
    Run detection on a single frame (BGR numpy array, as read by cv2.imread /
    VideoCapture.read()). Returns counts per vehicle type.
    """
    model = _get_model()
    results = model.predict(frame, conf=conf_threshold, verbose=False)

    counts = {name: 0 for name in VEHICLE_CLASSES.values()}
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            if class_id in VEHICLE_CLASSES:
                counts[VEHICLE_CLASSES[class_id]] += 1
    return counts


def count_vehicles_in_video(video_path: str, sample_every_n_frames: int = 15) -> Dict[str, int]:
    """
    Process a video file and return the MAX count seen per vehicle type across
    sampled frames. Sampling avoids re-running detection on every single frame.
    """
    import cv2

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    best_counts = {name: 0 for name in VEHICLE_CLASSES.values()}
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % sample_every_n_frames == 0:
            frame_counts = count_vehicles_in_frame(frame)
            for k, v in frame_counts.items():
                best_counts[k] = max(best_counts[k], v)
        frame_idx += 1

    cap.release()
    return best_counts
