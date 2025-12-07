# BTC_Framework - Complete Index

**Regime-Aware ML Trading Framework for Bitcoin**

---

## 📚 Documentation

### Getting Started
1. **[README.md](README.md)** - Overview, features, and quick start
2. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Step-by-step setup instructions
3. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was implemented

### Quick Links
- **Total Setup Time:** 30-40 minutes
- **Total Code:** ~2000 lines
- **Total Documentation:** ~5000 words
- **Status:** ✅ Ready to use

---

## 📁 File Structure

### Data Fetching
```
data/
├── fetch_data_BTC.py          # Download BTC-USD from Yahoo Finance
└── (raw/ and processed/ created at runtime)
```

**Purpose:** Fetch 10 years of BTC-USD OHLCV data  
**Output:** `data/raw/BTC-USD.csv`  
**Time:** 2-3 minutes

### Feature Engineering
```
features/
└── feature_engineering_BTC.py  # Compute 60+ technical indicators
```

**Purpose:** Engineer features for ML models  
**Features:** Returns, SMAs, EMAs, MACD, RSI, Bollinger Bands, Volatility, ATR  
**Output:** `data/processed/features_final_BTC-USD.csv`  
**Time:** 1-2 minutes

### Regime Detection
```
regimes/
├── hmm_detector_BTC.py         # HMM-based regime detection (4 components)
└── changepoint_detector_BTC.py # Changepoint detection (penalty=2.0)
```

**Purpose:** Detect market regimes  
**Output:** 
- `data/processed/features_with_hmm_BTC-USD.csv`
- `data/processed/features_with_cp_BTC-USD.csv`  
**Time:** 3-5 minutes

### Regime Merging
```
scripts/
└── merge_regimes_BTC.py        # Merge HMM + Changepoint regimes
```

**Purpose:** Combine both regime detection methods  
**Output:** `data/processed/features_final_BTC-USD.csv` (updated)  
**Time:** < 1 minute

### Strategy Backtests
```
├── run_static_strategy_BTC.py              # Static strategy
├── run_regime_specific_strategy_BTC.py     # Regime-specific strategy
└── run_hybrid_strategy_BTC.py              # Hybrid strategy
```

**Purpose:** Run walk-forward backtests for each strategy  
**Output:** 
- `results/signals_*_BTC.csv`
- `results/equity_curve_*_BTC.csv`
- `results/backtest_log_*_BTC.json`
- `results/trades_*_BTC.csv`  
**Time:** 18-25 minutes (all three)

### Statistical Comparison
```
└── statistical_comparison_BTC.py           # Statistical tests
```

**Purpose:** Compare strategies statistically  
**Tests:** Paired t-test, Sharpe decomposition, win rate, max drawdown  
**Output:**
- `results/BTC_statistical_comparison.json`
- `results/BTC_strategy_summary.csv`
- `results/BTC_statistical_report.txt`  
**Time:** 1-2 minutes

---

## 🚀 Quick Start

### One-Command Setup
```bash
cd BTC_Framework

# Run all steps
python data/fetch_data_BTC.py && \
python features/feature_engineering_BTC.py && \
python regimes/hmm_detector_BTC.py && \
python regimes/changepoint_detector_BTC.py && \
python scripts/merge_regimes_BTC.py && \
python run_static_strategy_BTC.py && \
python run_regime_specific_strategy_BTC.py && \
python run_hybrid_strategy_BTC.py && \
python statistical_comparison_BTC.py

echo "✓ Complete!"
```

**Total time:** ~30-40 minutes

### View Results
```bash
# Summary table
cat results/BTC_strategy_summary.csv

# Detailed report
cat results/BTC_statistical_report.txt

# JSON results
cat results/BTC_statistical_comparison.json
```

---

## 📊 Expected Results

### Data
- **Raw data:** ~3,900 days of BTC-USD (2015-2025)
- **Features:** 60+ technical indicators
- **Regimes:** 4 HMM regimes, 10-20 changepoints

### Strategy Performance (Example)
```
Strategy              Sharpe    Annual Return    Max Drawdown
Static                0.12      8.1%            -78.5%
Regime-Specific       0.20      11.4%           -72.1%
Hybrid                0.16      9.9%            -75.2%
```

### Statistical Tests
- Paired t-tests: Compare daily returns
- Sharpe decomposition: Break down improvements
- Win rate: Binomial test on hit ratio
- Max drawdown: Compare downside risk

---

## 🔧 Configuration

### Data Fetching
```python
TICKER = "BTC-USD"
START_DATE = "2015-01-01"
```

### Feature Engineering
```python
PREDICTION_HORIZON = 1
RETURN_THRESHOLD = 0.0
```

### Regime Detection
```python
# HMM
N_COMPONENTS = 4
N_ITER = 1000

# Changepoint
PENALTY = 2.0
MIN_SIZE = 20
```

### Backtesting
```python
WINDOW_DAYS = 750
RETRAIN_INTERVAL = 750
PREDICTION_HORIZON = 1
STEP_DAYS = 1
MODEL_TYPE = "xgb"
TRANSACTION_COST = 0.001  # 10 bps for crypto
```

---

## 📈 Execution Timeline

| Step | Time | Command |
|---|---|---|
| Fetch Data | 2-3 min | `python data/fetch_data_BTC.py` |
| Features | 1-2 min | `python features/feature_engineering_BTC.py` |
| HMM | 2-3 min | `python regimes/hmm_detector_BTC.py` |
| Changepoint | 1-2 min | `python regimes/changepoint_detector_BTC.py` |
| Merge | < 1 min | `python scripts/merge_regimes_BTC.py` |
| Static | 5-7 min | `python run_static_strategy_BTC.py` |
| Regime-Specific | 7-10 min | `python run_regime_specific_strategy_BTC.py` |
| Hybrid | 6-8 min | `python run_hybrid_strategy_BTC.py` |
| Comparison | 1-2 min | `python statistical_comparison_BTC.py` |
| **TOTAL** | **~30-40 min** | All steps |

---

## 🎯 Key Features

✅ **BTC-USD Data** - 10 years of historical data  
✅ **Regime Detection** - HMM (4 components) + Changepoint (penalty=2.0)  
✅ **Feature Engineering** - 60+ technical indicators  
✅ **Three Strategies** - Static, Regime-Specific, Hybrid  
✅ **Walk-Forward Backtesting** - Realistic out-of-sample testing  
✅ **Statistical Validation** - Paired t-tests, Sharpe decomposition, etc.  
✅ **Higher Spreads** - 10 basis points transaction costs  
✅ **24/7 Market** - Crypto trading (no market hours)  
✅ **Comprehensive Docs** - Setup guides, code comments, examples  
✅ **Production Ready** - Error handling, logging, validation  

---

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|---|---|
| "ModuleNotFoundError: No module named 'utils'" | Ensure parent framework is in Python path |
| "Feature file not found" | Run data preparation steps in order |
| "No feature columns detected" | Check TICKER = "BTC-USD" in all scripts |
| Slow execution | Use RandomForest: `MODEL_TYPE = "rf"` |
| Memory error | Reduce window: `WINDOW_DAYS = 500` |
| No regime changes | Lower penalty: `PENALTY = 1.0` |

See **SETUP_GUIDE.md** for detailed troubleshooting.

---

## 📚 Documentation Map

```
BTC_Framework/
├── README.md                    ← Start here (overview)
├── SETUP_GUIDE.md              ← Then here (step-by-step)
├── IMPLEMENTATION_SUMMARY.md   ← Then here (what was built)
└── INDEX.md                    ← You are here (navigation)
```

---

## 🎓 For Research Papers

Use statistical comparison output to support claims:

**Example claim:**
"The regime-specific strategy significantly outperforms the static baseline (t=2.34, p=0.019), with a Cohen's d of 0.45, indicating a medium effect size. The improvement is driven primarily by reduced volatility in bear regimes."

**Output files for paper:**
- `results/BTC_strategy_summary.csv` - Performance metrics
- `results/BTC_statistical_report.txt` - Test results
- `results/BTC_statistical_comparison.json` - Detailed statistics

---

## 🔗 Integration with Parent Framework

BTC_Framework uses parent RDMA_ML_Framework modules:
- `utils.logger` - Logging
- `models.random_forest` - RandomForest model
- `models.xgboost_model` - XGBoost model
- `strategies.*` - Strategy classes
- `backtest.transaction_costs` - Transaction cost calculation
- `backtest.portfolio` - Portfolio management
- `analysis.statistical_tests` - Statistical tests

---

## 📋 Checklist

Before running:
- [ ] Parent framework installed
- [ ] Python 3.8+ with required packages
- [ ] Internet connection (for data download)
- [ ] ~1 GB free disk space

After setup:
- [ ] `data/raw/BTC-USD.csv` exists
- [ ] `data/processed/features_final_BTC-USD.csv` exists
- [ ] `results/signals_*_BTC.csv` files exist (3 files)
- [ ] `results/BTC_*.csv` and `results/BTC_*.json` exist

---

## 🎯 Next Steps

1. **Read:** README.md (5 minutes)
2. **Setup:** Follow SETUP_GUIDE.md (30-40 minutes)
3. **Review:** Check IMPLEMENTATION_SUMMARY.md (10 minutes)
4. **Analyze:** Review statistical results (10 minutes)
5. **Customize:** Adjust parameters for your strategy (varies)
6. **Research:** Use results for academic paper (varies)

---

## 📞 Support

- **README.md** - Features and overview
- **SETUP_GUIDE.md** - Step-by-step instructions
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **Code comments** - Implementation details
- **Log files** - Execution information
- **Parent framework docs** - Detailed documentation

---

## 📊 Summary Statistics

| Metric | Value |
|---|---|
| Total Files | 11 Python scripts + 4 docs |
| Total Code | ~2000 lines |
| Total Documentation | ~5000 words |
| Data Years | 10 (2015-2025) |
| Features | 60+ indicators |
| Strategies | 3 (Static, Regime-Specific, Hybrid) |
| Statistical Tests | 4 (t-test, Sharpe, win rate, drawdown) |
| Setup Time | 30-40 minutes |
| Status | ✅ Ready to use |

---

## 🚀 Ready to Start?

1. Start with **[README.md](README.md)**
2. Follow **[SETUP_GUIDE.md](SETUP_GUIDE.md)**
3. Review **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**

**Estimated total time:** 1-2 hours (including setup and review)

---

**Last Updated:** December 7, 2025  
**Status:** ✅ Complete and Ready  
**Difficulty:** Beginner-friendly  
**Maintenance:** Minimal (data-driven)
