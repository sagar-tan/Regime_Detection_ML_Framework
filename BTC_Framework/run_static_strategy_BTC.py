# BTC_Framework/run_static_strategy_BTC.py
# Walk-forward backtest for BTC-USD STATIC STRATEGY
# Modified from RDMA_ML_Framework/backtest/walk_forward_engine.py

import json
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import timedelta
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from models.random_forest import RandomForestTradingModel
from models.xgboost_model import XGBoostTradingModel

from strategies.static import StaticStrategy
from strategies.regime_specific import RegimeSpecificStrategy
from strategies.hybrid import HybridStrategy

from backtest.transaction_costs import TransactionCosts
from backtest.portfolio import Portfolio

logger = setup_logger("walk_forward_engine_static_BTC", log_file="walk_forward_engine_static_BTC.log")

# --------------------------
# Configuration
# --------------------------
TICKER = "BTC-USD"
FEATURE_FILE = Path("data/processed/features_final_BTC-USD.csv")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Walk-forward params
WINDOW_DAYS = 750
RETRAIN_INTERVAL = WINDOW_DAYS
PREDICTION_HORIZON = 1
STEP_DAYS = 1

# Model choice
MODEL_TYPE = "xgb"

# Strategy mode: STATIC
STRATEGY_MODE = "static"

# Transaction cost - crypto has higher spreads
TRANSACTION_COST = 0.001  # 10 basis points for crypto

# Feature selection
REGIME_COLS = [f"{TICKER}_HMM_Regime", f"{TICKER}_CP_Regime"]
BLACKLIST = [f"{TICKER}_Target"] + REGIME_COLS

# Minimal samples
MIN_TRAIN_SAMPLES = 50

# Seed
RANDOM_STATE = 42

# --------------------------
# Helper functions
# --------------------------
def load_features(filepath=FEATURE_FILE):
    if not filepath.exists():
        logger.error(f"Feature file not found: {filepath}")
        raise FileNotFoundError(filepath)
    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.set_index("date").sort_index()
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
    """Create regime signature from HMM and CP regimes."""
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

    if strategy_mode == "static":
        strategy = StaticStrategy()
    elif strategy_mode == "regime_specific":
        strategy = RegimeSpecificStrategy()
    elif strategy_mode == "hybrid":
        strategy = HybridStrategy()
    else:
        raise ValueError(f"Unknown strategy_mode {strategy_mode}")

    # Results containers
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

    # Index pointers
    start_idx = window_days
    last_retrain_idx = start_idx - 1
    model = None
    regime_models = {}

    prev_signal = 0

    tc = TransactionCosts(base_cost_rate=TRANSACTION_COST, slippage_per_trade=0.0000)
    portfolio = Portfolio(initial_equity=1.0, prev_signal=prev_signal)

    # Walk-forward loop
    i = start_idx
    while i + horizon - 1 < n:
        train_end_idx = i - 1
        train_start_idx = max(0, train_end_idx - window_days + 1)
        train_slice = df.iloc[train_start_idx: train_end_idx + 1]

        if len(train_slice) < MIN_TRAIN_SAMPLES:
            logger.warning(f"Skipping index {i}, not enough training samples: {len(train_slice)}")
            i += STEP_DAYS
            continue

        regime_changed = False
        if train_end_idx >= 1:
            prev_row = df.iloc[train_end_idx - 1]
            cur_row = df.iloc[train_end_idx]
            if regime_signature(prev_row) != regime_signature(cur_row):
                regime_changed = True

        steps_since_last_retrain = train_end_idx - last_retrain_idx
        force_retrain = strategy.should_retrain(
            regime_changed,
            steps_since_last_retrain,
            retrain_interval
        )

        cur_sig = regime_signature(df.iloc[train_end_idx])

        retrained = False
        if strategy_mode == "regime_specific":
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
            model = strategy.select_model(regime_models, cur_sig, model)
        else:
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

        # Predict
        preds = []
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

        signal = preds[0] if len(preds) > 0 else 0

        next_ret_idx = i
        if next_ret_idx < n:
            day_ret = df.iloc[next_ret_idx][ret_col]
        else:
            day_ret = 0.0

        trade_cost = tc.compute_trade_cost(prev_signal, signal, notional=portfolio.cash_equity)
        pnl, new_equity = portfolio.step(df.index[next_ret_idx], int(signal), float(day_ret), float(trade_cost))
        prev_signal = portfolio.prev_signal

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
            "equity": float(portfolio.cash_equity),
            "model_used": model.get_name() if model is not None else None
        }
        backtest_log["runs"].append(step_log)

        signals.append({
            "Date": df.index[next_ret_idx],
            "Signal": int(signal),
            "DayReturn": float(day_ret),
            "TradeCost": float(trade_cost),
            "PnL": float(pnl),
            "Equity": float(portfolio.cash_equity),
            "Regime": cur_sig
        })
        equity.append({"Date": df.index[next_ret_idx], "Equity": float(portfolio.cash_equity)})

        prev_signal = signal
        i += STEP_DAYS

    # Save results with STATIC suffix
    signals_df = pd.DataFrame(signals).set_index("Date")
    equity_df = pd.DataFrame(equity).set_index("Date")

    signals_out = RESULTS_DIR / f"signals_static_BTC.csv"
    equity_out = RESULTS_DIR / f"equity_curve_static_BTC.csv"
    log_out = RESULTS_DIR / f"backtest_log_static_BTC.json"

    signals_df.to_csv(signals_out, index=True)
    equity_df.to_csv(equity_out, index=True)
    with open(log_out, "w") as f:
        json.dump(backtest_log, f, indent=2)

    trades_out = RESULTS_DIR / f"trades_static_BTC.csv"
    portfolio.save_trades(trades_out)

    logger.info(f"Saved trades to {trades_out}")
    logger.info(f"Saved signals to {signals_out}")
    logger.info(f"Saved equity curve to {equity_out}")
    logger.info(f"Saved backtest log to {log_out}")

    return signals_df, equity_df, backtest_log

# --------------------------
# CLI runner
# --------------------------
if __name__ == "__main__":
    logger.info("===== WALK-FORWARD BACKTEST ENGINE (STATIC STRATEGY - BTC) STARTED =====")
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
    logger.info("===== WALK-FORWARD BACKTEST ENGINE (STATIC STRATEGY - BTC) FINISHED =====")
