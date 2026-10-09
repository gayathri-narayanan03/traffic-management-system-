"""
Turns raw vehicle counts into a weighted load figure and a congestion level.
"""
from app.config import VEHICLE_WEIGHTS, CONGESTION_THRESHOLDS


def compute_weighted_load(car=0, motorcycle=0, bus=0, truck=0) -> float:
    """Weight vehicle types by how much road space/time they occupy."""
    return round(
        car * VEHICLE_WEIGHTS["car"]
        + motorcycle * VEHICLE_WEIGHTS["motorcycle"]
        + bus * VEHICLE_WEIGHTS["bus"]
        + truck * VEHICLE_WEIGHTS["truck"],
        2,
    )


def classify_congestion(weighted_load: float) -> str:
    """Map a weighted load value to a congestion label."""
    if weighted_load < CONGESTION_THRESHOLDS["low"]:
        return "low"
    if weighted_load < CONGESTION_THRESHOLDS["medium"]:
        return "medium"
    if weighted_load < CONGESTION_THRESHOLDS["high"]:
        return "high"
    return "severe"


def analyze_road(car=0, motorcycle=0, bus=0, truck=0) -> dict:
    """Convenience wrapper returning everything needed for storage/display."""
    total = car + motorcycle + bus + truck
    weighted_load = compute_weighted_load(car, motorcycle, bus, truck)
    congestion_level = classify_congestion(weighted_load)
    return {
        "car_count": car,
        "motorcycle_count": motorcycle,
        "bus_count": bus,
        "truck_count": truck,
        "total_vehicles": total,
        "weighted_load": weighted_load,
        "congestion_level": congestion_level,
    }
