from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, List

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/records", response_model=List[schemas.TrafficRecordOut])
def get_records(
    road_name: Optional[str] = None,
    hours: int = Query(24, description="Look back this many hours"),
    db: Session = Depends(get_db),
):
    """Raw traffic records, optionally filtered by road, for the last N hours."""
    since = datetime.utcnow() - timedelta(hours=hours)
    q = db.query(models.TrafficRecord).filter(models.TrafficRecord.timestamp >= since)
    if road_name:
        q = q.filter(models.TrafficRecord.road_name == road_name)
    return q.order_by(models.TrafficRecord.timestamp.desc()).limit(500).all()


@router.get("/recommendations", response_model=List[schemas.SignalRecommendationOut])
def get_recommendations(
    road_name: Optional[str] = None,
    hours: int = Query(24),
    db: Session = Depends(get_db),
):
    """Past signal recommendations, optionally filtered by road."""
    since = datetime.utcnow() - timedelta(hours=hours)
    q = db.query(models.SignalRecommendation).filter(models.SignalRecommendation.timestamp >= since)
    if road_name:
        q = q.filter(models.SignalRecommendation.road_name == road_name)
    return q.order_by(models.SignalRecommendation.timestamp.desc()).limit(500).all()


@router.get("/peak-periods")
def peak_periods(road_name: Optional[str] = None, days: int = 7, db: Session = Depends(get_db)):
    """
    Average weighted load grouped by hour-of-day, to identify peak traffic
    periods over the last N days.
    """
    since = datetime.utcnow() - timedelta(days=days)
    q = db.query(
        func.strftime("%H", models.TrafficRecord.timestamp).label("hour"),
        func.avg(models.TrafficRecord.weighted_load).label("avg_load"),
        func.count(models.TrafficRecord.id).label("sample_count"),
    ).filter(models.TrafficRecord.timestamp >= since)

    if road_name:
        q = q.filter(models.TrafficRecord.road_name == road_name)

    q = q.group_by("hour").order_by("hour")
    return [
        {"hour": int(row.hour), "avg_weighted_load": round(row.avg_load, 2), "sample_count": row.sample_count}
        for row in q.all()
    ]


@router.get("/road-comparison")
def road_comparison(hours: int = 24, db: Session = Depends(get_db)):
    """Average congestion metrics per road, for comparing roads against each other."""
    since = datetime.utcnow() - timedelta(hours=hours)
    q = (
        db.query(
            models.TrafficRecord.road_name,
            func.avg(models.TrafficRecord.weighted_load).label("avg_load"),
            func.max(models.TrafficRecord.weighted_load).label("max_load"),
            func.avg(models.TrafficRecord.total_vehicles).label("avg_vehicles"),
        )
        .filter(models.TrafficRecord.timestamp >= since)
        .group_by(models.TrafficRecord.road_name)
    )
    return [
        {
            "road_name": row.road_name,
            "avg_weighted_load": round(row.avg_load, 2),
            "max_weighted_load": round(row.max_load, 2),
            "avg_vehicles": round(row.avg_vehicles, 1),
        }
        for row in q.all()
    ]
