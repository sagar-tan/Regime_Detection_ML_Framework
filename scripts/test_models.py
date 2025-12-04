# scripts/test_models.py
import pandas as pd
import numpy as np
from pathlib import Path

from models.random_forest import RandomForestTradingModel
from models.xgboost_model import XGBoostTradingModel

def load_sample_features(path="data/processed/features_merged.csv", ticker="SPY"):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(p, parse_dates=["Date"]).set_index("Date")
    # pick a narrow window to test quickly
    df = df.dropna().iloc[:100]
    # build X from a few features that exist in your file
    feat_cols = [c for c in df.columns if c.startswith(f"{ticker}_") and c not in [f"{ticker}_Target", f"{ticker}_HMM_Regime", f"{ticker}_CP_Regime"]]
    X = df[feat_cols].values
    y = df[f"{ticker}_Target"].values
    return X, y

def main():
    X, y = load_sample_features()
    # simple train/test split
    split = int(0.7 * len(X))
    X_tr, X_te = X[:split], X[split:]
    y_tr, y_te = y[:split], y[split:]

    rf = RandomForestTradingModel(n_estimators=50, max_depth=5)
    rf.fit(X_tr, y_tr)
    preds_rf = rf.predict(X_te)
    print("RF test acc:", (preds_rf == y_te).mean())

    xgb = XGBoostTradingModel(n_estimators=50, max_depth=3, learning_rate=0.1)
    xgb.fit(X_tr, y_tr)
    preds_xgb = xgb.predict(X_te)
    print("XGB test acc:", (preds_xgb == y_te).mean())

if __name__ == "__main__":
    main()
