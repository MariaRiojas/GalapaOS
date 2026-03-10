"""GET /api/model-info -- metrics, feature importance."""

import json
from fastapi import APIRouter
from ..config import RESULTS_DIR

router = APIRouter()


@router.get("/api/model-info")
def model_info():
    metrics_path = RESULTS_DIR / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            all_metrics = json.load(f)

        # Find best model
        best_model = "LSTM"
        best_prauc = 0
        for target, models in all_metrics.items():
            for model_name, m in models.items():
                if m.get("PR-AUC", 0) > best_prauc:
                    best_prauc = m["PR-AUC"]
                    best_model = model_name

        return {
            "best_model": best_model,
            "targets": all_metrics,
            "feature_count": 140,
            "lookback_hours": 24,
            "data_range": "2015-06 to 2026-03",
        }

    return {
        "best_model": "LSTM",
        "targets": {
            "solar_ramp_3h": {"LSTM": {"PR-AUC": 0.0, "CSI": 0.0, "POD": 0.0, "FAR": 0.0}},
            "heavy_rain_3h": {"LSTM": {"PR-AUC": 0.0, "CSI": 0.0, "POD": 0.0, "FAR": 0.0}},
        },
        "feature_count": 140,
        "lookback_hours": 24,
        "data_range": "2015-06 to 2026-03",
    }
