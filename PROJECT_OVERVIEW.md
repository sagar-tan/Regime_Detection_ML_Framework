# Project Overview - Regime-Aware ML Trading Framework

**Document Version:** 1.0  
**Last Updated:** December 2025

---

## Core Objective

Provide a **modular, reusable framework** to evaluate machine learning-based trading models under market regime shifts using:

- **Realistic walk-forward backtesting** with rolling training windows
- **Multiple regime detection methods** (HMM and Changepoint)
- **Multiple adaptation strategies** (Static, Regime-Specific, Hybrid)
- **Comprehensive performance evaluation** per regime and around regime transitions
- **Fully extensible architecture** for adding new models, strategies, and detectors

---

## Key Differentiators

### 1. Pluggable ML Models
- **Abstraction:** Any model with `fit()` and `predict()` methods can be inserted
- **Current Support:** RandomForest, XGBoost
- **Extensibility:** Add LSTM, SVM, or any scikit-learn compatible model without rewriting core logic
- **Interface:** `BaseTradingModel` defines minimal contract

### 2. Multiple Regime Detection Methods
- **HMM Detector:** 2-state Gaussian Hidden Markov Model on daily returns
- **Changepoint Detector:** PELT algorithm for structural breaks
- **Treated as Modules:** Both are replaceable; can add more detectors independently
- **Combined Usage:** Both run in parallel; results merged for comprehensive regime identification

### 3. Adaptation Strategies
- **Static Strategy:** Single model across all regimes; retrains on fixed interval only
- **Regime-Specific Strategy:** Maintains separate model per detected regime; switches on regime change
- **Hybrid Strategy:** Global model with forced retrain on regime change + interval retrain
- **Fair Comparison:** All strategies tested under identical conditions (same data, features, costs)

### 4. Regime-Aware Performance Metrics
- **Per-Regime Evaluation:** Separate metrics for each detected regime
- **Transition Analysis:** Performance ±20 days around regime shifts
- **Stress Testing:** Identify model weakness during regime transitions
- **Sensitivity Analysis:** Compare HMM vs Changepoint regime labels

### 5. Walk-Forward Validation
- **Mandatory:** Not optional; all backtests use rolling windows
- **Realistic:** Prevents look-ahead bias and overfitting
- **Configuration:**
  - Training window: 750 days (≈3 years)
  - Test window: 1 day (daily prediction)
  - Step size: 1 day forward
  - Total backtest: 2,975 trading days

### 6. Fully Modular Code Structure
- **Separation of Concerns:** Data, features, models, strategies, backtesting are isolated
- **No Hardcoding:** Configuration via parameters, not magic numbers
- **Reproducibility:** All random states seeded (RANDOM_STATE=42)
- **Logging:** Every module logs to file and console for debugging
- **Extensibility:** Add new components without modifying existing code

---

## Supported Assets

### Tested Assets
- **SPY** (S&P 500 ETF) - Large cap equity
- **QQQ** (Nasdaq-100 ETF) - Tech-heavy equity
- **IWM** (Russell 2000 ETF) - Small cap equity
- **XLF** (Financial Sector ETF) - Sector-specific
- **GLD** (Gold ETF) - Commodity
- **TLT** (20+ Year Treasury ETF) - Fixed income

### Data Characteristics
- **Time Period:** 2010-01-01 to 2025-01-01 (15 years)
- **Frequency:** Daily OHLCV (Open, High, Low, Close, Volume)
- **Total Rows:** 3,774 per asset
- **After Processing:** 3,725 rows (49 dropped due to NaN from rolling calculations)

### Extensibility
- **Any Ticker:** Framework supports any ticker available via Yahoo Finance
- **Custom Assets:** Modify `TICKERS` list in `fetch_data.py`
- **International Assets:** Works with any yfinance-supported symbol
- **Crypto:** Can be extended to crypto data with minor modifications

---

## Problem Statement

### Traditional Backtesting Limitations
1. **Ignores Regime Changes:** Most frameworks assume constant market dynamics
2. **Single Model:** Uses one model across all market conditions
3. **Limited Metrics:** Focus on global Sharpe ratio, ignoring regime-specific performance
4. **Unrealistic Costs:** Often ignore transaction costs or apply them incorrectly
5. **Overfitting:** Walk-forward validation not enforced

### This Framework Solves
- ✅ **Regime Awareness:** Detects and adapts to market structure changes
- ✅ **Multiple Strategies:** Compares static, regime-specific, and hybrid approaches
- ✅ **Comprehensive Metrics:** Per-regime, transition, and global performance
- ✅ **Realistic Costs:** Configurable transaction costs, slippage, spreads
- ✅ **Enforced Validation:** Walk-forward backtesting built-in

---

## Architecture Overview

### High-Level Flow

```
Raw Data (Yahoo Finance)
    ↓
Data Cleaning & Alignment
    ↓
Feature Engineering (Return, Vol, SMA, etc.)
    ↓
Regime Detection (HMM + Changepoint)
    ↓
Walk-Forward Backtest Loop:
  ├─ Train Window: 750 days
  ├─ Detect Regime Change
  ├─ Strategy Decision: Retrain?
  ├─ Train/Select Model
  ├─ Predict Next Day Signal
  ├─ Apply Transaction Costs
  └─ Update Portfolio
    ↓
Performance Analysis
    ├─ Global Metrics (Sharpe, Sortino, etc.)
    ├─ Per-Regime Metrics
    └─ Transition Analysis
    ↓
Visualization
    ├─ Equity Curve
    ├─ Regime Timeline
    └─ Transition Windows
```

### Design Patterns

**1. Strategy Pattern**
- Three interchangeable strategies control model retraining
- Each implements `should_retrain()` and `select_model()`
- Enables fair comparison without code duplication

**2. Factory Pattern**
- `build_model()` creates RF or XGBoost on demand
- Configurable via `MODEL_TYPE` parameter
- Easy to add new model types

**3. Base Class Pattern**
- `BaseTradingModel` defines interface
- All models inherit and implement `fit()`, `predict()`, `get_name()`
- Ensures compatibility with backtest engine

**4. Pipeline Architecture**
- Sequential stages: Fetch → Features → Regimes → Backtest → Analysis
- Each stage independent; can re-run without affecting others
- Modular and maintainable

---

## Key Concepts

### Regime Detection

**Hidden Markov Model (HMM)**
- **Method:** 2-state Gaussian HMM fitted on daily returns
- **Interpretation:** State 0 and State 1 represent different market regimes
- **Advantage:** Probabilistic; captures hidden state transitions
- **Output:** Regime labels (0 or 1) for each day

**Changepoint Detection (PELT)**
- **Method:** Pruned Exact Linear Time algorithm on returns
- **Interpretation:** Identifies structural breaks in return distribution
- **Advantage:** Deterministic; identifies exact breakpoints
- **Output:** Regime labels (0, 1, 2, ...) for each segment

**Combined Usage:**
- Both run independently
- Regime signature combines both: `"{HMM_Regime}|{CP_Regime}"`
- Provides robust regime identification

### Adaptation Strategies

**Static Strategy**
- Single global model trained once
- Retrains only on fixed interval (750 days)
- Ignores regime changes
- **Use Case:** Baseline; tests if regime awareness helps

**Regime-Specific Strategy**
- Maintains separate model per regime signature
- Retrains when entering new regime or on interval
- Switches model based on current regime
- **Use Case:** Tests if regime-specific models outperform

**Hybrid Strategy**
- Single global model (like Static)
- Retrains aggressively on regime change (like Regime-Specific)
- Combines benefits: model stability + regime responsiveness
- **Use Case:** Practical approach balancing stability and adaptation

### Walk-Forward Backtesting

**Rolling Window Approach**
```
Day 1-750:     Training window
Day 751:       Test (predict, execute, measure PnL)
Day 2-751:     Training window (shifted 1 day)
Day 752:       Test
...
Day 2975-3724: Training window
Day 3725:      Final test
```

**Prevents Overfitting:**
- No look-ahead bias (train on past, test on future)
- Realistic performance estimation
- Models adapt to changing market conditions

### Transaction Costs

**Cost Components**
- **Base Cost:** Fraction per trade (e.g., 0.0005 = 5 basis points)
- **Slippage:** Additional cost per trade (e.g., 0.0001 = 1 basis point)
- **Minimum Cost:** Floor cost per trade (e.g., 0.0001)

**Calculation**
```
cost = base_cost_rate * position_change + slippage_per_trade * position_change
cost = max(cost, min_cost)
```

**Impact on Returns**
- Reduces gross returns by cost amount
- Penalizes high-turnover strategies
- Encourages model stability

---

## Performance Metrics

### Global Metrics
- **Cumulative Return:** Total return from start to end
- **Annualized Return:** Annualized growth rate (252 trading days/year)
- **Annualized Volatility:** Annualized standard deviation of returns
- **Sharpe Ratio:** Return per unit of risk
- **Sortino Ratio:** Return per unit of downside risk
- **Max Drawdown:** Worst peak-to-trough decline
- **Calmar Ratio:** Return per unit of max drawdown
- **CVaR (5%):** Expected loss in worst 5% of days
- **Hit Ratio:** Fraction of correct predictions

### Per-Regime Metrics
- **Days in Regime:** Count of trading days
- **Average Return:** Mean daily return in regime
- **Sharpe Ratio:** Risk-adjusted return in regime
- **Max Drawdown:** Worst decline in regime
- **Calmar Ratio:** Return/drawdown in regime

### Transition Metrics
- **Transition Date:** When regime changed
- **From/To Regime:** Previous and new regime
- **Before/After Returns:** Average return ±20 days around transition
- **Before/After Drawdown:** Max drawdown ±20 days around transition

---

## Use Cases

### 1. Strategy Research
- Compare Static vs Regime-Specific vs Hybrid approaches
- Identify which strategy works best for different assets
- Quantify value of regime awareness

### 2. Model Evaluation
- Test new ML models (LSTM, SVM, etc.)
- Compare RandomForest vs XGBoost vs custom models
- Measure model stability across regimes

### 3. Risk Analysis
- Identify regime transition risks
- Analyze performance during market stress
- Stress-test strategies around structural breaks

### 4. Parameter Tuning
- Optimize transaction cost assumptions
- Tune regime detection parameters
- Adjust training window size

### 5. Academic Research
- Publish findings on regime-aware trading
- Compare regime detection methods
- Validate adaptation strategy effectiveness

---

## Limitations & Assumptions

### Limitations
1. **Daily Data Only:** Intraday dynamics not captured
2. **Single Asset:** Tests one asset at a time (can extend to portfolios)
3. **Binary Signals:** Predicts direction only (not magnitude)
4. **Fixed Position Size:** Always 1 unit (no dynamic sizing)
5. **No Shorting:** Only long or flat positions (can extend)

### Assumptions
1. **Frictionless Execution:** Assumes trades execute at close price
2. **No Slippage Variation:** Slippage constant (can be made dynamic)
3. **Regime Stationarity:** Assumes regimes are stationary (they evolve)
4. **Feature Stationarity:** Features don't have structural breaks (may not hold)
5. **No Regime Prediction:** Assumes regimes are detected, not predicted

---

## Future Enhancements

### Short-Term
- [ ] Add LSTM neural network model
- [ ] Implement ensemble strategies
- [ ] Add portfolio-level backtesting
- [ ] Support short positions

### Medium-Term
- [ ] Real-time backtesting engine
- [ ] Hyperparameter optimization (Optuna integration)
- [ ] Multi-asset portfolio optimization
- [ ] Risk parity strategy

### Long-Term
- [ ] Regime prediction (not just detection)
- [ ] Reinforcement learning strategies
- [ ] Market microstructure modeling
- [ ] High-frequency trading support

---

## Getting Started

### Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Run data fetch: `python data/fetch_data.py`
3. Engineer features: `python features/feature_engineering.py`
4. Detect regimes: `python regimes/hmm_detector.py && python regimes/changepoint_detector.py`
5. Merge regimes: `python scripts/merge_regimes.py`
6. Run backtest: `python backtest/walk_forward_engine.py`
7. Analyze results: `python scripts/perfMet_Script.py`

### Next Steps
- Read **DIRECTORY_STRUCTURE.md** for file organization
- Review **MODULE_BACKTEST.md** for configuration options
- Check **RESULTS_OUTPUTS.md** to interpret results
- See **EXTENSION_GUIDE.md** to add custom components

---

## References

### Key Papers
- Rabiner, L. R. (1989). "A tutorial on hidden Markov models"
- Killick, R., et al. (2012). "Optimal detection of changepoints"
- Sharpe, W. F. (1966). "Mutual fund performance"

### Libraries Used
- **hmmlearn:** Hidden Markov Models
- **ruptures:** Changepoint detection
- **scikit-learn:** Machine learning
- **xgboost:** Gradient boosting
- **yfinance:** Data fetching
- **pandas:** Data manipulation

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025
