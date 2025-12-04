import yfinance as yf
import pandas as pd
from pathlib import Path
from utils.logger import setup_logger

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

logger = setup_logger("fetch_data", log_file="fetch_data.log")

def download_single_ticker(ticker, start, end):
    logger.info(f"Starting download for {ticker} from {start} to {end}")

    try:
        df = yf.download(ticker, start=start, end=end)
    except Exception as e:
        logger.error(f"Download failed for {ticker}: {e}")
        return None

    if df.empty:
        logger.warning(f"No data found for {ticker}. Skipping.")
        return None

    # flatten multiindex if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # now clean
    try:
        df = df[['Open','High','Low','Close','Volume']].dropna()
    except KeyError as e:
        logger.error(f"Missing columns for {ticker}: {e}")
        return None

    logger.info(f"Final cleaned rows for {ticker}: {len(df)}")
    return df


def save_ticker_data(ticker, df):
    filepath = RAW_DATA_DIR / f"{ticker}.csv"
    df.to_csv(filepath)
    logger.info(f"Saved {ticker} to {filepath}")


def download_data(tickers, start, end):
    logger.info("===== Fetch Data Script Started =====")
    logger.info(f"Tickers: {tickers}")
    logger.info(f"Date Range: {start} to {end}")

    for ticker in tickers:
        df = download_single_ticker(ticker, start, end)
        if df is not None:
            save_ticker_data(ticker, df)
        else:
            logger.warning(f"Skipping save for {ticker} due to previous errors.")
    
    logger.info("===== Fetch Data Script Completed =====")


if __name__ == "__main__":
    TICKERS = ["SPY", "QQQ", "IWM", "XLF", "GLD", "TLT"]
    START = "2010-01-01"
    END = "2025-01-01"

    download_data(TICKERS, START, END)
