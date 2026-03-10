"""GalapaOS configuration: constants, paths, hyperparameters, column maps."""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # galapaos/
BACKEND_ROOT = Path(__file__).resolve().parent.parent          # galapaos/backend/

DATA_DIR = Path(os.getenv("DATA_DIR", str(PROJECT_ROOT / "data" / "raw")))
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHECKPOINTS_DIR = BACKEND_ROOT / "checkpoints"
RESULTS_DIR = BACKEND_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

for d in [PROCESSED_DIR, CHECKPOINTS_DIR, RESULTS_DIR, FIGURES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

# ---------------------------------------------------------------------------
# Stations
# ---------------------------------------------------------------------------
STATIONS = ["cer", "jun", "merc", "mira"]
TARGET_STATION = "jun"

STATION_META = {
    "mira": {"name": "El Mirador",  "elevation": "coastal",  "order": 1},
    "merc": {"name": "Merceditas",  "elevation": "mid",      "order": 2},
    "cer":  {"name": "Cerro Alto",  "elevation": "highland",  "order": 3},
    "jun":  {"name": "El Junco",    "elevation": "summit",    "order": 4},
}

STATION_FILES = {
    "cer":  "CER_consolid_f15.csv",
    "jun":  "JUN_consolid_f15.csv",
    "merc": "MERC_consolid_f15.csv",
    "mira": "MIRA_consolid_f15.csv",
}

# ---------------------------------------------------------------------------
# Column mapping  (canonical name -> possible raw names)
# ---------------------------------------------------------------------------
COLUMN_MAP = {
    "rain_mm":        ["Rain_mm_Tot"],
    "temp_c":         ["AirTC_Avg"],
    "rh_avg":         ["RH_Avg"],
    "rh_max":         ["RH_Max"],
    "rh_min":         ["RH_Min"],
    "solar_kw":       ["SlrkW_Avg"],
    "net_rad_wm2":    ["NR_Wm2_Avg"],
    "wind_speed_ms":  ["WS_ms_Avg"],
    "wind_dir":       ["WindDir"],
    "soil_moisture_1": ["VW_Avg", "VW"],
    "soil_moisture_2": ["VW_2_Avg", "VW_2"],
    "soil_moisture_3": ["VW_3_Avg", "VW_3"],
    "leaf_wetness":   ["LWmV_Avg"],
    "leaf_wet_minutes": ["LWMWet_Tot"],
}

TIMESTAMP_FORMAT = "%m/%d/%Y %H:%M"

# ---------------------------------------------------------------------------
# Train / Val / Test splits
# ---------------------------------------------------------------------------
TRAIN_END = "2023-01-01"
VAL_END = "2024-07-01"
EMBARGO_STEPS = 48  # 12 hours at 15-min resolution

# ---------------------------------------------------------------------------
# Model hyperparameters
# ---------------------------------------------------------------------------
LOOKBACK = 96        # 24 hours
BATCH_SIZE = 256
LEARNING_RATE = 1e-3
PATIENCE = 10
MAX_EPOCHS = 50
HIDDEN_DIM = 128
NUM_LAYERS = 2
DROPOUT = 0.3

# ---------------------------------------------------------------------------
# RDI thresholds
# ---------------------------------------------------------------------------
RDI_GREEN = 1.0
RDI_YELLOW = 0.6
DEMAND_AVG_KW = 800

# ---------------------------------------------------------------------------
# Target definitions
# ---------------------------------------------------------------------------
SOLAR_RAMP_THRESHOLD = -0.3   # kt drop threshold
RAIN_PERCENTILE = 95          # heavy rain = above p95

HORIZONS = {
    "1h": 4,
    "3h": 12,
    "6h": 24,
    "12h": 48,
}
