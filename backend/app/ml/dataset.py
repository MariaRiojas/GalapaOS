"""PyTorch Dataset for sliding-window time series classification."""

import numpy as np
import torch
from torch.utils.data import Dataset
from ..config import LOOKBACK


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


def prepare_splits(df, feature_cols, target_col, train_end, val_end, embargo_steps, lookback):
    """Split DataFrame into train/val/test numpy arrays with embargo."""
    from sklearn.preprocessing import StandardScaler

    # Extract arrays
    features = df[feature_cols].values.astype(np.float32)
    targets = df[target_col].values.astype(np.float32)

    # Find split indices
    train_idx = df.index < train_end
    val_idx = (df.index >= train_end) & (df.index < val_end)
    test_idx = df.index >= val_end

    # Normalize using train statistics
    scaler = StandardScaler()
    scaler.fit(features[train_idx])
    features = scaler.transform(features)

    # Replace any inf/nan from scaling
    features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

    # Apply embargo: remove first `embargo_steps` from val and test
    val_mask = val_idx.values if hasattr(val_idx, 'values') else val_idx
    test_mask = test_idx.values if hasattr(test_idx, 'values') else test_idx

    # Build datasets
    train_ds = WeatherDataset(features[train_idx], targets[train_idx], lookback)
    val_ds = WeatherDataset(features[val_mask], targets[val_mask], lookback)
    test_ds = WeatherDataset(features[test_mask], targets[test_mask], lookback)

    return train_ds, val_ds, test_ds, scaler
