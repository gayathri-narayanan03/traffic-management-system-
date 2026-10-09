from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class TrafficRecord(Base):
    """One snapshot of detected traffic on a single road at a point in time."""
    __tablename__ = "traffic_records"

    id = Column(Integer, primary_key=True, index=True)
    road_name = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    car_count = Column(Integer, default=0)
    motorcycle_count = Column(Integer, default=0)
    bus_count = Column(Integer, default=0)
    truck_count = Column(Integer, default=0)
    total_vehicles = Column(Integer, default=0)

    weighted_load = Column(Float, default=0.0)
    congestion_level = Column(String, default="low")  # low/medium/high/severe

    source = Column(String, default="simulated")  # simulated | uploaded_video | live_camera


class SignalRecommendation(Base):
    """A decision-engine output: recommended green-light durations for one cycle."""
    __tablename__ = "signal_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cycle_id = Column(String, index=True)

    road_name = Column(String, index=True, nullable=False)
    green_time_seconds = Column(Integer, default=0)
    congestion_level = Column(String, default="low")
    weighted_load = Column(Float, default=0.0)


class Incident(Base):
    """Alerts / incidents detected or manually logged (e.g. sudden congestion spike)."""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    road_name = Column(String, index=True)
    incident_type = Column(String)  # e.g. "congestion_spike", "manual_report"
    description = Column(Text)
    severity = Column(String, default="info")  # info | warning | critical
    resolved = Column(Integer, default=0)  # 0 = open, 1 = resolved
