# backtest/walk_forward_engine.py
import json
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import timedelta

from utils.logger import setup_logger
from models.random_forest import RandomForestTradingModel
from models.xgboost_model import XGBoostTradingModel

logger = setup_logger("walk_forward_engine", log_file="walk_forward_engine.log")

# --------------------------
# Configuration (change here)
# --------------------------
TICKER = "SPY"
FEATURE_FILE = Path("data/processed/features_final_SPY.csv")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Walk-forward params
WINDOW_DAYS = 750            # training window size in days
RETRAIN_INTERVAL = WINDOW_DAYS  # force retrain after this many days if no regime change
PREDICTION_HORIZON = 1      # days ahead to predict
STEP_DAYS = 1               # move forward by 1 day each iteration

# Model choice: "rf" or "xgb"
MODEL_TYPE = "xgb"

# Strategy mode: "static" | "regime_specific" | "hybrid"
# static: single model used across all regimes
# regime_specific: maintain one model per regime value (combined HMM+CP label)
# hybrid: sliding window + retrain when regime changes (this engine does hybrid behavior regardless, but "regime_specific" trains separate models per regime segment within window)
STRATEGY_MODE = "hybrid"

# Transaction cost per trade (fraction). Example 0.0005 = 5 bps
TRANSACTION_COST = 0.0005

# Feature selection blacklist
REGIME_COLS = [f"{TICKER}_HMM_Regime", f"{TICKER}_CP_Regime"]
BLACKLIST = [f"{TICKER}_Target"] + REGIME_COLS

# Minimal samples required to train
MIN_TRAIN_SAMPLES = 50

# Seed for reproducibility
RANDOM_STATE = 42

# --------------------------
# Helper functions
# --------------------------
def load_features(filepath=FEATURE_FILE):
    if not filepath.exists():
        logger.error(f"Feature file not found: {filepath}")
        raise FileNotFoundError(filepath)
    df = pd.read_csv(filepath, parse_dates=["Date"])
    df = df.set_index("Date").sort_index()
    logger.info(f"Loaded features: {df.shape}")
    return df

def get_feature_columns(df, ticker=TICKER):
    cols = [c for c in df.columns if c.startswith(f"{ticker}_") and c not in BLACKLIST]
    logger.info(f"Detected {len(cols)} feature columns for {ticker}")
    return cols

def build_model(model_type=MODEL_TYPE):
    if model_type == "rf":
        return RandomForestTradingModel(n_estimators=200, max_depth=6, random_state=RANDOM_STATE)
    elif model_type == "xgb":
        return XGBoostTradingModel(n_estimators=200, max_depth=4, learning_rate=0.1, random_state=RANDOM_STATE)
    else:
        raise ValueError(f"Unknown model_type {model_type}")

def regime_signature(df_row):
    """
    Create a simple signature combining available regime indicators.
    This is used to decide if regime changed.
    """
    values = []
    for col in REGIME_COLS:
        if col in df_row.index:
            values.append(str(int(df_row[col])))
        else:
            values.append("NA")
    return "|".join(values)

# --------------------------
# Core walk-forward engine
# --------------------------
def walk_forward_backtest(
    df,
    ticker=TICKER,
    window_days=WINDOW_DAYS,
    retrain_interval=RETRAIN_INTERVAL,
    model_type=MODEL_TYPE,
    strategy_mode=STRATEGY_MODE,
    horizon=PREDICTION_HORIZON,
    transaction_cost=TRANSACTION_COST
):
    dates = df.index
    feature_cols = get_feature_columns(df, ticker)
    if len(feature_cols) == 0:
        raise ValueError("No feature columns detected")

    target_col = f"{ticker}_Target"
    ret_col = f"{ticker}_Return"

    if target_col not in df.columns:
        raise ValueError(f"Target column {target_col} missing")

    n = len(df)
    logger.info(f"Starting walk-forward. total samples: {n}")

    # results containers
    signals = []
    equity = []
    backtest_log = {
        "params": {
            "ticker": ticker,
            "window_days": window_days,
            "retrain_interval": retrain_interval,
            "model_type": model_type,
            "strategy_mode": strategy_mode,
            "horizon": horizon,
            "transaction_cost": transaction_cost
        },
        "runs": []
    }

    # index pointers
    start_idx = window_days
    last_retrain_idx = start_idx - 1  # last index used to train
    model = None
    regime_models = {}  # for regime_specific: map signature -> model

    # Starting position and equity
    cash_equity = 1.0
    prev_signal = 0

    # we'll iterate day by day
    i = start_idx
    while i + horizon - 1 < n:
        train_end_idx = i - 1  # we train on data up to day i-1 and predict for day i ... i+horizon-1
        train_start_idx = max(0, train_end_idx - window_days + 1)
        train_slice = df.iloc[train_start_idx: train_end_idx + 1]

        # if not enough data skip
        if len(train_slice) < MIN_TRAIN_SAMPLES:
            logger.warning(f"Skipping index {i}, not enough training samples: {len(train_slice)}")
            i += STEP_DAYS
            continue

        # detect regime change between previous day and current day
        regime_changed = False
        if train_end_idx >= 1:
            prev_row = df.iloc[train_end_idx - 1]
            cur_row = df.iloc[train_end_idx]
            if regime_signature(prev_row) != regime_signature(cur_row):
                regime_changed = True

        force_retrain = regime_changed or ((train_end_idx - last_retrain_idx) >= retrain_interval)

        # in regime_specific mode we may need a model per regime; determine current signature
        cur_sig = regime_signature(df.iloc[train_end_idx])

        retrained = False
        if strategy_mode == "regime_specific":
            # If model for this signature not present or retrain forced, (re)train one
            if (cur_sig not in regime_models) or force_retrain:
                X_train = train_slice[feature_cols].values
                y_train = train_slice[target_col].values
                if len(np.unique(y_train)) < 2:
                    logger.warning(f"Not enough classes in training slice for regime {cur_sig}. Skipping retrain.")
                else:
                    m = build_model(model_type)
                    m.fit(X_train, y_train)
                    regime_models[cur_sig] = m
                    last_retrain_idx = train_end_idx
                    retrained = True
                    logger.info(f"Trained new regime model for signature {cur_sig} at idx {train_end_idx}")
            model = regime_models.get(cur_sig)
        else:
            # static or hybrid or default
            if (model is None) or force_retrain:
                X_train = train_slice[feature_cols].values
                y_train = train_slice[target_col].values
                if len(np.unique(y_train)) < 2:
                    logger.warning(f"Not enough classes in training slice. Skipping retrain.")
                else:
                    model = build_model(model_type)
                    model.fit(X_train, y_train)
                    last_retrain_idx = train_end_idx
                    retrained = True
                    logger.info(f"Trained new global model at idx {train_end_idx}, retrain forced={force_retrain}, regime_changed={regime_changed}")

        # Predict for horizon days: use features available at prediction day(s)
        preds = []
        pred_probs = None
        predict_dates = []
        for h in range(horizon):
            pred_idx = i + h
            if pred_idx >= n:
                break
            row = df.iloc[pred_idx]
            x = row[feature_cols].values.reshape(1, -1)
            if model is None:
                sig = 0
            else:
                try:
                    sig = int(model.predict(x)[0])
                except Exception as e:
                    logger.error(f"Prediction error at idx {pred_idx}: {e}")
                    sig = 0
            preds.append(sig)
            predict_dates.append(df.index[pred_idx])

        # convert to single-day signal (we only use the first horizon entry for returns)
        signal = preds[0] if len(preds) > 0 else 0

        # compute pnl for day i (the day we predicted)
        next_ret_idx = i  # SPY_Return value at index i corresponds to return used after we predict at i
        if next_ret_idx < n:
            day_ret = df.iloc[next_ret_idx][ret_col]
        else:
            day_ret = 0.0

        # simple PnL: signal * day_return minus trades cost when signal changes
        trade_cost = transaction_cost * abs(signal - prev_signal)
        pnl = signal * day_ret - trade_cost

        cash_equity = cash_equity * (1.0 + pnl)

        # log step
        step_log = {
            "date": df.index[next_ret_idx].strftime("%Y-%m-%d"),
            "train_start": df.index[train_start_idx].strftime("%Y-%m-%d"),
            "train_end": df.index[train_end_idx].strftime("%Y-%m-%d"),
            "retrained": bool(retrained),
            "regime_changed": bool(regime_changed),
            "regime_signature": cur_sig,
            "signal": int(signal),
            "prev_signal": int(prev_signal),
            "day_return": float(day_ret),
            "trade_cost": float(trade_cost),
            "pnl": float(pnl),
            "equity": float(cash_equity),
            "model_used": model.get_name() if model is not None else None
        }
        backtest_log["runs"].append(step_log)

        # append to series
        signals.append({
            "Date": df.index[next_ret_idx],
            "Signal": int(signal),
            "DayReturn": float(day_ret),
            "TradeCost": float(trade_cost),
            "PnL": float(pnl),
            "Equity": float(cash_equity),
            "Regime": cur_sig
        })
        equity.append({"Date": df.index[next_ret_idx], "Equity": float(cash_equity)})

        prev_signal = signal
        i += STEP_DAYS

    # save results
    signals_df = pd.DataFrame(signals).set_index("Date")
    equity_df = pd.DataFrame(equity).set_index("Date")

    signals_out = RESULTS_DIR / f"signals_{ticker}.csv"
    equity_out = RESULTS_DIR / f"equity_curve_{ticker}.csv"
    log_out = RESULTS_DIR / f"backtest_log_{ticker}.json"

    signals_df.to_csv(signals_out, index=True)
    equity_df.to_csv(equity_out, index=True)
    with open(log_out, "w") as f:
        json.dump(backtest_log, f, indent=2)

    logger.info(f"Saved signals to {signals_out}")
    logger.info(f"Saved equity curve to {equity_out}")
    logger.info(f"Saved backtest log to {log_out}")

    return signals_df, equity_df, backtest_log

# --------------------------
# CLI runner
# --------------------------
if __name__ == "__main__":
    logger.info("===== WALK-FORWARD BACKTEST ENGINE STARTED =====")
    df = load_features(FEATURE_FILE)
    signals_df, equity_df, backtest_log = walk_forward_backtest(
        df,
        ticker=TICKER,
        window_days=WINDOW_DAYS,
        retrain_interval=RETRAIN_INTERVAL,
        model_type=MODEL_TYPE,
        strategy_mode=STRATEGY_MODE,
        horizon=PREDICTION_HORIZON,
        transaction_cost=TRANSACTION_COST
    )
    logger.info("===== WALK-FORWARD BACKTEST ENGINE FINISHED =====")
