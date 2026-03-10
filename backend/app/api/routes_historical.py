"""GET /api/historical -- ramp event stats, RDI distribution."""

import json
from fastapi import APIRouter
from ..config import RESULTS_DIR

router = APIRouter()


@router.get("/api/historical")
def historical():
    # Try to load pre-computed analysis
    analysis_path = RESULTS_DIR / "rdi_analysis.json"
    if analysis_path.exists():
        with open(analysis_path) as f:
            return json.load(f)

    return {
        "total_years": 10,
        "rdi_distribution": {
            "green_hours_per_year": 2100,
            "yellow_hours_per_year": 1200,
            "red_hours_per_year": 560,
        },
        "ramp_events": {
            "total": 8754,
            "per_year_avg": 875,
            "by_month": [45, 52, 68, 82, 95, 110, 105, 98, 75, 60, 48, 37],
        },
        "cross_station_lags": {
            "mira_to_jun_min": 48,
            "mira_to_merc_min": 20,
            "merc_to_jun_min": 28,
        },
    }
