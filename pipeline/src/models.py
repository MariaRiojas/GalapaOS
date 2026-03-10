"""RecurrentClassifier (RNN/LSTM/GRU) and XGBoost wrapper."""

import numpy as np
import torch
import torch.nn as nn


class RecurrentClassifier(nn.Module):
    """Flexible RNN/LSTM/GRU binary classifier."""

    def __init__(self, input_dim, hidden_dim=128, num_layers=2,
                 dropout=0.3, rnn_type="lstm"):
        super().__init__()
        rnn_cls = {"rnn": nn.RNN, "lstm": nn.LSTM, "gru": nn.GRU}[rnn_type]
        self.rnn = rnn_cls(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
        )
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x):
        output, _ = self.rnn(x)
        return self.classifier(output[:, -1, :]).squeeze(-1)


class XGBoostClassifierWrapper:
    """Wrapper for XGBoost that flattens the lookback window."""

    def __init__(self, **kwargs):
        import xgboost as xgb
        self.model = xgb.XGBClassifier(
            n_estimators=kwargs.get("n_estimators", 300),
            max_depth=kwargs.get("max_depth", 6),
            learning_rate=kwargs.get("learning_rate", 0.05),
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=kwargs.get("scale_pos_weight", 10),
            eval_metric="aucpr",
            random_state=42,
        )

    def fit(self, train_ds, val_ds):
        """Fit on flattened sliding-window data."""
        X_train, y_train = self._flatten(train_ds)
        X_val, y_val = self._flatten(val_ds)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )
        return self

    def predict_proba(self, ds):
        X, _ = self._flatten(ds)
        return self.model.predict_proba(X)[:, 1]

    def feature_importances(self):
        return self.model.feature_importances_

    def save(self, path):
        self.model.save_model(str(path))

    def load(self, path):
        self.model.load_model(str(path))
        return self

    @staticmethod
    def _flatten(ds):
        """Flatten (N, T, F) -> (N, T*F)."""
        xs, ys = [], []
        for i in range(len(ds)):
            x, y = ds[i]
            xs.append(x.numpy().flatten())
            ys.append(y.item())
        return np.array(xs), np.array(ys)
