import pandas as pd
import numpy as np
from pathlib import Path

from utils.logger import setup_logger
from models.random_forest import RandomForestTradingModel
from models.xgboost_model import XGBoostTradingModel

logger = setup_logger("test_models", log_file="test_models.log")


def load_sample_features(path="data/processed/features_with.csv", ticker="SPY"):
    logger.info(f"Loading features for testing from {path}")

    p = Path(path)
    if not p.exists():
        logger.error(f"Feature file not found: {path}")
        raise FileNotFoundError(path)

    df = pd.read_csv(p, parse_dates=["Date"]).set_index("Date")

    # Sanitise the dataset
    df = df.dropna()
    logger.info(f"Loaded dataframe with shape {df.shape}")

    # Build feature set
    feat_cols = [
        c for c in df.columns 
        if c.startswith(f"{ticker}_") 
        and c not in [f"{ticker}_Target", f"{ticker}_HMM_Regime", f"{ticker}_CP_Regime"]
    ]

    if len(feat_cols) == 0:
        logger.error(f"No feature columns found for {ticker}. Columns present: {list(df.columns)}")
        raise ValueError(f"No usable features for {ticker}")

    logger.info(f"Using {len(feat_cols)} features: {feat_cols}")

    X = df[feat_cols].values
    y = df[f"{ticker}_Target"].values

    logger.info(f"Feature matrix shape: {X.shape}, Target shape: {y.shape}")

    return X, y


def main():
    logger.info("===== TEST MODELS SCRIPT STARTED =====")

    try:
        X, y = load_sample_features()
    except Exception as e:
        logger.error(f"Feature load failed: {e}")
        raise

    # Train-test split
    split = int(0.7 * len(X))
    X_tr, X_te = X[:split], X[split:]
    y_tr, y_te = y[:split], y[split:]

    logger.info(f"Train size: {len(X_tr)}, Test size: {len(X_te)}")

    # -------------------------
    # RandomForest Test
    # -------------------------
    logger.info("Testing RandomForestTradingModel")

    rf = RandomForestTradingModel(n_estimators=50, max_depth=5)
    rf.fit(X_tr, y_tr)
    preds_rf = rf.predict(X_te)

    acc_rf = (preds_rf == y_te).mean()
    logger.info(f"RandomForest accuracy: {acc_rf:.4f}")
    print("RF test acc:", acc_rf)

    # -------------------------
    # XGBoost Test
    # -------------------------
    logger.info("Testing XGBoostTradingModel")

    xgb = XGBoostTradingModel(n_estimators=50, max_depth=3, learning_rate=0.1)
    xgb.fit(X_tr, y_tr)
    preds_xgb = xgb.predict(X_te)

    acc_xgb = (preds_xgb == y_te).mean()
    logger.info(f"XGBoost accuracy: {acc_xgb:.4f}")
    print("XGB test acc:", acc_xgb)

    logger.info("===== TEST MODELS SCRIPT COMPLETED =====")


if __name__ == "__main__":
    main()
