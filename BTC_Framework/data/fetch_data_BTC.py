# BTC_Framework/data/fetch_data_BTC.py
# Fetch BTC-USD OHLCV data from Yahoo Finance

import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TICKER = "BTC-USD"
START_DATE = "2015-01-01"  # Earlier start for more historical data
END_DATE = datetime.now().strftime("%Y-%m-%d")
RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_btc_data(ticker=TICKER, start=START_DATE, end=END_DATE):
    """
    Fetch BTC-USD OHLCV data from Yahoo Finance.
    
    Args:
        ticker: Ticker symbol (default: BTC-USD)
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
    
    Returns:
        DataFrame with OHLCV data
    """
    logger.info(f"Fetching {ticker} data from {start} to {end}...")
    
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        
        if df.empty:
            logger.error(f"No data fetched for {ticker}")
            raise ValueError(f"No data available for {ticker}")
        
        logger.info(f"Successfully fetched {len(df)} rows of data")
        logger.info(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")
        logger.info(f"Columns: {list(df.columns)}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

def clean_btc_data(df):
    """
    Clean BTC data: handle missing values, duplicates, etc.
    
    Args:
        df: Raw OHLCV DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    logger.info("Cleaning data...")
    
    # Reset index to make Date a column
    df = df.reset_index()
    
    new_columns = []
    for col in df.columns:
        if isinstance(col, tuple):
            # Take the first element of the tuple ('Close', 'BTC-USD') -> 'Close'
            new_columns.append(col[0].lower())
        else:
            # Handle standard strings (like the 'Date' column)
            new_columns.append(str(col).lower())

    # Rename columns to lowercase for consistency
    df.columns = new_columns
    
    # Handle missing values
    initial_rows = len(df)
    df = df.dropna()
    dropped = initial_rows - len(df)
    if dropped > 0:
        logger.warning(f"Dropped {dropped} rows with missing values")
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['date'])
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    # Ensure numeric columns
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'adj close']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    logger.info(f"Cleaned data: {len(df)} rows remaining")
    
    return df

def save_raw_data(df, ticker=TICKER):
    """
    Save raw data to CSV.
    
    Args:
        df: DataFrame to save
        ticker: Ticker symbol (used for filename)
    """
    output_path = RAW_DATA_DIR / f"{ticker}.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved raw data to {output_path}")
    return output_path

def main():
    """Main execution."""
    logger.info("=" * 80)
    logger.info("BTC-USD DATA FETCHING STARTED")
    logger.info("=" * 80)
    
    # Fetch data
    df = fetch_btc_data(TICKER, START_DATE, END_DATE)
    
    # Clean data
    df = clean_btc_data(df)
    
    # Save raw data
    output_path = save_raw_data(df, TICKER)
    
    logger.info("=" * 80)
    logger.info("BTC-USD DATA FETCHING COMPLETED")
    logger.info("=" * 80)
    logger.info(f"\nData Summary:")
    logger.info(f"  Rows: {len(df)}")
    logger.info(f"  Date Range: {df['date'].min()} to {df['date'].max()}")
    logger.info(f"  Close Price Range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    logger.info(f"  Saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    df = main()
