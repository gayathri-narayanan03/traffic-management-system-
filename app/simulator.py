"""
Generates synthetic traffic readings for the simulated four-way intersection.
Useful for demos, testing the dashboard, and generating historical data
without needing real camera footage.
"""
import random
from app.config import ROADS


def simulate_intersection_reading(peak: bool = False) -> dict:
    """
    Returns raw vehicle counts per road. If peak=True, generates heavier,
    more uneven traffic (simulating rush hour).
    """
    readings = {}
    for road in ROADS:
        if peak:
            car = random.randint(15, 40)
            motorcycle = random.randint(5, 20)
            bus = random.randint(0, 4)
            truck = random.randint(0, 3)
        else:
            car = random.randint(2, 15)
            motorcycle = random.randint(0, 8)
            bus = random.randint(0, 2)
            truck = random.randint(0, 2)

        readings[road] = {
            "car_count": car,
            "motorcycle_count": motorcycle,
            "bus_count": bus,
            "truck_count": truck,
        }
    return readings
