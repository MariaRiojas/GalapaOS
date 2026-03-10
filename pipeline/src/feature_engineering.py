"""Feature engineering: baseline + NEW solar/geographic features."""

import pandas as pd
import numpy as np
from .config import STATIONS, TRAIN_END, STATION_META, LAPSE_RATE_C_PER_KM


# ── Baseline Features ──────────────────────────────────────────────

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cyclical time encodings."""
    hour = df.index.hour + df.index.minute / 60.0
    doy = df.index.dayofyear
    df["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    df["hour_cos"] = np.cos(2 * np.pi * hour / 24)
    df["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    return df


def add_wind_decomposition(df: pd.DataFrame) -> pd.DataFrame:
    """Decompose wind into x/y components per station."""
    for stn in STATIONS:
        ws = f"{stn}_wind_speed_ms"
        wd = f"{stn}_wind_dir"
        if ws in df.columns and wd in df.columns:
            rad = np.deg2rad(df[wd])
            df[f"{stn}_wind_x"] = df[ws] * np.cos(rad)
            df[f"{stn}_wind_y"] = df[ws] * np.sin(rad)
    return df


def add_dewpoint(df: pd.DataFrame) -> pd.DataFrame:
    """Dewpoint and dewpoint depression via Magnus formula."""
    a, b = 17.27, 237.7
    for stn in STATIONS:
        tc = f"{stn}_temp_c"
        rh = f"{stn}_rh_avg"
        if tc in df.columns and rh in df.columns:
            rh_frac = df[rh].clip(1, 100) / 100.0
            gamma = (a * df[tc]) / (b + df[tc]) + np.log(rh_frac + 1e-8)
            df[f"{stn}_dewpoint"] = (b * gamma) / (a - gamma)
            df[f"{stn}_dewpoint_depression"] = df[tc] - df[f"{stn}_dewpoint"]
    return df


def add_soil_tendency(df: pd.DataFrame) -> pd.DataFrame:
    """Soil moisture 3h tendency."""
    for stn in STATIONS:
        for i in [1, 2, 3]:
            col = f"{stn}_soil_moisture_{i}"
            if col in df.columns:
                df[f"{col}_tend_3h"] = df[col].diff(12)
    return df


def add_rolling_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Rolling statistics at 1h, 3h, 6h windows."""
    import warnings
    warnings.filterwarnings("ignore", message="DataFrame is highly fragmented")

    windows = {"1h": 4, "3h": 12, "6h": 24}
    for stn in STATIONS:
        rain_col = f"{stn}_rain_mm"
        if rain_col in df.columns:
            for label, w in windows.items():
                df[f"{stn}_rain_sum_{label}"] = df[rain_col].rolling(w, min_periods=1).sum()

        for var, aggs in [("temp_c", ["mean", "std"]),
                          ("wind_speed_ms", ["mean"]),
                          ("rh_avg", ["mean"])]:
            col = f"{stn}_{var}"
            if col not in df.columns:
                continue
            for label, w in windows.items():
                for agg in aggs:
                    df[f"{stn}_{var}_{agg}_{label}"] = (
                        df[col].rolling(w, min_periods=1).agg(agg)
                    )
    # Defragment after many column additions
    df = df.copy()
    return df


# ── NEW Solar Features ──────────────────────────────────────────────

def add_clearsky_index(df: pd.DataFrame) -> pd.DataFrame:
    """Clear-sky index (kt) per station."""
    train_mask = df.index < TRAIN_END

    for stn in STATIONS:
        solar_col = f"{stn}_solar_kw"
        if solar_col not in df.columns:
            continue

        daytime_mask = df[solar_col] > 0.01
        train_day = train_mask & daytime_mask
        if train_day.sum() == 0:
            continue

        clear_sky_lookup = (
            df.loc[train_day]
            .groupby([df.loc[train_day].index.hour, df.loc[train_day].index.month])[solar_col]
            .quantile(0.95)
        )

        keys = list(zip(df.index.hour, df.index.month))
        cs_values = [clear_sky_lookup.get(k, 0.01) for k in keys]
        df[f"{stn}_solar_clearsky"] = np.maximum(cs_values, 0.01)

        # kt = observed / clearsky
        df[f"{stn}_kt"] = (df[solar_col] / df[f"{stn}_solar_clearsky"]).clip(0, 1.5)

        # Ramp rates of kt
        df[f"{stn}_kt_ramp_15m"] = df[f"{stn}_kt"].diff(1)
        df[f"{stn}_kt_ramp_30m"] = df[f"{stn}_kt"].diff(2)
        df[f"{stn}_kt_ramp_1h"] = df[f"{stn}_kt"].diff(4)

        # Solar variability
        df[f"{stn}_kt_std_1h"] = df[f"{stn}_kt"].rolling(4, min_periods=1).std()
        df[f"{stn}_kt_std_3h"] = df[f"{stn}_kt"].rolling(12, min_periods=1).std()

    return df


def add_cross_station_features(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-station gradient: spatial cloud tracking."""
    # D. Coast-highland gradient
    if "mira_kt" in df.columns and "jun_kt" in df.columns:
        df["kt_gradient_coast_highland"] = df["mira_kt"] - df["jun_kt"]
        for lag in [2, 4, 8]:
            if "mira_kt_ramp_15m" in df.columns:
                df[f"mira_kt_ramp_lag_{lag}"] = df["mira_kt_ramp_15m"].shift(lag)

    if "merc_kt" in df.columns and "jun_kt" in df.columns:
        df["kt_gradient_mid_summit"] = df["merc_kt"] - df["jun_kt"]

    return df


def add_daytime_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Binary daytime indicator."""
    cs_col = "jun_solar_clearsky"
    if cs_col in df.columns:
        df["is_daytime"] = (df[cs_col] > 0.01).astype(float)
    else:
        hour = df.index.hour
        df["is_daytime"] = ((hour >= 6) & (hour <= 18)).astype(float)
    return df


# ── NEW Geographic Features ──────────────────────────────────────────

def add_lapse_rate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Thermal lapse rate deviation and inversion detection."""
    mira_temp = "mira_temp_c"
    if mira_temp not in df.columns:
        return df

    for stn in ["merc", "cer", "jun"]:
        temp_col = f"{stn}_temp_c"
        if temp_col not in df.columns:
            continue
        elev_km = (STATION_META[stn]["elevation_m"] - STATION_META["mira"]["elevation_m"]) / 1000
        df[f"{stn}_temp_expected"] = df[mira_temp] - elev_km * LAPSE_RATE_C_PER_KM
        df[f"{stn}_temp_lapse_deviation"] = df[temp_col] - df[f"{stn}_temp_expected"]
        df[f"{stn}_thermal_inversion"] = (df[f"{stn}_temp_lapse_deviation"] > 1.0).astype(float)

    if "jun_temp_lapse_deviation" in df.columns:
        df["inversion_strength"] = df["jun_temp_lapse_deviation"]

    return df


def add_cross_station_lagged(df: pd.DataFrame) -> pd.DataFrame:
    """Cross-station lagged features for propagation tracking."""
    lag_configs = [("mira", 6), ("mira", 4), ("merc", 3)]
    variables = ["kt", "kt_ramp_15m", "dewpoint_depression", "wind_speed_ms"]

    for source, lag_steps in lag_configs:
        for var in variables:
            col = f"{source}_{var}"
            if col in df.columns:
                df[f"{source}_{var}_lag{lag_steps}"] = df[col].shift(lag_steps)

    return df


def add_humidity_gradient(df: pd.DataFrame) -> pd.DataFrame:
    """Humidity gradient between coast and summit."""
    if "mira_rh_avg" in df.columns and "jun_rh_avg" in df.columns:
        df["rh_gradient_coast_summit"] = df["jun_rh_avg"] - df["mira_rh_avg"]
        df["rh_gradient_trend_1h"] = df["rh_gradient_coast_summit"].diff(4)
    return df


# ── Master function ──────────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run all feature engineering steps."""
    print("=== Feature engineering ===")

    steps = [
        ("Time features", add_time_features),
        ("Wind decomposition", add_wind_decomposition),
        ("Dewpoint", add_dewpoint),
        ("Soil moisture tendency", add_soil_tendency),
        ("Rolling statistics", add_rolling_stats),
        ("Clear-sky index (kt)", add_clearsky_index),
        ("Cross-station gradient", add_cross_station_features),
        ("Daytime flag", add_daytime_flag),
        ("Lapse rate / inversion", add_lapse_rate_features),
        ("Cross-station lagged", add_cross_station_lagged),
        ("Humidity gradient", add_humidity_gradient),
    ]

    for name, fn in steps:
        print(f"  {name}...")
        df = fn(df)

    # Defragment and fill remaining NaN
    df = df.copy()
    df = df.fillna(0.0)
    print(f"  Final feature matrix: {df.shape[0]} rows, {df.shape[1]} cols")
    return df
