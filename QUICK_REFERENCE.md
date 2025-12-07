# Quick Reference - Regime-Aware ML Trading Framework

**Document Version:** 1.0  
**Last Updated:** December 2025

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run full pipeline
python data/fetch_data.py
python features/feature_engineering.py
python regimes/hmm_detector.py
python regimes/changepoint_detector.py
python scripts/merge_regimes.py
python backtest/walk_forward_engine.py
python scripts/perfMet_Script.py

# 3. View results
# Check: results/signals_SPY.csv, results/equity_curve_SPY.csv
```

---

## 📁 Key Files

| File | Purpose | Input | Output |
|---|---|---|---|
| `data/fetch_data.py` | Download data | Tickers, dates | `data/raw/*.csv` |
| `features/feature_engineering.py` | Compute features | `data/raw/*.csv` | `data/processed/features_merged.csv` |
| `regimes/hmm_detector.py` | HMM regime detection | `features_merged.csv` | `features_with_hmm_SPY.csv` |
| `regimes/changepoint_detector.py` | Changepoint detection | `features_merged.csv` | `features_with_cp_SPY.csv` |
| `scripts/merge_regimes.py` | Merge regimes | HMM + CP files | `features_final_SPY.csv` |
| `backtest/walk_forward_engine.py` | Run backtest | `features_final_SPY.csv` | `signals_SPY.csv`, `equity_curve_SPY.csv` |
| `scripts/perfMet_Script.py` | Compute metrics | `signals_SPY.csv` | Metrics (printed) |
| `analysis/generate_all_plots.py` | Generate plots | Backtest outputs | `results/figures/*.png` |

---

## ⚙️ Configuration

### Backtest Parameters (`backtest/walk_forward_engine.py`)

```python
TICKER = "SPY"                    # Asset to backtest
WINDOW_DAYS = 750                 # Training window (days)
MODEL_TYPE = "xgb"                # "rf" or "xgb"
STRATEGY_MODE = "hybrid"          # "static", "regime_specific", or "hybrid"
TRANSACTION_COST = 0.0005         # 5 basis points per trade
```

### Regime Detection Parameters

**HMM (`regimes/hmm_detector.py`, line 75):**
```python
n_states=2              # Number of hidden states
```

**Changepoint (`regimes/changepoint_detector.py`, line 98):**
```python
penalty=10              # Higher = fewer breakpoints
```

---

## 📊 Data Shapes

| File | Rows | Columns | Notes |
|---|---|---|---|
| `data/raw/SPY.csv` | 3,774 | 5 | OHLCV data |
| `features_merged.csv` | 3,725 | 60 | 6 tickers × 10 features each |
| `features_final_SPY.csv` | 3,725 | 62 | + 2 regime columns |
| `signals_SPY.csv` | 2,975 | 7 | Backtest results |
| `equity_curve_SPY.csv` | 2,975 | 1 | Portfolio equity |

---

## 🎯 Key Concepts

### Regime Detection
- **HMM:** 2-state Gaussian Hidden Markov Model
- **Changepoint:** PELT algorithm for structural breaks
- **Combined:** Regime signature = "HMM|CP" (e.g., "1|0")

### Adaptation Strategies
- **Static:** Single model, interval retrain only
- **Regime-Specific:** Separate model per regime
- **Hybrid:** Global model, retrain on regime change

### Walk-Forward Backtest
- **Training Window:** 750 days (≈3 years)
- **Test Window:** 1 day (daily prediction)
- **Total Period:** 2,975 trading days (day 750 to 3724)

### Performance Metrics
- **Global:** Sharpe, Sortino, CVaR, Calmar, Max Drawdown
- **Per-Regime:** Metrics for each detected regime
- **Transitions:** Performance ±20 days around regime shifts

---

## 📈 Output Files

### signals_SPY.csv
```
Date, Signal, DayReturn, TradeCost, PnL, Equity, Regime
2013-01-02, 1, 0.0123, 0.0005, 0.0118, 1.0118, 0|0
2013-01-03, 1, 0.0050, 0.0000, 0.0050, 1.0168, 0|0
...
```

### equity_curve_SPY.csv
```
Date, Equity
2013-01-02, 1.0118
2013-01-03, 1.0168
...
```

### backtest_log_SPY.json
```json
{
  "params": {
    "ticker": "SPY",
    "window_days": 750,
    "model_type": "xgb",
    "strategy_mode": "hybrid",
    "transaction_cost": 0.0005
  },
  "runs": [
    {
      "date": "2013-01-02",
      "train_start": "2010-01-04",
      "train_end": "2012-12-31",
      "retrained": false,
      "regime_changed": false,
      "signal": 1,
      "day_return": 0.0123,
      "pnl": 0.0118,
      "equity": 1.0118
    },
    ...
  ]
}
```

---

## 🔧 Common Tasks

### Run Backtest with Different Strategy
```python
# Edit backtest/walk_forward_engine.py, line 44
STRATEGY_MODE = "static"  # or "regime_specific" or "hybrid"
python backtest/walk_forward_engine.py
```

### Run Backtest with Different Model
```python
# Edit backtest/walk_forward_engine.py, line 38
MODEL_TYPE = "rf"  # or "xgb"
python backtest/walk_forward_engine.py
```

### Adjust Transaction Costs
```python
# Edit backtest/walk_forward_engine.py, line 47
TRANSACTION_COST = 0.0010  # 10 basis points instead of 5
python backtest/walk_forward_engine.py
```

### Change Training Window
```python
# Edit backtest/walk_forward_engine.py, line 32
WINDOW_DAYS = 500  # Shorter window (≈2 years)
python backtest/walk_forward_engine.py
```

### Test Different Asset
```python
# Edit backtest/walk_forward_engine.py, line 26
TICKER = "QQQ"  # Test QQQ instead of SPY
# Also update FEATURE_FILE to point to correct processed file
python backtest/walk_forward_engine.py
```

---

## 📋 Module Overview

### Data Module (`data/`)
- **fetch_data.py:** Download OHLCV from Yahoo Finance
- **Input:** Tickers, date range
- **Output:** `data/raw/*.csv`

### Features Module (`features/`)
- **feature_engineering.py:** Compute trading features
- **Features:** Return, Vol20, SMA10, SMA50, Target
- **Output:** `data/processed/features_merged.csv`

### Regimes Module (`regimes/`)
- **hmm_detector.py:** 2-state Gaussian HMM
- **changepoint_detector.py:** PELT algorithm
- **Output:** Regime-labeled feature files

### Models Module (`models/`)
- **base_model.py:** Abstract interface
- **random_forest.py:** RandomForest classifier (200 trees, depth 6)
- **xgboost_model.py:** XGBoost classifier (200 trees, depth 4, lr=0.1)

### Strategies Module (`strategies/`)
- **static.py:** No regime adaptation
- **regime_specific.py:** Model per regime
- **hybrid.py:** Global model, retrain on regime change

### Backtest Module (`backtest/`)
- **walk_forward_engine.py:** Core backtesting logic
- **portfolio.py:** Portfolio state and PnL tracking
- **transaction_costs.py:** Cost computation

### Analysis Module (`analysis/`)
- **performance_metrics.py:** Metric computation
- **plot_*.py:** Visualization functions
- **generate_all_plots.py:** Batch plot generation

---

## 🐛 Debugging

### Check Logs
```bash
tail -f logs/walk_forward_engine.log      # Watch backtest execution
tail logs/feature_engineering.log         # Check feature computation
tail logs/xgboost_model.log              # Check model training
```

### Inspect Backtest Log
```python
import json
with open("results/backtest_log_SPY.json") as f:
    log = json.load(f)

# Check configuration
print(log["params"])

# Check first run
print(log["runs"][0])

# Count retrains
retrains = sum(1 for r in log["runs"] if r["retrained"])
print(f"Total retrains: {retrains}")

# Count regime changes
regime_changes = sum(1 for r in log["runs"] if r["regime_changed"])
print(f"Total regime changes: {regime_changes}")
```

### Analyze Results
```python
import pandas as pd

# Load results
signals = pd.read_csv("results/signals_SPY.csv", parse_dates=["Date"]).set_index("Date")
equity = pd.read_csv("results/equity_curve_SPY.csv", parse_dates=["Date"]).set_index("Date")

# Basic stats
print(f"Final Equity: {equity['Equity'].iloc[-1]:.4f}")
print(f"Total Return: {(equity['Equity'].iloc[-1] - 1) * 100:.2f}%")
print(f"Max Drawdown: {(equity['Equity'].min() / equity['Equity'].max() - 1) * 100:.2f}%")
print(f"Total Trades: {(signals['Signal'] != signals['Signal'].shift()).sum()}")
print(f"Win Rate: {(signals['PnL'] > 0).sum() / len(signals) * 100:.2f}%")
```

---

## 📚 Documentation Files

| File | Purpose |
|---|---|
| `Main_log_INDEX.md` | Documentation index |
| `PROJECT_OVERVIEW.md` | Project goals and architecture |
| `DIRECTORY_STRUCTURE.md` | File organization |
| `DEPENDENCIES.md` | Package requirements |
| `MODULE_*.md` | Detailed module documentation |
| `DATA_PIPELINE.md` | Data flow and processing |
| `EXECUTION_GUIDE.md` | Step-by-step execution |
| `RESULTS_OUTPUTS.md` | Output file descriptions |
| `LOG_ANALYSIS.md` | Log findings and insights |
| `EXTENSION_GUIDE.md` | Adding new components |
| `DESIGN_PATTERNS.md` | Architecture patterns |
| `QUICK_REFERENCE.md` | This file |

---

## ⚡ Performance

### Typical Execution Times
- Data fetching: ~10 seconds
- Feature engineering: ~5 seconds
- HMM detection: ~2 seconds
- Changepoint detection: ~2 seconds
- Merge regimes: <1 second
- Walk-forward backtest: ~5 seconds
- Metrics computation: ~2 seconds
- Plot generation: ~3 seconds
- **Total:** ~30 seconds

### Memory Usage
- Raw data: ~500 MB
- Processed features: ~50 MB
- Backtest outputs: ~100 MB
- **Total:** ~600 MB

### Optimization Tips
1. Reduce WINDOW_DAYS for faster backtesting
2. Use RandomForest instead of XGBoost (faster training)
3. Increase STEP_DAYS to skip days (e.g., test every 5 days)
4. Use smaller date range for testing

---

## 🎓 Learning Path

### For Beginners
1. Read `PROJECT_OVERVIEW.md` (understand goals)
2. Follow `EXECUTION_GUIDE.md` (run full pipeline)
3. Review `RESULTS_OUTPUTS.md` (interpret results)
4. Explore `QUICK_REFERENCE.md` (this file)

### For Developers
1. Study `DESIGN_PATTERNS.md` (architecture)
2. Review `DIRECTORY_STRUCTURE.md` (file organization)
3. Read relevant `MODULE_*.md` files
4. Follow `EXTENSION_GUIDE.md` (add features)

### For Researchers
1. Understand `PROJECT_OVERVIEW.md` (research questions)
2. Study `MODULE_REGIMES.md` (regime detection)
3. Review `MODULE_ANALYSIS.md` (metrics)
4. Analyze `LOG_ANALYSIS.md` (findings)

---

## 📞 Troubleshooting

| Issue | Solution |
|---|---|
| "FileNotFoundError" | Run previous steps in pipeline |
| "No feature columns detected" | Check TICKER matches column names |
| "Memory error" | Reduce WINDOW_DAYS or dataset size |
| "Slow execution" | Use RandomForest, reduce WINDOW_DAYS |
| "Unrealistic results" | Check transaction costs, verify regime detection |

---

## 🔗 Key Links

- **Project Root:** `c:\Users\tanwa\RDMA_ML_Framework\`
- **Data:** `data/raw/` and `data/processed/`
- **Results:** `results/`
- **Logs:** `logs/`
- **Documentation:** `*.md` files in root

---

## 💡 Tips & Tricks

### Quick Test
```bash
# Test with smaller dataset (faster)
# Edit backtest/walk_forward_engine.py:
WINDOW_DAYS = 250  # Smaller window
STEP_DAYS = 5      # Skip days
python backtest/walk_forward_engine.py
```

### Compare Strategies
```bash
# Run 3 times with different strategies
for strategy in "static" "regime_specific" "hybrid"; do
  sed -i "s/STRATEGY_MODE = .*/STRATEGY_MODE = \"$strategy\"/" backtest/walk_forward_engine.py
  python backtest/walk_forward_engine.py
  mv results/signals_SPY.csv results/signals_$strategy.csv
done
```

### Analyze Regime Transitions
```python
import pandas as pd
signals = pd.read_csv("results/signals_SPY.csv", parse_dates=["Date"]).set_index("Date")
transitions = signals[signals['Regime'] != signals['Regime'].shift()]
print(f"Regime transitions: {len(transitions)}")
print(f"Average days per regime: {len(signals) / len(transitions):.0f}")
```

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**Total Documentation:** 18 markdown files
