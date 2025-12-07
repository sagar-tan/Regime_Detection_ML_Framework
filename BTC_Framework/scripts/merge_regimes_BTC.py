# BTC_Framework/scripts/merge_regimes_BTC.py
# Merge HMM and changepoint regimes for BTC-USD

import pandas as pd
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TICKER = "BTC-USD"
HMM_FILE = Path("data/processed") / f"features_with_hmm_{TICKER}.csv"
CP_FILE = Path("data/processed") / f"features_with_cp_{TICKER}.csv"
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_features(hmm_path=HMM_FILE, cp_path=CP_FILE):
    """Load HMM and changepoint features."""
    logger.info(f"Loading HMM features from {hmm_path}")
    df_hmm = pd.read_csv(hmm_path, parse_dates=['date'])
    
    logger.info(f"Loading CP features from {cp_path}")
    df_cp = pd.read_csv(cp_path, parse_dates=['date'])
    
    logger.info(f"Loaded {len(df_hmm)} rows from HMM file")
    logger.info(f"Loaded {len(df_cp)} rows from CP file")
    
    return df_hmm, df_cp

def merge_regimes(df_hmm, df_cp, ticker=TICKER):
    """Merge HMM and changepoint regimes."""
    logger.info("Merging regimes...")
    
    # Start with HMM features
    df = df_hmm.copy()
    
    # Add CP regime from CP file
    cp_regime_col = f'{ticker}_CP_Regime'
    if cp_regime_col in df_cp.columns:
        df[cp_regime_col] = df_cp[cp_regime_col]
        logger.info(f"Added {cp_regime_col} column")
    else:
        logger.warning(f"Column {cp_regime_col} not found in CP file")
    
    logger.info("Regimes merged successfully")
    return df

def save_merged_features(df, ticker=TICKER):
    """Save merged features."""
    output_path = OUTPUT_DIR / f"features_final_{ticker}.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Saved merged features to {output_path}")
    return output_path

def main():
    """Main execution."""
    logger.info("=" * 80)
    logger.info(f"MERGING REGIMES FOR {TICKER} STARTED")
    logger.info("=" * 80)
    
    # Load features
    df_hmm, df_cp = load_features()
    
    # Merge regimes
    df = merge_regimes(df_hmm, df_cp, TICKER)
    
    # Save
    output_path = save_merged_features(df, TICKER)
    
    logger.info("=" * 80)
    logger.info(f"MERGING REGIMES FOR {TICKER} COMPLETED")
    logger.info("=" * 80)
    logger.info(f"\nMerge Summary:")
    logger.info(f"  Total rows: {len(df)}")
    logger.info(f"  Total columns: {len(df.columns)}")
    logger.info(f"  Saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    df = main()
