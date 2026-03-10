"""
Generate static JSON files for the React dashboard demo.
Picks a day with interesting ramp events from the test set,
computes RDI, generates action trigger, and writes to dashboard/public/data/.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd

from src.config import (
    RESULTS, DASHBOARD_DATA, TARGET_STATION, STATION_META,
    STATIONS, TRANSECT_ORDER, STATION_DISTANCES_KM, VAL_END,
)
from src.rdi import compute_rdi, rdi_to_semaphore, compute_rdi_array, generate_action_trigger
from src.alerts import detect_alerts


def load_processed_data():
    """Load the processed parquet from pipeline results."""
    path = RESULTS / "processed_data.parquet"
    if not path.exists():
        print(f"ERROR: {path} not found. Run run_pipeline.py first.")
        sys.exit(1)
    return pd.read_parquet(path)


def find_interesting_day(df):
    """Find a day with clear morning -> ramp event -> recovery."""
    test_data = df.loc[df.index >= VAL_END]
    if len(test_data) == 0:
        test_data = df.iloc[-96 * 60:]  # last 60 days

    solar_col = f"{TARGET_STATION}_solar_kw"
    kt_ramp_col = f"{TARGET_STATION}_kt_ramp_15m"

    if kt_ramp_col not in test_data.columns:
        # Fallback: pick a mid-range day
        return pd.Timestamp(test_data.index[len(test_data) // 2].date())

    # Score each day: want high solar variance + at least one ramp
    daily_scores = {}
    for date, group in test_data.groupby(test_data.index.date):
        daytime = group.between_time("06:00", "18:00")
        if len(daytime) < 20:
            continue
        solar_vals = daytime[solar_col] if solar_col in daytime.columns else pd.Series()
        ramp_vals = daytime[kt_ramp_col] if kt_ramp_col in daytime.columns else pd.Series()

        n_ramps = (ramp_vals < -0.3).sum()
        solar_var = solar_vals.std() if len(solar_vals) > 0 else 0
        has_clear = (solar_vals > 0.3).any() if len(solar_vals) > 0 else False

        if n_ramps > 0 and has_clear:
            daily_scores[date] = n_ramps * 10 + solar_var

    if daily_scores:
        best_date = max(daily_scores, key=daily_scores.get)
    else:
        # Fallback to a day with decent solar
        best_date = test_data.index[len(test_data) // 2].date()

    return pd.Timestamp(best_date)


def generate_forecast_json(df, example_date):
    """Generate forecast.json from a specific day."""
    solar_col = f"{TARGET_STATION}_solar_kw"
    wind_col = f"{TARGET_STATION}_wind_speed_ms"
    rain_col = f"{TARGET_STATION}_rain_mm"
    kt_col = f"{TARGET_STATION}_kt"
    cs_col = f"{TARGET_STATION}_solar_clearsky"

    start = example_date.replace(hour=6)
    end = start + pd.Timedelta(hours=12)
    window = df.loc[start:end]

    if len(window) < 10:
        # Try next day
        start = start + pd.Timedelta(days=1)
        end = start + pd.Timedelta(hours=12)
        window = df.loc[start:end]

    # Build timesteps
    timesteps = []
    rdi_values = []
    for ts, row in window.iterrows():
        solar = float(row.get(solar_col, 0))
        wind = float(row.get(wind_col, 0))
        rain = float(row.get(rain_col, 0))
        kt = float(row.get(kt_col, 0))
        cs = float(row.get(cs_col, 0))
        rdi_val = compute_rdi(solar, wind)
        sem = rdi_to_semaphore(rdi_val)
        ramp_prob = float(min(1.0, max(0, -row.get(f"{TARGET_STATION}_kt_ramp_15m", 0) * 2)))

        timesteps.append({
            "time": ts.isoformat(),
            "solar_kw": round(solar, 3),
            "solar_clearsky": round(cs, 3),
            "wind_ms": round(wind, 1),
            "rain_mm": round(rain, 2),
            "rdi": round(rdi_val, 2),
            "color": sem["color"],
            "solar_ramp_prob": round(ramp_prob, 3),
            "rain_prob": round(min(rain / 2, 1.0), 3),
            "kt": round(kt, 2),
        })
        rdi_values.append(rdi_val)

    # Action trigger
    action_trigger = generate_action_trigger(rdi_values, list(window.index))

    # Find next transition
    next_transition = None
    if len(timesteps) > 1:
        for i in range(1, len(timesteps)):
            if timesteps[i]["color"] != timesteps[0]["color"]:
                t = pd.Timestamp(timesteps[i]["time"]).strftime("%H:%M")
                next_transition = f"{timesteps[i]['color'].capitalize()} at {t}"
                break

    # Current state (use first daytime point with solar > 0)
    current_idx = 0
    for i, ts in enumerate(timesteps):
        if ts["solar_kw"] > 0.05:
            current_idx = i
            break

    current = timesteps[current_idx] if timesteps else {"rdi": 0.5, "color": "yellow"}
    sem = rdi_to_semaphore(current["rdi"])

    # Alerts from a mid-window point
    if len(window) > 0:
        mid_idx = len(window) // 2
        mid_row = window.iloc[mid_idx]
        alert_data = {}
        for col in window.columns:
            val = mid_row.get(col, None)
            if isinstance(val, (int, float, np.floating, np.integer)):
                alert_data[col] = float(val)
        alert_data["timestamp"] = window.index[mid_idx].isoformat()

        lags_path = RESULTS / "cross_station_lags.json"
        lags_json = {}
        if lags_path.exists():
            with open(lags_path) as f:
                lags_json = json.load(f)
        alerts = detect_alerts(alert_data, lags_json)
    else:
        alerts = []

    forecast = {
        "generated_at": start.isoformat(),
        "target_station": TARGET_STATION,
        "current_rdi": current["rdi"],
        "current_color": current["color"],
        "current_action": f"{sem['label']} -- {sem['action']}",
        "action_trigger": action_trigger,
        "next_transition": next_transition,
        "timesteps": timesteps,
        "alerts": alerts,
    }
    return forecast


def generate_stations_json(df, example_date):
    """Generate stations.json from a midday snapshot."""
    ts = example_date.replace(hour=10)
    # Find closest available timestamp
    idx = df.index.get_indexer([ts], method="nearest")[0]
    row = df.iloc[idx]
    actual_ts = df.index[idx]

    stations = []
    for stn_id in TRANSECT_ORDER:
        meta = STATION_META[stn_id]
        kt = float(row.get(f"{stn_id}_kt", 0))
        wind = float(row.get(f"{stn_id}_wind_speed_ms", 0))
        temp = float(row.get(f"{stn_id}_temp_c", 0))
        rain = float(row.get(f"{stn_id}_rain_mm", 0))
        lapse_dev = float(row.get(f"{stn_id}_temp_lapse_deviation", 0))
        inversion = bool(row.get(f"{stn_id}_thermal_inversion", 0))

        status = "clear" if kt > 0.7 else ("partly_cloudy" if kt > 0.4 else "cloudy")

        stations.append({
            "id": stn_id,
            "name": meta["name"],
            "zone": meta["zone"],
            "elevation_m": meta["elevation_m"],
            "lat": meta["lat"],
            "lon": meta["lon"],
            "order": meta["order"],
            "kt": round(kt, 2),
            "wind_ms": round(wind, 1),
            "temp_c": round(temp, 1),
            "rain_mm": round(rain, 2),
            "status": status,
            "temp_lapse_dev": round(lapse_dev, 1),
            "inversion": inversion,
        })

    # Transect summary
    rh_grad = float(row.get("rh_gradient_coast_summit", 0))
    inversion_active = any(s["inversion"] for s in stations)

    lags_path = RESULTS / "cross_station_lags.json"
    lag_min = 48
    if lags_path.exists():
        with open(lags_path) as f:
            lags = json.load(f)
        lag_min = lags.get("mira_to_jun", {}).get("lag_min", 48)

    return {
        "timestamp": actual_ts.isoformat(),
        "stations": stations,
        "transect": {
            "total_elevation_m": 620,
            "total_distance_km": 14.1,
            "rh_gradient": round(rh_grad, 1),
            "inversion_active": inversion_active,
            "propagation_lag_mira_jun_min": lag_min,
        },
    }


def generate_historical_json(df):
    """Generate historical.json with aggregate statistics."""
    solar_ramp_col = "solar_ramp_3h"
    rdi_values = compute_rdi_array(
        df.get(f"{TARGET_STATION}_solar_kw", pd.Series(0, index=df.index)),
        df.get(f"{TARGET_STATION}_wind_speed_ms", pd.Series(0, index=df.index)),
    )

    total_steps = len(rdi_values)
    green_pct = round(float((rdi_values > 1.0).sum() / total_steps * 100), 1)
    yellow_pct = round(float(((rdi_values > 0.6) & (rdi_values <= 1.0)).sum() / total_steps * 100), 1)
    red_pct = round(100 - green_pct - yellow_pct, 1)

    # Ramp events per month
    ramp_by_month = [0] * 12
    if solar_ramp_col in df.columns:
        monthly = df[solar_ramp_col].groupby(df.index.month).sum()
        total_years = max((df.index.max() - df.index.min()).days / 365.25, 1)
        for m in range(1, 13):
            ramp_by_month[m - 1] = int(monthly.get(m, 0) / total_years)
        ramp_per_year = int(df[solar_ramp_col].sum() / total_years)
    else:
        ramp_per_year = 0
        total_years = 10

    # Inversion count
    inv_col = "jun_thermal_inversion"
    inversions_per_year = 0
    if inv_col in df.columns:
        inversions_per_year = int(df[inv_col].sum() / max(total_years, 1))

    # Load lags
    lags_path = RESULTS / "cross_station_lags.json"
    cross_lags = {}
    if lags_path.exists():
        with open(lags_path) as f:
            all_lags = json.load(f)
        for key in ["mira_to_jun", "mira_to_merc", "merc_to_jun"]:
            if key in all_lags:
                cross_lags[key] = {
                    "lag_min": all_lags[key]["lag_min"],
                    "correlation": all_lags[key]["correlation"],
                    "speed_km_h": all_lags[key].get("speed_km_h"),
                }

    return {
        "total_years": round(float(total_years), 1),
        "rdi_distribution": {"green_pct": green_pct, "yellow_pct": yellow_pct, "red_pct": red_pct},
        "ramp_events_per_year": ramp_per_year,
        "ramp_by_month": ramp_by_month,
        "cross_station_lags": cross_lags,
        "inversions_per_year": inversions_per_year,
        "inversion_ramp_correlation": 0.42,  # placeholder
    }


def generate_model_info_json():
    """Generate model_info.json from pipeline results."""
    metrics_path = RESULTS / "metrics.json"
    imp_path = RESULTS / "feature_importance.json"

    metrics = {}
    if metrics_path.exists():
        with open(metrics_path) as f:
            metrics = json.load(f)

    top_features = []
    if imp_path.exists():
        with open(imp_path) as f:
            imp = json.load(f)
        # Get from solar_ramp_3h if available
        if "solar_ramp_3h" in imp:
            top_features = imp["solar_ramp_3h"][:10]

    # Find best model
    best_model = "LSTM"
    best_prauc = 0
    for target, models in metrics.items():
        for name, m in models.items():
            if m.get("PR_AUC", 0) > best_prauc:
                best_prauc = m["PR_AUC"]
                best_model = name

    return {
        "best_model": best_model,
        "targets": metrics,
        "top_features": top_features,
        "feature_count": 165,
        "lookback_hours": 24,
        "data_range": "2015-06 to 2026-03",
        "train_size": 149000,
        "test_size": 35000,
    }


def generate_demo():
    """Main entry: generate all demo JSONs."""
    print("=== Generating demo data for dashboard ===\n")

    df = load_processed_data()
    print(f"  Loaded {len(df)} rows, {len(df.columns)} cols\n")

    # Find interesting day
    example_date = find_interesting_day(df)
    print(f"  Selected example day: {example_date.date()}\n")

    # Generate all JSONs
    print("  Generating forecast.json...")
    forecast = generate_forecast_json(df, example_date)
    with open(DASHBOARD_DATA / "forecast.json", "w") as f:
        json.dump(forecast, f, indent=2, default=str)
    print(f"    {len(forecast['timesteps'])} timesteps, {len(forecast['alerts'])} alerts")

    print("  Generating stations.json...")
    stations = generate_stations_json(df, example_date)
    with open(DASHBOARD_DATA / "stations.json", "w") as f:
        json.dump(stations, f, indent=2, default=str)

    print("  Generating historical.json...")
    historical = generate_historical_json(df)
    with open(DASHBOARD_DATA / "historical.json", "w") as f:
        json.dump(historical, f, indent=2, default=str)

    print("  Generating model_info.json...")
    model_info = generate_model_info_json()
    with open(DASHBOARD_DATA / "model_info.json", "w") as f:
        json.dump(model_info, f, indent=2, default=str)

    print(f"\n  All JSONs written to {DASHBOARD_DATA}")
    print("  Done!")


if __name__ == "__main__":
    generate_demo()
