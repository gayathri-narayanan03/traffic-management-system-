import uuid
import tempfile
import os
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.traffic_analyzer import analyze_road
from app.decision_engine import allocate_green_times
from app.simulator import simulate_intersection_reading
from app.config import ROADS

router = APIRouter(prefix="/api/traffic", tags=["traffic"])


def _persist_cycle(db: Session, road_analyses: dict) -> schemas.CycleResult:
    """Shared logic: analyze -> store TrafficRecords -> compute signal plan -> store recommendations."""
    cycle_id = str(uuid.uuid4())[:8]
    timestamp = datetime.utcnow()

    road_loads = {}
    for road_name, analysis in road_analyses.items():
        record = models.TrafficRecord(
            road_name=road_name,
            timestamp=timestamp,
            source=analysis.get("source", "manual"),
            **{k: v for k, v in analysis.items() if k != "source"},
        )
        db.add(record)
        road_loads[road_name] = analysis["weighted_load"]

    green_times = allocate_green_times(road_loads)

    result_roads = []
    for road_name, analysis in road_analyses.items():
        rec = models.SignalRecommendation(
            cycle_id=cycle_id,
            timestamp=timestamp,
            road_name=road_name,
            green_time_seconds=green_times[road_name],
            congestion_level=analysis["congestion_level"],
            weighted_load=analysis["weighted_load"],
        )
        db.add(rec)
        result_roads.append(
            schemas.CycleResultRoad(
                road_name=road_name,
                total_vehicles=analysis["total_vehicles"],
                weighted_load=analysis["weighted_load"],
                congestion_level=analysis["congestion_level"],
                green_time_seconds=green_times[road_name],
            )
        )

        # Auto-log an incident if congestion is severe
        if analysis["congestion_level"] == "severe":
            db.add(models.Incident(
                road_name=road_name,
                incident_type="congestion_spike",
                description=f"{road_name} reached severe congestion "
                            f"(weighted load {analysis['weighted_load']}).",
                severity="critical",
            ))

    db.commit()

    return schemas.CycleResult(cycle_id=cycle_id, timestamp=timestamp, roads=result_roads)


@router.post("/cycle", response_model=schemas.CycleResult)
def submit_cycle(payload: schemas.CycleRequest, db: Session = Depends(get_db)):
    """
    Accepts manual/pre-counted vehicle numbers for each road (e.g. from an
    external detector or manual entry) and returns the recommended signal plan.
    """
    road_analyses = {}
    for road in payload.roads:
        analysis = analyze_road(
            car=road.car_count,
            motorcycle=road.motorcycle_count,
            bus=road.bus_count,
            truck=road.truck_count,
        )
        analysis["source"] = "manual"
        road_analyses[road.road_name] = analysis

    return _persist_cycle(db, road_analyses)


@router.post("/simulate", response_model=schemas.CycleResult)
def simulate_cycle(peak: bool = False, db: Session = Depends(get_db)):
    """
    Generates a synthetic reading for all four roads and computes the
    resulting signal plan. Use this to populate the dashboard without a
    camera or uploaded video.
    """
    raw = simulate_intersection_reading(peak=peak)
    road_analyses = {}
    for road_name, counts in raw.items():
        analysis = analyze_road(
            car=counts["car_count"],
            motorcycle=counts["motorcycle_count"],
            bus=counts["bus_count"],
            truck=counts["truck_count"],
        )
        analysis["source"] = "simulated"
        road_analyses[road_name] = analysis

    return _persist_cycle(db, road_analyses)


@router.post("/upload/{road_name}")
async def upload_video_for_road(road_name: str, file: UploadFile = File(...)):
    """
    Accepts a video file for a single road, runs vehicle detection on it,
    and returns raw counts. Combine results for all 4 roads client-side,
    then POST them to /api/traffic/cycle to get a signal recommendation.
    """
    if road_name not in ROADS:
        raise HTTPException(status_code=400, detail=f"Unknown road '{road_name}'. Must be one of {ROADS}")

    from app.vehicle_detector import count_vehicles_in_video  # lazy import (heavy deps)

    suffix = os.path.splitext(file.filename)[1] or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        counts = count_vehicles_in_video(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {e}")
    finally:
        os.unlink(tmp_path)

    return {"road_name": road_name, **counts}
