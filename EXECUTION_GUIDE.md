# Execution Guide - Running the Framework

**Document Version:** 1.0  
**Last Updated:** December 2025

---

## Prerequisites

### System Requirements
- Python 3.8+
- 2GB+ RAM
- Internet connection (for Yahoo Finance data)
- ~600 MB disk space (for full project with outputs)

### Installation

```bash
# Clone or navigate to project directory
cd RDMA_ML_Framework

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation
```bash
python -c "import pandas, numpy, sklearn, xgboost, ruptures, hmmlearn; print('All dependencies installed!')"
```

---

## Typical Workflow

### Step 1: Download Data
```bash
python data/fetch_data.py
```

**What it does:**
- Downloads OHLCV data for 6 tickers (SPY, QQQ, IWM, XLF, GLD, TLT)
- Date range: 2010-01-01 to 2025-01-01
- Saves to `data/raw/{ticker}.csv`

**Output:**
- 6 CSV files, ~500 MB total
- Each: 3774 rows × 5 columns (Open, High, Low, Close, Volume)

**Time:** ~10 seconds

**Log:** `logs/fetch_data.log`

---

### Step 2: Engineer Features
```bash
python features/feature_engineering.py
```

**What it does:**
- Loads all raw CSV files
- Aligns by date (multi-ticker merge)
- Computes features per ticker:
  - Return: Daily percentage change
  - Vol20: 20-day rolling volatility
  - SMA10: 10-day simple moving average
  - SMA50: 50-day simple moving average
  - Target: Binary label (1 if return > 0, else 0)
- Drops rows with NaN (rolling window initialization)

**Output:**
- `data/processed/features_merged.csv`
- Shape: 3725 rows × 60 columns
- Size: ~50 MB

**Time:** ~5 seconds

**Log:** `logs/feature_engineering.log`

---

### Step 3: Detect Regimes (HMM)
```bash
python regimes/hmm_detector.py
```

**What it does:**
- Loads processed features
- Fits 2-state Gaussian HMM on SPY returns
- Predicts hidden states (0 or 1)
- Saves regime labels

**Output:**
- `data/processed/features_with_hmm_SPY.csv`
- New column: `SPY_HMM_Regime` (values: 0 or 1)

**Time:** ~2 seconds

**Log:** `logs/hmm_detector.log`

**Configuration (line 75):**
```python
n_states=2              # Number of HMM states
covariance_type="full" # Covariance type
n_iter=200            # Iterations for convergence
```

---

### Step 4: Detect Regimes (Changepoint)
```bash
python regimes/changepoint_detector.py
```

**What it does:**
- Loads processed features
- Detects structural breaks using PELT algorithm
- Converts breakpoints to regime labels
- Saves regime labels

**Output:**
- `data/processed/features_with_cp_SPY.csv`
- New column: `SPY_CP_Regime` (values: 0, 1, 2, ...)

**Time:** ~2 seconds

**Log:** `logs/changepoint_detector.log`

**Configuration (line 98):**
```python
model="rbf"     # Kernel type
penalty=10      # Penalty for adding breakpoints (higher = fewer breaks)
```

---

### Step 5: Merge Regimes
```bash
python scripts/merge_regimes.py
```

**What it does:**
- Loads base features
- Loads HMM regime labels
- Loads Changepoint regime labels
- Merges all into single file

**Output:**
- `data/processed/features_final_SPY.csv`
- Shape: 3725 rows × 62 columns
- Columns: All base features + `SPY_HMM_Regime` + `SPY_CP_Regime`

**Time:** <1 second

**Note:** This is the input file for backtesting

---

### Step 6: Run Walk-Forward Backtest
```bash
python backtest/walk_forward_engine.py
```

**What it does:**
- Loads final features with regimes
- Runs rolling window backtest:
  - Training window: 750 days (≈3 years)
  - Test window: 1 day (daily prediction)
  - Step size: 1 day forward
  - Total: 2,975 trading days
- Detects regime changes
- Trains/selects models based on strategy
- Applies transaction costs
- Tracks portfolio equity and trades

**Output:**
- `results/signals_SPY.csv` (2975 rows × 7 cols)
- `results/equity_curve_SPY.csv` (2975 rows × 1 col)
- `results/trades_SPY.csv` (trade log)
- `results/backtest_log_SPY.json` (detailed step log, ~50 MB)

**Time:** ~5 seconds

**Log:** `logs/walk_forward_engine.log`

**Configuration (lines 24-57):**
```python
TICKER = "SPY"
WINDOW_DAYS = 750
MODEL_TYPE = "xgb"              # "rf" or "xgb"
STRATEGY_MODE = "hybrid"        # "static", "regime_specific", or "hybrid"
TRANSACTION_COST = 0.0005       # 5 basis points
```

---

### Step 7: Compute Performance Metrics
```bash
python scripts/perfMet_Script.py
```

**What it does:**
- Loads signals and equity from backtest
- Computes global metrics:
  - Sharpe ratio, Sortino ratio, CVaR, Calmar ratio, etc.
- Computes per-regime metrics
- Analyzes regime transitions (±20 days)
- Prints results to console

**Output:**
- Printed to console (can redirect to file)
- Metrics dictionary structure:
  ```python
  {
      "cumulative_return": float,
      "annualized_return": float,
      "sharpe_ratio": float,
      "sortino_ratio": float,
      "max_drawdown": float,
      "regime_performance": {...},
      "transition_metrics": [...]
  }
  ```

**Time:** ~2 seconds

**Log:** `logs/performance_metrics.log`

---

### Step 8: Generate Visualizations
```bash
python analysis/generate_all_plots.py
```

**What it does:**
- Generates 3 plots:
  1. Equity curve (model vs buy-and-hold)
  2. Regime timeline (price with HMM regimes)
  3. Transition windows (returns around regime shifts)

**Output:**
- `results/figures/equity_curve_SPY.png`
- `results/figures/hmm_timeline_SPY.png`
- `results/figures/transition_window_SPY.png`

**Time:** ~3 seconds

**Note:** Requires `results/figures/` directory to exist

---

## Complete Workflow Script

```bash
#!/bin/bash
# Run entire pipeline

echo "Step 1: Fetching data..."
python data/fetch_data.py

echo "Step 2: Engineering features..."
python features/feature_engineering.py

echo "Step 3: Detecting regimes (HMM)..."
python regimes/hmm_detector.py

echo "Step 4: Detecting regimes (Changepoint)..."
python regimes/changepoint_detector.py

echo "Step 5: Merging regimes..."
python scripts/merge_regimes.py

echo "Step 6: Running backtest..."
python backtest/walk_forward_engine.py

echo "Step 7: Computing metrics..."
python scripts/perfMet_Script.py

echo "Step 8: Generating plots..."
python analysis/generate_all_plots.py

echo "Done! Results in results/ directory"
```

**Total Time:** ~30 seconds

---

## Configuration Points

### 1. Data Fetching (`data/fetch_data.py`)

**Line 61-63:**
```python
TICKERS = ["SPY", "QQQ", "IWM", "XLF", "GLD", "TLT"]
START = "2010-01-01"
END = "2025-01-01"
```

**To change:**
- Modify `TICKERS` list to add/remove assets
- Adjust `START` and `END` dates

---

### 2. Regime Detection

**HMM (`regimes/hmm_detector.py`, line 75):**
```python
model = fit_hmm(series, n_states=2)
```

**To change:**
- `n_states`: Number of hidden states (default: 2)
- `covariance_type`: "full", "diag", "spherical", "tied"

**Changepoint (`regimes/changepoint_detector.py`, line 98):**
```python
breakpoints = detect_changepoints(series, model="rbf", penalty=10)
```

**To change:**
- `model`: Kernel type ("rbf", "l2", "linear", "cosine")
- `penalty`: Higher = fewer breakpoints (default: 10)

---

### 3. Walk-Forward Backtest (`backtest/walk_forward_engine.py`, lines 24-57)

**Key Parameters:**

| Parameter | Default | Description |
|---|---|---|
| `TICKER` | "SPY" | Asset to backtest |
| `WINDOW_DAYS` | 750 | Training window (days) |
| `RETRAIN_INTERVAL` | 750 | Force retrain interval |
| `MODEL_TYPE` | "xgb" | "rf" or "xgb" |
| `STRATEGY_MODE` | "hybrid" | "static", "regime_specific", or "hybrid" |
| `TRANSACTION_COST` | 0.0005 | Cost per trade (5 bps) |
| `MIN_TRAIN_SAMPLES` | 50 | Minimum training samples |

**To change:**
```python
# Example: Test RandomForest with Static strategy
MODEL_TYPE = "rf"
STRATEGY_MODE = "static"
TRANSACTION_COST = 0.0010  # 10 bps

# Example: Longer training window
WINDOW_DAYS = 1000  # ≈4 years
```

---

### 4. Model Hyperparameters

**RandomForest (`models/random_forest.py`, line 11):**
```python
def __init__(self, n_estimators=200, max_depth=6, random_state=42)
```

**XGBoost (`models/xgboost_model.py`, line 11):**
```python
def __init__(self, n_estimators=200, max_depth=4, learning_rate=0.1, random_state=42)
```

**To change:**
- Edit default parameters in `__init__()` method
- Or pass parameters when instantiating in `walk_forward_engine.py`

---

## Comparing Strategies

Run backtest 3 times with different strategies:

```bash
# Static strategy
sed -i 's/STRATEGY_MODE = .*/STRATEGY_MODE = "static"/' backtest/walk_forward_engine.py
python backtest/walk_forward_engine.py
mv results/signals_SPY.csv results/signals_static.csv
mv results/equity_curve_SPY.csv results/equity_static.csv

# Regime-specific strategy
sed -i 's/STRATEGY_MODE = .*/STRATEGY_MODE = "regime_specific"/' backtest/walk_forward_engine.py
python backtest/walk_forward_engine.py
mv results/signals_SPY.csv results/signals_regime_specific.csv
mv results/equity_curve_SPY.csv results/equity_regime_specific.csv

# Hybrid strategy
sed -i 's/STRATEGY_MODE = .*/STRATEGY_MODE = "hybrid"/' backtest/walk_forward_engine.py
python backtest/walk_forward_engine.py
# Keep as is (signals_SPY.csv, equity_curve_SPY.csv)
```

Then compare results:
```python
import pandas as pd

static = pd.read_csv("results/equity_static.csv", parse_dates=["Date"]).set_index("Date")
regime_spec = pd.read_csv("results/equity_regime_specific.csv", parse_dates=["Date"]).set_index("Date")
hybrid = pd.read_csv("results/equity_hybrid.csv", parse_dates=["Date"]).set_index("Date")

# Compare final returns
print("Static return:", (static["Equity"].iloc[-1] - 1) * 100)
print("Regime-Specific return:", (regime_spec["Equity"].iloc[-1] - 1) * 100)
print("Hybrid return:", (hybrid["Equity"].iloc[-1] - 1) * 100)
```

---

## Comparing Models

Run backtest with both models:

```bash
# RandomForest
sed -i 's/MODEL_TYPE = .*/MODEL_TYPE = "rf"/' backtest/walk_forward_engine.py
python backtest/walk_forward_engine.py
mv results/signals_SPY.csv results/signals_rf.csv

# XGBoost
sed -i 's/MODEL_TYPE = .*/MODEL_TYPE = "xgb"/' backtest/walk_forward_engine.py
python backtest/walk_forward_engine.py
# Keep as is (signals_SPY.csv)
```

---

## Troubleshooting

### Error: "FileNotFoundError: data/processed/features_merged.csv"
**Solution:** Run `python features/feature_engineering.py` first

### Error: "Missing column 'Date'"
**Solution:** This was fixed in feature_engineering.py. Re-run the script.

### Error: "No feature columns detected"
**Solution:** Check that features_final_SPY.csv has correct columns. Verify TICKER variable matches column names.

### Backtest runs very slowly
**Solution:**
- Reduce WINDOW_DAYS (e.g., 500 instead of 750)
- Reduce dataset size (e.g., use only 2010-2020 data)
- Use RandomForest instead of XGBoost (faster training)

### Results look unrealistic
**Solution:**
- Check transaction costs (TRANSACTION_COST parameter)
- Verify regime detection is working (check logs)
- Check if model is retraining (look for "retrained=True" in logs)

### Out of memory error
**Solution:**
- Reduce WINDOW_DAYS
- Close other applications
- Use smaller dataset (fewer tickers or shorter date range)

---

## Performance Tips

### Speed Up Backtesting
1. **Reduce training window:** WINDOW_DAYS = 500 (instead of 750)
2. **Use RandomForest:** MODEL_TYPE = "rf" (faster than XGBoost)
3. **Increase step size:** STEP_DAYS = 5 (test every 5 days instead of daily)

### Reduce Memory Usage
1. **Reduce dataset:** Use fewer tickers or shorter date range
2. **Reduce window:** Smaller WINDOW_DAYS
3. **Reduce features:** Remove unnecessary features from feature_engineering.py

### Improve Results
1. **Tune transaction costs:** Adjust TRANSACTION_COST to match real costs
2. **Optimize regime detection:** Adjust HMM n_states or CP penalty
3. **Tune model hyperparameters:** Adjust n_estimators, max_depth, learning_rate
4. **Longer training window:** Increase WINDOW_DAYS for more stable models

---

## Output Interpretation

### signals_SPY.csv
- **Signal:** Predicted direction (0=down, 1=up)
- **DayReturn:** Actual daily return of SPY
- **TradeCost:** Transaction cost incurred
- **PnL:** Daily profit/loss
- **Equity:** Portfolio equity after PnL
- **Regime:** Regime signature (e.g., "1|0" = HMM=1, CP=0)

### equity_curve_SPY.csv
- **Equity:** Portfolio value over time
- Use for plotting equity curve and computing returns-based metrics

### backtest_log_SPY.json
- **params:** Backtest configuration
- **runs:** Array of daily step logs
  - Each run contains: date, train_start, train_end, retrained, regime_changed, signal, day_return, pnl, equity, etc.
- Use for detailed debugging and analysis

---

## Next Steps

After running the framework:

1. **Analyze Results:** Review `results/signals_SPY.csv` and plots
2. **Compute Metrics:** Run `python scripts/perfMet_Script.py` for detailed metrics
3. **Compare Strategies:** Run backtest with different STRATEGY_MODE values
4. **Tune Parameters:** Adjust configuration and re-run
5. **Extend Framework:** Add new models, strategies, or regime detectors (see EXTENSION_GUIDE.md)

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025
