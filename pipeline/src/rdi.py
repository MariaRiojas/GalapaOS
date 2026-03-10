"""Renewable Dispatch Index (RDI): semaphore + action trigger."""

import numpy as np
from .config import (
    RDI_GREEN, RDI_YELLOW, DEMAND_AVG_KW,
    WIND_TURBINE_CAPACITY_KW, N_WIND_TURBINES,
    WIND_CUT_IN_MS, WIND_RATED_MS,
)


def estimate_wind_power_kw(wind_ms):
    """Estimate total wind power from wind speed using cubic power curve."""
    wind_ms = float(wind_ms)
    total = N_WIND_TURBINES * WIND_TURBINE_CAPACITY_KW
    if wind_ms < WIND_CUT_IN_MS:
        return 0.0
    if wind_ms > WIND_RATED_MS:
        return float(total)
    return total * ((wind_ms - WIND_CUT_IN_MS) / (WIND_RATED_MS - WIND_CUT_IN_MS)) ** 3


def compute_rdi(solar_kw_avg, wind_ms, demand_kw=DEMAND_AVG_KW):
    """Compute RDI from solar radiation and wind speed."""
    renewable = float(solar_kw_avg) * 1000 + estimate_wind_power_kw(wind_ms)
    return min(renewable / demand_kw, 2.0)


def compute_rdi_array(solar_array, wind_array, demand_kw=DEMAND_AVG_KW):
    """Vectorized RDI computation for arrays."""
    solar = np.asarray(solar_array, dtype=float)
    wind = np.asarray(wind_array, dtype=float)

    total_cap = N_WIND_TURBINES * WIND_TURBINE_CAPACITY_KW
    wind_power = np.where(
        wind < WIND_CUT_IN_MS, 0.0,
        np.where(
            wind > WIND_RATED_MS, total_cap,
            total_cap * ((wind - WIND_CUT_IN_MS) / (WIND_RATED_MS - WIND_CUT_IN_MS)) ** 3
        )
    )
    renewable = solar * 1000 + wind_power
    return np.clip(renewable / demand_kw, 0, 2.0)


def rdi_to_semaphore(rdi):
    """Convert RDI value to semaphore dict."""
    rdi = float(rdi)
    if rdi > RDI_GREEN:
        return {"color": "green", "label": "SURPLUS",
                "action": "Diesel OFF -- safe on renewables"}
    elif rdi > RDI_YELLOW:
        return {"color": "yellow", "label": "WATCH",
                "action": "Diesel STANDBY -- ramp approaching"}
    else:
        return {"color": "red", "label": "DEFICIT",
                "action": "Diesel ON -- renewables insufficient"}


def generate_action_trigger(rdi_forecast, timestamps):
    """Generate the action trigger message from a forecast series."""
    for i in range(1, len(rdi_forecast)):
        prev = rdi_to_semaphore(rdi_forecast[i - 1])["color"]
        curr = rdi_to_semaphore(rdi_forecast[i])["color"]
        if prev != curr:
            t = timestamps[i].strftime("%H:%M") if hasattr(timestamps[i], "strftime") else str(timestamps[i])
            if curr == "green":
                return f"Status: Surplus Expected. Recommendation: Power down Generator #2 at {t}."
            elif curr == "red":
                return f"Status: Deficit Expected. Recommendation: Start Generator #2 at {t}."
            elif curr == "yellow":
                return f"Status: Ramp approaching. Recommendation: Standby Generator #2 by {t}."

    s = rdi_to_semaphore(rdi_forecast[0])
    hours = len(rdi_forecast) * 15 // 60
    return f"Status: {s['label']}. No transitions expected in next {hours}h."
