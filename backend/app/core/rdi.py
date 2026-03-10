"""Renewable Dispatch Index (RDI): Layer 2 semaphore logic."""

import numpy as np
from ..config import RDI_GREEN, RDI_YELLOW, DEMAND_AVG_KW


def compute_rdi(solar_pred_kw, wind_pred_ms, demand_avg_kw=DEMAND_AVG_KW):
    """Compute RDI from predicted solar radiation and wind speed.

    RDI > 1.0 = green (renewables sufficient)
    0.6 < RDI <= 1.0 = yellow (monitor)
    RDI <= 0.6 = red (diesel needed)
    """
    solar_pred_kw = np.asarray(solar_pred_kw, dtype=float)
    wind_pred_ms = np.asarray(wind_pred_ms, dtype=float)

    # Wind power curve (simplified cubic for 2.4 MW turbine)
    wind_power = np.where(
        wind_pred_ms < 3, 0,
        np.where(
            wind_pred_ms > 12, 2400,
            2400 * ((wind_pred_ms - 3) / (12 - 3)) ** 3
        )
    )

    # Solar power (kW to W)
    solar_power = solar_pred_kw * 1000

    rdi = np.clip((solar_power + wind_power) / demand_avg_kw, 0, 2.0)
    return rdi


def rdi_to_semaphore(rdi_value):
    """Convert scalar RDI to semaphore color and action."""
    rdi_value = float(rdi_value)
    if rdi_value > RDI_GREEN:
        return {
            "color": "green",
            "action": "DIESEL OFF -- renewables sufficient",
        }
    elif rdi_value > RDI_YELLOW:
        return {
            "color": "yellow",
            "action": "DIESEL STANDBY -- monitor",
        }
    else:
        return {
            "color": "red",
            "action": "DIESEL ON -- renewables insufficient",
        }


def compute_rdi_series(solar_series, wind_series):
    """Compute RDI for a time series, return RDI + colors."""
    rdi_values = compute_rdi(solar_series, wind_series)
    colors = [rdi_to_semaphore(r)["color"] for r in rdi_values]
    actions = [rdi_to_semaphore(r)["action"] for r in rdi_values]
    return rdi_values, colors, actions
