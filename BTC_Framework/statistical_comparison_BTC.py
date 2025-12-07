# BTC_Framework/statistical_comparison_BTC.py
# Statistical significance comparison for BTC-USD strategies

import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.statistical_tests import (
    paired_ttest_returns,
    sharpe_decomposition,
    win_rate_significance,
    max_drawdown_significance,
    compare_strategies
)
from utils.logger import setup_logger

logger = setup_logger("statistical_comparison_BTC", log_file="statistical_comparison_BTC.log")

# Configuration
TICKER = "BTC-USD"
RESULTS_DIR = Path("results")
OUTPUT_DIR = RESULTS_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_signals(filepath):
    """Load signals CSV."""
    if not Path(filepath).exists():
        logger.warning(f"File not found: {filepath}")
        return None
    
    df = pd.read_csv(filepath, parse_dates=['Date'])
    df = df.set_index('Date').sort_index()
    logger.info(f"Loaded {len(df)} rows from {filepath}")
    return df

def extract_returns(signals_df):
    """Extract daily returns from signals."""
    if signals_df is None:
        return None
    return signals_df['DayReturn'].values

def extract_equity(signals_df):
    """Extract equity curve from signals."""
    if signals_df is None:
        return None
    return signals_df['Equity'].values

def run_pairwise_comparisons(strategy_dict):
    """Run pairwise statistical comparisons."""
    logger.info("Running pairwise comparisons...")
    
    # Load all signals
    signals = {}
    for name, filepath in strategy_dict.items():
        signals[name] = load_signals(filepath)
    
    # Filter out missing files
    existing_signals = {k: v for k, v in signals.items() if v is not None}
    
    if len(existing_signals) < 2:
        logger.error("Need at least 2 strategy files to compare!")
        return None
    
    logger.info(f"Comparing {len(existing_signals)} strategies: {list(existing_signals.keys())}")
    
    # Run pairwise comparisons
    results = {}
    strategy_names = list(existing_signals.keys())
    
    for i, strat1 in enumerate(strategy_names):
        for strat2 in strategy_names[i+1:]:
            pair_name = f"{strat1}_vs_{strat2}"
            logger.info(f"Comparing {pair_name}...")
            
            returns1 = extract_returns(existing_signals[strat1])
            returns2 = extract_returns(existing_signals[strat2])
            equity1 = extract_equity(existing_signals[strat1])
            equity2 = extract_equity(existing_signals[strat2])
            
            # Paired t-test
            ttest_result = paired_ttest_returns(returns1, returns2, strat1, strat2)
            
            # Sharpe decomposition
            sharpe_result = sharpe_decomposition(returns1, returns2, strat1, strat2)
            
            # Win rate
            hit_ratio1 = np.mean(returns1 > 0)
            hit_ratio2 = np.mean(returns2 > 0)
            winrate_result = win_rate_significance(hit_ratio1, len(returns1), hit_ratio2, len(returns2))
            
            # Max drawdown
            dd_result = max_drawdown_significance(equity1, equity2, strat1, strat2)
            
            results[pair_name] = {
                "paired_ttest": ttest_result,
                "sharpe_decomposition": sharpe_result,
                "win_rate": winrate_result,
                "max_drawdown": dd_result
            }
    
    return results, existing_signals

def generate_summary_table(existing_signals):
    """Generate summary metrics table."""
    logger.info("Generating summary table...")
    
    summary_data = []
    
    for strategy_name, signals_df in existing_signals.items():
        if signals_df is None:
            continue
        
        returns = signals_df['DayReturn'].values
        equity = signals_df['Equity'].values
        
        # Calculate metrics
        total_return = (equity[-1] - 1.0) * 100
        annual_return = ((equity[-1] ** (252 / len(equity))) - 1) * 100
        volatility = np.std(returns) * np.sqrt(252) * 100
        sharpe = (np.mean(returns) * 252) / (np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
        
        # Max drawdown
        cummax = np.maximum.accumulate(equity)
        drawdown = (equity - cummax) / cummax
        max_dd = np.min(drawdown) * 100
        
        # Win rate
        win_rate = np.mean(returns > 0) * 100
        
        # Trades
        signals = signals_df['Signal'].values
        trades = np.sum(np.abs(np.diff(signals)) > 0)
        
        summary_data.append({
            'Strategy': strategy_name,
            'Total Return (%)': round(total_return, 2),
            'Annual Return (%)': round(annual_return, 2),
            'Volatility (%)': round(volatility, 2),
            'Sharpe Ratio': round(sharpe, 3),
            'Max Drawdown (%)': round(max_dd, 2),
            'Win Rate (%)': round(win_rate, 2),
            'Num Trades': int(trades),
            'Days': len(equity)
        })
    
    summary_df = pd.DataFrame(summary_data)
    logger.info(f"Generated summary for {len(summary_df)} strategies")
    return summary_df

def export_results(results, summary_df, existing_signals):
    """Export results to JSON, CSV, and TXT."""
    logger.info("Exporting results...")
    
    # Export JSON
    json_path = OUTPUT_DIR / f"BTC_statistical_comparison.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Saved JSON to {json_path}")
    
    # Export CSV
    csv_path = OUTPUT_DIR / f"BTC_strategy_summary.csv"
    summary_df.to_csv(csv_path, index=False)
    logger.info(f"Saved CSV to {csv_path}")
    
    # Export TXT report
    txt_path = OUTPUT_DIR / f"BTC_statistical_report.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("STATISTICAL SIGNIFICANCE REPORT - BTC-USD\n")
        f.write("=" * 80 + "\n\n")
        
        # Summary table
        f.write("STRATEGY PERFORMANCE SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(summary_df.to_string(index=False))
        f.write("\n\n")
        
        # Pairwise comparisons
        f.write("PAIRWISE STATISTICAL COMPARISONS\n")
        f.write("-" * 80 + "\n\n")
        
        for pair_name, pair_results in results.items():
            f.write(f"\n{pair_name.upper()}\n")
            f.write("-" * 40 + "\n")
            
            # T-test
            ttest = pair_results['paired_ttest']
            f.write(f"\n1. PAIRED T-TEST (Daily Returns)\n")
            f.write(f"   t-statistic: {ttest['t_statistic']:.4f}\n")
            f.write(f"   p-value: {ttest['p_value']:.6f}\n")
            f.write(f"   Significant: {'YES' if ttest['significant'] else 'NO'}\n")
            f.write(f"   Effect Size (Cohen's d): {ttest['effect_size']:.4f}\n")
            f.write(f"   Interpretation: {ttest['interpretation']}\n")
            
            # Sharpe decomposition
            sharpe = pair_results['sharpe_decomposition']
            f.write(f"\n2. SHARPE RATIO DECOMPOSITION\n")
            f.write(f"   Return Difference: {sharpe['return_diff']:.6f}\n")
            f.write(f"   Volatility Difference: {sharpe['vol_diff']:.6f}\n")
            f.write(f"   Sharpe Difference: {sharpe['sharpe_diff']:.4f}\n")
            f.write(f"   Source: {sharpe['source']}\n")
            
            # Win rate
            winrate = pair_results['win_rate']
            f.write(f"\n3. WIN RATE SIGNIFICANCE\n")
            f.write(f"   Hit Ratio 1: {winrate['hit_ratio1']:.4f}\n")
            f.write(f"   Hit Ratio 2: {winrate['hit_ratio2']:.4f}\n")
            f.write(f"   p-value: {winrate['p_value']:.6f}\n")
            f.write(f"   Significant: {'YES' if winrate['significant'] else 'NO'}\n")
            
            # Max drawdown
            dd = pair_results['max_drawdown']
            f.write(f"\n4. MAXIMUM DRAWDOWN COMPARISON\n")
            f.write(f"   Max DD 1: {dd['max_dd1']:.4f}\n")
            f.write(f"   Max DD 2: {dd['max_dd2']:.4f}\n")
            f.write(f"   Difference: {dd['dd_diff']:.4f}\n")
            f.write(f"   Interpretation: {dd['interpretation']}\n")
    
    logger.info(f"Saved TXT report to {txt_path}")
    return json_path, csv_path, txt_path

def main():
    """Main execution."""
    logger.info("=" * 80)
    logger.info("STATISTICAL COMPARISON FOR BTC-USD STARTED")
    logger.info("=" * 80)
    
    # Define strategy files
    strategy_dict = {
        "Static": str(RESULTS_DIR / "signals_static_BTC.csv"),
        "Regime-Specific": str(RESULTS_DIR / "signals_regime_specific_BTC.csv"),
        "Hybrid": str(RESULTS_DIR / "signals_hybrid_BTC.csv"),
    }
    
    # Run comparisons
    results, existing_signals = run_pairwise_comparisons(strategy_dict)
    
    if results is None:
        logger.error("Could not run comparisons")
        return
    
    # Generate summary
    summary_df = generate_summary_table(existing_signals)
    
    # Export results
    json_path, csv_path, txt_path = export_results(results, summary_df, existing_signals)
    
    logger.info("=" * 80)
    logger.info("STATISTICAL COMPARISON FOR BTC-USD COMPLETED")
    logger.info("=" * 80)
    logger.info(f"\nResults saved to:")
    logger.info(f"  JSON: {json_path}")
    logger.info(f"  CSV: {csv_path}")
    logger.info(f"  TXT: {txt_path}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("BTC-USD STRATEGY PERFORMANCE SUMMARY")
    print("=" * 80)
    print(summary_df.to_string(index=False))
    print("=" * 80)

if __name__ == "__main__":
    main()
