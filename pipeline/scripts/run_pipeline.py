"""Full pipeline: load -> preprocess -> features -> geo -> targets -> train -> eval -> metrics."""

import sys
import json
from pathlib import Path

# Add pipeline root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
import numpy as np
import pandas as pd

from src.config import (
    RESULTS, CHECKPOINTS, TRAIN_END, VAL_END, LOOKBACK,
    HIDDEN_DIM, NUM_LAYERS, DROPOUT,
)
from src.data_loading import load_all_stations
from src.preprocessing import merge_stations, impute
from src.feature_engineering import engineer_features
from src.geo_spatial import compute_propagation_lags, save_lags
from src.targets import build_all_targets
from src.dataset import prepare_splits
from src.models import RecurrentClassifier, XGBoostClassifierWrapper
from src.train import train_model
from src.evaluate import evaluate_model, compute_metrics


def run():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}\n")

    # Step 1: Load
    stations = load_all_stations()

    # Step 2: Merge + Impute
    df = merge_stations(stations)
    df = impute(df)

    # Step 3: Feature engineering
    df = engineer_features(df)

    # Step 4: Geo-spatial analysis
    lags = compute_propagation_lags(df, variable="solar_kw")
    save_lags(lags)

    # Step 5: Build targets
    df = build_all_targets(df)

    # Save processed data
    processed_path = RESULTS / "processed_data.parquet"
    df.to_parquet(processed_path)
    print(f"\n  Saved processed data: {processed_path}")

    # Step 6: Identify feature vs target columns
    target_prefixes = ["solar_ramp_", "heavy_rain_"]
    feature_cols = [
        c for c in df.columns
        if not any(c.startswith(p) for p in target_prefixes)
    ]
    print(f"\n  Features: {len(feature_cols)}")

    # Step 7: Train + Evaluate
    all_metrics = {}
    priority_targets = ["solar_ramp_3h", "heavy_rain_3h"]
    xgb_importances = {}

    for target_name in priority_targets:
        if target_name not in df.columns:
            print(f"\n  Skipping {target_name} (not found)")
            continue

        print(f"\n{'='*60}")
        print(f"  Target: {target_name}")
        print(f"{'='*60}")

        # Drop NaN targets
        valid = df[target_name].notna()
        df_valid = df.loc[valid]

        train_ds, val_ds, test_ds, scaler = prepare_splits(
            df_valid, feature_cols, target_name,
            TRAIN_END, VAL_END, LOOKBACK,
        )

        target_metrics = {}

        # LSTM
        for rnn_type in ["lstm"]:
            model = RecurrentClassifier(
                input_dim=len(feature_cols),
                hidden_dim=HIDDEN_DIM,
                num_layers=NUM_LAYERS,
                dropout=DROPOUT,
                rnn_type=rnn_type,
            )
            model = train_model(model, train_ds, val_ds, target_name, rnn_type, device)
            metrics, probs, labels = evaluate_model(model, test_ds, target_name, device)
            target_metrics[rnn_type.upper()] = metrics

        # XGBoost
        print(f"\n  Training XGBoost for {target_name}...")
        try:
            xgb = XGBoostClassifierWrapper()
            xgb.fit(train_ds, val_ds)
            xgb_probs = xgb.predict_proba(test_ds)
            test_labels = np.array([test_ds[i][1].item() for i in range(len(test_ds))])
            xgb_metrics = compute_metrics(xgb_probs, test_labels)
            target_metrics["XGBoost"] = xgb_metrics
            xgb.save(CHECKPOINTS / f"xgboost_{target_name}.json")
            print(f"  XGBoost: PR_AUC={xgb_metrics['PR_AUC']:.4f}, CSI={xgb_metrics['CSI']:.4f}")

            # Feature importance (use last lookback * n_features naming)
            importances = xgb.feature_importances()
            # Map back to feature names (averaged over lookback)
            n_feat = len(feature_cols)
            if len(importances) == LOOKBACK * n_feat:
                avg_imp = importances.reshape(LOOKBACK, n_feat).mean(axis=0)
                top_idx = np.argsort(avg_imp)[::-1][:20]
                xgb_importances[target_name] = [
                    {"name": feature_cols[i], "importance": round(float(avg_imp[i]), 6)}
                    for i in top_idx
                ]
        except Exception as e:
            print(f"  XGBoost failed: {e}")

        all_metrics[target_name] = target_metrics

    # Save metrics
    metrics_path = RESULTS / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\n  Metrics saved: {metrics_path}")

    # Save feature importance
    if xgb_importances:
        imp_path = RESULTS / "feature_importance.json"
        with open(imp_path, "w") as f:
            json.dump(xgb_importances, f, indent=2)

    # Find best model
    best_model = "LSTM"
    best_prauc = 0
    for target, models in all_metrics.items():
        for model_name, m in models.items():
            if m.get("PR_AUC", 0) > best_prauc:
                best_prauc = m["PR_AUC"]
                best_model = model_name

    print(f"\n{'='*60}")
    print(f"  Pipeline complete. Best: {best_model} (PR_AUC={best_prauc:.4f})")
    print(f"{'='*60}")

    return all_metrics


if __name__ == "__main__":
    run()
