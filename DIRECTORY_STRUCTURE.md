# Directory Structure - Regime-Aware ML Trading Framework

**Document Version:** 1.0  
**Last Updated:** December 2025

---

## Complete Project Hierarchy

```
RDMA_ML_Framework/
│
├── 📁 data/                          # Data storage (raw and processed)
│   ├── 📁 raw/                       # Downloaded OHLCV data
│   │   ├── SPY.csv                   # 3774 rows × 5 cols (Open, High, Low, Close, Volume)
│   │   ├── QQQ.csv                   # 2010-01-01 to 2025-01-01
│   │   ├── IWM.csv
│   │   ├── XLF.csv
│   │   ├── GLD.csv
│   │   └── TLT.csv
│   │
│   └── 📁 processed/                 # Processed features and regimes
│       ├── features_merged.csv       # Base features (3725 rows × 60 cols)
│       │                             # Columns: Date, {ticker}_{OHLCV,Return,Vol20,SMA10,SMA50,Target}
│       ├── features_with_hmm_SPY.csv # Base features + SPY_HMM_Regime column
│       ├── features_with_cp_SPY.csv  # Base features + SPY_CP_Regime column
│       └── features_final_SPY.csv    # Merged: all features + both regime columns (3725 × 62)
│
├── 📁 features/                      # Feature engineering module
│   ├── feature_engineering.py        # Main feature computation script
│   │                                 # Functions: load_and_merge_data(), compute_features(), save_processed()
│   └── __pycache__/                  # Python cache
│
├── 📁 regimes/                       # Regime detection module
│   ├── hmm_detector.py               # HMM-based regime detection
│   │                                 # Functions: load_features(), extract_series_for_regime(),
│   │                                 #           fit_hmm(), infer_regimes(), attach_regime_labels(),
│   │                                 #           save_regime_file()
│   ├── changepoint_detector.py       # Changepoint-based regime detection
│   │                                 # Functions: load_features(), extract_series_for_cp(),
│   │                                 #           detect_changepoints(), convert_breaks_to_labels(),
│   │                                 #           attach_cp_labels(), save_cp_file()
│   └── __pycache__/
│
├── 📁 models/                        # ML model implementations
│   ├── base_model.py                 # Abstract base class
│   │                                 # Class: BaseTradingModel
│   │                                 # Methods: fit(), predict(), get_name()
│   ├── random_forest.py              # RandomForest classifier
│   │                                 # Class: RandomForestTradingModel(BaseTradingModel)
│   │                                 # Hyperparams: n_estimators=200, max_depth=6
│   ├── xgboost_model.py              # XGBoost classifier
│   │                                 # Class: XGBoostTradingModel(BaseTradingModel)
│   │                                 # Hyperparams: n_estimators=200, max_depth=4, lr=0.1
│   └── __pycache__/
│
├── 📁 strategies/                    # Adaptation strategy implementations
│   ├── static.py                     # Static strategy (no regime adaptation)
│   │                                 # Class: StaticStrategy
│   │                                 # Methods: should_retrain(), select_model()
│   ├── regime_specific.py            # Regime-specific strategy (separate model per regime)
│   │                                 # Class: RegimeSpecificStrategy
│   ├── hybrid.py                     # Hybrid strategy (global model, retrain on regime change)
│   │                                 # Class: HybridStrategy
│   └── __pycache__/
│
├── 📁 backtest/                      # Backtesting module
│   ├── walk_forward_engine.py        # Core walk-forward backtesting engine
│   │                                 # Configuration: TICKER, WINDOW_DAYS, MODEL_TYPE, STRATEGY_MODE, etc.
│   │                                 # Functions: load_features(), get_feature_columns(), build_model(),
│   │                                 #           regime_signature(), walk_forward_backtest()
│   ├── portfolio.py                  # Portfolio state and PnL management
│   │                                 # Class: Portfolio (dataclass)
│   │                                 # Methods: step(), to_equity_df(), trades_df(), stats(),
│   │                                 #         save_equity(), save_trades()
│   ├── transaction_costs.py          # Transaction cost computation
│   │                                 # Class: TransactionCosts
│   │                                 # Methods: compute_trade_cost(), compute_round_trip_cost(),
│   │                                 #         get_config()
│   └── __pycache__/
│
├── 📁 analysis/                      # Performance analysis and visualization
│   ├── performance_metrics.py        # Metric computation
│   │                                 # Functions: cumulative_return(), annualized_return(),
│   │                                 #           sharpe_ratio(), sortino_ratio(), max_drawdown(),
│   │                                 #           calmar_ratio(), cvar(), hit_ratio(),
│   │                                 #           regime_performance(), transition_metrics(),
│   │                                 #           compute_all_metrics()
│   ├── plot_equity.py                # Equity curve visualization
│   │                                 # Function: plot_equity_curve()
│   ├── plot_regimes.py               # Regime timeline visualization
│   │                                 # Function: plot_regime_timeline()
│   ├── plot_transitions.py           # Regime transition window analysis
│   │                                 # Function: plot_transition_windows()
│   ├── utils_plot.py                 # Plotting utilities
│   │                                 # Variables: colors (dict)
│   │                                 # Function: savefig()
│   ├── generate_all_plots.py         # Batch plot generation
│   │                                 # Function: generate_all()
│   └── __pycache__/
│
├── 📁 scripts/                       # Utility scripts
│   ├── test_models.py                # Quick model validation
│   │                                 # Functions: load_sample_features(), main()
│   ├── merge_regimes.py              # Merge HMM and CP regime columns
│   │                                 # Merges features_with_hmm_SPY.csv + features_with_cp_SPY.csv
│   │                                 # Output: features_final_SPY.csv
│   ├── perfMet_Script.py             # Performance metrics runner
│   │                                 # Calls: compute_all_metrics()
│   └── __pycache__/
│
├── 📁 utils/                         # Utility modules
│   ├── __init__.py                   # Package initialization (empty)
│   ├── logger.py                     # Centralized logging setup
│   │                                 # Function: setup_logger()
│   └── __pycache__/
│
├── 📁 logs/                          # Execution logs (one per module)
│   ├── fetch_data.log                # Data fetching logs
│   ├── feature_engineering.log       # Feature computation logs
│   ├── hmm_detector.log              # HMM regime detection logs
│   ├── changepoint_detector.log      # Changepoint detection logs
│   ├── random_forest.log             # RandomForest training logs
│   ├── xgboost_model.log             # XGBoost training logs
│   ├── walk_forward_engine.log       # Backtest execution logs
│   ├── performance_metrics.log       # Metrics computation logs
│   ├── strategy_static.log           # Static strategy logs
│   ├── strategy_regime_specific.log  # Regime-specific strategy logs
│   ├── strategy_hybrid.log           # Hybrid strategy logs
│   ├── test_models.log               # Model testing logs
│   └── base_model.log                # Base model logs
│
├── 📁 results/                       # Backtest outputs
│   ├── signals_SPY.csv               # Daily signals and returns
│   │                                 # Columns: Date, Signal, DayReturn, TradeCost, PnL, Equity, Regime
│   │                                 # Rows: 2975 (from day 750 to 3724)
│   ├── equity_curve_SPY.csv          # Portfolio equity over time
│   │                                 # Columns: Date, Equity
│   ├── trades_SPY.csv                # Trade execution log
│   │                                 # Columns: Date, prev_signal, new_signal, trade_cost,
│   │                                 #         equity_before, equity_after
│   ├── backtest_log_SPY.json         # Detailed step-by-step backtest log
│   │                                 # Structure: params (dict) + runs (list of dicts)
│   │                                 # Each run: date, train_start, train_end, retrained,
│   │                                 #          regime_changed, regime_signature, signal,
│   │                                 #          day_return, trade_cost, pnl, equity, model_used
│   └── 📁 figures/                   # Generated plots
│       ├── equity_curve_SPY.png      # Equity curve plot
│       ├── hmm_timeline_SPY.png      # HMM regime timeline
│       └── transition_window_SPY.png # Regime transition window analysis
│
├── 📄 Details.json                   # Project specification document
│                                     # Contains: project_name, goals, inputs, processing_pipeline,
│                                     #          outputs, folder_structure, modularity_design
│
├── 📄 requirements.txt               # Python package dependencies
│                                     # Packages: numpy, pandas, scipy, matplotlib, seaborn,
│                                     #          scikit-learn, xgboost, ruptures, yfinance,
│                                     #          hmmlearn, jupyter, ipykernel, pyyaml, tqdm
│
├── 📄 main.py                        # Entry point (currently placeholder)
│
├── 📄 Main_log_INDEX.md              # Documentation index (this file)
├── 📄 PROJECT_OVERVIEW.md            # Project overview and objectives
├── 📄 DIRECTORY_STRUCTURE.md         # This file
├── 📄 DEPENDENCIES.md                # Dependencies and requirements
├── 📄 MODULE_UTILS.md                # Utils module documentation
├── 📄 MODULE_DATA.md                 # Data module documentation
├── 📄 MODULE_FEATURES.md             # Features module documentation
├── 📄 MODULE_REGIMES.md              # Regimes module documentation
├── 📄 MODULE_MODELS.md               # Models module documentation
├── 📄 MODULE_STRATEGIES.md           # Strategies module documentation
├── 📄 MODULE_BACKTEST.md             # Backtest module documentation
├── 📄 MODULE_ANALYSIS.md             # Analysis module documentation
├── 📄 MODULE_SCRIPTS.md              # Scripts module documentation
├── 📄 DATA_PIPELINE.md               # Data pipeline documentation
├── 📄 EXECUTION_GUIDE.md             # Execution and configuration guide
├── 📄 RESULTS_OUTPUTS.md             # Results and outputs documentation
├── 📄 LOG_ANALYSIS.md                # Log analysis and findings
├── 📄 EXTENSION_GUIDE.md             # Extension and development guide
├── 📄 DESIGN_PATTERNS.md             # Design patterns documentation
│
├── 📄 .git/                          # Git repository
└── 📄 .venv/                         # Virtual environment (if created)
```

---

## Directory Purposes

### `data/`
**Purpose:** Store raw and processed data  
**Contents:**
- `raw/`: Downloaded OHLCV data from Yahoo Finance (6 tickers × 3774 rows)
- `processed/`: Computed features and regime labels

**Key Files:**
- `features_merged.csv`: Base features before regime detection
- `features_final_SPY.csv`: Final feature file with all regimes (input to backtest)

**Typical Size:** ~500 MB (raw data) + ~50 MB (processed)

---

### `features/`
**Purpose:** Feature engineering pipeline  
**Contents:**
- `feature_engineering.py`: Main script for feature computation

**Key Functions:**
- Load and merge multi-ticker data
- Compute Return, Vol20, SMA10, SMA50, Target per ticker
- Handle NaN values and data alignment

**Output:** `data/processed/features_merged.csv`

---

### `regimes/`
**Purpose:** Regime detection implementations  
**Contents:**
- `hmm_detector.py`: HMM-based detection
- `changepoint_detector.py`: Changepoint-based detection

**Key Functions:**
- Fit regime detection models
- Predict regime labels
- Save regime-augmented feature files

**Output:** 
- `data/processed/features_with_hmm_SPY.csv`
- `data/processed/features_with_cp_SPY.csv`

---

### `models/`
**Purpose:** ML model implementations  
**Contents:**
- `base_model.py`: Abstract interface
- `random_forest.py`: RandomForest classifier
- `xgboost_model.py`: XGBoost classifier

**Key Classes:**
- `BaseTradingModel`: Interface all models must implement
- `RandomForestTradingModel`: RF with 200 trees, depth 6
- `XGBoostTradingModel`: XGB with 200 trees, depth 4, lr=0.1

**Extensibility:** Add new models by inheriting from `BaseTradingModel`

---

### `strategies/`
**Purpose:** Adaptation strategy implementations  
**Contents:**
- `static.py`: Static strategy (no regime adaptation)
- `regime_specific.py`: Regime-specific strategy
- `hybrid.py`: Hybrid strategy

**Key Classes:**
- `StaticStrategy`: Single model, interval retrain
- `RegimeSpecificStrategy`: Model per regime, retrain on change
- `HybridStrategy`: Global model, retrain on regime change

**Extensibility:** Add new strategies by implementing `should_retrain()` and `select_model()`

---

### `backtest/`
**Purpose:** Backtesting engine and portfolio management  
**Contents:**
- `walk_forward_engine.py`: Core backtesting logic
- `portfolio.py`: Portfolio state and PnL tracking
- `transaction_costs.py`: Cost computation

**Key Functions:**
- Rolling window training and testing
- Regime change detection
- Strategy-based model selection
- Portfolio equity tracking

**Configuration:** Edit parameters in `walk_forward_engine.py` (lines 24-57)

---

### `analysis/`
**Purpose:** Performance analysis and visualization  
**Contents:**
- `performance_metrics.py`: Metric computation
- `plot_*.py`: Visualization functions
- `utils_plot.py`: Plotting utilities

**Key Functions:**
- Compute Sharpe, Sortino, CVaR, Calmar, etc.
- Per-regime performance analysis
- Regime transition analysis
- Generate equity curve, regime timeline, transition plots

**Output:** `results/figures/*.png` and metrics dictionary

---

### `scripts/`
**Purpose:** Utility and helper scripts  
**Contents:**
- `test_models.py`: Quick model validation
- `merge_regimes.py`: Merge regime files
- `perfMet_Script.py`: Metrics runner

**Key Functions:**
- Test model implementations
- Merge HMM and CP regimes
- Compute and print performance metrics

**Usage:** Run individually for specific tasks

---

### `utils/`
**Purpose:** Shared utility modules  
**Contents:**
- `logger.py`: Centralized logging setup

**Key Functions:**
- `setup_logger()`: Create logger with file and console handlers

**Usage:** Imported by all modules for consistent logging

---

### `logs/`
**Purpose:** Store execution logs  
**Contents:** One log file per module

**Key Files:**
- `walk_forward_engine.log`: Most important; shows backtest execution
- `feature_engineering.log`: Data processing status
- `xgboost_model.log`: Model training details

**Usage:** Debug issues by reviewing relevant log file

---

### `results/`
**Purpose:** Store backtest outputs  
**Contents:**
- `signals_SPY.csv`: Daily signals and returns
- `equity_curve_SPY.csv`: Portfolio equity
- `trades_SPY.csv`: Trade execution log
- `backtest_log_SPY.json`: Detailed step-by-step log
- `figures/`: Generated plots

**Key Files:**
- `signals_SPY.csv`: Input to performance metrics
- `backtest_log_SPY.json`: Detailed debugging info

**Usage:** Analyze results, generate reports, visualize performance

---

## Data Flow Between Directories

```
data/raw/
  ↓ (fetch_data.py)
  ↓
features/feature_engineering.py
  ↓
data/processed/features_merged.csv
  ↓ (parallel)
  ├─→ regimes/hmm_detector.py
  │     ↓
  │     data/processed/features_with_hmm_SPY.csv
  │
  └─→ regimes/changepoint_detector.py
        ↓
        data/processed/features_with_cp_SPY.csv
  ↓ (merge_regimes.py)
  ↓
data/processed/features_final_SPY.csv
  ↓ (walk_forward_engine.py)
  ↓
results/signals_SPY.csv
results/equity_curve_SPY.csv
results/trades_SPY.csv
results/backtest_log_SPY.json
  ↓ (parallel)
  ├─→ analysis/performance_metrics.py
  │     ↓
  │     Metrics dictionary (printed)
  │
  └─→ analysis/generate_all_plots.py
        ↓
        results/figures/*.png
```

---

## File Size Estimates

| File/Directory | Size | Notes |
|---|---|---|
| data/raw/ | ~500 MB | 6 tickers × 3774 rows × 5 columns |
| data/processed/features_merged.csv | ~50 MB | 3725 rows × 60 columns |
| data/processed/features_final_SPY.csv | ~5 MB | 3725 rows × 62 columns (used for backtest) |
| results/signals_SPY.csv | ~5 MB | 2975 rows × 7 columns |
| results/backtest_log_SPY.json | ~50 MB | 2975 runs × detailed step info |
| logs/ | ~5 MB | All log files combined |
| results/figures/ | ~2 MB | 3 PNG plots at 200 DPI |
| **Total** | **~600 MB** | Full project with all outputs |

---

## Key Relationships

### Module Dependencies

```
main.py
  ↓
backtest/walk_forward_engine.py
  ├─→ models/ (base_model, random_forest, xgboost_model)
  ├─→ strategies/ (static, regime_specific, hybrid)
  ├─→ backtest/ (portfolio, transaction_costs)
  └─→ utils/logger.py

analysis/performance_metrics.py
  ├─→ utils/logger.py
  └─→ (reads results/signals_SPY.csv)

analysis/plot_*.py
  ├─→ analysis/utils_plot.py
  └─→ (reads results/signals_SPY.csv, data/processed/features_final_SPY.csv)

features/feature_engineering.py
  ├─→ utils/logger.py
  └─→ (reads data/raw/*.csv)

regimes/hmm_detector.py, changepoint_detector.py
  ├─→ utils/logger.py
  └─→ (reads data/processed/features_merged.csv)

scripts/merge_regimes.py
  └─→ (reads data/processed/features_with_hmm_SPY.csv, features_with_cp_SPY.csv)
```

---

## Configuration Files

### `Details.json`
- **Purpose:** Project specification document
- **Contents:** Project goals, inputs, processing pipeline, outputs, folder structure
- **Usage:** Reference for project design decisions

### `requirements.txt`
- **Purpose:** Python package dependencies
- **Contents:** Package names (versions not specified for flexibility)
- **Usage:** `pip install -r requirements.txt`

### `walk_forward_engine.py` (lines 24-57)
- **Purpose:** Backtest configuration
- **Contents:** TICKER, WINDOW_DAYS, MODEL_TYPE, STRATEGY_MODE, TRANSACTION_COST, etc.
- **Usage:** Edit to change backtest parameters

---

## Adding New Components

### To Add a New Model
1. Create `models/my_model.py`
2. Inherit from `BaseTradingModel`
3. Implement `fit()`, `predict()`, `get_name()`
4. Update `walk_forward_engine.py` to support new model type

### To Add a New Strategy
1. Create `strategies/my_strategy.py`
2. Implement `should_retrain()` and `select_model()`
3. Update `walk_forward_engine.py` to support new strategy

### To Add a New Regime Detector
1. Create `regimes/my_detector.py`
2. Implement regime detection logic
3. Update `merge_regimes.py` to include new regime column

### To Add a New Metric
1. Add function to `analysis/performance_metrics.py`
2. Call from `compute_all_metrics()`
3. Update results output format

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025
