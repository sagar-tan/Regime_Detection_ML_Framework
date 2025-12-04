import numpy as np
import pandas as pd
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("metrics", log_file="performance_metrics.log")


# ================================
# ---- BASIC METRIC FUNCTIONS ----
# ================================

def cumulative_return(equity_series):
    return equity_series.iloc[-1] - 1.0


def annualized_return(equity_series):
    days = len(equity_series)
    if days == 0:
        return 0.0
    total_return = equity_series.iloc[-1]
    return (total_return ** (252 / days)) - 1


def annualized_volatility(returns):
    return np.sqrt(252) * np.std(returns)


def sharpe_ratio(returns, risk_free=0.0):
    vol = annualized_volatility(returns)
    if vol == 0:
        return 0.0
    ann_ret = (1 + returns.mean()) ** 252 - 1
    return (ann_ret - risk_free) / vol


def sortino_ratio(returns, risk_free=0.0):
    downside = returns[returns < 0]
    if len(downside) == 0:
        return 0.0
    downside_vol = np.sqrt(252) * np.std(downside)
    if downside_vol == 0:
        return 0.0
    ann_ret = (1 + returns.mean()) ** 252 - 1
    return (ann_ret - risk_free) / downside_vol


def max_drawdown(equity):
    roll_max = equity.cummax()
    dd = (equity - roll_max) / roll_max
    return dd.min()


def calmar_ratio(equity):
    mdd = abs(max_drawdown(equity))
    if mdd == 0:
        return 0.0
    ann_ret = annualized_return(equity)
    return ann_ret / mdd


def cvar(returns, alpha=0.05):
    if len(returns) == 0:
        return 0.0
    cutoff = np.quantile(returns, alpha)
    return returns[returns <= cutoff].mean()


def hit_ratio(signals, returns):
    preds = signals.shift(1).dropna()  # compare prev-day signal to next-day return
    aligned_returns = returns.loc[preds.index]
    correct = (preds * aligned_returns > 0).sum()
    return correct / len(preds)


# ======================================
# ----- PER-REGIME PERFORMANCE ---------
# ======================================

def regime_performance(df_signals):
    """
    df_signals must contain:
        Signal
        DayReturn
        Equity
        Regime (string like "1|0")
    """
    regimes = df_signals["Regime"].unique()
    output = {}

    for reg in regimes:
        subset = df_signals[df_signals["Regime"] == reg]
        if len(subset) < 5:
            continue

        ret = subset["DayReturn"]
        equity = subset["Equity"]

        output[reg] = {
            "days": len(subset),
            "avg_return": float(ret.mean()),
            "sharpe": float(sharpe_ratio(ret)),
            "max_dd": float(max_drawdown(equity)),
            "calmar": float(calmar_ratio(equity)),
        }

    return output


# =====================================================
# ----- REGIME TRANSITION METRICS (NOVEL FEATURE) -----
# =====================================================

def transition_metrics(df):
    """
    Input df must contain:
        Date, DayReturn, Equity, Regime
    Computes performance 20 days before and after every regime shift.
    """
    df = df.copy()
    df["RegimePrev"] = df["Regime"].shift(1)

    transition_points = df[df["Regime"] != df["RegimePrev"]].index

    before_after_results = []

    for date in transition_points:
        idx = df.index.get_loc(date)

        before_start = max(0, idx - 20)
        after_end = min(len(df)-1, idx + 20)

        before = df.iloc[before_start:idx]
        after = df.iloc[idx:after_end]

        if len(before) >= 3 and len(after) >= 3:
            before_after_results.append({
                "transition_date": str(date),
                "from_regime": df.iloc[idx-1]["Regime"],
                "to_regime": df.iloc[idx]["Regime"],
                "before_avg_ret": float(before["DayReturn"].mean()),
                "after_avg_ret": float(after["DayReturn"].mean()),
                "before_dd": float(max_drawdown(before["Equity"])),
                "after_dd": float(max_drawdown(after["Equity"])),
            })

    return before_after_results


# ===========================
# ----- MAIN METRIC API -----
# ===========================

def compute_all_metrics(signals_path, equity_path):
    logger.info("Loading signals & equity files...")
    
    df_sig = pd.read_csv(signals_path, parse_dates=["Date"]).set_index("Date")
    df_eq = pd.read_csv(equity_path, parse_dates=["Date"]).set_index("Date")

    returns = df_sig["DayReturn"]
    equity = df_sig["Equity"]
    signals = df_sig["Signal"]

    logger.info("Computing core metrics...")
    metrics = {
        "cumulative_return": float(cumulative_return(equity)),
        "annualized_return": float(annualized_return(equity)),
        "annualized_volatility": float(annualized_volatility(returns)),
        "sharpe_ratio": float(sharpe_ratio(returns)),
        "sortino_ratio": float(sortino_ratio(returns)),
        "max_drawdown": float(max_drawdown(equity)),
        "calmar_ratio": float(calmar_ratio(equity)),
        "hit_ratio": float(hit_ratio(signals, returns)),
        "cvar_5": float(cvar(returns)),
    }

    logger.info("Computing per-regime metrics...")
    metrics["regime_performance"] = regime_performance(df_sig)

    logger.info("Computing transition metrics...")
    metrics["transition_metrics"] = transition_metrics(df_sig)

    logger.info("Metrics computation complete.")
    return metrics
