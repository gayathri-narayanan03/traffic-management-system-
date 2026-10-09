"""
Decision-support module: given weighted loads for each road in the
intersection, recommend a green-light duration for each, proportional to
demand, within safety floors/ceilings and a fixed total cycle budget.
"""
from typing import Dict, List
from app.config import MIN_GREEN_TIME, MAX_GREEN_TIME, BASE_CYCLE_TIME


def allocate_green_times(road_loads: Dict[str, float]) -> Dict[str, int]:
    """
    road_loads: {"North": 12.5, "South": 30.0, "East": 4.0, "West": 8.0}
    Returns: {"North": seconds, ...} summing close to BASE_CYCLE_TIME,
    each clamped to [MIN_GREEN_TIME, MAX_GREEN_TIME].
    """
    roads = list(road_loads.keys())
    total_load = sum(road_loads.values())

    # Edge case: no traffic anywhere -> split evenly
    if total_load <= 0:
        equal_share = BASE_CYCLE_TIME // len(roads)
        return {r: max(MIN_GREEN_TIME, equal_share) for r in roads}

    # First pass: proportional allocation
    raw_allocation = {
        r: (load / total_load) * BASE_CYCLE_TIME for r, load in road_loads.items()
    }

    # Clamp to min/max
    clamped = {
        r: min(MAX_GREEN_TIME, max(MIN_GREEN_TIME, round(v)))
        for r, v in raw_allocation.items()
    }

    return _rebalance_to_budget(clamped, roads)


def _rebalance_to_budget(clamped: Dict[str, int], roads: List[str]) -> Dict[str, int]:
    """
    Clamping can push the total above/below BASE_CYCLE_TIME. Redistribute the
    difference across roads that still have headroom, respecting min/max.
    """
    result = dict(clamped)
    diff = BASE_CYCLE_TIME - sum(result.values())

    # Nothing to fix
    if diff == 0:
        return result

    adjustable = [r for r in roads]
    step = 1 if diff > 0 else -1
    remaining = abs(diff)

    # Spread the difference one second at a time across roads with headroom
    guard = 0
    while remaining > 0 and guard < 10000:
        guard += 1
        progressed = False
        for r in adjustable:
            candidate = result[r] + step
            if MIN_GREEN_TIME <= candidate <= MAX_GREEN_TIME:
                result[r] = candidate
                remaining -= 1
                progressed = True
                if remaining == 0:
                    break
        if not progressed:
            break  # can't rebalance further without violating limits

    return result
