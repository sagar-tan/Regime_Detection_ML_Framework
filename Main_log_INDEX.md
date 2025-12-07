# Regime-Aware ML Trading Framework - Documentation Index

**Project Name:** RegimeAwareTradingFramework  
**Version:** 1.0  
**Last Updated:** December 2025  
**Purpose:** Complete technical reference for developers and contributors

---

## 📚 Documentation Structure

This documentation is organized into modular files for easy navigation and reference:

### **Core Documentation**

1. **[PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)**
   - Project objectives and goals
   - Key differentiators from existing frameworks
   - Architecture and design philosophy
   - Supported assets and extensibility

2. **[DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md)**
   - Complete folder hierarchy
   - File organization and purposes
   - Data flow between directories
   - Output locations

3. **[DEPENDENCIES.md](./DEPENDENCIES.md)**
   - Python package requirements
   - Version compatibility
   - System requirements
   - Installation instructions

---

### **Module Documentation**

4. **[MODULE_UTILS.md](./MODULE_UTILS.md)**
   - Logger configuration and setup
   - Logging patterns used throughout project
   - Debug and error tracking

5. **[MODULE_DATA.md](./MODULE_DATA.md)**
   - Data fetching from Yahoo Finance
   - Data cleaning and validation
   - Raw data structure and format

6. **[MODULE_FEATURES.md](./MODULE_FEATURES.md)**
   - Feature engineering pipeline
   - Feature definitions and calculations
   - Data transformation steps

7. **[MODULE_REGIMES.md](./MODULE_REGIMES.md)**
   - HMM-based regime detection
   - Changepoint-based regime detection
   - Regime label generation and merging

8. **[MODULE_MODELS.md](./MODULE_MODELS.md)**
   - Base model interface
   - RandomForest implementation
   - XGBoost implementation
   - Model training and prediction

9. **[MODULE_STRATEGIES.md](./MODULE_STRATEGIES.md)**
   - Static strategy (baseline)
   - Regime-specific strategy
   - Hybrid strategy
   - Strategy comparison framework

10. **[MODULE_BACKTEST.md](./MODULE_BACKTEST.md)**
    - Walk-forward backtesting engine
    - Portfolio management and PnL calculation
    - Transaction cost computation
    - Backtest configuration and execution

11. **[MODULE_ANALYSIS.md](./MODULE_ANALYSIS.md)**
    - Performance metrics computation
    - Equity curve visualization
    - Regime timeline analysis
    - Transition window analysis

12. **[MODULE_SCRIPTS.md](./MODULE_SCRIPTS.md)**
    - Test models script
    - Merge regimes script
    - Performance metrics runner

---

### **Execution & Results**

13. **[DATA_PIPELINE.md](./DATA_PIPELINE.md)**
    - Step-by-step data flow
    - Processing sequence
    - Intermediate outputs
    - Final outputs

14. **[EXECUTION_GUIDE.md](./EXECUTION_GUIDE.md)**
    - Typical workflow commands
    - Configuration points
    - Parameter tuning
    - Troubleshooting

15. **[RESULTS_OUTPUTS.md](./RESULTS_OUTPUTS.md)**
    - Output file descriptions
    - CSV structure and columns
    - JSON log format
    - Results interpretation

16. **[LOG_ANALYSIS.md](./LOG_ANALYSIS.md)**
    - Log file summaries
    - Key findings from execution
    - Performance insights
    - Debugging information

---

### **Extension & Development**

17. **[EXTENSION_GUIDE.md](./EXTENSION_GUIDE.md)**
    - Adding new ML models
    - Creating custom strategies
    - Implementing new regime detectors
    - Adding performance metrics

18. **[DESIGN_PATTERNS.md](./DESIGN_PATTERNS.md)**
    - Strategy pattern implementation
    - Factory pattern usage
    - Base class pattern
    - Pipeline architecture

---

## 🚀 Quick Start

### For New Users:
1. Start with **PROJECT_OVERVIEW.md** to understand the framework
2. Read **DIRECTORY_STRUCTURE.md** to see how files are organized
3. Follow **EXECUTION_GUIDE.md** to run your first backtest
4. Check **RESULTS_OUTPUTS.md** to interpret results

### For Developers:
1. Review **DESIGN_PATTERNS.md** for architectural decisions
2. Study **MODULE_*.md** files for specific components
3. Use **EXTENSION_GUIDE.md** to add new features
4. Refer to **LOG_ANALYSIS.md** for debugging

### For Data Scientists:
1. Check **DATA_PIPELINE.md** for data flow
2. Review **MODULE_FEATURES.md** for feature definitions
3. Study **MODULE_REGIMES.md** for regime detection methods
4. Analyze **RESULTS_OUTPUTS.md** for performance metrics

---

## 📊 Project Statistics

- **Total Python Files:** 25
- **Total Modules:** 8 (data, features, regimes, models, strategies, backtest, analysis, scripts)
- **Data Points:** 3,725 trading days (2010-2025)
- **Assets Tested:** 6 (SPY, QQQ, IWM, XLF, GLD, TLT)
- **Features Computed:** 60 (10 per asset)
- **Regime Detection Methods:** 2 (HMM, Changepoint)
- **Adaptation Strategies:** 3 (Static, Regime-Specific, Hybrid)
- **ML Models Supported:** 2+ (RandomForest, XGBoost, extensible)
- **Performance Metrics:** 9+ (Sharpe, Sortino, CVaR, Calmar, etc.)

---

## 🔗 Cross-References

### By Topic

**Data Processing:**
- DIRECTORY_STRUCTURE.md → data/ folder
- MODULE_DATA.md → fetch_data.py
- MODULE_FEATURES.md → feature_engineering.py
- DATA_PIPELINE.md → Full sequence

**Regime Detection:**
- MODULE_REGIMES.md → hmm_detector.py, changepoint_detector.py
- LOG_ANALYSIS.md → Regime detection results
- RESULTS_OUTPUTS.md → Regime columns in outputs

**Model Training:**
- MODULE_MODELS.md → Model implementations
- MODULE_BACKTEST.md → Training within walk-forward loop
- EXTENSION_GUIDE.md → Adding new models

**Strategy Comparison:**
- MODULE_STRATEGIES.md → Strategy implementations
- MODULE_BACKTEST.md → Strategy selection logic
- RESULTS_OUTPUTS.md → Strategy-specific outputs

**Performance Analysis:**
- MODULE_ANALYSIS.md → Metric calculations
- RESULTS_OUTPUTS.md → Output formats
- LOG_ANALYSIS.md → Actual performance results

---

## 📝 Key Concepts

### Regime Detection
Two complementary methods detect market structure changes:
- **HMM:** 2-state Gaussian Hidden Markov Model on returns
- **Changepoint:** PELT algorithm for structural breaks

### Adaptation Strategies
Three strategies compare how models adapt to regimes:
- **Static:** Single model, interval retrain only
- **Regime-Specific:** Separate model per regime
- **Hybrid:** Global model, retrain on regime change

### Walk-Forward Backtesting
Rolling window validation ensures realistic performance:
- **Training Window:** 750 days (≈3 years)
- **Test Window:** 1 day (daily prediction)
- **Step Size:** 1 day forward
- **Total Backtest Period:** 2,975 trading days

### Transaction Costs
Realistic cost modeling includes:
- **Base Cost:** 5 basis points per trade (configurable)
- **Slippage:** Additional cost per trade (configurable)
- **Minimum Cost:** Floor cost per trade (configurable)

---

## 🎯 Common Tasks

### Run Full Backtest
See: **EXECUTION_GUIDE.md** → "Typical Workflow"

### Add New ML Model
See: **EXTENSION_GUIDE.md** → "Adding a New ML Model"

### Analyze Regime Transitions
See: **MODULE_ANALYSIS.md** → "Transition Analysis"

### Debug Training Issues
See: **LOG_ANALYSIS.md** → "Debugging Information"

### Compare Strategies
See: **MODULE_STRATEGIES.md** → "Strategy Comparison"

### Compute Custom Metrics
See: **MODULE_ANALYSIS.md** → "Extending Metrics"

---

## 📞 Support & Troubleshooting

### Common Issues

**"Missing column 'Date'" error:**
- See: LOG_ANALYSIS.md → feature_engineering.log findings

**Regime changes not detected:**
- See: MODULE_REGIMES.md → Changepoint penalty parameter

**Models not retraining:**
- See: MODULE_BACKTEST.md → Retrain decision logic

**Low backtest performance:**
- See: RESULTS_OUTPUTS.md → Interpreting metrics

---

## 📖 Document Conventions

- **Code blocks:** Python syntax highlighted
- **File paths:** Absolute paths from project root
- **Parameters:** Bold for emphasis, type hints included
- **Returns:** Documented with examples
- **Dependencies:** Listed at end of each module doc

---

## Version History

- **v1.0 (Dec 2025):** Initial release with HMM, Changepoint, RF, XGBoost, 3 strategies
- **Future:** LSTM models, ensemble strategies, real-time backtesting

---

**Last Updated:** December 7, 2025  
**Maintainer:** Regime Detection ML Framework Team
