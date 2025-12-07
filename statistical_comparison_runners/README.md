# Statistical Comparison Runners

**Purpose:** Generate strategy-specific backtest results for statistical significance comparison

**Status:** ✅ Ready to use

---

## Overview

This folder contains 3 modified copies of `walk_forward_engine.py`, each configured to run a specific strategy and generate the required CSV files for statistical comparison.

### Files

1. **run_static_strategy.py** - Generates `signals_static.csv`
2. **run_regime_specific_strategy.py** - Generates `signals_regime_specific.csv`
3. **run_hybrid_strategy.py** - Generates `signals_hybrid.csv`

---

## Quick Start

### Step 1: Run Static Strategy
```bash
python statistical_comparison_runners/run_static_strategy.py
```

**Output:**
- `results/signals_static.csv`
- `results/equity_curve_static.csv`
- `results/backtest_log_static.json`
- `results/trades_static.csv`

### Step 2: Run Regime-Specific Strategy
```bash
python statistical_comparison_runners/run_regime_specific_strategy.py
```

**Output:**
- `results/signals_regime_specific.csv`
- `results/equity_curve_regime_specific.csv`
- `results/backtest_log_regime_specific.json`
- `results/trades_regime_specific.csv`

### Step 3: Run Hybrid Strategy
```bash
python statistical_comparison_runners/run_hybrid_strategy.py
```

**Output:**
- `results/signals_hybrid.csv`
- `results/equity_curve_hybrid.csv`
- `results/backtest_log_hybrid.json`
- `results/trades_hybrid.csv`

### Step 4: Generate Buy-and-Hold Baseline (Optional)
```bash
python scripts/buy_and_hold_baseline.py
```

**Output:**
- `results/signals_bah.csv`

### Step 5: Run Statistical Comparison
```bash
python scripts/statistical_comparison.py
```

**Output:**
- `results/statistical_comparison.json`
- `results/strategy_summary.csv`
- `results/statistical_report.txt`

---

## What Changed from Original

Each script is a modified copy of `backtest/walk_forward_engine.py` with the following changes:

### 1. run_static_strategy.py
```python
# Line 44: Strategy mode set to STATIC
STRATEGY_MODE = "static"

# Lines 298-300: Output files use "static" suffix
signals_out = RESULTS_DIR / f"signals_static.csv"
equity_out = RESULTS_DIR / f"equity_curve_static.csv"
log_out = RESULTS_DIR / f"backtest_log_static.json"
```

### 2. run_regime_specific_strategy.py
```python
# Line 44: Strategy mode set to REGIME-SPECIFIC
STRATEGY_MODE = "regime_specific"

# Lines 298-300: Output files use "regime_specific" suffix
signals_out = RESULTS_DIR / f"signals_regime_specific.csv"
equity_out = RESULTS_DIR / f"equity_curve_regime_specific.csv"
log_out = RESULTS_DIR / f"backtest_log_regime_specific.json"
```

### 3. run_hybrid_strategy.py
```python
# Line 44: Strategy mode set to HYBRID
STRATEGY_MODE = "hybrid"

# Lines 298-300: Output files use "hybrid" suffix
signals_out = RESULTS_DIR / f"signals_hybrid.csv"
equity_out = RESULTS_DIR / f"equity_curve_hybrid.csv"
log_out = RESULTS_DIR / f"backtest_log_hybrid.json"
```

---

## Configuration

All three scripts share the same configuration parameters:

```python
TICKER = "SPY"
FEATURE_FILE = Path("data/processed/features_final_SPY.csv")
RESULTS_DIR = Path("results")

# Walk-forward params
WINDOW_DAYS = 750
RETRAIN_INTERVAL = WINDOW_DAYS
PREDICTION_HORIZON = 1
STEP_DAYS = 1

# Model choice: "rf" or "xgb"
MODEL_TYPE = "xgb"

# Transaction cost per trade (fraction)
TRANSACTION_COST = 0.0005
```

### Customization

To change any parameter, edit the script directly. For example:

**Change model type:**
```python
MODEL_TYPE = "rf"  # Use RandomForest instead of XGBoost
```

**Change transaction costs:**
```python
TRANSACTION_COST = 0.001  # 10 basis points instead of 5
```

**Change training window:**
```python
WINDOW_DAYS = 500  # Shorter window (≈2 years)
```

---

## Output Files

### Signals CSV
Each script generates a signals CSV with the following columns:

```
Date, Signal, DayReturn, TradeCost, PnL, Equity, Regime
2013-01-02, 1, 0.0123, 0.0005, 0.0118, 1.0118, 0|0
2013-01-03, 1, 0.0050, 0.0000, 0.0050, 1.0168, 0|0
...
```

### Equity Curve CSV
```
Date, Equity
2013-01-02, 1.0118
2013-01-03, 1.0168
...
```

### Backtest Log JSON
Detailed step-by-step log with:
- Training dates
- Retrain decisions
- Regime changes
- Signals and returns
- Trade costs and PnL

### Trades CSV
Portfolio trade history

---

## Execution Time

Each script takes approximately **5-10 minutes** to run on a standard machine:

- **Static Strategy:** ~5-7 minutes
- **Regime-Specific Strategy:** ~7-10 minutes (more models to train)
- **Hybrid Strategy:** ~6-8 minutes

**Total for all 3:** ~20-25 minutes

---

## Troubleshooting

### Error: "Feature file not found"
**Solution:** Run the full pipeline first:
```bash
python data/fetch_data.py
python features/feature_engineering.py
python regimes/hmm_detector.py
python regimes/changepoint_detector.py
python scripts/merge_regimes.py
```

### Error: "No feature columns detected"
**Solution:** Check that FEATURE_FILE path is correct and file exists

### Error: "Not enough training samples"
**Solution:** This is a warning, not an error. The script skips days with insufficient data.

### Slow execution
**Solution:** Use RandomForest instead of XGBoost:
```python
MODEL_TYPE = "rf"
```

### Memory error
**Solution:** Reduce WINDOW_DAYS:
```python
WINDOW_DAYS = 500
```

---

## Next Steps

After running all 3 scripts:

1. **Generate Buy-and-Hold Baseline:**
   ```bash
   python scripts/buy_and_hold_baseline.py
   ```

2. **Run Statistical Comparison:**
   ```bash
   python scripts/statistical_comparison.py
   ```

3. **Review Results:**
   - Console output (printed)
   - `results/statistical_comparison.json` (detailed)
   - `results/strategy_summary.csv` (metrics table)
   - `results/statistical_report.txt` (formatted report)

---

## Integration with Statistical Comparison

The `statistical_comparison.py` script expects these files:

```python
strategy_dict = {
    "Static": "results/signals_static.csv",
    "Regime-Specific": "results/signals_regime_specific.csv",
    "Hybrid": "results/signals_hybrid.csv",
    "Buy-and-Hold": "results/signals_bah.csv",
}
```

All 3 runners generate the required files with the correct naming convention.

---

## Batch Execution

To run all 3 strategies in sequence:

```bash
# Run all 3 strategies
python statistical_comparison_runners/run_static_strategy.py
python statistical_comparison_runners/run_regime_specific_strategy.py
python statistical_comparison_runners/run_hybrid_strategy.py

# Generate baseline
python scripts/buy_and_hold_baseline.py

# Run statistical comparison
python scripts/statistical_comparison.py
```

**Total time:** ~30-40 minutes

---

## Logging

Each script creates a log file:

- `logs/walk_forward_engine_static.log`
- `logs/walk_forward_engine_regime_specific.log`
- `logs/walk_forward_engine_hybrid.log`

Check these logs for debugging and detailed execution information.

---

## Separation from Main Codebase

These scripts are in a dedicated `statistical_comparison_runners/` folder to:

✅ Keep the main codebase clean  
✅ Avoid modifying the original `walk_forward_engine.py`  
✅ Make it easy to run multiple strategies in parallel  
✅ Provide clear separation of concerns  

The original `backtest/walk_forward_engine.py` remains unchanged and can still be used independently.

---

## Key Differences from Original

| Aspect | Original | Runners |
|---|---|---|
| Location | `backtest/walk_forward_engine.py` | `statistical_comparison_runners/` |
| Strategy Mode | Configurable (default: hybrid) | Fixed per script |
| Output Files | `signals_SPY.csv` | `signals_static.csv`, etc. |
| Logger Name | `walk_forward_engine` | `walk_forward_engine_static`, etc. |
| Log File | `walk_forward_engine.log` | `walk_forward_engine_static.log`, etc. |
| Purpose | General backtesting | Statistical comparison |

---

## Summary

✅ 3 pre-configured scripts for each strategy  
✅ Generates required CSV files for statistical comparison  
✅ Separated from main codebase  
✅ Ready to run immediately  
✅ Comprehensive logging and error handling  
✅ Integration with statistical_comparison.py  

**Ready to use!**

---

*For statistical comparison guide, see: STATISTICAL_SIGNIFICANCE.md*  
*For comparison script, see: scripts/statistical_comparison.py*
