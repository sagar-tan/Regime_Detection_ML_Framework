# BTC_Framework/features/feature_engineering_BTC.py
# Feature engineering for BTC-USD

import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TICKER = "BTC-USD"
RAW_DATA_PATH = Path("data/raw") / f"{TICKER}.csv"
PROCESSED_DATA_DIR = Path("data/processed")
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Feature parameters
PREDICTION_HORIZON = 1
RETURN_THRESHOLD = 0.0

def load_raw_data(filepath=RAW_DATA_PATH):
    """Load raw BTC data."""
    logger.info(f"Loading raw data from {filepath}")
    df = pd.read_csv(filepath, parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    logger.info(f"Loaded {len(df)} rows")
    return df

def compute_returns(df, ticker=TICKER):
    """Compute daily returns."""
    logger.info("Computing daily returns...")
    df[f'{ticker}_Return'] = df['close'].pct_change()
    logger.info(f"Added {ticker}_Return column")
    return df

def compute_sma(df, ticker=TICKER, periods=[10, 20, 50, 100, 200]):
    """Compute Simple Moving Averages."""
    logger.info(f"Computing SMAs: {periods}")
    for period in periods:
        col_name = f'{ticker}_SMA{period}'
        df[col_name] = df['close'].rolling(window=period).mean()
    logger.info(f"Added {len(periods)} SMA columns")
    return df

def compute_ema(df, ticker=TICKER, periods=[12, 26]):
    """Compute Exponential Moving Averages."""
    logger.info(f"Computing EMAs: {periods}")
    for period in periods:
        col_name = f'{ticker}_EMA{period}'
        df[col_name] = df['close'].ewm(span=period, adjust=False).mean()
    logger.info(f"Added {len(periods)} EMA columns")
    return df

def compute_macd(df, ticker=TICKER):
    """Compute MACD."""
    logger.info("Computing MACD...")
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df[f'{ticker}_MACD'] = ema12 - ema26
    df[f'{ticker}_Signal'] = df[f'{ticker}_MACD'].ewm(span=9, adjust=False).mean()
    df[f'{ticker}_MACD_Hist'] = df[f'{ticker}_MACD'] - df[f'{ticker}_Signal']
    logger.info("Added MACD columns")
    return df

def compute_rsi(df, ticker=TICKER, period=14):
    """Compute Relative Strength Index."""
    logger.info(f"Computing RSI (period={period})...")
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df[f'{ticker}_RSI{period}'] = 100 - (100 / (1 + rs))
    logger.info("Added RSI column")
    return df

def compute_bollinger_bands(df, ticker=TICKER, period=20, num_std=2):
    """Compute Bollinger Bands."""
    logger.info(f"Computing Bollinger Bands (period={period}, std={num_std})...")
    sma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    df[f'{ticker}_BB_Upper'] = sma + (std * num_std)
    df[f'{ticker}_BB_Middle'] = sma
    df[f'{ticker}_BB_Lower'] = sma - (std * num_std)
    logger.info("Added Bollinger Bands columns")
    return df

def compute_volatility(df, ticker=TICKER, period=20):
    """Compute rolling volatility."""
    logger.info(f"Computing volatility (period={period})...")
    df[f'{ticker}_Vol{period}'] = df[f'{ticker}_Return'].rolling(window=period).std()
    logger.info("Added volatility column")
    return df

def compute_atr(df, ticker=TICKER, period=14):
    """Compute Average True Range."""
    logger.info(f"Computing ATR (period={period})...")
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df[f'{ticker}_ATR{period}'] = tr.rolling(window=period).mean()
    logger.info("Added ATR column")
    return df

def compute_target(df, ticker=TICKER, horizon=PREDICTION_HORIZON, threshold=RETURN_THRESHOLD):
    """Compute binary target: 1 if future return > threshold, else 0."""
    logger.info(f"Computing target (horizon={horizon}, threshold={threshold})...")
    future_return = df[f'{ticker}_Return'].shift(-horizon)
    df[f'{ticker}_Target'] = (future_return > threshold).astype(int)
    logger.info(f"Added {ticker}_Target column")
    return df

def engineer_features(df, ticker=TICKER):
    """Apply all feature engineering steps."""
    logger.info("Starting feature engineering...")
    
    df = compute_returns(df, ticker)
    df = compute_sma(df, ticker)
    df = compute_ema(df, ticker)
    df = compute_macd(df, ticker)
    df = compute_rsi(df, ticker)
    df = compute_bollinger_bands(df, ticker)
    df = compute_volatility(df, ticker)
    df = compute_atr(df, ticker)
    df = compute_target(df, ticker)
    
    logger.info("Feature engineering completed")
    return df

def select_features(df, ticker=TICKER):
    """Select relevant features for modeling."""
    logger.info("Selecting features...")
    
    feature_cols = [col for col in df.columns if col.startswith(ticker)]
    feature_cols = [col for col in feature_cols if col not in [f'{ticker}_Target']]
    
    logger.info(f"Selected {len(feature_cols)} features")
    return feature_cols

def save_features(df, ticker=TICKER):
    """Save engineered features."""
    output_path = PROCESSED_DATA_DIR / f"features_final_{ticker}.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved features to {output_path}")
    return output_path

def main():
    """Main execution."""
    logger.info("=" * 80)
    logger.info(f"FEATURE ENGINEERING FOR {TICKER} STARTED")
    logger.info("=" * 80)
    
    # Load raw data
    df = load_raw_data()
    
    # Engineer features
    df = engineer_features(df, TICKER)
    
    # Remove rows with NaN (from rolling calculations)
    initial_rows = len(df)
    df = df.dropna()
    logger.info(f"Removed {initial_rows - len(df)} rows with NaN values")
    
    # Save features
    output_path = save_features(df, TICKER)
    
    logger.info("=" * 80)
    logger.info(f"FEATURE ENGINEERING FOR {TICKER} COMPLETED")
    logger.info("=" * 80)
    logger.info(f"\nFeature Summary:")
    logger.info(f"  Rows: {len(df)}")
    logger.info(f"  Columns: {len(df.columns)}")
    logger.info(f"  Date Range: {df['date'].min()} to {df['date'].max()}")
    logger.info(f"  Saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    df = main()
