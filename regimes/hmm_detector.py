import numpy as np
import pandas as pd
from pathlib import Path
from hmmlearn.hmm import GaussianHMM
from utils.logger import setup_logger

logger = setup_logger("hmm_detector", log_file="hmm_detector.log")


def load_features(filepath="data/processed/features_merged.csv"):
    """
    Load processed feature dataset and validate presence of required fields.
    """
    logger.info("Loading processed feature file...")
    path = Path(filepath)

    if not path.exists():
        logger.error("Processed data not found. Run feature_engineering.py first.")
        raise FileNotFoundError("Missing processed dataset.")

    df = pd.read_csv(path, index_col="Date", parse_dates=True)
    logger.info(f"Loaded processed feature dataset with shape {df.shape}")
    return df


def extract_series_for_regime(df, ticker, column="Return"):
    """
    Extracts the time series input for fitting HMM.
    Usually returns or volatility.
    """
    try:
        series = df[(ticker, column)].dropna().values.reshape(-1, 1)
    except Exception as e:
        logger.error(f"Failed to extract series for {ticker}: {e}")
        raise

    logger.info(f"Extracted series for {ticker}: length {len(series)}")
    return series


def fit_hmm(series, n_states=2, covariance_type="full"):
    """
    Fit a Gaussian HMM to a given series.
    """
    logger.info("Fitting HMM model...")
    logger.info(f"States={n_states}, cov_type={covariance_type}")

    model = GaussianHMM(
        n_components=n_states,
        covariance_type=covariance_type,
        n_iter=200,
        random_state=42
    )

    try:
        model.fit(series)
    except Exception as e:
        logger.error(f"HMM fitting failed: {e}")
        raise

    logger.info("HMM fitting completed successfully.")
    return model


def infer_regimes(model, series):
    """
    Uses fitted HMM to predict hidden states for each date.
    """
    logger.info("Predicting HMM hidden states...")
    regimes = model.predict(series)
    logger.info(f"Predicted regime states: {np.unique(regimes)}")
    return regimes


def attach_regime_labels(df, ticker, regimes):
    """
    Append regime labels to dataframe for the chosen ticker.
    """
