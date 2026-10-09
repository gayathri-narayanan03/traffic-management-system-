from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models
from app.config import ROADS

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/current-status")
def current_status(db: Session = Depends(get_db)):
    """Latest traffic record and signal recommendation per road, for the live dashboard view."""
    status = []
    for road in ROADS:
        latest_record = (
            db.query(models.TrafficRecord)
            .filter(models.TrafficRecord.road_name == road)
            .order_by(models.TrafficRecord.timestamp.desc())
            .first()
        )
        latest_signal = (
            db.query(models.SignalRecommendation)
            .filter(models.SignalRecommendation.road_name == road)
            .order_by(models.SignalRecommendation.timestamp.desc())
            .first()
        )
        status.append({
            "road_name": road,
            "traffic": {
                "total_vehicles": latest_record.total_vehicles if latest_record else None,
                "congestion_level": latest_record.congestion_level if latest_record else None,
                "weighted_load": latest_record.weighted_load if latest_record else None,
                "timestamp": latest_record.timestamp if latest_record else None,
            },
            "signal": {
                "green_time_seconds": latest_signal.green_time_seconds if latest_signal else None,
                "cycle_id": latest_signal.cycle_id if latest_signal else None,
            },
        })
    return status


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    """High-level counts for dashboard cards: total records, open incidents, busiest road."""
    total_records = db.query(func.count(models.TrafficRecord.id)).scalar()
    open_incidents = (
        db.query(func.count(models.Incident.id)).filter(models.Incident.resolved == 0).scalar()
    )
    busiest = (
        db.query(models.TrafficRecord.road_name, func.avg(models.TrafficRecord.weighted_load).label("avg_load"))
        .group_by(models.TrafficRecord.road_name)
        .order_by(func.avg(models.TrafficRecord.weighted_load).desc())
        .first()
    )
    return {
        "total_traffic_records": total_records,
        "open_incidents": open_incidents,
        "busiest_road": busiest[0] if busiest else None,
        "busiest_road_avg_load": round(busiest[1], 2) if busiest else None,
    }
