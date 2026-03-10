"""Merge stations into wide DataFrame and impute missing values."""

import pandas as pd
import numpy as np
from .config import STATIONS


def merge_stations(stations: dict) -> pd.DataFrame:
    """Merge all station DataFrames into a single wide DataFrame."""
    print("=== Merging stations ===")
    dfs = list(stations.values())
    df = dfs[0].join(dfs[1:], how="outer")
    df = df.sort_index()

    # Ensure 15-min frequency
    full_idx = pd.date_range(df.index.min(), df.index.max(), freq="15min")
    df = df.reindex(full_idx)
    df.index.name = "TIMESTAMP"

    print(f"  Merged: {len(df)} rows, {len(df.columns)} cols")
    missing_pct = df.isnull().mean().mean() * 100
    print(f"  Missing: {missing_pct:.1f}%")
    return df


def impute(df: pd.DataFrame) -> pd.DataFrame:
    """Per-station imputation strategy."""
    print("=== Imputing missing values ===")

    for stn in STATIONS:
        # Temperature, humidity, radiation, soil moisture: interpolate up to 6h (24 steps)
        for var in ["temp_c", "rh_avg", "rh_max", "rh_min", "solar_kw", "net_rad_wm2",
                     "soil_moisture_1", "soil_moisture_2", "soil_moisture_3"]:
            col = f"{stn}_{var}"
            if col in df.columns:
                df[col] = df[col].interpolate(method="linear", limit=24)

        # Wind speed: forward-fill 2 steps, then interpolate up to 2h (8 steps)
        ws_col = f"{stn}_wind_speed_ms"
        if ws_col in df.columns:
            df[ws_col] = df[ws_col].ffill(limit=2)
            df[ws_col] = df[ws_col].interpolate(method="linear", limit=8)

        # Wind direction: forward-fill only (circular variable)
        wd_col = f"{stn}_wind_dir"
        if wd_col in df.columns:
            df[wd_col] = df[wd_col].ffill()

        # Leaf wetness: forward-fill up to 2h (8 steps)
        for var in ["leaf_wetness", "leaf_wet_minutes"]:
            col = f"{stn}_{var}"
            if col in df.columns:
                df[col] = df[col].ffill(limit=8)

        # Rain: zero-fill + add missing indicator
        rain_col = f"{stn}_rain_mm"
        if rain_col in df.columns:
            df[f"{stn}_rain_missing"] = df[rain_col].isnull().astype(float)
            df[rain_col] = df[rain_col].fillna(0.0)

    # Global: ffill/bfill 96 steps, then fill remaining with 0
    df = df.ffill(limit=96).bfill(limit=96)
    df = df.fillna(0.0)

    remaining_null = df.isnull().sum().sum()
    print(f"  After imputation: {remaining_null} NaN remaining")
    return df
