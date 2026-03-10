"""Load and harmonize 4 station CSVs."""

import pandas as pd
from .config import DATA_RAW, STATION_FILES, COLUMN_MAP, TIMESTAMP_FORMAT


def load_station(name: str) -> pd.DataFrame:
    """Load a single station CSV, parse timestamps, harmonize column names."""
    filepath = DATA_RAW / STATION_FILES[name]
    print(f"  Loading {name.upper()} from {filepath.name}...")

    df = pd.read_csv(filepath, parse_dates=["TIMESTAMP"], date_format=TIMESTAMP_FORMAT, low_memory=False)
    df = df.set_index("TIMESTAMP").sort_index()

    # Drop non-numeric utility columns
    drop_cols = [c for c in ["RECORD"] if c in df.columns]
    df = df.drop(columns=drop_cols, errors="ignore")

    # Harmonize column names using COLUMN_MAP
    rename = {}
    for canonical, raw_options in COLUMN_MAP.items():
        for raw in raw_options:
            if raw in df.columns:
                rename[raw] = f"{name}_{canonical}"
                break

    df = df.rename(columns=rename)

    # Keep only harmonized columns (prefixed with station name)
    keep = [c for c in df.columns if c.startswith(f"{name}_")]
    df = df[keep]

    # Convert to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"    {len(df)} rows, {len(df.columns)} cols, "
          f"{df.index.min().date()} to {df.index.max().date()}")
    return df


def load_all_stations() -> dict:
    """Load all 4 stations, return dict of DataFrames."""
    print("=== Loading stations ===")
    stations = {}
    for name in STATION_FILES:
        stations[name] = load_station(name)
    return stations
