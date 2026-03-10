"""Dual target construction: solar ramp events + heavy precipitation."""

import pandas as pd
import numpy as np
from .config import (
    STATIONS, TARGET_STATION, KT_RAMP_THRESHOLD,
    RAIN_PERCENTILE, HORIZONS, TRAIN_END,
)


def build_solar_ramp_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Build forward-looking solar ramp event targets."""
    print("  Building solar ramp targets...")
    for stn in STATIONS:
        kt_col = f"{stn}_kt"
        if kt_col not in df.columns:
            continue
        ramp_rate = df[kt_col].diff()
        ramp_event = (ramp_rate < KT_RAMP_THRESHOLD).astype(int)

        for label, steps in HORIZONS.items():
            target_col = f"solar_ramp_{label}_{stn}"
            df[target_col] = ramp_event.rolling(steps, min_periods=1).max().shift(-steps)

    # Primary targets for target station
    for label in HORIZONS:
        src = f"solar_ramp_{label}_{TARGET_STATION}"
        if src in df.columns:
            df[f"solar_ramp_{label}"] = df[src]

    return df


def build_rain_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Build forward-looking heavy precipitation targets."""
    print("  Building heavy rain targets...")
    rain_col = f"{TARGET_STATION}_rain_mm"
    if rain_col not in df.columns:
        return df

    # p95 threshold from training data non-zero rain
    train_rain = df.loc[df.index < TRAIN_END, rain_col]
    nonzero = train_rain[train_rain > 0]
    if len(nonzero) == 0:
        return df
    threshold = float(np.percentile(nonzero, RAIN_PERCENTILE))
    print(f"    Heavy rain threshold (p{RAIN_PERCENTILE}): {threshold:.3f} mm")

    heavy_rain = (df[rain_col] > threshold).astype(int)

    for label, steps in HORIZONS.items():
        df[f"heavy_rain_{label}"] = heavy_rain.rolling(steps, min_periods=1).max().shift(-steps)

    return df


def build_all_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Build all target variables."""
    print("=== Building targets ===")
    df = build_solar_ramp_targets(df)
    df = build_rain_targets(df)
    return df


def get_target_columns() -> list:
    """Return list of primary target column names."""
    targets = []
    for label in HORIZONS:
        targets.append(f"solar_ramp_{label}")
        targets.append(f"heavy_rain_{label}")
    return targets
