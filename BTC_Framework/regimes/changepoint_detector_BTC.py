# BTC_Framework/regimes/changepoint_detector_BTC.py
# Changepoint-based regime detection for BTC-USD

import pandas as pd
import numpy as np
from pathlib import Path
from ruptures import Pelt
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TICKER = "BTC-USD"
FEATURE_FILE = Path("data/processed") / f"features_with_hmm_{TICKER}.csv"
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Changepoint detection parameters - lower penalty for crypto volatility
PENALTY = 2.0  # Lower penalty to detect more changepoints
MIN_SIZE = 20  # Minimum segment size

def load_features(filepath=FEATURE_FILE):
    """Load features with HMM regimes."""
    logger.info(f"Loading features from {filepath}")
    df = pd.read_csv(filepath, parse_dates=['date'])
    logger.info(f"Loaded {len(df)} rows")
    return df

def prepare_cpd_data(df, ticker=TICKER):
    """Prepare data for changepoint detection: use returns."""
    logger.info("Preparing data for changepoint detection...")
    
    # Use returns as the signal
    returns = df[f'{ticker}_Return'].values
    
    # Replace NaN with 0
    returns = np.nan_to_num(returns, nan=0.0)
    
    # Reshape for ruptures (needs 2D array)
    signal = returns.reshape(-1, 1)
    
    logger.info(f"Using {len(signal)} observations for CPD")
    return signal

def detect_changepoints(signal, penalty=PENALTY, min_size=MIN_SIZE):
    """Detect changepoints using PELT algorithm."""
    logger.info(f"Detecting changepoints (penalty={penalty}, min_size={min_size})...")
    
    algo = Pelt(kernel="l2", min_size=min_size, jump=1).fit(signal)
    changepoints = algo.predict(pen=penalty)
    
    logger.info(f"Detected {len(changepoints)} changepoints")
    if len(changepoints) > 0:
        logger.info(f"Changepoint indices: {changepoints[:10]}...")  # Show first 10
    
    return changepoints

def create_regime_labels(df, changepoints, ticker=TICKER):
    """Create regime labels from changepoints."""
    logger.info("Creating regime labels from changepoints...")
    
    regimes = np.zeros(len(df), dtype=int)
    
    for i, cp in enumerate(changepoints[:-1]):
        regimes[cp:changepoints[i+1]] = i
    
    # Last regime
    if len(changepoints) > 0:
        regimes[changepoints[-1]:] = len(changepoints) - 1
    
    df[f'{ticker}_CP_Regime'] = regimes
    
    logger.info(f"Added {ticker}_CP_Regime column")
    return df

def save_features_with_cp(df, ticker=TICKER):
    """Save features with changepoint regimes."""
    output_path = OUTPUT_DIR / f"features_with_cp_{ticker}.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved features with CP to {output_path}")
    return output_path

def main():
    """Main execution."""
    logger.info("=" * 80)
    logger.info(f"CHANGEPOINT DETECTION FOR {TICKER} STARTED")
    logger.info("=" * 80)
    
    # Load features
    df = load_features()
    
    # Prepare data
    signal = prepare_cpd_data(df, TICKER)
    
    # Detect changepoints
    changepoints = detect_changepoints(signal, PENALTY, MIN_SIZE)
    
    # Create regime labels
    df = create_regime_labels(df, changepoints, TICKER)
    
    # Save
    output_path = save_features_with_cp(df, TICKER)
    
    logger.info("=" * 80)
    logger.info(f"CHANGEPOINT DETECTION FOR {TICKER} COMPLETED")
    logger.info("=" * 80)
    logger.info(f"\nChangepoint Summary:")
    logger.info(f"  Number of changepoints: {len(changepoints)}")
    logger.info(f"  Number of regimes: {len(changepoints)}")
    regime_counts = df[f'{ticker}_CP_Regime'].value_counts().sort_index()
    for regime, count in regime_counts.items():
        logger.info(f"  Regime {regime}: {count} days ({100*count/len(df):.1f}%)")
    logger.info(f"  Saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    df = main()
