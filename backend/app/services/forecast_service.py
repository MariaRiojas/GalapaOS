"""Generate forecast for a given timestamp (demo or live mode)."""

import json
from pathlib import Path
from ..config import RESULTS_DIR, DEMO_MODE


def get_forecast(station="jun", hours=12):
    """Return forecast data. In demo mode, read from pre-computed JSON."""
    demo_path = RESULTS_DIR / "demo_forecast.json"

    if DEMO_MODE and demo_path.exists():
        with open(demo_path) as f:
            data = json.load(f)
        return data

    # Fallback: return minimal structure
    return {
        "generated_at": "2024-09-15T08:00:00",
        "target_station": station,
        "forecast_hours": hours,
        "current_rdi": 0.0,
        "current_color": "yellow",
        "current_action": "DIESEL STANDBY -- monitor",
        "timesteps": [],
        "alerts": [],
    }


def get_stations():
    """Return current state of all 4 stations."""
    demo_path = RESULTS_DIR / "demo_stations.json"

    if DEMO_MODE and demo_path.exists():
        with open(demo_path) as f:
            return json.load(f)

    return {
        "timestamp": "2024-09-15T08:00:00",
        "stations": [
            {"id": "mira", "name": "El Mirador", "elevation": "coastal",
             "kt": 0.0, "wind_ms": 0.0, "temp_c": 0.0, "rain_mm": 0.0,
             "status": "unknown", "order": 1},
            {"id": "merc", "name": "Merceditas", "elevation": "mid",
             "kt": 0.0, "wind_ms": 0.0, "temp_c": 0.0, "rain_mm": 0.0,
             "status": "unknown", "order": 2},
            {"id": "cer", "name": "Cerro Alto", "elevation": "highland",
             "kt": 0.0, "wind_ms": 0.0, "temp_c": 0.0, "rain_mm": 0.0,
             "status": "unknown", "order": 3},
            {"id": "jun", "name": "El Junco", "elevation": "summit",
             "kt": 0.0, "wind_ms": 0.0, "temp_c": 0.0, "rain_mm": 0.0,
             "status": "unknown", "order": 4},
        ],
    }
