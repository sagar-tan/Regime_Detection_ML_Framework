"""
Statistical Significance Testing Module

This module provides statistical tests to validate trading strategy performance
and determine if differences between strategies are statistically significant
(not due to luck).

Key Tests:
- Paired t-test: Compare daily returns between two strategies
- Sharpe ratio comparison: Decompose improvement into return vs volatility
- Win rate significance: Test if hit ratio is better than random
- Maximum drawdown significance: Compare downside risk
"""

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("statistical_tests", log_file="statistical_tests.log")


# ============================================================
# ----- PAIRED T-TEST: COMPARE DAILY RETURNS -----
# ============================================================

def paired_ttest_returns(returns_strategy1, returns_strategy2, strategy1_name="Strategy1", strategy2_name="Strategy2"):
    """
    Paired t-test to determine if two strategies have significantly different daily returns.
    
    Parameters:
    -----------
    returns_strategy1 : pd.Series or np.array
        Daily returns for strategy 1
    returns_strategy2 : pd.Series or np.array
        Daily returns for strategy 2
    strategy1_name : str
        Name of strategy 1 (for logging)
    strategy2_name : str
        Name of strategy 2 (for logging)
    
    Returns:
    --------
    dict with keys:
        - t_statistic: t-test statistic
        - p_value: Two-tailed p-value
        - significant: Boolean (True if p < 0.05)
        - mean_diff: Mean difference in daily returns
        - std_diff: Std dev of differences
        - effect_size: Cohen's d (standardized effect size)
        - interpretation: Human-readable interpretation
    
    Notes:
    ------
    - Null hypothesis: Mean daily returns are equal
    - Alternative: Mean daily returns are different
    - If p-value < 0.05: Reject null hypothesis (significant difference)
    - If p-value >= 0.05: Fail to reject null hypothesis (no significant difference)
    
    Example:
    --------
    >>> result = paired_ttest_returns(hybrid_returns, static_returns, "Hybrid", "Static")
    >>> if result['significant']:
    ...     print(f"Hybrid significantly outperforms Static (p={result['p_value']:.4f})")
    """
    # Convert to numpy arrays
    r1 = np.asarray(returns_strategy1)
    r2 = np.asarray(returns_strategy2)
    
    # Ensure same length
    if len(r1) != len(r2):
        logger.warning(f"Different lengths: {len(r1)} vs {len(r2)}. Truncating to shorter.")
        min_len = min(len(r1), len(r2))
        r1 = r1[:min_len]
        r2 = r2[:min_len]
    
    # Compute differences
    differences = r1 - r2
    
    # Paired t-test
    t_stat, p_value = stats.ttest_rel(r1, r2)
    
    # Effect size (Cohen's d)
    mean_diff = np.mean(differences)
    std_diff = np.std(differences, ddof=1)
    cohens_d = mean_diff / std_diff if std_diff > 0 else 0.0
    
    # Interpretation
    significant = p_value < 0.05
    if significant:
        if mean_diff > 0:
            interpretation = f"{strategy1_name} significantly outperforms {strategy2_name}"
        else:
            interpretation = f"{strategy2_name} significantly outperforms {strategy1_name}"
    else:
        interpretation = f"No significant difference between {strategy1_name} and {strategy2_name}"
    
    result = {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant": bool(significant),
        "mean_diff": float(mean_diff),
        "std_diff": float(std_diff),
        "effect_size": float(cohens_d),
        "interpretation": interpretation,
        "n_observations": len(r1),
    }
    
    logger.info(f"Paired t-test: {strategy1_name} vs {strategy2_name}")
    logger.info(f"  t-statistic: {t_stat:.4f}")
    logger.info(f"  p-value: {p_value:.6f}")
    logger.info(f"  Significant: {significant}")
    logger.info(f"  Mean difference: {mean_diff:.6f}")
    logger.info(f"  Cohen's d: {cohens_d:.4f}")
    logger.info(f"  Interpretation: {interpretation}")
    
    return result


# ============================================================
# ----- SHARPE RATIO DECOMPOSITION -----
# ============================================================

def sharpe_decomposition(returns1, returns2, strategy1_name="Strategy1", strategy2_name="Strategy2"):
    """
    Decompose Sharpe ratio improvement into return and volatility components.
    
    This shows whether strategy 1 outperforms strategy 2 due to:
    1. Higher returns
    2. Lower volatility (risk)
    3. Both
    
    Parameters:
    -----------
    returns1 : pd.Series or np.array
        Daily returns for strategy 1
    returns2 : pd.Series or np.array
        Daily returns for strategy 2
    strategy1_name : str
        Name of strategy 1
    strategy2_name : str
        Name of strategy 2
    
    Returns:
    --------
    dict with keys:
        - sharpe_ratio_1: Sharpe ratio for strategy 1
        - sharpe_ratio_2: Sharpe ratio for strategy 2
        - sharpe_diff: Difference in Sharpe ratios
        - return_1: Annualized return for strategy 1
        - return_2: Annualized return for strategy 2
        - return_diff: Difference in annualized returns
        - vol_1: Annualized volatility for strategy 1
        - vol_2: Annualized volatility for strategy 2
        - vol_diff: Difference in annualized volatility
        - improvement_source: "Higher Return", "Lower Volatility", or "Both"
        - interpretation: Human-readable interpretation
    
    Example:
    --------
    >>> decomp = sharpe_decomposition(hybrid_returns, static_returns, "Hybrid", "Static")
    >>> print(decomp['interpretation'])
    """
    r1 = np.asarray(returns1)
    r2 = np.asarray(returns2)
    
    # Annualized metrics
    ann_ret_1 = (1 + r1.mean()) ** 252 - 1
    ann_ret_2 = (1 + r2.mean()) ** 252 - 1
    
    ann_vol_1 = np.std(r1, ddof=1) * np.sqrt(252)
    ann_vol_2 = np.std(r2, ddof=1) * np.sqrt(252)
    
    # Sharpe ratios (assuming 0% risk-free rate)
    sharpe_1 = ann_ret_1 / ann_vol_1 if ann_vol_1 > 0 else 0.0
    sharpe_2 = ann_ret_2 / ann_vol_2 if ann_vol_2 > 0 else 0.0
    
    sharpe_diff = sharpe_1 - sharpe_2
    return_diff = ann_ret_1 - ann_ret_2
    vol_diff = ann_vol_2 - ann_vol_1  # Negative means lower vol (better)
    
    # Determine source of improvement
    if sharpe_diff > 0:
        if return_diff > 0 and vol_diff > 0:
            improvement_source = "Both Higher Return & Lower Volatility"
        elif return_diff > 0:
            improvement_source = "Higher Return"
        elif vol_diff > 0:
            improvement_source = "Lower Volatility"
        else:
            improvement_source = "Mixed"
    else:
        improvement_source = "No Improvement"
    
    # Interpretation
    interpretation = (
        f"{strategy1_name} vs {strategy2_name}:\n"
        f"  Sharpe Ratio: {sharpe_1:.4f} vs {sharpe_2:.4f} (diff: {sharpe_diff:+.4f})\n"
        f"  Annual Return: {ann_ret_1*100:.2f}% vs {ann_ret_2*100:.2f}% (diff: {return_diff*100:+.2f}%)\n"
        f"  Annual Volatility: {ann_vol_1*100:.2f}% vs {ann_vol_2*100:.2f}% (diff: {vol_diff*100:+.2f}%)\n"
        f"  Improvement Source: {improvement_source}"
    )
    
    result = {
        "sharpe_ratio_1": float(sharpe_1),
        "sharpe_ratio_2": float(sharpe_2),
        "sharpe_diff": float(sharpe_diff),
        "return_1": float(ann_ret_1),
        "return_2": float(ann_ret_2),
        "return_diff": float(return_diff),
        "vol_1": float(ann_vol_1),
        "vol_2": float(ann_vol_2),
        "vol_diff": float(vol_diff),
        "improvement_source": improvement_source,
        "interpretation": interpretation,
    }
    
    logger.info("Sharpe Ratio Decomposition:")
    logger.info(interpretation)
    
    return result


# ============================================================
# ----- WIN RATE SIGNIFICANCE TEST -----
# ============================================================

def win_rate_significance(hit_ratio, n_predictions, null_hypothesis=0.5):
    """
    Test if hit ratio (win rate) is significantly different from random guessing.
    
    Parameters:
    -----------
    hit_ratio : float
        Fraction of correct predictions (0 to 1)
    n_predictions : int
        Total number of predictions
    null_hypothesis : float
        Null hypothesis hit rate (default 0.5 for random)
    
    Returns:
    --------
    dict with keys:
        - hit_ratio: Observed hit ratio
        - null_hypothesis: Null hypothesis hit rate
        - n_predictions: Number of predictions
        - z_statistic: Z-test statistic
        - p_value: Two-tailed p-value
        - significant: Boolean (True if p < 0.05)
        - interpretation: Human-readable interpretation
    
    Example:
    --------
    >>> result = win_rate_significance(0.52, 2975)
    >>> if result['significant']:
    ...     print("Hit rate is significantly better than random!")
    """
    # Binomial test
    n_correct = int(hit_ratio * n_predictions)
    p_value = stats.binom_test(n_correct, n_predictions, null_hypothesis, alternative='two-sided')
    
    # Z-statistic
    p_obs = hit_ratio
    se = np.sqrt(null_hypothesis * (1 - null_hypothesis) / n_predictions)
    z_stat = (p_obs - null_hypothesis) / se if se > 0 else 0.0
    
    significant = p_value < 0.05
    
    if significant:
        if hit_ratio > null_hypothesis:
            interpretation = f"Hit rate ({hit_ratio*100:.2f}%) is significantly BETTER than random ({null_hypothesis*100:.1f}%)"
        else:
            interpretation = f"Hit rate ({hit_ratio*100:.2f}%) is significantly WORSE than random ({null_hypothesis*100:.1f}%)"
    else:
        interpretation = f"Hit rate ({hit_ratio*100:.2f}%) is NOT significantly different from random ({null_hypothesis*100:.1f}%)"
    
    result = {
        "hit_ratio": float(hit_ratio),
        "null_hypothesis": float(null_hypothesis),
        "n_predictions": int(n_predictions),
        "z_statistic": float(z_stat),
        "p_value": float(p_value),
        "significant": bool(significant),
        "interpretation": interpretation,
    }
    
    logger.info("Win Rate Significance Test:")
    logger.info(f"  Hit Ratio: {hit_ratio*100:.2f}%")
    logger.info(f"  Z-statistic: {z_stat:.4f}")
    logger.info(f"  P-value: {p_value:.6f}")
    logger.info(f"  Significant: {significant}")
    logger.info(f"  {interpretation}")
    
    return result


# ============================================================
# ----- MAXIMUM DRAWDOWN SIGNIFICANCE -----
# ============================================================

def max_drawdown_significance(equity1, equity2, strategy1_name="Strategy1", strategy2_name="Strategy2"):
    """
    Compare maximum drawdowns between two strategies using bootstrap.
    
    Parameters:
    -----------
    equity1 : pd.Series or np.array
        Equity curve for strategy 1
    equity2 : pd.Series or np.array
        Equity curve for strategy 2
    strategy1_name : str
        Name of strategy 1
    strategy2_name : str
        Name of strategy 2
    
    Returns:
    --------
    dict with keys:
        - max_dd_1: Max drawdown for strategy 1
        - max_dd_2: Max drawdown for strategy 2
        - dd_diff: Difference in max drawdowns (positive = strategy 1 better)
        - interpretation: Human-readable interpretation
    
    Example:
    --------
    >>> result = max_drawdown_significance(hybrid_equity, static_equity, "Hybrid", "Static")
    >>> print(result['interpretation'])
    """
    eq1 = np.asarray(equity1)
    eq2 = np.asarray(equity2)
    
    # Compute max drawdowns
    def compute_max_dd(equity):
        roll_max = np.maximum.accumulate(equity)
        dd = (equity - roll_max) / roll_max
        return np.min(dd)
    
    mdd1 = compute_max_dd(eq1)
    mdd2 = compute_max_dd(eq2)
    
    dd_diff = mdd2 - mdd1  # Positive means strategy 1 has lower drawdown (better)
    
    if dd_diff > 0:
        interpretation = (
            f"{strategy1_name} has LOWER max drawdown ({mdd1*100:.2f}%) "
            f"than {strategy2_name} ({mdd2*100:.2f}%). "
            f"Risk reduction: {dd_diff*100:.2f}%"
        )
    elif dd_diff < 0:
        interpretation = (
            f"{strategy1_name} has HIGHER max drawdown ({mdd1*100:.2f}%) "
            f"than {strategy2_name} ({mdd2*100:.2f}%). "
            f"Risk increase: {abs(dd_diff)*100:.2f}%"
        )
    else:
        interpretation = f"Both strategies have same max drawdown ({mdd1*100:.2f}%)"
    
    result = {
        "max_dd_1": float(mdd1),
        "max_dd_2": float(mdd2),
        "dd_diff": float(dd_diff),
        "interpretation": interpretation,
    }
    
    logger.info("Maximum Drawdown Comparison:")
    logger.info(f"  {strategy1_name} Max DD: {mdd1*100:.2f}%")
    logger.info(f"  {strategy2_name} Max DD: {mdd2*100:.2f}%")
    logger.info(f"  {interpretation}")
    
    return result


# ============================================================
# ----- COMPREHENSIVE COMPARISON -----
# ============================================================

def compare_strategies(signals_path_1, signals_path_2, strategy1_name="Strategy1", strategy2_name="Strategy2"):
    """
    Comprehensive statistical comparison of two strategies.
    
    Performs all statistical tests and returns a complete report.
    
    Parameters:
    -----------
    signals_path_1 : str
        Path to signals CSV for strategy 1
    signals_path_2 : str
        Path to signals CSV for strategy 2
    strategy1_name : str
        Name of strategy 1
    strategy2_name : str
        Name of strategy 2
    
    Returns:
    --------
    dict with keys:
        - paired_ttest: Paired t-test results
        - sharpe_decomposition: Sharpe ratio decomposition
        - win_rate_test: Win rate significance
        - max_dd_comparison: Max drawdown comparison
        - summary: Human-readable summary
    
    Example:
    --------
    >>> report = compare_strategies(
    ...     "results/signals_hybrid.csv",
    ...     "results/signals_static.csv",
    ...     "Hybrid",
    ...     "Static"
    ... )
    >>> print(report['summary'])
    """
    logger.info(f"Loading signals for {strategy1_name} and {strategy2_name}...")
    
    # Load signals
    df1 = pd.read_csv(signals_path_1, parse_dates=["Date"]).set_index("Date")
    df2 = pd.read_csv(signals_path_2, parse_dates=["Date"]).set_index("Date")
    
    # Align by date
    common_dates = df1.index.intersection(df2.index)
    df1 = df1.loc[common_dates]
    df2 = df2.loc[common_dates]
    
    logger.info(f"Aligned to {len(common_dates)} common dates")
    
    # Extract returns and equity
    returns1 = df1["DayReturn"].values
    returns2 = df2["DayReturn"].values
    equity1 = df1["Equity"].values
    equity2 = df2["Equity"].values
    signals1 = df1["Signal"].values
    
    # Run all tests
    logger.info("Running statistical tests...")
    
    ttest_result = paired_ttest_returns(returns1, returns2, strategy1_name, strategy2_name)
    sharpe_result = sharpe_decomposition(returns1, returns2, strategy1_name, strategy2_name)
    
    # Hit ratio test (using strategy 1's signals)
    correct = (signals1 * returns1 > 0).sum()
    hit_ratio = correct / len(signals1)
    hit_result = win_rate_significance(hit_ratio, len(signals1))
    
    dd_result = max_drawdown_significance(equity1, equity2, strategy1_name, strategy2_name)
    
    # Generate summary
    summary = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║  STATISTICAL SIGNIFICANCE REPORT: {strategy1_name} vs {strategy2_name}
╚════════════════════════════════════════════════════════════════════════════╝

1. DAILY RETURNS COMPARISON (Paired t-test)
   ─────────────────────────────────────────
   {ttest_result['interpretation']}
   
   t-statistic: {ttest_result['t_statistic']:.4f}
   p-value: {ttest_result['p_value']:.6f} {'✓ SIGNIFICANT' if ttest_result['significant'] else '✗ Not significant'}
   Mean daily return difference: {ttest_result['mean_diff']*100:+.4f}%
   Effect size (Cohen's d): {ttest_result['effect_size']:.4f}
   Observations: {ttest_result['n_observations']}

2. SHARPE RATIO DECOMPOSITION
   ──────────────────────────
{sharpe_result['interpretation']}

3. WIN RATE ANALYSIS
   ──────────────────
   {hit_result['interpretation']}
   
   Z-statistic: {hit_result['z_statistic']:.4f}
   P-value: {hit_result['p_value']:.6f}

4. MAXIMUM DRAWDOWN COMPARISON
   ────────────────────────────
   {dd_result['interpretation']}

╔════════════════════════════════════════════════════════════════════════════╗
║  CONCLUSION
╚════════════════════════════════════════════════════════════════════════════╝

Overall Assessment:
  • Daily returns significantly different: {ttest_result['significant']}
  • Sharpe ratio improvement: {sharpe_result['sharpe_diff']:+.4f}
  • Win rate better than random: {hit_result['significant']}
  • Lower maximum drawdown: {dd_result['dd_diff'] > 0}

Research Paper Recommendation:
  {_get_research_recommendation(ttest_result, sharpe_result, hit_result, dd_result)}
"""
    
    result = {
        "paired_ttest": ttest_result,
        "sharpe_decomposition": sharpe_result,
        "win_rate_test": hit_result,
        "max_dd_comparison": dd_result,
        "summary": summary,
    }
    
    logger.info("Comparison complete.")
    return result


def _get_research_recommendation(ttest_result, sharpe_result, hit_result, dd_result):
    """Generate research paper recommendation based on test results."""
    points = 0
    reasons = []
    
    if ttest_result['significant']:
        points += 1
        reasons.append("✓ Statistically significant daily return difference (p < 0.05)")
    
    if sharpe_result['sharpe_diff'] > 0.1:
        points += 1
        reasons.append("✓ Meaningful Sharpe ratio improvement (>0.1)")
    
    if hit_result['significant']:
        points += 1
        reasons.append("✓ Win rate significantly better than random (p < 0.05)")
    
    if dd_result['dd_diff'] > 0.02:
        points += 1
        reasons.append("✓ Significant risk reduction in max drawdown (>2%)")
    
    if points >= 3:
        recommendation = "STRONG EVIDENCE FOR PUBLICATION\n  " + "\n  ".join(reasons)
    elif points >= 2:
        recommendation = "MODERATE EVIDENCE FOR PUBLICATION\n  " + "\n  ".join(reasons)
    else:
        recommendation = "WEAK EVIDENCE - NEEDS IMPROVEMENT\n  " + "\n  ".join(reasons)
    
    return recommendation


# ============================================================
# ----- BATCH COMPARISON (Multiple Strategies) -----
# ============================================================

def compare_multiple_strategies(strategy_results_dict):
    """
    Compare multiple strategies pairwise.
    
    Parameters:
    -----------
    strategy_results_dict : dict
        Dict mapping strategy names to signals CSV paths
        Example: {
            "Static": "results/signals_static.csv",
            "Regime-Specific": "results/signals_regime_specific.csv",
            "Hybrid": "results/signals_hybrid.csv"
        }
    
    Returns:
    --------
    dict with pairwise comparison results
    
    Example:
    --------
    >>> strategies = {
    ...     "Static": "results/signals_static.csv",
    ...     "Hybrid": "results/signals_hybrid.csv",
    ... }
    >>> results = compare_multiple_strategies(strategies)
    """
    results = {}
    strategy_names = list(strategy_results_dict.keys())
    
    for i, strat1 in enumerate(strategy_names):
        for strat2 in strategy_names[i+1:]:
            key = f"{strat1} vs {strat2}"
            logger.info(f"Comparing {key}...")
            
            results[key] = compare_strategies(
                strategy_results_dict[strat1],
                strategy_results_dict[strat2],
                strat1,
                strat2
            )
    
    return results
