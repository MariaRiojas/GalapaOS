"""Load and harmonize 4 station CSVs into a single wide DataFrame."""

import pandas as pd
import numpy as np
from ..config import DATA_DIR, STATION_FILES, STATIONS, COLUMN_MAP, TIMESTAMP_FORMAT


def _harmonize_columns(df: pd.DataFrame, station: str) -> pd.DataFrame:
    """Rename raw CSV columns to canonical names with station prefix."""
    renamed = {}
    for canonical, raw_options in COLUMN_MAP.items():
        for raw in raw_options:
            if raw in df.columns:
                renamed[raw] = f"{station}_{canonical}"
                break
    df = df.rename(columns=renamed)
    # Drop columns that weren't mapped (keep only canonical + TIMESTAMP)
    keep = [c for c in df.columns if c.startswith(f"{station}_")]
    return df[keep]


def load_station(station: str) -> pd.DataFrame:
    """Load a single station CSV and return harmonized DataFrame with datetime index."""
    path = DATA_DIR / STATION_FILES[station]
    df = pd.read_csv(path, low_memory=False)

    # Parse timestamp
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"], format=TIMESTAMP_FORMAT)
    df = df.set_index("TIMESTAMP").sort_index()

    # Remove duplicate timestamps
    df = df[~df.index.duplicated(keep="first")]

    # Harmonize column names
    df = _harmonize_columns(df, station)

    # Convert to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_all_stations() -> pd.DataFrame:
    """Load all 4 stations and merge into a single wide DataFrame."""
    frames = []
    for stn in STATIONS:
        print(f"  Loading {stn.upper()}...")
        stn_df = load_station(stn)
        frames.append(stn_df)
        print(f"    {stn_df.shape[0]} rows, {stn_df.shape[1]} cols")

    # Outer join on timestamp index so we keep all timesteps
    merged = frames[0]
    for f in frames[1:]:
        merged = merged.join(f, how="outer")

    # Ensure regular 15-min frequency
    full_idx = pd.date_range(merged.index.min(), merged.index.max(), freq="15min")
    merged = merged.reindex(full_idx)
    merged.index.name = "TIMESTAMP"

    print(f"  Merged: {merged.shape[0]} rows, {merged.shape[1]} cols")
    return merged
