# BTC_Framework/regimes/hmm_detector_BTC.py
# HMM-based regime detection for BTC-USD

import pandas as pd
import numpy as np
from pathlib import Path
from hmmlearn import hmm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TICKER = "BTC-USD"
FEATURE_FILE = Path("data/processed") / f"features_final_{TICKER}.csv"
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# HMM parameters - increased sensitivity for crypto volatility
N_COMPONENTS = 4  # More regimes for BTC's higher volatility
N_ITER = 1000
RANDOM_STATE = 42

def load_features(filepath=FEATURE_FILE):
    """Load engineered features."""
    logger.info(f"Loading features from {filepath}")
    df = pd.read_csv(filepath, parse_dates=['date'])
    logger.info(f"Loaded {len(df)} rows")
    return df

def prepare_hmm_data(df, ticker=TICKER):
    """Prepare data for HMM: use returns as input."""
    logger.info("Preparing data for HMM...")
    
    # Use returns as the observation
    returns = df[f'{ticker}_Return'].values.reshape(-1, 1)
    
    # Remove NaN
    valid_idx = ~np.isnan(returns.flatten())
    returns = returns[valid_idx]
    
    logger.info(f"Using {len(returns)} observations for HMM")
    return returns

def fit_hmm(returns, n_components=N_COMPONENTS):
    """Fit Gaussian HMM."""
    logger.info(f"Fitting HMM with {n_components} components...")
    
    model = hmm.GaussianHMM(n_components=n_components, covariance_type="full", n_iter=N_ITER, random_state=RANDOM_STATE)
    model.fit(returns)
    
    logger.info(f"HMM converged: {model.monitor_.converged}")
    logger.info(f"Final log-likelihood: {model.score(returns):.4f}")
    
    return model

def predict_regimes(model, returns):
    """Predict hidden states (regimes)."""
    logger.info("Predicting regimes...")
    regimes = model.predict(returns)
    logger.info(f"Predicted {len(regimes)} regime labels")
    return regimes

def add_hmm_regimes(df, regimes, ticker=TICKER):
    """Add HMM regime labels to dataframe."""
    logger.info("Adding HMM regimes to dataframe...")
    
    # Create a temporary dataframe with regimes
    temp_df = df.copy()
    
    # Handle NaN values in returns
    valid_idx = ~temp_df[f'{ticker}_Return'].isna()
    
    # Initialize regime column with -1 (for NaN rows)
    temp_df[f'{ticker}_HMM_Regime'] = -1
    
    # Assign predicted regimes to valid rows
    temp_df.loc[valid_idx, f'{ticker}_HMM_Regime'] = regimes
    
    logger.info(f"Added {ticker}_HMM_Regime column")
    return temp_df

def save_features_with_hmm(df, ticker=TICKER):
    """Save features with HMM regimes."""
    output_path = OUTPUT_DIR / f"features_with_hmm_{ticker}.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved features with HMM to {output_path}")
    return output_path

def main():
    """Main execution."""
    logger.info("=" * 80)
    logger.info(f"HMM REGIME DETECTION FOR {TICKER} STARTED")
    logger.info("=" * 80)
    
    # Load features
    df = load_features()
    
    # Prepare data
    returns = prepare_hmm_data(df, TICKER)
    
    # Fit HMM
    model = fit_hmm(returns, N_COMPONENTS)
    
    # Predict regimes
    regimes = predict_regimes(model, returns)
    
    # Add to dataframe
    df = add_hmm_regimes(df, regimes, TICKER)
    
    # Save
    output_path = save_features_with_hmm(df, TICKER)
    
    logger.info("=" * 80)
    logger.info(f"HMM REGIME DETECTION FOR {TICKER} COMPLETED")
    logger.info("=" * 80)
    logger.info(f"\nRegime Summary:")
    regime_counts = df[f'{TICKER}_HMM_Regime'].value_counts().sort_index()
    for regime, count in regime_counts.items():
        if regime >= 0:
            logger.info(f"  Regime {regime}: {count} days ({100*count/len(df):.1f}%)")
    logger.info(f"  Saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    df = main()
