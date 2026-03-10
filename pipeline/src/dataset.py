"""PyTorch Dataset for sliding-window time series classification."""

import numpy as np
import torch
from torch.utils.data import Dataset
from sklearn.preprocessing import StandardScaler
from .config import LOOKBACK


class WeatherDataset(Dataset):
    """Sliding-window dataset for weather time series."""

    def __init__(self, features: np.ndarray, targets: np.ndarray, lookback: int = LOOKBACK):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
        self.lookback = lookback

    def __len__(self):
        return len(self.features) - self.lookback

    def __getitem__(self, idx):
        x = self.features[idx: idx + self.lookback]
        y = self.targets[idx + self.lookback - 1]
        return x, y


def prepare_splits(df, feature_cols, target_col, train_end, val_end, lookback=LOOKBACK):
    """Split DataFrame into train/val/test and return datasets + scaler."""
    features = df[feature_cols].values.astype(np.float32)
    targets = df[target_col].values.astype(np.float32)

    train_idx = df.index < train_end
    val_idx = (df.index >= train_end) & (df.index < val_end)
    test_idx = df.index >= val_end

    # Normalize using train statistics
    scaler = StandardScaler()
    scaler.fit(features[train_idx])
    features = scaler.transform(features)
    features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

    train_ds = WeatherDataset(features[train_idx], targets[train_idx], lookback)
    val_ds = WeatherDataset(features[val_idx], targets[val_idx], lookback)
    test_ds = WeatherDataset(features[test_idx], targets[test_idx], lookback)

    print(f"    Train: {len(train_ds)}, Val: {len(val_ds)}, Test: {len(test_ds)}")
    return train_ds, val_ds, test_ds, scaler
