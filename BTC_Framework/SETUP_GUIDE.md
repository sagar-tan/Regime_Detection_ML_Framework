# BTC_Framework Setup Guide

**Quick setup for Bitcoin trading strategy framework**

---

## Prerequisites

1. **Parent Framework:** RDMA_ML_Framework must be installed
2. **Python:** 3.8+
3. **Dependencies:** All packages from parent framework
4. **Data:** Internet connection for Yahoo Finance

---

## Step-by-Step Setup

### Step 1: Verify Parent Framework
```bash
# Check that parent framework is accessible
python -c "from utils.logger import setup_logger; print('✓ Parent framework OK')"
```

### Step 2: Fetch BTC Data
```bash
cd BTC_Framework
python data/fetch_data_BTC.py
```

**Expected output:**
```
INFO:__main__:Fetching BTC-USD data from 2015-01-01 to 2025-12-07...
INFO:__main__:Successfully fetched 3956 rows of data
INFO:__main__:Saved raw data to data/raw/BTC-USD.csv
```

**Output file:** `data/raw/BTC-USD.csv` (~500 KB)

### Step 3: Engineer Features
```bash
python features/feature_engineering_BTC.py
```

**Expected output:**
```
INFO:__main__:Starting feature engineering...
INFO:__main__:Computing daily returns...
INFO:__main__:Computing SMAs: [10, 20, 50, 100, 200]
...
INFO:__main__:Saved features to data/processed/features_final_BTC-USD.csv
```

**Output file:** `data/processed/features_final_BTC-USD.csv` (~2 MB)

### Step 4: Detect Regimes - HMM
```bash
python regimes/hmm_detector_BTC.py
```

**Expected output:**
```
INFO:__main__:Fitting HMM with 4 components...
INFO:__main__:HMM converged: True
INFO:__main__:Final log-likelihood: -1234.5678
INFO:__main__:Regime 0: 1200 days (30.3%)
INFO:__main__:Regime 1: 950 days (24.0%)
...
```

**Output file:** `data/processed/features_with_hmm_BTC-USD.csv`

### Step 5: Detect Regimes - Changepoint
```bash
python regimes/changepoint_detector_BTC.py
```

**Expected output:**
```
INFO:__main__:Detecting changepoints (penalty=2.0, min_size=20)...
INFO:__main__:Detected 15 changepoints
INFO:__main__:Regime 0: 250 days (6.3%)
INFO:__main__:Regime 1: 340 days (8.6%)
...
```

**Output file:** `data/processed/features_with_cp_BTC-USD.csv`

### Step 6: Merge Regimes
```bash
python scripts/merge_regimes_BTC.py
```

**Expected output:**
```
INFO:__main__:Merging regimes...
INFO:__main__:Added BTC-USD_CP_Regime column
INFO:__main__:Saved merged features to data/processed/features_final_BTC-USD.csv
```

**Output file:** `data/processed/features_final_BTC-USD.csv` (updated with both regimes)

### Step 7: Run Static Strategy Backtest
```bash
python run_static_strategy_BTC.py
```

**Expected output:**
```
INFO:walk_forward_engine_static_BTC:===== WALK-FORWARD BACKTEST ENGINE (STATIC STRATEGY - BTC) STARTED =====
INFO:walk_forward_engine_static_BTC:Starting walk-forward. total samples: 3956
INFO:walk_forward_engine_static_BTC:Trained new global model at idx 750
...
INFO:walk_forward_engine_static_BTC:Saved signals to results/signals_static_BTC.csv
```

**Time:** 5-7 minutes  
**Output files:**
- `results/signals_static_BTC.csv`
- `results/equity_curve_static_BTC.csv`
- `results/backtest_log_static_BTC.json`
- `results/trades_static_BTC.csv`

### Step 8: Run Regime-Specific Strategy Backtest
```bash
python run_regime_specific_strategy_BTC.py
```

**Expected output:**
```
INFO:walk_forward_engine_regime_specific_BTC:===== WALK-FORWARD BACKTEST ENGINE (REGIME-SPECIFIC STRATEGY - BTC) STARTED =====
INFO:walk_forward_engine_regime_specific_BTC:Starting walk-forward. total samples: 3956
INFO:walk_forward_engine_regime_specific_BTC:Trained new regime model for signature 0|0 at idx 750
...
```

**Time:** 7-10 minutes  
**Output files:**
- `results/signals_regime_specific_BTC.csv`
- `results/equity_curve_regime_specific_BTC.csv`
- `results/backtest_log_regime_specific_BTC.json`
- `results/trades_regime_specific_BTC.csv`

### Step 9: Run Hybrid Strategy Backtest
```bash
python run_hybrid_strategy_BTC.py
```

**Expected output:**
```
INFO:walk_forward_engine_hybrid_BTC:===== WALK-FORWARD BACKTEST ENGINE (HYBRID STRATEGY - BTC) STARTED =====
INFO:walk_forward_engine_hybrid_BTC:Starting walk-forward. total samples: 3956
...
```

**Time:** 6-8 minutes  
**Output files:**
- `results/signals_hybrid_BTC.csv`
- `results/equity_curve_hybrid_BTC.csv`
- `results/backtest_log_hybrid_BTC.json`
- `results/trades_hybrid_BTC.csv`

### Step 10: Run Statistical Comparison
```bash
python statistical_comparison_BTC.py
```

**Expected output:**
```
INFO:statistical_comparison_BTC:Running pairwise comparisons...
INFO:statistical_comparison_BTC:Comparing Static_vs_Regime-Specific...
INFO:statistical_comparison_BTC:Comparing Static_vs_Hybrid...
...
================================================================================
BTC-USD STRATEGY PERFORMANCE SUMMARY
================================================================================
                Strategy  Total Return (%)  Annual Return (%)  Volatility (%)  Sharpe Ratio  Max Drawdown (%)  Win Rate (%)  Num Trades  Days
                  Static              45.23              8.12            65.34          0.124              -78.45         51.23       1234  3200
          Regime-Specific              67.89             11.45            58.12          0.197              -72.10         54.12       2345  3200
                   Hybrid              56.34              9.87            61.23          0.161              -75.23         52.89       1890  3200
================================================================================
```

**Time:** 1-2 minutes  
**Output files:**
- `results/BTC_statistical_comparison.json`
- `results/BTC_strategy_summary.csv`
- `results/BTC_statistical_report.txt`

---

## Full Automated Setup

Run all steps in sequence:

```bash
cd BTC_Framework

# Data preparation (5 minutes)
python data/fetch_data_BTC.py
python features/feature_engineering_BTC.py
python regimes/hmm_detector_BTC.py
python regimes/changepoint_detector_BTC.py
python scripts/merge_regimes_BTC.py

# Backtests (20 minutes)
python run_static_strategy_BTC.py
python run_regime_specific_strategy_BTC.py
python run_hybrid_strategy_BTC.py

# Statistical comparison (2 minutes)
python statistical_comparison_BTC.py

echo "✓ BTC_Framework setup complete!"
```

**Total time:** ~30-40 minutes

---

## Verify Setup

After setup, check for these files:

```bash
# Data files
ls -lh data/raw/BTC-USD.csv
ls -lh data/processed/features_final_BTC-USD.csv

# Backtest results
ls -lh results/signals_*_BTC.csv
ls -lh results/equity_curve_*_BTC.csv

# Statistical results
ls -lh results/BTC_*.csv
ls -lh results/BTC_*.json
ls -lh results/BTC_*.txt
```

All files should exist and have non-zero size.

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'utils'"
**Solution:** Ensure parent framework is in Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Issue: "Feature file not found"
**Solution:** Run data preparation steps in order:
```bash
python data/fetch_data_BTC.py
python features/feature_engineering_BTC.py
```

### Issue: "No feature columns detected"
**Solution:** Check that TICKER = "BTC-USD" in all scripts

### Issue: Slow execution
**Solution:** Use RandomForest instead of XGBoost:
```python
MODEL_TYPE = "rf"
```

### Issue: Memory error
**Solution:** Reduce training window:
```python
WINDOW_DAYS = 500
```

### Issue: No regime changes detected
**Solution:** Lower changepoint penalty:
```python
PENALTY = 1.0
```

---

## Configuration Adjustments

### Faster Setup (Lower Quality)
```python
# In run_*_strategy_BTC.py
WINDOW_DAYS = 500        # Shorter training window
MODEL_TYPE = "rf"        # Faster model
STEP_DAYS = 5            # Weekly instead of daily
```

### Higher Quality (Slower)
```python
# In run_*_strategy_BTC.py
WINDOW_DAYS = 1000       # Longer training window
MODEL_TYPE = "xgb"       # Better model
N_ESTIMATORS = 500       # More trees
```

### More Sensitive Regimes
```python
# In regimes/changepoint_detector_BTC.py
PENALTY = 1.0            # More changepoints
MIN_SIZE = 10            # Shorter segments
```

### Less Sensitive Regimes
```python
# In regimes/changepoint_detector_BTC.py
PENALTY = 5.0            # Fewer changepoints
MIN_SIZE = 50            # Longer segments
```

---

## Monitoring Progress

### Check logs
```bash
tail -f logs/walk_forward_engine_static_BTC.log
tail -f logs/walk_forward_engine_regime_specific_BTC.log
tail -f logs/walk_forward_engine_hybrid_BTC.log
```

### Monitor file creation
```bash
watch -n 5 'ls -lh results/signals_*_BTC.csv'
```

### Check data size
```bash
du -sh data/
du -sh results/
```

---

## Next Steps

1. **Review Results:** Check `results/BTC_statistical_report.txt`
2. **Analyze Regimes:** Look at regime detection quality
3. **Customize:** Adjust parameters for your strategy
4. **Backtest:** Run with different parameters
5. **Research:** Use results for research paper

---

## Expected Output Summary

After complete setup, you should have:

**Data Files:**
- Raw BTC data: `data/raw/BTC-USD.csv`
- Engineered features: `data/processed/features_final_BTC-USD.csv`

**Backtest Results (3 strategies × 4 files each = 12 files):**
- Signals: `results/signals_*_BTC.csv`
- Equity curves: `results/equity_curve_*_BTC.csv`
- Logs: `results/backtest_log_*_BTC.json`
- Trades: `results/trades_*_BTC.csv`

**Statistical Results:**
- Summary: `results/BTC_strategy_summary.csv`
- Detailed: `results/BTC_statistical_comparison.json`
- Report: `results/BTC_statistical_report.txt`

**Total files:** ~20+  
**Total size:** ~50-100 MB

---

## Support

- **README.md** - Overview and features
- **Parent framework docs** - Detailed documentation
- **Log files** - Detailed execution information
- **Code comments** - Implementation details

---

**Status:** ✅ Ready to use  
**Estimated Setup Time:** 30-40 minutes  
**Difficulty:** Beginner-friendly
