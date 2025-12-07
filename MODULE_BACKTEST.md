# Module Documentation: Backtest - Walk-Forward Engine, Portfolio, Transaction Costs

**Document Version:** 1.0  
**Last Updated:** December 2025

---

## Overview

The backtest module implements realistic walk-forward backtesting with:
- Rolling training windows (750 days)
- Daily prediction and portfolio updates
- Regime change detection and strategy-based model selection
- Transaction cost application
- Detailed logging and result tracking

**Key Files:**
- `walk_forward_engine.py`: Core backtesting logic
- `portfolio.py`: Portfolio state and PnL tracking
- `transaction_costs.py`: Cost computation

---

## walk_forward_engine.py

### Purpose
Implements rolling window backtesting with regime-aware model selection and retraining.

### Configuration Parameters (Lines 24-57)

```python
TICKER = "SPY"                              # Asset to backtest
FEATURE_FILE = Path("data/processed/features_final_SPY.csv")
RESULTS_DIR = Path("results")               # Output directory
WINDOW_DAYS = 750                           # Training window (≈3 years)
RETRAIN_INTERVAL = WINDOW_DAYS              # Force retrain after this many days
PREDICTION_HORIZON = 1                      # Predict 1 day ahead
STEP_DAYS = 1                               # Move forward 1 day per iteration
MODEL_TYPE = "xgb"                          # "rf" or "xgb"
STRATEGY_MODE = "hybrid"                    # "static", "regime_specific", or "hybrid"
TRANSACTION_COST = 0.0005                   # 5 basis points per trade
REGIME_COLS = [f"{TICKER}_HMM_Regime", f"{TICKER}_CP_Regime"]
BLACKLIST = [f"{TICKER}_Target"] + REGIME_COLS  # Exclude from features
MIN_TRAIN_SAMPLES = 50                      # Minimum samples to train
RANDOM_STATE = 42                           # Reproducibility seed
```

### Helper Functions

#### `load_features(filepath=FEATURE_FILE) -> pd.DataFrame`
**Purpose:** Load processed features with regime labels

**Parameters:**
- `filepath` (Path): Path to features_final_SPY.csv

**Returns:** DataFrame with Date index, shape (3725, 62)

**Columns:**
- `SPY_Open`, `SPY_High`, `SPY_Low`, `SPY_Close`, `SPY_Volume`
- `SPY_Return`, `SPY_Vol20`, `SPY_SMA10`, `SPY_SMA50`
- `SPY_Target` (binary label: 0 or 1)
- `SPY_HMM_Regime` (0 or 1)
- `SPY_CP_Regime` (0, 1, 2, ...)

**Error Handling:**
- Raises `FileNotFoundError` if file doesn't exist
- Logs file path and shape

**Example:**
```python
df = load_features()
print(df.shape)  # (3725, 62)
print(df.columns)
```

---

#### `get_feature_columns(df, ticker=TICKER) -> list`
**Purpose:** Extract feature columns (exclude Target and Regime)

**Parameters:**
- `df` (pd.DataFrame): Feature DataFrame
- `ticker` (str): Asset symbol (default: "SPY")

**Returns:** List of feature column names

**Logic:**
```python
cols = [c for c in df.columns 
        if c.startswith(f"{ticker}_") and c not in BLACKLIST]
```

**Example:**
```python
feature_cols = get_feature_columns(df)
# Returns: ['SPY_Open', 'SPY_High', 'SPY_Low', 'SPY_Close', 'SPY_Volume',
#           'SPY_Return', 'SPY_Vol20', 'SPY_SMA10', 'SPY_SMA50']
# Length: 9
```

---

#### `build_model(model_type=MODEL_TYPE) -> BaseTradingModel`
**Purpose:** Factory function to create model instance

**Parameters:**
- `model_type` (str): "rf" or "xgb"

**Returns:** Instantiated model object

**Logic:**
```python
if model_type == "rf":
    return RandomForestTradingModel(n_estimators=200, max_depth=6, random_state=RANDOM_STATE)
elif model_type == "xgb":
    return XGBoostTradingModel(n_estimators=200, max_depth=4, learning_rate=0.1, random_state=RANDOM_STATE)
else:
    raise ValueError(f"Unknown model_type {model_type}")
```

**Example:**
```python
model = build_model("xgb")
print(model.get_name())  # "XGBoostTradingModel"
```

---

#### `regime_signature(df_row) -> str`
**Purpose:** Create regime identifier combining HMM and CP labels

**Parameters:**
- `df_row`: Single row from DataFrame (pd.Series)

**Returns:** String signature, e.g., "1|0"

**Logic:**
```python
values = []
for col in REGIME_COLS:  # [SPY_HMM_Regime, SPY_CP_Regime]
    if col in df_row.index:
        values.append(str(int(df_row[col])))
    else:
        values.append("NA")
return "|".join(values)
```

**Example:**
```python
row = df.iloc[100]
sig = regime_signature(row)
print(sig)  # "1|0" (HMM=1, CP=0)
```

**Usage:** Detect regime changes by comparing signatures between consecutive days

---

### Main Function: walk_forward_backtest()

#### Signature
```python
def walk_forward_backtest(
    df,
    ticker=TICKER,
    window_days=WINDOW_DAYS,
    retrain_interval=RETRAIN_INTERVAL,
    model_type=MODEL_TYPE,
    strategy_mode=STRATEGY_MODE,
    horizon=PREDICTION_HORIZON,
    transaction_cost=TRANSACTION_COST
) -> tuple(pd.DataFrame, pd.DataFrame, dict)
```

#### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `df` | DataFrame | - | Feature DataFrame with Date index |
| `ticker` | str | "SPY" | Asset symbol |
| `window_days` | int | 750 | Training window size in days |
| `retrain_interval` | int | 750 | Force retrain after this many days |
| `model_type` | str | "xgb" | "rf" or "xgb" |
| `strategy_mode` | str | "hybrid" | "static", "regime_specific", or "hybrid" |
| `horizon` | int | 1 | Prediction horizon (days ahead) |
| `transaction_cost` | float | 0.0005 | Cost per trade as fraction |

#### Returns

**Tuple of 3 elements:**
1. **signals_df** (DataFrame): Daily signals and returns
   - Columns: Signal, DayReturn, TradeCost, PnL, Equity, Regime
   - Index: Date
   - Shape: (2975, 6)

2. **equity_df** (DataFrame): Portfolio equity over time
   - Columns: Equity
   - Index: Date
   - Shape: (2975, 1)

3. **backtest_log** (dict): Detailed step-by-step log
   - Keys: "params" (dict), "runs" (list)
   - Each run contains: date, train_start, train_end, retrained, regime_changed, etc.

#### Algorithm

**Initialization (Lines 100-161):**
```
1. Load feature columns
2. Validate Target and Return columns exist
3. Instantiate strategy based on STRATEGY_MODE
4. Initialize Portfolio (equity=1.0)
5. Initialize TransactionCosts
6. Set start_idx = WINDOW_DAYS (750)
7. Initialize empty signals, equity, backtest_log lists
```

**Main Loop (Lines 164-292):**
```
for i from WINDOW_DAYS to len(df):
    1. Define training window: [i-WINDOW_DAYS, i-1]
    2. Skip if insufficient training samples
    
    3. Detect regime change:
       - Compare regime_signature(i-1) vs regime_signature(i)
       - Set regime_changed = True/False
    
    4. Strategy decision:
       - Call strategy.should_retrain(regime_changed, steps_since_last_retrain, retrain_interval)
       - Get force_retrain decision
    
    5. Model selection/training:
       - If STRATEGY_MODE == "regime_specific":
           * Get current regime signature
           * If model for this regime doesn't exist OR force_retrain:
               - Train new model on training window
               - Store in regime_models[signature]
           * Select model from regime_models
       - Else (static or hybrid):
           * If model is None OR force_retrain:
               - Train new global model
               - Update last_retrain_idx
           * Use global model
    
    6. Prediction:
       - For each day in horizon:
           * Get features for prediction day
           * Call model.predict(features)
           * Store prediction
       - Use first horizon prediction as signal
    
    7. Portfolio update:
       - Compute trade cost: tc.compute_trade_cost(prev_signal, signal)
       - Call portfolio.step(date, signal, day_return, trade_cost)
       - Get pnl and new_equity
    
    8. Logging:
       - Create step_log dict with all details
       - Append to backtest_log["runs"]
       - Append to signals and equity lists
    
    9. Advance: i += STEP_DAYS
```

**Output (Lines 294-315):**
```
1. Convert signals and equity lists to DataFrames
2. Save signals_df to results/signals_SPY.csv
3. Save equity_df to results/equity_curve_SPY.csv
4. Save trades_df to results/trades_SPY.csv
5. Save backtest_log to results/backtest_log_SPY.json
6. Return (signals_df, equity_df, backtest_log)
```

#### Key Variables

| Variable | Type | Purpose |
|---|---|---|
| `dates` | Index | DataFrame date index |
| `feature_cols` | list | Feature column names (9 for SPY) |
| `target_col` | str | Target column name |
| `ret_col` | str | Return column name |
| `regime_cols` | list | Regime detection columns |
| `n` | int | Total number of rows (3725) |
| `strategy` | Strategy | Strategy instance (Static/RegimeSpecific/Hybrid) |
| `model` | BaseTradingModel | Current global model |
| `regime_models` | dict | Maps regime signature → model (for regime_specific) |
| `portfolio` | Portfolio | Portfolio instance |
| `tc` | TransactionCosts | Transaction cost instance |
| `signals` | list | List of signal records |
| `equity` | list | List of equity records |
| `backtest_log` | dict | Detailed step log |
| `prev_signal` | int | Previous position (0 or 1) |
| `last_retrain_idx` | int | Index of last model training |

#### Example Execution

```python
# Load features
df = load_features()

# Run backtest
signals_df, equity_df, backtest_log = walk_forward_backtest(
    df,
    ticker="SPY",
    window_days=750,
    model_type="xgb",
    strategy_mode="hybrid",
    transaction_cost=0.0005
)

# Check results
print(f"Signals shape: {signals_df.shape}")  # (2975, 6)
print(f"Equity shape: {equity_df.shape}")    # (2975, 1)
print(f"Final equity: {equity_df['Equity'].iloc[-1]:.4f}")
print(f"Total retrains: {len([r for r in backtest_log['runs'] if r['retrained']])}")
```

#### Log Output Example

```
2025-12-04 21:32:04 | INFO | walk_forward_engine | ===== WALK-FORWARD BACKTEST ENGINE STARTED =====
2025-12-04 21:32:04 | INFO | walk_forward_engine | Loaded features: (3725, 62)
2025-12-04 21:32:04 | INFO | walk_forward_engine | Detected 9 feature columns for SPY
2025-12-04 21:32:04 | INFO | walk_forward_engine | Starting walk-forward. total samples: 3725
2025-12-04 21:32:04 | INFO | walk_forward_engine | Trained new global model at idx 749, retrain forced=False, regime_changed=False
2025-12-04 21:32:05 | INFO | walk_forward_engine | Trained new global model at idx 1149, retrain forced=True, regime_changed=True
[... more training events ...]
2025-12-04 21:32:09 | INFO | walk_forward_engine | Saved signals to results\signals_SPY.csv
2025-12-04 21:32:09 | INFO | walk_forward_engine | Saved equity curve to results\equity_curve_SPY.csv
2025-12-04 21:32:09 | INFO | walk_forward_engine | ===== WALK-FORWARD BACKTEST ENGINE FINISHED =====
```

---

## portfolio.py

### Purpose
Track portfolio state, compute PnL, and maintain trade history.

### Class: Portfolio (Dataclass)

#### Attributes

```python
@dataclass
class Portfolio:
    initial_equity: float = 1.0              # Starting capital
    cash_equity: float = field(default=None) # Current equity (auto-init to initial_equity)
    prev_signal: int = 0                     # Previous position (0 or 1)
    trade_count: int = 0                     # Total trades executed
    equity_history: list = field(default_factory=list)  # List of {Date, Equity} dicts
    trades_history: list = field(default_factory=list)  # List of trade dicts
```

#### Methods

##### `__post_init__() -> None`
**Purpose:** Initialize cash_equity if None; log initialization

**Behavior:**
```python
if self.cash_equity is None:
    self.cash_equity = float(self.initial_equity)
logger.info(f"Portfolio initialized with equity {self.cash_equity}")
```

---

##### `step(date, signal: int, day_return: float, trade_cost: float) -> tuple`
**Purpose:** Advance portfolio by one day

**Parameters:**
- `date`: Timestamp (pd.Timestamp or str)
- `signal` (int): Current position (0 or 1)
- `day_return` (float): Daily return as fraction (e.g., 0.01 for +1%)
- `trade_cost` (float): Transaction cost as fraction

**Returns:** Tuple (pnl, new_equity)

**Algorithm:**
```
1. Detect trade: trade_happened = (signal != prev_signal)
2. Increment trade_count if trade occurred
3. Compute PnL: pnl = signal * day_return - trade_cost
4. Update equity: new_equity = old_equity * (1.0 + pnl)
5. Record equity_history: {Date, Equity}
6. If trade occurred, record trades_history: {Date, prev_signal, new_signal, trade_cost, equity_before, equity_after}
7. Update prev_signal
8. Return (pnl, new_equity)
```

**Example:**
```python
portfolio = Portfolio(initial_equity=1.0)

# Day 1: Enter long position
pnl, equity = portfolio.step("2013-01-02", signal=1, day_return=0.0123, trade_cost=0.0005)
# pnl = 1 * 0.0123 - 0.0005 = 0.0118
# equity = 1.0 * (1.0 + 0.0118) = 1.0118

# Day 2: Stay long, positive return
pnl, equity = portfolio.step("2013-01-03", signal=1, day_return=0.0050, trade_cost=0.0000)
# pnl = 1 * 0.0050 - 0.0000 = 0.0050
# equity = 1.0118 * (1.0 + 0.0050) = 1.0168

# Day 3: Exit position
pnl, equity = portfolio.step("2013-01-04", signal=0, day_return=-0.0020, trade_cost=0.0005)
# pnl = 0 * (-0.0020) - 0.0005 = -0.0005
# equity = 1.0168 * (1.0 - 0.0005) = 1.0163
```

---

##### `to_equity_df() -> pd.DataFrame`
**Purpose:** Convert equity history to DataFrame

**Returns:** DataFrame with Date index and Equity column

**Example:**
```python
df_equity = portfolio.to_equity_df()
# Columns: Equity
# Index: Date (sorted)
# Shape: (2975, 1)
```

---

##### `trades_df() -> pd.DataFrame`
**Purpose:** Convert trade history to DataFrame

**Returns:** DataFrame with trade details

**Columns:**
- `Date`: Trade date
- `prev_signal`: Previous position
- `new_signal`: New position
- `trade_cost`: Cost of this trade
- `equity_before`: Equity before trade
- `equity_after`: Equity after trade

**Example:**
```python
df_trades = portfolio.trades_df()
# Shows only days when position changed
# Shape: (n_trades, 6)
```

---

##### `stats() -> dict`
**Purpose:** Compute portfolio statistics

**Returns:** Dictionary with portfolio metrics

**Keys:**
- `final_equity` (float): Final portfolio value
- `initial_equity` (float): Starting value
- `cumulative_return` (float): (final/initial) - 1
- `total_trades` (int): Number of trades
- `max_drawdown` (float): Worst peak-to-trough decline

**Algorithm:**
```
1. Extract equity values as numpy array
2. Compute cumulative return: (final / initial) - 1
3. Compute high-water mark (HWM): cummax(equities)
4. Compute drawdowns: (equity - HWM) / HWM
5. Get max_drawdown: min(drawdowns)
6. Return dict with all metrics
```

**Example:**
```python
stats = portfolio.stats()
# {
#     'final_equity': 1.2345,
#     'initial_equity': 1.0,
#     'cumulative_return': 0.2345,
#     'total_trades': 42,
#     'max_drawdown': -0.0567
# }
```

---

##### `save_equity(path: str) -> None`
**Purpose:** Save equity history to CSV

**Parameters:**
- `path` (str): Output file path

**Behavior:** Calls `to_equity_df().to_csv(path, index=True)`

**Example:**
```python
portfolio.save_equity("results/equity_curve_SPY.csv")
```

---

##### `save_trades(path: str) -> None`
**Purpose:** Save trade history to CSV

**Parameters:**
- `path` (str): Output file path

**Behavior:** Calls `trades_df().to_csv(path, index=True)`

**Example:**
```python
portfolio.save_trades("results/trades_SPY.csv")
```

---

## transaction_costs.py

### Purpose
Compute transaction costs, slippage, and spreads.

### Class: TransactionCosts

#### Constructor

```python
def __init__(self, base_cost_rate=0.0005, slippage_per_trade=0.0000, min_cost=0.0)
```

**Parameters:**
- `base_cost_rate` (float): Fraction charged per trade (default: 0.0005 = 5 bps)
- `slippage_per_trade` (float): Extra slippage fraction (default: 0.0)
- `min_cost` (float): Minimum absolute cost per trade (default: 0.0)

**Example:**
```python
tc = TransactionCosts(base_cost_rate=0.0005, slippage_per_trade=0.0001, min_cost=0.0)
```

---

#### Methods

##### `compute_trade_cost(prev_signal: int, new_signal: int, notional: float = 1.0) -> float`
**Purpose:** Compute cost for position change

**Parameters:**
- `prev_signal` (int): Previous position (0 or 1)
- `new_signal` (int): New position (0 or 1)
- `notional` (float): Portfolio notional for scaling (default: 1.0)

**Returns:** Cost as fraction of notional

**Algorithm:**
```
1. Compute position change: change = abs(new_signal - prev_signal)
2. If change == 0: return 0.0 (no trade)
3. Compute base cost: cost = base_cost_rate * change
4. Add slippage: cost += slippage_per_trade * change
5. Apply minimum cost: cost = max(cost, min_cost / notional)
6. Return cost
```

**Examples:**
```python
tc = TransactionCosts(base_cost_rate=0.0005, slippage_per_trade=0.0001)

# No trade
cost = tc.compute_trade_cost(0, 0, notional=1.0)
# cost = 0.0

# Enter long
cost = tc.compute_trade_cost(0, 1, notional=1.0)
# cost = 0.0005 * 1 + 0.0001 * 1 = 0.0006

# Exit long
cost = tc.compute_trade_cost(1, 0, notional=1.0)
# cost = 0.0005 * 1 + 0.0001 * 1 = 0.0006

# Stay long
cost = tc.compute_trade_cost(1, 1, notional=1.0)
# cost = 0.0
```

---

##### `compute_round_trip_cost(n_trades: int, notional: float = 1.0) -> float`
**Purpose:** Estimate total cost for n round-trip trades

**Parameters:**
- `n_trades` (int): Number of round-trip trades
- `notional` (float): Portfolio notional

**Returns:** Total cost

**Algorithm:**
```
cost_per_trade = compute_trade_cost(0, 1, notional)
return n_trades * cost_per_trade
```

**Example:**
```python
tc = TransactionCosts(base_cost_rate=0.0005)
total_cost = tc.compute_round_trip_cost(n_trades=50, notional=1.0)
# total_cost = 50 * 0.0005 = 0.025 (2.5% of notional)
```

---

##### `get_config() -> dict`
**Purpose:** Return cost configuration

**Returns:** Dictionary with cost parameters

**Example:**
```python
config = tc.get_config()
# {
#     'base_cost_rate': 0.0005,
#     'slippage_per_trade': 0.0001,
#     'min_cost': 0.0
# }
```

---

## Integration Example

```python
# Load features
df = load_features()

# Run backtest with all components
signals_df, equity_df, backtest_log = walk_forward_backtest(
    df,
    ticker="SPY",
    window_days=750,
    model_type="xgb",
    strategy_mode="hybrid",
    transaction_cost=0.0005
)

# Analyze results
print(f"Final Equity: {equity_df['Equity'].iloc[-1]:.4f}")
print(f"Total Return: {(equity_df['Equity'].iloc[-1] - 1.0) * 100:.2f}%")
print(f"Total Trades: {len(signals_df[signals_df['Signal'] != signals_df['Signal'].shift()])}")
print(f"Max Drawdown: {signals_df['Equity'].min() / signals_df['Equity'].max() - 1:.4f}")

# Save results
signals_df.to_csv("results/signals_SPY.csv")
equity_df.to_csv("results/equity_curve_SPY.csv")
```

---

## Dependencies

- `json`: Backtest log serialization
- `pathlib`: File path handling
- `numpy`: Numerical computations
- `pandas`: Data manipulation
- `datetime`: Date/time handling
- `logging`: Logging
- `dataclasses`: Portfolio dataclass
- `models`: ML model implementations
- `strategies`: Strategy implementations
- `transaction_costs`: Cost computation
- `portfolio`: Portfolio management

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025
