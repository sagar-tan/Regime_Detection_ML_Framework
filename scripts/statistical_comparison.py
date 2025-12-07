"""
Statistical Comparison Script

This script runs comprehensive statistical significance tests comparing
different trading strategies (Static, Regime-Specific, Hybrid, Buy-and-Hold).

Usage:
    python scripts/statistical_comparison.py

Output:
    - Printed statistical reports
    - JSON file with detailed results
    - CSV file with comparison summary
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from analysis.statistical_tests import (
    paired_ttest_returns,
    sharpe_decomposition,
    win_rate_significance,
    max_drawdown_significance,
    compare_strategies,
    compare_multiple_strategies,
)
from utils.logger import setup_logger

logger = setup_logger("statistical_comparison", log_file="statistical_comparison.log")


def load_signals(filepath):
    """Load signals CSV and compute buy-and-hold benchmark."""
    df = pd.read_csv(filepath, parse_dates=["Date"]).set_index("Date")
    return df


def compute_buy_and_hold_returns(signals_df):
    """
    Compute buy-and-hold returns from signals dataframe.
    
    Buy-and-hold means always holding the asset (signal=1).
    """
    bah_returns = signals_df["DayReturn"].copy()
    return bah_returns


def run_pairwise_comparison(strategy_dict):
    """
    Run pairwise statistical comparisons between all strategies.
    
    Parameters:
    -----------
    strategy_dict : dict
        Maps strategy names to signals CSV paths
    
    Returns:
    --------
    dict with all pairwise comparisons
    """
    logger.info("=" * 80)
    logger.info("RUNNING PAIRWISE STATISTICAL COMPARISONS")
    logger.info("=" * 80)
    
    results = {}
    strategy_names = list(strategy_dict.keys())
    
    for i, strat1 in enumerate(strategy_names):
        for strat2 in strategy_names[i+1:]:
            comparison_key = f"{strat1} vs {strat2}"
            logger.info(f"\n{'='*80}")
            logger.info(f"COMPARISON: {comparison_key}")
            logger.info(f"{'='*80}\n")
            
            try:
                result = compare_strategies(
                    strategy_dict[strat1],
                    strategy_dict[strat2],
                    strat1,
                    strat2
                )
                results[comparison_key] = result
                print(result['summary'])
            except Exception as e:
                logger.error(f"Error comparing {comparison_key}: {e}")
                results[comparison_key] = {"error": str(e)}
    
    return results


def generate_summary_table(strategy_dict):
    """
    Generate a summary table with key metrics for all strategies.
    
    Parameters:
    -----------
    strategy_dict : dict
        Maps strategy names to signals CSV paths
    
    Returns:
    --------
    pd.DataFrame with summary metrics
    """
    logger.info("\n" + "=" * 80)
    logger.info("GENERATING SUMMARY TABLE")
    logger.info("=" * 80 + "\n")
    
    summary_data = []
    
    for strategy_name, filepath in strategy_dict.items():
        logger.info(f"Processing {strategy_name}...")
        
        try:
            df = load_signals(filepath)
            returns = df["DayReturn"].values
            equity = df["Equity"].values
            signals = df["Signal"].values
            
            # Compute metrics
            total_return = (equity[-1] - 1.0) * 100
            ann_return = ((1 + returns.mean()) ** 252 - 1) * 100
            ann_vol = np.std(returns, ddof=1) * np.sqrt(252) * 100
            sharpe = ann_return / ann_vol if ann_vol > 0 else 0
            
            # Max drawdown
            roll_max = np.maximum.accumulate(equity)
            dd = (equity - roll_max) / roll_max
            max_dd = np.min(dd) * 100
            
            # Win rate
            correct = (signals * returns > 0).sum()
            hit_ratio = (correct / len(signals)) * 100
            
            # Sortino ratio
            downside = returns[returns < 0]
            downside_vol = np.std(downside, ddof=1) * np.sqrt(252) if len(downside) > 0 else 0
            sortino = ann_return / (downside_vol * 100) if downside_vol > 0 else 0
            
            # CVaR (5%)
            cvar_5 = np.quantile(returns, 0.05) * 100
            
            summary_data.append({
                "Strategy": strategy_name,
                "Total Return (%)": round(total_return, 2),
                "Ann. Return (%)": round(ann_return, 2),
                "Ann. Volatility (%)": round(ann_vol, 2),
                "Sharpe Ratio": round(sharpe, 4),
                "Sortino Ratio": round(sortino, 4),
                "Max Drawdown (%)": round(max_dd, 2),
                "Hit Ratio (%)": round(hit_ratio, 2),
                "CVaR 5% (%)": round(cvar_5, 2),
                "Observations": len(returns),
            })
        except Exception as e:
            logger.error(f"Error processing {strategy_name}: {e}")
    
    summary_df = pd.DataFrame(summary_data)
    return summary_df


def export_results(pairwise_results, summary_df, output_dir="results"):
    """
    Export results to JSON and CSV files.
    
    Parameters:
    -----------
    pairwise_results : dict
        Pairwise comparison results
    summary_df : pd.DataFrame
        Summary metrics table
    output_dir : str
        Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Export JSON
    json_path = output_path / "statistical_comparison.json"
    
    # Convert results to JSON-serializable format
    json_results = {}
    for key, value in pairwise_results.items():
        if isinstance(value, dict) and "error" not in value:
            json_results[key] = {
                "paired_ttest": value.get("paired_ttest", {}),
                "sharpe_decomposition": value.get("sharpe_decomposition", {}),
                "win_rate_test": value.get("win_rate_test", {}),
                "max_dd_comparison": value.get("max_dd_comparison", {}),
            }
        else:
            json_results[key] = value
    
    with open(json_path, 'w') as f:
        json.dump(json_results, f, indent=2)
    logger.info(f"Exported JSON results to {json_path}")
    
    # Export CSV
    csv_path = output_path / "strategy_summary.csv"
    summary_df.to_csv(csv_path, index=False)
    logger.info(f"Exported summary table to {csv_path}")
    
    # Export formatted report
    report_path = output_path / "statistical_report.txt"
    with open(report_path, 'w', encoding= "utf-8") as f:
        f.write("STATISTICAL SIGNIFICANCE REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("SUMMARY TABLE\n")
        f.write("-" * 80 + "\n")
        f.write(summary_df.to_string(index=False))
        f.write("\n\n")
        
        f.write("PAIRWISE COMPARISONS\n")
        f.write("-" * 80 + "\n")
        for key, value in pairwise_results.items():
            if isinstance(value, dict) and "summary" in value:
                f.write(value["summary"])
                f.write("\n\n")
    
    logger.info(f"Exported formatted report to {report_path}")


def main():
    """Main execution function."""
    logger.info("Starting statistical comparison analysis...")
    
    # Define strategies to compare
    # NOTE: You need to run backtest multiple times with different STRATEGY_MODE values
    # to generate these files. See instructions below.
    strategy_dict = {
        "Static": "results/signals_static.csv",
        "Regime-Specific": "results/signals_regime_specific.csv",
        "Hybrid": "results/signals_hybrid.csv",
        "Buy-and-Hold": "results/signals_bah.csv",
    }
    
    # Check which files exist
    existing_strategies = {}
    for strategy_name, filepath in strategy_dict.items():
        if Path(filepath).exists():
            existing_strategies[strategy_name] = filepath
            logger.info(f"[OK] Found {strategy_name}: {filepath}")
        else:
            logger.warning(f"[MISSING] Missing {strategy_name}: {filepath}")
    
    if len(existing_strategies) < 2:
        logger.error("Need at least 2 strategy files to compare!")
        print("\n" + "=" * 80)
        print("SETUP INSTRUCTIONS")
        print("=" * 80)
        print("""
To run statistical comparisons, you need to generate results for multiple strategies:

1. STATIC STRATEGY:
   - Edit: backtest/walk_forward_engine.py, line 44
   - Set: STRATEGY_MODE = "static"
   - Run: python backtest/walk_forward_engine.py
   - Save: mv results/signals_SPY.csv results/signals_static.csv

2. REGIME-SPECIFIC STRATEGY:
   - Edit: backtest/walk_forward_engine.py, line 44
   - Set: STRATEGY_MODE = "regime_specific"
   - Run: python backtest/walk_forward_engine.py
   - Save: mv results/signals_SPY.csv results/signals_regime_specific.csv

3. HYBRID STRATEGY:
   - Edit: backtest/walk_forward_engine.py, line 44
   - Set: STRATEGY_MODE = "hybrid"
   - Run: python backtest/walk_forward_engine.py
   - Save: mv results/signals_SPY.csv results/signals_hybrid.csv

4. BUY-AND-HOLD (OPTIONAL):
   - Create a baseline with signal=1 always
   - Or use the provided buy_and_hold_baseline.py script

After generating all strategy files, run this script again:
    python scripts/statistical_comparison.py
""")
        return
    
    # Generate summary table
    summary_df = generate_summary_table(existing_strategies)
    print("\n" + "=" * 80)
    print("STRATEGY SUMMARY TABLE")
    print("=" * 80 + "\n")
    print(summary_df.to_string(index=False))
    print("\n")
    
    # Run pairwise comparisons
    pairwise_results = run_pairwise_comparison(existing_strategies)
    
    # Export results
    export_results(pairwise_results, summary_df)
    
    logger.info("\n" + "=" * 80)
    logger.info("STATISTICAL COMPARISON COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Results exported to results/ directory")


if __name__ == "__main__":
    main()
