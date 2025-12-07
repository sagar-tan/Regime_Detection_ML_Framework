"""
Buy-and-Hold Baseline Generator

Creates a buy-and-hold baseline strategy for comparison.
Buy-and-hold means always holding the asset (signal=1 always).

Usage:
    python scripts/buy_and_hold_baseline.py

Output:
    results/signals_bah.csv - Buy-and-hold signals and equity
"""

import pandas as pd
import numpy as np
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("buy_and_hold_baseline", log_file="buy_and_hold_baseline.log")


def create_buy_and_hold_baseline(signals_path="results/signals_SPY.csv", output_path="results/signals_bah.csv"):
    """
    Create buy-and-hold baseline from existing signals file.
    
    Parameters:
    -----------
    signals_path : str
        Path to existing signals CSV (used as template)
    output_path : str
        Path to save buy-and-hold signals
    
    Returns:
    --------
    pd.DataFrame with buy-and-hold signals
    """
    logger.info(f"Loading template from {signals_path}...")
    
    # Load template
    df = pd.read_csv(signals_path, parse_dates=["Date"]).set_index("Date")
    
    logger.info(f"Loaded {len(df)} rows")
    
    # Create buy-and-hold version
    bah_df = df.copy()
    
    # Always hold (signal=1)
    bah_df["Signal"] = 1
    
    # Recompute PnL and Equity
    # For buy-and-hold: PnL = signal * day_return - trade_cost
    # Since signal is always 1, trade_cost only on first day
    
    equity = 1.0
    equity_list = []
    pnl_list = []
    trade_cost_list = []
    
    for i, (date, row) in enumerate(bah_df.iterrows()):
        day_return = row["DayReturn"]
        
        # Trade cost only on first day (entering position)
        if i == 0:
            trade_cost = 0.0005  # 5 basis points to enter
        else:
            trade_cost = 0.0  # No trades after first day
        
        # PnL = return - trade_cost
        pnl = day_return - trade_cost
        
        # Update equity
        equity = equity * (1.0 + pnl)
        
        equity_list.append(equity)
        pnl_list.append(pnl)
        trade_cost_list.append(trade_cost)
    
    bah_df["PnL"] = pnl_list
    bah_df["Equity"] = equity_list
    bah_df["TradeCost"] = trade_cost_list
    
    # Keep other columns as is
    # Reorder columns to match original
    column_order = ["Signal", "DayReturn", "TradeCost", "PnL", "Equity", "Regime"]
    bah_df = bah_df[column_order]
    
    # Save
    bah_df.to_csv(output_path)
    logger.info(f"Saved buy-and-hold baseline to {output_path}")
    
    # Print summary
    final_equity = bah_df["Equity"].iloc[-1]
    total_return = (final_equity - 1.0) * 100
    ann_return = ((1 + bah_df["DayReturn"].mean()) ** 252 - 1) * 100
    ann_vol = np.std(bah_df["DayReturn"], ddof=1) * np.sqrt(252) * 100
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0
    
    logger.info(f"\nBuy-and-Hold Summary:")
    logger.info(f"  Final Equity: {final_equity:.4f}")
    logger.info(f"  Total Return: {total_return:.2f}%")
    logger.info(f"  Annualized Return: {ann_return:.2f}%")
    logger.info(f"  Annualized Volatility: {ann_vol:.2f}%")
    logger.info(f"  Sharpe Ratio: {sharpe:.4f}")
    
    return bah_df


def main():
    """Main execution."""
    logger.info("Creating buy-and-hold baseline...")
    
    # Check if signals file exists
    signals_path = Path("results/signals_SPY.csv")
    if not signals_path.exists():
        logger.error(f"Signals file not found: {signals_path}")
        print("Error: Run backtest first to generate signals_SPY.csv")
        return
    
    # Create baseline
    bah_df = create_buy_and_hold_baseline(
        signals_path="results/signals_SPY.csv",
        output_path="results/signals_bah.csv"
    )
    
    print("\n" + "=" * 80)
    print("BUY-AND-HOLD BASELINE CREATED")
    print("=" * 80)
    print(f"\nFile saved: results/signals_bah.csv")
    print(f"Rows: {len(bah_df)}")
    print(f"\nYou can now run statistical comparison:")
    print("  python scripts/statistical_comparison.py")


if __name__ == "__main__":
    main()
