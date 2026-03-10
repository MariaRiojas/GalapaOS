"""EcoDispatch configuration: ALL constants, paths, station metadata, hyperparameters."""

import os
from pathlib import Path

# === Paths ===
PIPELINE_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = PIPELINE_ROOT.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
CHECKPOINTS = PIPELINE_ROOT / "checkpoints"
RESULTS = PIPELINE_ROOT / "results"
FIGURES = RESULTS / "figures"
# Output JSONs go DIRECTLY to dashboard's public/data/
DASHBOARD_DATA = PROJECT_ROOT / "dashboard" / "public" / "data"

for d in [CHECKPOINTS, RESULTS, FIGURES, DASHBOARD_DATA]:
    d.mkdir(parents=True, exist_ok=True)

# === Station config ===
STATION_FILES = {
    "cer": "CER_consolid_f15.csv",
    "jun": "JUN_consolid_f15.csv",
    "merc": "MERC_consolid_f15.csv",
    "mira": "MIRA_consolid_f15.csv",
}
STATIONS = ["cer", "jun", "merc", "mira"]
TARGET_STATION = "jun"
TRANSECT_ORDER = ["mira", "merc", "cer", "jun"]

TIMESTAMP_FORMAT = "%m/%d/%Y %H:%M"

COLUMN_MAP = {
    "rain_mm": ["Rain_mm_Tot"],
    "temp_c": ["AirTC_Avg"],
    "rh_avg": ["RH_Avg"],
    "rh_max": ["RH_Max"],
    "rh_min": ["RH_Min"],
    "solar_kw": ["SlrkW_Avg"],
    "net_rad_wm2": ["NR_Wm2_Avg"],
    "wind_speed_ms": ["WS_ms_Avg"],
    "wind_dir": ["WindDir"],
    "soil_moisture_1": ["VW_Avg", "VW"],
    "soil_moisture_2": ["VW_2_Avg", "VW_2"],
    "soil_moisture_3": ["VW_3_Avg", "VW_3"],
    "leaf_wetness": ["LWmV_Avg"],
    "leaf_wet_minutes": ["LWMWet_Tot"],
}

STATION_META = {
    "mira": {"name": "El Mirador", "elevation_m": 80, "lat": -0.910, "lon": -89.610, "zone": "coastal", "order": 1},
    "merc": {"name": "Merceditas", "elevation_m": 300, "lat": -0.895, "lon": -89.575, "zone": "mid-elevation", "order": 2},
    "cer":  {"name": "Cerro Alto", "elevation_m": 500, "lat": -0.880, "lon": -89.555, "zone": "highland", "order": 3},
    "jun":  {"name": "El Junco", "elevation_m": 700, "lat": -0.870, "lon": -89.540, "zone": "summit", "order": 4},
}

STATION_DISTANCES_KM = {
    ("mira", "merc"): 5.2, ("mira", "cer"): 9.8, ("mira", "jun"): 14.1,
    ("merc", "cer"): 4.6, ("merc", "jun"): 8.9, ("cer", "jun"): 4.3,
}

# === Time splits ===
TRAIN_END = "2023-01-01"
VAL_END = "2024-07-01"
EMBARGO_HOURS = 12

# === Model hyperparameters ===
LOOKBACK = 96        # 24 hours at 15-min resolution
BATCH_SIZE = 256
HIDDEN_DIM = 128
NUM_LAYERS = 2
DROPOUT = 0.3
LR = 1e-3
MAX_EPOCHS = 50
PATIENCE = 10
SEED = 42

# === Thresholds ===
KT_RAMP_THRESHOLD = -0.3
RAIN_PERCENTILE = 95
RDI_GREEN = 1.0
RDI_YELLOW = 0.6
LAPSE_RATE_C_PER_KM = 6.5

# === San Cristobal grid specs ===
WIND_TURBINE_CAPACITY_KW = 800
N_WIND_TURBINES = 3
WIND_CUT_IN_MS = 3
WIND_RATED_MS = 12
DEMAND_AVG_KW = 800

# === Horizons ===
HORIZONS = {"1h": 4, "3h": 12, "6h": 24, "12h": 48}
