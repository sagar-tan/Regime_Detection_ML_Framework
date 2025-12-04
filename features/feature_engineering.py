import pandas as pd
import numpy as np
from pathlib import Path
from utils.logger import setup_logger

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

logger = setup_logger("feature_engineering", log_file="feature_engineering.log")


def load_and_merge_data():
    """
    Loads all CSVs from data/raw, aligns dates, and merges them 
    into a single MultiIndex DataFrame: (ticker, feature).
    """
    logger.info("===== Loading raw data =====")

    files = list(RAW_DIR.glob("*.csv"))
    if not files:
        logger.error("No raw data found in data/raw/. Run fetch_data.py first!")
        raise FileNotFoundError("Missing raw CSV files.")

    dataframes = []
    for file in files:
        ticker = file.stem
        logger.info(f"Loading {ticker} from {file}")
        try:
            df = pd.read_csv(file, parse_dates=["Date"], index_col="Date")
        except Exception as e:
            logger.error(f"Failed to read {file}: {e}")
            continue

        if df.empty:
            logger.warning(f"{ticker} has empty data. Skipping.")
            continue

        # Convert columns to MultiIndex for merging
        df.columns = pd.MultiIndex.from_product([[ticker], df.columns])
        dataframes.append(df)

    if not dataframes:
        logger.error("No valid raw CSVs loaded. Stopping.")
        raise ValueError("Failed to load raw data.")

    merged_df = pd.concat(dataframes, axis=1).sort_index()
    logger.info(f"Merged dataframe shape: {merged_df.shape}")

    return merged_df


def compute_features(merged_df):
    """
    Computes:
    - returns
    - rolling volatility
    - SMA10, SMA50
    - binary target labels
    """
    logger.info("===== Computing features =====")

    df = merged_df.copy()
    tickers = merged_df.columns.get_level_values(0).unique()

    for ticker in tickers:
        try:
            close = merged_df[(ticker, "Close")]
        except KeyError:
            logger.warning(f"{ticker} missing Close column. Skipping features.")
            continue

        logger.info(f"Computing features for {ticker}")

        df[(ticker, "Return")] = close.pct_change()
        df[(ticker, "Vol20")] = close.pct_change().rolling(20).std()
        df[(ticker, "SMA10")] = close.rolling(10).mean()
        df[(ticker, "SMA50")] = close.rolling(50).mean()

        # Setup binary target (for ML classification)
        df[(ticker, "Target")] = (df[(ticker, "Return")] > 0).astype(int)

    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    logger.info(f"Final feature dataframe shape: {df.shape}")

    return df


def save_processed(df):
    """
    Saves processed features with flattened columns and Date as a proper column.
    """
    filepath = PROCESSED_DIR / "features_merged.csv"

    # Flatten MultiIndex columns like ('GLD','Close') → 'GLD_Close'
    df_flat = df.copy()
    df_flat.columns = [f"{lvl0}_{lvl1}" for lvl0, lvl1 in df_flat.columns]

    # Date index → column
    df_flat = df_flat.reset_index()

    df_flat.to_csv(filepath, index=False)
    logger.info(f"Processed features saved to {filepath}")



if __name__ == "__main__":
    logger.info("===== Feature Engineering Started =====")

    merged = load_and_merge_data()
    features = compute_features(merged)
    save_processed(features)

    logger.info("===== Feature Engineering Completed Successfully =====")
