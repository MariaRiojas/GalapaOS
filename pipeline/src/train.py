"""Training loop with early stopping and checkpointing."""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np

from .config import BATCH_SIZE, LR, PATIENCE, MAX_EPOCHS, CHECKPOINTS


def train_model(model, train_ds, val_ds, target_name, rnn_type="lstm", device="cpu"):
    """Train a RecurrentClassifier with early stopping."""
    model = model.to(device)

    # Handle class imbalance
    train_labels = np.array([train_ds[i][1].item() for i in range(len(train_ds))])
    pos_count = train_labels.sum()
    neg_count = len(train_labels) - pos_count
    pos_weight = torch.tensor([neg_count / max(pos_count, 1)], device=device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5
    )

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

    best_val_loss = float("inf")
    patience_counter = 0
    best_state = None

    print(f"\n  Training {rnn_type.upper()} for {target_name}")
    print(f"    Train: {len(train_ds)}, pos_rate: {pos_count/len(train_ds):.4f}")

    for epoch in range(MAX_EPOCHS):
        model.train()
        train_loss = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item()
        train_loss /= len(train_loader)

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                logits = model(x)
                loss = criterion(logits, y)
                val_loss += loss.item()
        val_loss /= max(len(val_loader), 1)

        scheduler.step(val_loss)

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"    Epoch {epoch+1:3d} | train: {train_loss:.4f} | val: {val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"    Early stopping at epoch {epoch+1}")
                break

    if best_state:
        model.load_state_dict(best_state)
    ckpt_path = CHECKPOINTS / f"{rnn_type}_{target_name}.pt"
    torch.save(model.state_dict(), ckpt_path)
    print(f"    Saved: {ckpt_path.name}")

    return model
