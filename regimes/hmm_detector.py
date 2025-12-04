import numpy as np
import pandas as pd
from pathlib import Path
from hmmlearn.hmm import GaussianHMM
from utils.logger import setup_logger

logger = setup_logger("hmm_detector", log_file="hmm_detector.log")


def load_features(filepath="data/processed/features_merged.csv"):
    logger.info("Loading processed feature file...")
    path = Path(filepath)

    if not path.exists():
        logger.error("Processed data not found. Run feature_engineering.py first.")
        raise FileNotFoundError("Missing processed dataset.")

    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.set_index("Date")
    logger.info(f"Loaded processed feature dataset with shape {df.shape}")
    return df


def extract_series_for_regime(df, ticker, column="Return"):
    col_name = f"{ticker}_{column}"

    if col_name not in df.columns:
        raise KeyError(f"Column {col_name} not found in processed features.")

    series = df[col_name].dropna().values.reshape(-1, 1)
    logger.info(f"Extracted series for {ticker}: length {len(series)}")
    return series


def fit_hmm(series, n_states=2, covariance_type="full"):
    logger.info("Fitting HMM model...")
    model = GaussianHMM(
        n_components=n_states,
        covariance_type=covariance_type,
        n_iter=200,
        random_state=42
    )
    model.fit(series)
    logger.info("HMM fitting completed successfully.")
    return model


def infer_regimes(model, series):
    logger.info("Predicting HMM hidden states...")
    regimes = model.predict(series)
    logger.info(f"Predicted regime states: {np.unique(regimes)}")
    return regimes


def attach_regime_labels(df, ticker, regimes):
    df_out = df.copy()
    df_out[f"{ticker}_HMM_Regime"] = regimes
    return df_out


def save_regime_file(df, ticker):
    path = Path(f"data/processed/features_with_hmm_{ticker}.csv")
    df.reset_index().to_csv(path, index=False)
    logger.info(f"Saved HMM regime file to {path}")


if __name__ == "__main__":
    logger.info("===== HMM Regime Detection Started =====")

    df = load_features()
    TICKER = "SPY"
    SERIES_COLUMN = "Return"

    series = extract_series_for_regime(df, TICKER, SERIES_COLUMN)
    model = fit_hmm(series, n_states=2)
    regimes = infer_regimes(model, series)

    df_with_regimes = attach_regime_labels(df, TICKER, regimes)
    save_regime_file(df_with_regimes, TICKER)

    logger.info("===== HMM Regime Detection Completed Successfully =====")
