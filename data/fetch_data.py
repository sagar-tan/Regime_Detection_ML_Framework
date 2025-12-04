import yfinance as yf
import pandas as pd
from pathlib import Path

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

def download_data(tickers, start, end):
    for ticker in tickers:
        print(f"Downloading: {ticker}")
        df = yf.download(ticker, start=start, end=end)

        if df.empty:
            print(f"Warning: No data for {ticker}, skipping.")
            continue

        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df = df.dropna()

        filepath = RAW_DATA_DIR / f"{ticker}.csv"
        df.to_csv(filepath)
        print(f"Saved: {filepath}")

    print("Data download complete")


if __name__ == "__main__":
    TICKERS = ["SPY", "QQQ", "IWM", "XLF", "GLD", "TLT"]
    START = "2010-01-01"
    END = "2025-01-01"

    download_data(TICKERS, START, END)
