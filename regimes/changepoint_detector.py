import numpy as np
import pandas as pd
from pathlib import Path
import ruptures as rpt
from utils.logger import setup_logger

logger = setup_logger("changepoint_detector", log_file="changepoint_detector.log")


def load_features(filepath="data/processed/features_merged.csv"):
    """
    Loads the processed flat-column feature file.
    """
    logger.info("Loading processed feature file...")
    path = Path(filepath)

    if not path.exists():
        logger.error("Processed data not found. Run feature_engineering.py first.")
        raise FileNotFoundError("Missing processed dataset.")

    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.set_index("Date")
    logger.info(f"Loaded processed features with shape {df.shape}")
    return df


def extract_series_for_cp(df, ticker, column="Return"):
    """
    Extracts a flat column like 'SPY_Return'
    """
    col_name = f"{ticker}_{column}"

    if col_name not in df.columns:
        raise KeyError(f"Column {col_name} not found. Available: {list(df.columns)}")

    series = df[col_name].dropna().values
    logger.info(f"Extracted CP series for {ticker}: length {len(series)}")
    return series


def detect_changepoints(series, model="rbf", penalty=10):
    """
    Detect structural breaks using PELT method.
    """
    logger.info("Running PELT CP detection")
    logger.info(f"Model={model}, Penalty={penalty}")

    algo = rpt.Pelt(model=model).fit(series)
    breakpoints = algo.predict(pen=penalty)

    logger.info(f"Detected breakpoints: {breakpoints}")
    return breakpoints


def convert_breaks_to_labels(length, breakpoints):
    """
    Converts breakpoints into labels: 0,1,2,3,...
    """
    labels = np.zeros(length, dtype=int)
    current_label = 0
    last = 0

    for bp in breakpoints:
        labels[last:bp] = current_label
        current_label += 1
        last = bp

    logger.info(f"Number of regimes formed: {current_label}")
    return labels


def attach_cp_labels(df, ticker, labels):
    """
    Attach flat-column CP regime label.
    """
    df_out = df.copy()
    df_out[f"{ticker}_CP_Regime"] = labels
    return df_out


def save_cp_file(df, ticker):
    """
    Save consistent flat CSV.
    """
    path = Path(f"data/processed/features_with_cp_{ticker}.csv")
    df.reset_index().to_csv(path, index=False)
    logger.info(f"Saved CP regime file to {path}")


if __name__ == "__main__":
    logger.info("===== CP Regime Detection Started =====")

    df = load_features()
    TICKER = "SPY"
    SERIES_COLUMN = "Return"

    series = extract_series_for_cp(df, TICKER, SERIES_COLUMN)
    breakpoints = detect_changepoints(series, model="rbf", penalty=10)
    labels = convert_breaks_to_labels(len(series), breakpoints)

    df_with_cp = attach_cp_labels(df, TICKER, labels)
    save_cp_file(df_with_cp, TICKER)

    logger.info("===== CP Regime Detection Finished =====")
