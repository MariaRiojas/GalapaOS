"""Generate static demo JSON data for frontend from processed data."""

import json
import numpy as np
import pandas as pd
from pathlib import Path

from ..config import (
    PROCESSED_DIR, RESULTS_DIR, STATIONS, STATION_META, TARGET_STATION,
)
from ..core.rdi import compute_rdi, rdi_to_semaphore
from ..core.alerts import detect_cross_station_alerts


def generate_demo_forecast(df: pd.DataFrame = None):
    """Generate a realistic demo forecast JSON from actual data."""
    if df is None:
        parquet_path = PROCESSED_DIR / "features_and_targets.parquet"
        if not parquet_path.exists():
            print("  No processed data found. Run pipeline first.")
            return
        df = pd.read_parquet(parquet_path)

    # Pick a good example day: a clear morning with an afternoon ramp
    # Find a day with at least one solar ramp event
    target_col = f"solar_ramp_3h_{TARGET_STATION}"
    if target_col not in df.columns:
        target_col = "solar_ramp_3h"

    # Try to find a day with interesting patterns
    solar_col = f"{TARGET_STATION}_solar_kw"
    wind_col = f"{TARGET_STATION}_wind_speed_ms"
    rain_col = f"{TARGET_STATION}_rain_mm"
    kt_col = f"{TARGET_STATION}_kt"

    # Pick a specific day from the test period with good data
    candidates = df.loc["2024-08-01":"2024-10-31"]
    if len(candidates) == 0:
        candidates = df.iloc[-96*30:]  # Last 30 days

    # Find a day with a solar ramp
    daily_ramps = candidates.groupby(candidates.index.date).apply(
        lambda g: g.get(target_col, pd.Series(dtype=float)).sum()
    )
    ramp_days = daily_ramps[daily_ramps > 0]

    if len(ramp_days) > 0:
        example_date = pd.Timestamp(ramp_days.index[len(ramp_days)//2])
    else:
        example_date = pd.Timestamp(candidates.index[len(candidates)//2].date())

    # Extract 12 hours of data starting at 6:00 AM
    start = example_date.replace(hour=6)
    end = start + pd.Timedelta(hours=12)
    window = df.loc[start:end]

    if len(window) == 0:
        window = candidates.iloc[:48]
        start = window.index[0]

    # Build forecast timesteps
    timesteps = []
    for ts, row in window.iterrows():
        solar = float(row.get(solar_col, 0))
        wind = float(row.get(wind_col, 0))
        rain = float(row.get(rain_col, 0))
        rdi_val = float(compute_rdi(solar, wind))
        sem = rdi_to_semaphore(rdi_val)
        ramp_prob = float(min(1.0, max(0, -row.get(f"{TARGET_STATION}_kt_ramp_15m", 0))))

        timesteps.append({
            "time": ts.isoformat(),
            "solar_kw": round(solar, 3),
            "wind_ms": round(wind, 1),
            "rain_mm": round(rain, 2),
            "rdi": round(rdi_val, 2),
            "color": sem["color"],
            "solar_ramp_prob": round(ramp_prob, 3),
            "rain_prob": round(min(rain / 2, 1.0), 3),
        })

    # Current state
    if len(timesteps) > 0:
        current = timesteps[len(timesteps) // 3]  # Use a mid-morning point
    else:
        current = {"rdi": 0.5, "color": "yellow", "action": "DIESEL STANDBY -- monitor"}

    # Detect alerts from the current data point
    if len(window) > 0:
        mid_row = window.iloc[len(window) // 3]
        alert_data = {col: float(mid_row.get(col, 0)) for col in window.columns
                      if isinstance(mid_row.get(col, None), (int, float, np.floating))}
        alert_data["timestamp"] = window.index[len(window) // 3].isoformat()
        alerts = detect_cross_station_alerts(alert_data)
    else:
        alerts = []

    forecast = {
        "generated_at": start.isoformat(),
        "target_station": TARGET_STATION,
        "forecast_hours": 12,
        "current_rdi": current.get("rdi", 0.5),
        "current_color": current.get("color", "yellow"),
        "current_action": rdi_to_semaphore(current.get("rdi", 0.5))["action"],
        "timesteps": timesteps,
        "alerts": alerts,
    }

    # Save
    out_path = RESULTS_DIR / "demo_forecast.json"
    with open(out_path, "w") as f:
        json.dump(forecast, f, indent=2, default=str)
    print(f"  Saved demo forecast: {out_path}")

    return forecast


def generate_demo_stations(df: pd.DataFrame = None):
    """Generate demo station status JSON."""
    if df is None:
        parquet_path = PROCESSED_DIR / "features_and_targets.parquet"
        if not parquet_path.exists():
            return
        df = pd.read_parquet(parquet_path)

    # Use a midday point from the data
    midday_mask = df.index.hour == 12
    if midday_mask.sum() > 0:
        sample = df.loc[midday_mask].iloc[-1]
        ts = df.loc[midday_mask].index[-1]
    else:
        sample = df.iloc[-1]
        ts = df.index[-1]

    stations = []
    for stn_id in ["mira", "merc", "cer", "jun"]:
        meta = STATION_META[stn_id]
        kt = float(sample.get(f"{stn_id}_kt", 0))
        wind = float(sample.get(f"{stn_id}_wind_speed_ms", 0))
        temp = float(sample.get(f"{stn_id}_temp_c", 0))
        rain = float(sample.get(f"{stn_id}_rain_mm", 0))

        if kt > 0.7:
            status = "clear"
        elif kt > 0.4:
            status = "partly_cloudy"
        else:
            status = "cloudy"

        stations.append({
            "id": stn_id,
            "name": meta["name"],
            "elevation": meta["elevation"],
            "kt": round(kt, 2),
            "wind_ms": round(wind, 1),
            "temp_c": round(temp, 1),
            "rain_mm": round(rain, 2),
            "status": status,
            "order": meta["order"],
        })

    result = {"timestamp": ts.isoformat(), "stations": stations}

    out_path = RESULTS_DIR / "demo_stations.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"  Saved demo stations: {out_path}")

    return result
