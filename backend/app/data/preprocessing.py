"""Merge wide DataFrame imputation strategies per variable type."""

import pandas as pd
import numpy as np
from ..config import STATIONS


def impute_station(df: pd.DataFrame, station: str) -> pd.DataFrame:
    """Apply per-variable imputation for one station's columns."""
    prefix = f"{station}_"

    # Temperature, humidity, radiation, soil moisture: linear interpolation up to 6h (24 steps)
    interp_vars = ["temp_c", "rh_avg", "rh_max", "rh_min", "solar_kw",
                   "net_rad_wm2", "soil_moisture_1", "soil_moisture_2",
                   "soil_moisture_3"]
    for var in interp_vars:
        col = f"{prefix}{var}"
        if col in df.columns:
            df[col] = df[col].interpolate(method="linear", limit=24)

    # Wind speed: forward-fill 2 steps, then interpolate up to 2h (8 steps)
    ws_col = f"{prefix}wind_speed_ms"
    if ws_col in df.columns:
        df[ws_col] = df[ws_col].ffill(limit=2)
        df[ws_col] = df[ws_col].interpolate(method="linear", limit=8)

    # Wind direction: forward-fill only (circular)
    wd_col = f"{prefix}wind_dir"
    if wd_col in df.columns:
        df[wd_col] = df[wd_col].ffill(limit=8)

    # Leaf wetness: forward-fill up to 2h
    for lvar in ["leaf_wetness", "leaf_wet_minutes"]:
        lcol = f"{prefix}{lvar}"
        if lcol in df.columns:
            df[lcol] = df[lcol].ffill(limit=8)

    # Precipitation: zero-fill + add binary missing indicator
    rain_col = f"{prefix}rain_mm"
    if rain_col in df.columns:
        missing_mask = df[rain_col].isna()
        df[f"{prefix}rain_missing"] = missing_mask.astype(float)
        df[rain_col] = df[rain_col].fillna(0.0)

    return df


def impute_all(df: pd.DataFrame) -> pd.DataFrame:
    """Apply imputation for all stations, then global fill."""
    for stn in STATIONS:
        df = impute_station(df, stn)

    # Global: ffill/bfill 96 steps, then fill remaining with 0
    df = df.ffill(limit=96).bfill(limit=96)
    df = df.fillna(0.0)

    return df
