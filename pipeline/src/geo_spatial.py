"""Cross-correlation lags, propagation speed, lapse rate analysis."""

import json
import numpy as np
import pandas as pd
from scipy.signal import correlate
from .config import STATIONS, STATION_DISTANCES_KM, TRAIN_END, RESULTS


def compute_propagation_lags(df: pd.DataFrame, variable: str = "solar_kw",
                              max_lag_steps: int = 16, step_minutes: int = 15) -> dict:
    """Cross-correlate variable between all station pairs."""
    print(f"=== Computing propagation lags for {variable} ===")
    lags = {}
    pairs = [
        ("mira", "merc"), ("mira", "cer"), ("mira", "jun"),
        ("merc", "cer"), ("merc", "jun"), ("cer", "jun"),
    ]
    train_mask = df.index < TRAIN_END

    for stn_a, stn_b in pairs:
        col_a = f"{stn_a}_{variable}"
        col_b = f"{stn_b}_{variable}"
        if col_a not in df.columns or col_b not in df.columns:
            continue

        a = df.loc[train_mask, col_a].dropna()
        b = df.loc[train_mask, col_b].dropna()
        common = a.index.intersection(b.index)
        if len(common) < 100:
            continue

        a, b = a.loc[common], b.loc[common]
        a_vals = a.values - a.mean()
        b_vals = b.values - b.mean()

        corr = correlate(a_vals, b_vals, mode="full")
        norm = len(a) * a.std() * b.std()
        if norm > 0:
            corr /= norm

        center = len(corr) // 2
        search = slice(center, center + max_lag_steps + 1)
        best_offset = int(corr[search].argmax())
        best_corr = float(corr[search].max())
        lag_min = best_offset * step_minutes

        dist = STATION_DISTANCES_KM.get((stn_a, stn_b), 0)
        speed = (dist / (lag_min / 60)) if lag_min > 0 else float("inf")

        key = f"{stn_a}_to_{stn_b}"
        lags[key] = {
            "lag_min": lag_min,
            "lag_steps": best_offset,
            "correlation": round(best_corr, 3),
            "speed_km_h": round(speed, 1) if speed != float("inf") else None,
            "distance_km": dist,
        }
        print(f"  {key}: {lag_min} min, r={best_corr:.3f}, {speed:.1f} km/h")

    return lags


def save_lags(lags: dict):
    """Save cross-station lags to JSON."""
    path = RESULTS / "cross_station_lags.json"
    with open(path, "w") as f:
        json.dump(lags, f, indent=2, default=str)
    print(f"  Saved lags: {path}")
    return path
