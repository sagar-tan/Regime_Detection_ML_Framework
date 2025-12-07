# BTC_Framework - Regime-Aware ML Trading Framework for Bitcoin

**Adapted from:** RDMA_ML_Framework  
**Asset:** BTC-USD (Bitcoin)  
**Status:** ✅ Ready to use  
**Date:** December 7, 2025

---

## Overview

BTC_Framework is a complete adaptation of the RDMA_ML_Framework for Bitcoin trading. It implements regime-aware machine learning strategies to detect market regimes and adapt trading signals accordingly.

### Key Features

- **BTC-USD Data:** Fetches Bitcoin OHLCV data from Yahoo Finance
- **Regime Detection:** HMM (4 components) and Changepoint detection (penalty=2.0)
- **Feature Engineering:** 60+ technical indicators adapted for crypto
- **Three Strategies:**
  - Static: Single model across all regimes
  - Regime-Specific: Separate model per regime
  - Hybrid: Global model with regime-triggered retraining
- **Statistical Validation:** Paired t-tests, Sharpe decomposition, win rate analysis
- **Higher Spreads:** 10 basis points transaction costs (vs 5 bps for stocks)

---

## Quick Start

### Prerequisites

Ensure you have the parent RDMA_ML_Framework installed with all dependencies:
```bash
pip install pandas numpy yfinance scikit-learn xgboost hmmlearn ruptures scipy
```

### Step 1: Fetch Data
```bash
python data/fetch_data_BTC.py
```
**Output:** `data/raw/BTC-USD.csv`

### Step 2: Engineer Features
```bash
python features/feature_engineering_BTC.py
```
**Output:** `data/processed/features_final_BTC-USD.csv`

### Step 3: Detect Regimes
```bash
python regimes/hmm_detector_BTC.py
python regimes/changepoint_detector_BTC.py
python scripts/merge_regimes_BTC.py
```
**Output:** `data/processed/features_final_BTC-USD.csv` (with regime labels)

### Step 4: Run Backtests
```bash
python run_static_strategy_BTC.py
python run_regime_specific_strategy_BTC.py
python run_hybrid_strategy_BTC.py
```
**Output:** 
- `results/signals_static_BTC.csv`
- `results/signals_regime_specific_BTC.csv`
- `results/signals_hybrid_BTC.csv`

### Step 5: Statistical Comparison
```bash
python statistical_comparison_BTC.py
```
**Output:**
- `results/BTC_statistical_comparison.json`
- `results/BTC_strategy_summary.csv`
- `results/BTC_statistical_report.txt`

---

## File Structure

```
BTC_Framework/
├── data/
│   ├── fetch_data_BTC.py              # Download BTC-USD data
│   └── (raw/ and processed/ created at runtime)
│
├── features/
│   └── feature_engineering_BTC.py     # Compute 60+ indicators
│
├── regimes/
│   ├── hmm_detector_BTC.py            # HMM regime detection
│   └── changepoint_detector_BTC.py    # Changepoint detection
│
├── scripts/
│   └── merge_regimes_BTC.py           # Merge HMM + CP regimes
│
├── run_static_strategy_BTC.py         # Static strategy backtest
├── run_regime_specific_strategy_BTC.py # Regime-specific backtest
├── run_hybrid_strategy_BTC.py         # Hybrid strategy backtest
│
├── statistical_comparison_BTC.py      # Statistical tests
│
├── README.md                          # This file
└── SETUP_GUIDE.md                     # Detailed setup instructions
```

---

## Configuration

### Data Fetching (fetch_data_BTC.py)
```python
TICKER = "BTC-USD"
START_DATE = "2015-01-01"  # Earlier start for more data
END_DATE = datetime.now().strftime("%Y-%m-%d")
```

### Feature Engineering (feature_engineering_BTC.py)
```python
PREDICTION_HORIZON = 1      # Predict 1-day ahead
RETURN_THRESHOLD = 0.0      # Binary target: return > 0
```

Features computed:
- Returns (daily % change)
- SMAs: 10, 20, 50, 100, 200 day
- EMAs: 12, 26 day
- MACD, RSI, Bollinger Bands
- Volatility (20-day rolling)
- ATR (14-day)

### Regime Detection

**HMM (hmm_detector_BTC.py):**
```python
N_COMPONENTS = 4        # 4 regimes (higher than stocks for crypto volatility)
N_ITER = 1000
RANDOM_STATE = 42
```

**Changepoint (changepoint_detector_BTC.py):**
```python
PENALTY = 2.0           # Lower penalty (more sensitive)
MIN_SIZE = 20           # Minimum segment size
```

### Backtesting (run_*_strategy_BTC.py)
```python
WINDOW_DAYS = 750       # 3-year training window
RETRAIN_INTERVAL = 750  # Retrain every 3 years or on regime change
PREDICTION_HORIZON = 1  # 1-day ahead prediction
STEP_DAYS = 1           # Daily updates
MODEL_TYPE = "xgb"      # XGBoost (or "rf" for RandomForest)
TRANSACTION_COST = 0.001 # 10 basis points (crypto spreads)
```

### Statistical Comparison (statistical_comparison_BTC.py)
Runs:
- Paired t-tests on daily returns
- Sharpe ratio decomposition
- Win rate significance (binomial test)
- Maximum drawdown comparison

---

## Output Files

### Data Files
- `data/raw/BTC-USD.csv` - Raw OHLCV data
- `data/processed/features_final_BTC-USD.csv` - Engineered features with regimes

### Backtest Results
- `results/signals_static_BTC.csv` - Static strategy signals
- `results/signals_regime_specific_BTC.csv` - Regime-specific signals
- `results/signals_hybrid_BTC.csv` - Hybrid strategy signals
- `results/equity_curve_*.csv` - Equity curves
- `results/backtest_log_*.json` - Detailed logs
- `results/trades_*.csv` - Trade history

### Statistical Results
- `results/BTC_statistical_comparison.json` - Detailed test results
- `results/BTC_strategy_summary.csv` - Performance metrics table
- `results/BTC_statistical_report.txt` - Formatted report

---

## Key Differences from RDMA_ML_Framework

| Aspect | RDMA (SPY) | BTC_Framework |
|---|---|---|
| Asset | SPY (stock) | BTC-USD (crypto) |
| Data Start | 2010 | 2015 |
| HMM Components | 3 | 4 (higher volatility) |
| Changepoint Penalty | 5.0 | 2.0 (more sensitive) |
| Transaction Cost | 0.0005 (5 bps) | 0.001 (10 bps) |
| Market Hours | 6.5 hours/day | 24/7 |
| Volatility | ~15% annual | ~70% annual |
| Regime Frequency | ~1-2 per year | ~3-5 per year |

---

## Execution Timeline

| Step | Time | Command |
|---|---|---|
| Fetch Data | 2-3 min | `python data/fetch_data_BTC.py` |
| Feature Engineering | 1-2 min | `python features/feature_engineering_BTC.py` |
| HMM Detection | 2-3 min | `python regimes/hmm_detector_BTC.py` |
| Changepoint Detection | 1-2 min | `python regimes/changepoint_detector_BTC.py` |
| Merge Regimes | < 1 min | `python scripts/merge_regimes_BTC.py` |
| Static Backtest | 5-7 min | `python run_static_strategy_BTC.py` |
| Regime-Specific Backtest | 7-10 min | `python run_regime_specific_strategy_BTC.py` |
| Hybrid Backtest | 6-8 min | `python run_hybrid_strategy_BTC.py` |
| Statistical Comparison | 1-2 min | `python statistical_comparison_BTC.py` |
| **TOTAL** | **~30-40 min** | All steps |

---

## Expected Results

### Regime Detection
BTC's high volatility typically results in:
- **HMM:** 4 distinct regimes (bull, bear, consolidation, extreme)
- **Changepoint:** 10-20 changepoints over 10 years

### Strategy Performance
Expected Sharpe ratios (will vary with data):
- **Static:** 0.3 - 0.6
- **Regime-Specific:** 0.5 - 0.9 (benefits from regime adaptation)
- **Hybrid:** 0.4 - 0.8 (balanced approach)

### Statistical Significance
- Regime-Specific vs Static: Often significant (p < 0.05)
- Hybrid vs Static: Often significant
- Higher volatility = larger effect sizes

---

## Troubleshooting

### Error: "Feature file not found"
**Solution:** Run data fetching and feature engineering first:
```bash
python data/fetch_data_BTC.py
python features/feature_engineering_BTC.py
```

### Error: "No feature columns detected"
**Solution:** Check that ticker in scripts matches "BTC-USD"

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

### No regime changes detected
**Solution:** Lower the changepoint penalty:
```python
PENALTY = 1.0  # More sensitive
```

---

## Customization

### Change Training Window
Edit any backtest script:
```python
WINDOW_DAYS = 500  # Shorter window
```

### Change Transaction Costs
Edit any backtest script:
```python
TRANSACTION_COST = 0.002  # 20 basis points
```

### Change Regime Sensitivity
Edit regime detection scripts:
```python
# HMM
N_COMPONENTS = 3  # Fewer regimes

# Changepoint
PENALTY = 3.0  # Less sensitive
```

### Use Different Model
Edit backtest scripts:
```python
MODEL_TYPE = "rf"  # RandomForest instead of XGBoost
```

---

## Integration with Parent Framework

BTC_Framework uses the parent RDMA_ML_Framework's modules:
- `utils.logger` - Logging utilities
- `models.random_forest` - RandomForest model
- `models.xgboost_model` - XGBoost model
- `strategies.*` - Strategy classes
- `backtest.transaction_costs` - Transaction cost calculation
- `backtest.portfolio` - Portfolio management
- `analysis.statistical_tests` - Statistical tests

Ensure the parent framework is in the Python path:
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

## For Research Papers

Use the statistical comparison output to support claims:

**Good claim:**
"The regime-specific strategy significantly outperforms the static baseline (t=2.34, p=0.019), with a Cohen's d of 0.45, indicating a medium effect size."

**Better claim:**
"The regime-specific strategy achieves a Sharpe ratio of 0.78 vs 0.52 for static (p=0.019). The improvement is driven primarily by reduced volatility in bear regimes (σ_RS=0.018 vs σ_Static=0.025), not increased returns."

Use templates from STATISTICAL_SIGNIFICANCE.md in parent framework.

---

## Next Steps

1. Run all data preparation scripts
2. Run all three strategy backtests
3. Review statistical comparison results
4. Analyze regime detection quality
5. Adjust parameters for your use case
6. Write research paper with statistical evidence

---

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review SETUP_GUIDE.md for detailed instructions
3. Consult parent RDMA_ML_Framework documentation
4. Check statistical test documentation in parent framework

---

## License

Same as parent RDMA_ML_Framework

---

**Status:** ✅ Ready to use  
**Last Updated:** December 7, 2025  
**Tested:** Yes
