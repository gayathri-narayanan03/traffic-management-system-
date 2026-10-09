from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TrafficRecordOut(BaseModel):
    id: int
    road_name: str
    timestamp: datetime
    car_count: int
    motorcycle_count: int
    bus_count: int
    truck_count: int
    total_vehicles: int
    weighted_load: float
    congestion_level: str
    source: str

    class Config:
        from_attributes = True


class SignalRecommendationOut(BaseModel):
    id: int
    timestamp: datetime
    cycle_id: str
    road_name: str
    green_time_seconds: int
    congestion_level: str
    weighted_load: float

    class Config:
        from_attributes = True


class IncidentCreate(BaseModel):
    road_name: str
    incident_type: str
    description: str
    severity: str = "info"


class IncidentOut(IncidentCreate):
    id: int
    timestamp: datetime
    resolved: int

    class Config:
        from_attributes = True


class RoadInput(BaseModel):
    """Manually supplied vehicle counts for a road (used when no video/camera is available)."""
    road_name: str
    car_count: int = 0
    motorcycle_count: int = 0
    bus_count: int = 0
    truck_count: int = 0


class CycleRequest(BaseModel):
    """A full four-way intersection reading, used to compute one signal cycle."""
    roads: List[RoadInput]


class CycleResultRoad(BaseModel):
    road_name: str
    total_vehicles: int
    weighted_load: float
    congestion_level: str
    green_time_seconds: int


class CycleResult(BaseModel):
    cycle_id: str
    timestamp: datetime
    roads: List[CycleResultRoad]
