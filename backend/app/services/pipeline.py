"""Full pipeline: load -> preprocess -> features -> targets -> train -> evaluate."""

import json
import pandas as pd
import torch

from ..config import (
    PROCESSED_DIR, RESULTS_DIR, CHECKPOINTS_DIR,
    TRAIN_END, VAL_END, EMBARGO_STEPS, LOOKBACK,
    HIDDEN_DIM, NUM_LAYERS, DROPOUT,
)
from ..data.loading import load_all_stations
from ..data.preprocessing import impute_all
from ..data.feature_engineering import engineer_features
from ..ml.targets import build_all_targets, get_target_columns
from ..ml.dataset import prepare_splits
from ..ml.models import RecurrentClassifier, XGBoostClassifierWrapper
from ..ml.train import train_model
from ..ml.evaluate import evaluate_model


def run_full_pipeline():
    """Execute the complete training pipeline."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Step 1: Load data
    print("\n=== Step 1: Loading data ===")
    df = load_all_stations()

    # Step 2: Impute
    print("\n=== Step 2: Imputation ===")
    df = impute_all(df)

    # Step 3: Feature engineering
    print("\n=== Step 3: Feature engineering ===")
    df = engineer_features(df)

    # Step 4: Build targets
    print("\n=== Step 4: Building targets ===")
    df = build_all_targets(df)

    # Save processed data
    print("\n  Saving processed data...")
    df.to_parquet(PROCESSED_DIR / "features_and_targets.parquet")

    # Step 5: Identify feature and target columns
    target_cols = [c for c in get_target_columns() if c in df.columns]
    non_feature_prefixes = ["solar_ramp_", "heavy_rain_"]
    feature_cols = [
        c for c in df.columns
        if not any(c.startswith(p) for p in non_feature_prefixes)
    ]
    print(f"\n  Features: {len(feature_cols)}, Targets: {target_cols}")

    # Step 6: Train models for priority targets
    all_metrics = {}
    priority_targets = ["solar_ramp_3h", "heavy_rain_3h"]

    for target_name in priority_targets:
        if target_name not in df.columns:
            print(f"\n  Skipping {target_name} (not in DataFrame)")
            continue

        print(f"\n=== Training for {target_name} ===")

        # Prepare data splits
        train_ds, val_ds, test_ds, scaler = prepare_splits(
            df, feature_cols, target_name,
            TRAIN_END, VAL_END, EMBARGO_STEPS, LOOKBACK
        )

        target_metrics = {}

        # Train LSTM
        for rnn_type in ["lstm", "gru"]:
            print(f"\n--- {rnn_type.upper()} ---")
            model = RecurrentClassifier(
                input_dim=len(feature_cols),
                hidden_dim=HIDDEN_DIM,
                num_layers=NUM_LAYERS,
                dropout=DROPOUT,
                rnn_type=rnn_type,
            )
            model = train_model(model, train_ds, val_ds, target_name, rnn_type, device)
            metrics, _, _ = evaluate_model(model, test_ds, target_name, device)
            target_metrics[rnn_type.upper()] = metrics

        # Train XGBoost
        print(f"\n--- XGBoost ---")
        try:
            xgb_model = XGBoostClassifierWrapper()
            xgb_model.fit(train_ds, val_ds)
            xgb_probs = xgb_model.predict_proba(test_ds)
            from ..ml.evaluate import compute_metrics
            import numpy as np
            test_labels = np.array([test_ds[i][1].item() for i in range(len(test_ds))])
            xgb_metrics = compute_metrics(xgb_probs, test_labels)
            target_metrics["XGBoost"] = xgb_metrics
            xgb_model.save(CHECKPOINTS_DIR / f"xgboost_{target_name}.json")
            print(f"  XGBoost: PR-AUC={xgb_metrics['PR-AUC']:.4f}, "
                  f"CSI={xgb_metrics['CSI']:.4f}")
        except Exception as e:
            print(f"  XGBoost failed: {e}")

        all_metrics[target_name] = target_metrics

    # Save metrics
    metrics_path = RESULTS_DIR / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\n  Metrics saved to {metrics_path}")

    # Find best model
    best_model = "LSTM"
    best_prauc = 0
    for target, models in all_metrics.items():
        for model_name, m in models.items():
            if m.get("PR-AUC", 0) > best_prauc:
                best_prauc = m["PR-AUC"]
                best_model = model_name

    print(f"\n=== Pipeline complete. Best model: {best_model} (PR-AUC={best_prauc:.4f}) ===")
    return all_metrics
