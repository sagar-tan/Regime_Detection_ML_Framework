# Statistical Comparison Setup Guide

**Quick Setup for Running 3 Strategies**

---

## What You Have

3 pre-configured Python scripts in `statistical_comparison_runners/`:

1. **run_static_strategy.py** → `signals_static.csv`
2. **run_regime_specific_strategy.py** → `signals_regime_specific.csv`
3. **run_hybrid_strategy.py** → `signals_hybrid.csv`

Each script is a modified copy of `walk_forward_engine.py` with:
- ✅ Strategy mode pre-set
- ✅ Output files named correctly
- ✅ Separate logging
- ✅ Ready to run immediately

---

## Prerequisites

Before running the scripts, ensure you have:

```bash
# 1. Data downloaded
python data/fetch_data.py

# 2. Features engineered
python features/feature_engineering.py

# 3. Regimes detected
python regimes/hmm_detector.py
python regimes/changepoint_detector.py

# 4. Regimes merged
python scripts/merge_regimes.py
```

This creates `data/processed/features_final_SPY.csv` which all 3 scripts need.

---

## Running the Scripts

### Option A: Run One by One (Recommended)

```bash
# 1. Static Strategy (5-7 minutes)
python statistical_comparison_runners/run_static_strategy.py

# 2. Regime-Specific Strategy (7-10 minutes)
python statistical_comparison_runners/run_regime_specific_strategy.py

# 3. Hybrid Strategy (6-8 minutes)
python statistical_comparison_runners/run_hybrid_strategy.py
```

### Option B: Run All in Sequence

```bash
# Run all 3 in one command
python statistical_comparison_runners/run_static_strategy.py && \
python statistical_comparison_runners/run_regime_specific_strategy.py && \
python statistical_comparison_runners/run_hybrid_strategy.py
```

---

## What Gets Generated

After running all 3 scripts, you'll have in `results/`:

```
results/
├── signals_static.csv                    # Static strategy results
├── equity_curve_static.csv
├── backtest_log_static.json
├── trades_static.csv
│
├── signals_regime_specific.csv           # Regime-Specific strategy results
├── equity_curve_regime_specific.csv
├── backtest_log_regime_specific.json
├── trades_regime_specific.csv
│
├── signals_hybrid.csv                    # Hybrid strategy results
├── equity_curve_hybrid.csv
├── backtest_log_hybrid.json
├── trades_hybrid.csv
│
└── (other existing files)
```

---

## Next: Generate Baseline and Compare

### Step 1: Generate Buy-and-Hold Baseline
```bash
python scripts/buy_and_hold_baseline.py
```

Creates: `results/signals_bah.csv`

### Step 2: Run Statistical Comparison
```bash
python scripts/statistical_comparison.py
```

Creates:
- `results/statistical_comparison.json`
- `results/strategy_summary.csv`
- `results/statistical_report.txt`

### Step 3: Review Results
```bash
# View formatted report
cat results/statistical_report.txt

# Or view CSV summary
cat results/strategy_summary.csv
```

---

## Customization

### Change Model Type

Edit any script (e.g., `run_static_strategy.py`):

```python
# Line 44: Change from "xgb" to "rf"
MODEL_TYPE = "rf"  # Use RandomForest instead of XGBoost
```

### Change Transaction Costs

Edit any script:

```python
# Line 47: Change from 0.0005 to 0.001
TRANSACTION_COST = 0.001  # 10 basis points instead of 5
```

### Change Training Window

Edit any script:

```python
# Line 32: Change from 750 to 500
WINDOW_DAYS = 500  # Shorter window (≈2 years)
```

---

## Monitoring Progress

### Check Logs

Each script creates a log file:

```bash
# Static strategy log
tail -f logs/walk_forward_engine_static.log

# Regime-specific strategy log
tail -f logs/walk_forward_engine_regime_specific.log

# Hybrid strategy log
tail -f logs/walk_forward_engine_hybrid.log
```

### Check Output Files

```bash
# Check if files are being created
ls -lh results/signals_*.csv

# Check file size (should grow as script runs)
watch -n 5 'ls -lh results/signals_*.csv'
```

---

## Troubleshooting

### Error: "Feature file not found"

**Problem:** `data/processed/features_final_SPY.csv` doesn't exist

**Solution:** Run the full pipeline first:
```bash
python data/fetch_data.py
python features/feature_engineering.py
python regimes/hmm_detector.py
python regimes/changepoint_detector.py
python scripts/merge_regimes.py
```

### Error: "No feature columns detected"

**Problem:** Feature file exists but columns are wrong

**Solution:** Check that TICKER = "SPY" matches your data

### Script runs very slowly

**Problem:** XGBoost is slow on your machine

**Solution:** Use RandomForest instead:
```python
MODEL_TYPE = "rf"
```

### Memory error during execution

**Problem:** Training window is too large

**Solution:** Reduce WINDOW_DAYS:
```python
WINDOW_DAYS = 500
```

### Output files not created

**Problem:** Script crashed or didn't complete

**Solution:** Check the log file:
```bash
tail -100 logs/walk_forward_engine_static.log
```

---

## Execution Timeline

| Step | Time | Command |
|---|---|---|
| Static Strategy | 5-7 min | `python statistical_comparison_runners/run_static_strategy.py` |
| Regime-Specific | 7-10 min | `python statistical_comparison_runners/run_regime_specific_strategy.py` |
| Hybrid Strategy | 6-8 min | `python statistical_comparison_runners/run_hybrid_strategy.py` |
| Buy-and-Hold | < 1 min | `python scripts/buy_and_hold_baseline.py` |
| Statistical Comparison | 1-2 min | `python scripts/statistical_comparison.py` |
| **TOTAL** | **~30-40 min** | All steps |

---

## Expected Output

After all steps, you should see:

### Console Output
```
╔════════════════════════════════════════════════════════════════════════════╗
║  STATISTICAL SIGNIFICANCE REPORT: Hybrid vs Static
╚════════════════════════════════════════════════════════════════════════════╝

1. DAILY RETURNS COMPARISON (Paired t-test)
   Hybrid significantly outperforms Static
   t-statistic: 2.1234
   p-value: 0.0342 ✓ SIGNIFICANT
   ...
```

### Files Created
```
✓ results/signals_static.csv
✓ results/signals_regime_specific.csv
✓ results/signals_hybrid.csv
✓ results/signals_bah.csv
✓ results/statistical_comparison.json
✓ results/strategy_summary.csv
✓ results/statistical_report.txt
```

---

## Quick Commands

```bash
# Run all 3 strategies (sequential)
python statistical_comparison_runners/run_static_strategy.py && \
python statistical_comparison_runners/run_regime_specific_strategy.py && \
python statistical_comparison_runners/run_hybrid_strategy.py

# Generate baseline
python scripts/buy_and_hold_baseline.py

# Run comparison
python scripts/statistical_comparison.py

# View results
cat results/statistical_report.txt
```

---

## File Locations

| File | Location |
|---|---|
| Static runner | `statistical_comparison_runners/run_static_strategy.py` |
| Regime-Specific runner | `statistical_comparison_runners/run_regime_specific_strategy.py` |
| Hybrid runner | `statistical_comparison_runners/run_hybrid_strategy.py` |
| Baseline generator | `scripts/buy_and_hold_baseline.py` |
| Comparison script | `scripts/statistical_comparison.py` |
| Output files | `results/signals_*.csv` |
| Logs | `logs/walk_forward_engine_*.log` |

---

## Summary

✅ 3 pre-configured scripts ready to run  
✅ Generates all required CSV files  
✅ Separated from main codebase  
✅ Comprehensive error handling  
✅ Detailed logging  
✅ ~30-40 minutes total execution time  

**You're ready to go!**

---

*For detailed documentation, see: README.md*  
*For statistical comparison guide, see: STATISTICAL_SIGNIFICANCE.md*
