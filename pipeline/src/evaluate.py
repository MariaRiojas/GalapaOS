"""Evaluation metrics: PR-AUC, CSI, POD, FAR, BSS, F1."""

import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import (
    precision_recall_curve, auc, brier_score_loss,
    confusion_matrix, f1_score,
)
from .config import BATCH_SIZE


def get_predictions(model, dataset, device="cpu"):
    """Get model predictions as probabilities."""
    model = model.to(device).eval()
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)
    all_probs, all_labels = [], []

    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            logits = model(x)
            probs = torch.sigmoid(logits).cpu().numpy()
            all_probs.append(probs)
            all_labels.append(y.numpy())

    return np.concatenate(all_probs), np.concatenate(all_labels)


def compute_metrics(probs, labels, threshold=0.5):
    """Compute all evaluation metrics."""
    results = {}

    # PR-AUC
    if labels.sum() > 0:
        precision, recall, _ = precision_recall_curve(labels, probs)
        results["PR_AUC"] = round(float(auc(recall, precision)), 4)
    else:
        results["PR_AUC"] = 0.0

    preds = (probs >= threshold).astype(int)

    if labels.sum() > 0 and preds.sum() > 0:
        tn, fp, fn, tp = confusion_matrix(labels, preds, labels=[0, 1]).ravel()
    else:
        tn = int((labels == 0).sum())
        fp = 0
        fn = int(labels.sum())
        tp = 0

    # POD (Recall)
    results["POD"] = round(float(tp / max(tp + fn, 1)), 4)
    # FAR
    results["FAR"] = round(float(fp / max(tp + fp, 1)), 4)
    # CSI
    results["CSI"] = round(float(tp / max(tp + fn + fp, 1)), 4)
    # F1
    results["F1"] = round(float(f1_score(labels, preds, zero_division=0)), 4)

    # BSS
    bs = brier_score_loss(labels, probs)
    climo = labels.mean()
    bs_ref = brier_score_loss(labels, np.full_like(probs, climo))
    results["BSS"] = round(float(1 - bs / max(bs_ref, 1e-10)), 4)

    results["n_samples"] = len(labels)
    results["n_positive"] = int(labels.sum())

    return results


def evaluate_model(model, test_ds, target_name, device="cpu"):
    """Full evaluation of a trained model."""
    probs, labels = get_predictions(model, test_ds, device)
    metrics = compute_metrics(probs, labels)
    print(f"  {target_name}: PR_AUC={metrics['PR_AUC']:.4f}, "
          f"CSI={metrics['CSI']:.4f}, POD={metrics['POD']:.4f}, "
          f"FAR={metrics['FAR']:.4f}, F1={metrics['F1']:.4f}")
    return metrics, probs, labels
