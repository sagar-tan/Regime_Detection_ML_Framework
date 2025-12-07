# Statistical Significance Testing - Implementation Guide

**Document Version:** 1.0  
**Last Updated:** December 7, 2025

---

## Overview

This guide explains how to implement and use statistical significance testing in your trading framework to prove that strategy outperformance is not due to luck.

**Key Question:** "Did Strategy A outperform Strategy B because it's genuinely better, or just by chance?"

**Answer:** Statistical significance testing with p-values < 0.05

---

## Why Statistical Significance Matters

### For Research Papers
- ✅ Reviewers demand p-values < 0.05 to claim "statistically significant outperformance"
- ✅ Separates genuine alpha from luck
- ✅ Makes your findings credible and publishable

### For Trading
- ✅ Validates strategy improvements are real
- ✅ Identifies which components actually help
- ✅ Prevents over-fitting and false positives

### Example
```
Claim: "Strategy A made 10% vs Strategy B made 8%"
Problem: Could be luck (2% difference might be noise)

Solution: Run t-test
Result: p-value = 0.02 (< 0.05)
Conclusion: "Strategy A significantly outperforms Strategy B (p=0.02)"
```

---

## Implementation Architecture

### New Files Created

```
analysis/
├── statistical_tests.py          # Core statistical testing functions
│   ├── paired_ttest_returns()    # Compare daily returns
│   ├── sharpe_decomposition()    # Break down Sharpe improvement
│   ├── win_rate_significance()   # Test if hit rate > random
│   ├── max_drawdown_significance() # Compare risk
│   └── compare_strategies()      # Comprehensive comparison
│
scripts/
├── statistical_comparison.py     # Main comparison script
│   └── Runs all pairwise tests
│
├── buy_and_hold_baseline.py      # Generate buy-and-hold baseline
│   └── Creates benchmark for comparison
```

### Workflow

```
1. Run Backtest (3 times with different strategies)
   ├─ STRATEGY_MODE = "static"
   ├─ STRATEGY_MODE = "regime_specific"
   └─ STRATEGY_MODE = "hybrid"
   
2. Generate Buy-and-Hold Baseline
   └─ python scripts/buy_and_hold_baseline.py
   
3. Run Statistical Comparison
   └─ python scripts/statistical_comparison.py
   
4. Review Results
   ├─ Console output (summary)
   ├─ results/statistical_comparison.json (detailed)
   ├─ results/strategy_summary.csv (metrics table)
   └─ results/statistical_report.txt (formatted report)
```

---

## Step-by-Step Implementation

### Step 1: Generate Strategy Results

You need to run the backtest 3 times with different strategies:

#### 1a. Static Strategy
```bash
# Edit: backtest/walk_forward_engine.py, line 44
STRATEGY_MODE = "static"

# Run backtest
python backtest/walk_forward_engine.py

# Save results
mv results/signals_SPY.csv results/signals_static.csv
mv results/equity_curve_SPY.csv results/equity_static.csv
```

#### 1b. Regime-Specific Strategy
```bash
# Edit: backtest/walk_forward_engine.py, line 44
STRATEGY_MODE = "regime_specific"

# Run backtest
python backtest/walk_forward_engine.py

# Save results
mv results/signals_SPY.csv results/signals_regime_specific.csv
mv results/equity_curve_SPY.csv results/equity_regime_specific.csv
```

#### 1c. Hybrid Strategy
```bash
# Edit: backtest/walk_forward_engine.py, line 44
STRATEGY_MODE = "hybrid"

# Run backtest
python backtest/walk_forward_engine.py

# Keep as is (or save if you want)
# results/signals_SPY.csv → results/signals_hybrid.csv
```

### Step 2: Generate Buy-and-Hold Baseline

```bash
python scripts/buy_and_hold_baseline.py
```

This creates `results/signals_bah.csv` - a baseline where you always hold the asset.

### Step 3: Run Statistical Comparison

```bash
python scripts/statistical_comparison.py
```

This runs all pairwise comparisons and generates:
- `results/statistical_comparison.json` - Detailed results
- `results/strategy_summary.csv` - Metrics table
- `results/statistical_report.txt` - Formatted report

---

## Statistical Tests Explained

### 1. Paired T-Test (Daily Returns)

**Purpose:** Test if two strategies have significantly different daily returns

**Null Hypothesis:** Mean daily returns are equal

**Code:**
```python
from scipy.stats import ttest_rel
from analysis.statistical_tests import paired_ttest_returns

# Load returns
hybrid_returns = df_hybrid["DayReturn"].values
static_returns = df_static["DayReturn"].values

# Run test
result = paired_ttest_returns(hybrid_returns, static_returns, "Hybrid", "Static")

# Interpret
if result['p_value'] < 0.05:
    print(f"✓ Significant difference (p={result['p_value']:.4f})")
else:
    print(f"✗ No significant difference (p={result['p_value']:.4f})")
```

**Output:**
```
t_statistic: 2.1234
p_value: 0.0342
significant: True
mean_diff: 0.000234 (daily return difference)
effect_size: 0.1567 (Cohen's d)
interpretation: "Hybrid significantly outperforms Static"
```

**Interpretation:**
- **p < 0.05:** Statistically significant difference ✓
- **p >= 0.05:** No significant difference ✗
- **Effect size (Cohen's d):**
  - 0.2 = small effect
  - 0.5 = medium effect
  - 0.8 = large effect

---

### 2. Sharpe Ratio Decomposition

**Purpose:** Understand if improvement comes from higher returns or lower volatility

**Why It Matters:** Regime-aware models often shine by reducing volatility, not just increasing returns

**Code:**
```python
from analysis.statistical_tests import sharpe_decomposition

result = sharpe_decomposition(
    hybrid_returns, 
    static_returns, 
    "Hybrid", 
    "Static"
)

print(result['interpretation'])
```

**Output:**
```
Hybrid vs Static:
  Sharpe Ratio: 0.8234 vs 0.7123 (diff: +0.1111)
  Annual Return: 12.45% vs 11.23% (diff: +1.22%)
  Annual Volatility: 15.10% vs 15.76% (diff: -0.66%)
  Improvement Source: Both Higher Return & Lower Volatility
```

**Interpretation:**
- **Higher Return + Lower Volatility:** Best case ✓✓
- **Higher Return Only:** Good but risky ✓
- **Lower Volatility Only:** Risk reduction (defensive) ✓
- **No Improvement:** Strategy doesn't help ✗

---

### 3. Win Rate Significance Test

**Purpose:** Test if hit ratio (prediction accuracy) is better than random guessing

**Null Hypothesis:** Hit rate = 50% (random)

**Code:**
```python
from analysis.statistical_tests import win_rate_significance

# Calculate hit ratio
correct = (signals * returns > 0).sum()
hit_ratio = correct / len(signals)

result = win_rate_significance(hit_ratio, len(signals))

print(result['interpretation'])
```

**Output:**
```
Hit Ratio: 52.34%
Z-statistic: 2.1456
P-value: 0.0319
Significant: True
Interpretation: "Hit rate (52.34%) is significantly BETTER than random (50.0%)"
```

**Interpretation:**
- **p < 0.05 and hit_ratio > 50%:** Predictions better than random ✓
- **p < 0.05 and hit_ratio < 50%:** Predictions worse than random ✗
- **p >= 0.05:** No significant difference from random ✗

---

### 4. Maximum Drawdown Comparison

**Purpose:** Compare downside risk between strategies

**Code:**
```python
from analysis.statistical_tests import max_drawdown_significance

result = max_drawdown_significance(
    hybrid_equity, 
    static_equity, 
    "Hybrid", 
    "Static"
)

print(result['interpretation'])
```

**Output:**
```
Hybrid has LOWER max drawdown (-8.23%) than Static (-9.45%).
Risk reduction: 1.22%
```

**Interpretation:**
- **Positive dd_diff:** Strategy 1 has lower drawdown (better) ✓
- **Negative dd_diff:** Strategy 1 has higher drawdown (worse) ✗

---

### 5. Comprehensive Comparison

**Purpose:** Run all tests at once

**Code:**
```python
from analysis.statistical_tests import compare_strategies

report = compare_strategies(
    "results/signals_hybrid.csv",
    "results/signals_static.csv",
    "Hybrid",
    "Static"
)

print(report['summary'])
```

**Output:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║  STATISTICAL SIGNIFICANCE REPORT: Hybrid vs Static
╚════════════════════════════════════════════════════════════════════════════╝

1. DAILY RETURNS COMPARISON (Paired t-test)
   Hybrid significantly outperforms Static
   t-statistic: 2.1234
   p-value: 0.0342 ✓ SIGNIFICANT
   Mean daily return difference: +0.0234%
   Effect size (Cohen's d): 0.1567

2. SHARPE RATIO DECOMPOSITION
   Sharpe Ratio: 0.8234 vs 0.7123 (diff: +0.1111)
   Annual Return: 12.45% vs 11.23% (diff: +1.22%)
   Annual Volatility: 15.10% vs 15.76% (diff: -0.66%)
   Improvement Source: Both Higher Return & Lower Volatility

3. WIN RATE ANALYSIS
   Hit rate (52.34%) is significantly BETTER than random (50.0%)
   Z-statistic: 2.1456
   P-value: 0.0319

4. MAXIMUM DRAWDOWN COMPARISON
   Hybrid has LOWER max drawdown (-8.23%) than Static (-9.45%).
   Risk reduction: 1.22%

╔════════════════════════════════════════════════════════════════════════════╗
║  CONCLUSION
╚════════════════════════════════════════════════════════════════════════════╝

Overall Assessment:
  • Daily returns significantly different: True
  • Sharpe ratio improvement: +0.1111
  • Win rate better than random: True
  • Lower maximum drawdown: True

Research Paper Recommendation:
  STRONG EVIDENCE FOR PUBLICATION
  ✓ Statistically significant daily return difference (p < 0.05)
  ✓ Meaningful Sharpe ratio improvement (>0.1)
  ✓ Win rate significantly better than random (p < 0.05)
  ✓ Significant risk reduction in max drawdown (>2%)
```

---

## Output Files

### 1. statistical_comparison.json
Detailed results for all pairwise comparisons

```json
{
  "Hybrid vs Static": {
    "paired_ttest": {
      "t_statistic": 2.1234,
      "p_value": 0.0342,
      "significant": true,
      "mean_diff": 0.000234,
      "effect_size": 0.1567
    },
    "sharpe_decomposition": {
      "sharpe_ratio_1": 0.8234,
      "sharpe_ratio_2": 0.7123,
      "sharpe_diff": 0.1111,
      "improvement_source": "Both Higher Return & Lower Volatility"
    },
    "win_rate_test": {
      "hit_ratio": 0.5234,
      "p_value": 0.0319,
      "significant": true
    },
    "max_dd_comparison": {
      "max_dd_1": -0.0823,
      "max_dd_2": -0.0945,
      "dd_diff": 0.0122
    }
  }
}
```

### 2. strategy_summary.csv
Summary metrics table for all strategies

```
Strategy,Total Return (%),Ann. Return (%),Ann. Volatility (%),Sharpe Ratio,Sortino Ratio,Max Drawdown (%),Hit Ratio (%)
Static,23.45,12.23,15.76,0.7761,1.2345,-9.45,51.23
Regime-Specific,25.67,13.45,14.89,0.9034,1.4567,-8.12,52.34
Hybrid,26.78,14.12,15.10,0.9345,1.5234,-8.23,52.89
Buy-and-Hold,18.90,10.12,16.23,0.6234,0.9876,-12.34,50.00
```

### 3. statistical_report.txt
Formatted report with all comparisons

---

## What to Report in Your Research Paper

### For Each Strategy Comparison

**Template:**
```
Strategy A significantly outperforms Strategy B across multiple dimensions:

1. Daily Returns:
   - Strategy A: +0.0234% average daily return
   - Strategy B: +0.0198% average daily return
   - Difference: +0.0036% (t=2.12, p=0.034) ✓ Significant

2. Risk-Adjusted Returns (Sharpe Ratio):
   - Strategy A: 0.824 vs Strategy B: 0.712 (+0.112 improvement)
   - Source: Both higher returns (+1.22%) and lower volatility (-0.66%)

3. Prediction Accuracy:
   - Hit Ratio: 52.34% vs 50.00% (random)
   - Z-statistic: 2.15, p-value: 0.032 ✓ Significant

4. Downside Risk:
   - Max Drawdown: -8.23% vs -9.45% (1.22% risk reduction)

Overall: Strategy A demonstrates statistically significant outperformance
with strong evidence across return, risk, and prediction metrics.
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Multiple Comparisons Problem
**Problem:** Running many tests increases chance of false positives

**Solution:** Use Bonferroni correction
```python
n_comparisons = 6  # Number of pairwise comparisons
alpha = 0.05 / n_comparisons  # Adjusted threshold
```

### Pitfall 2: Look-Ahead Bias
**Problem:** Using future data to train models

**Solution:** Use walk-forward backtesting (already implemented)

### Pitfall 3: Overfitting
**Problem:** Model fits noise, not signal

**Solution:** 
- Use out-of-sample testing
- Check if results hold on different assets
- Use cross-validation

### Pitfall 4: Ignoring Effect Size
**Problem:** Statistically significant but economically insignificant

**Solution:** Report both p-value AND effect size (Cohen's d)

### Pitfall 5: Cherry-Picking Results
**Problem:** Only reporting positive comparisons

**Solution:** Report all comparisons (even if not significant)

---

## Advanced: Custom Statistical Tests

### Add Your Own Test

```python
# In analysis/statistical_tests.py

def my_custom_test(returns1, returns2, strategy1_name, strategy2_name):
    """Your custom statistical test."""
    
    # Your test logic here
    result = {
        "test_statistic": float(stat),
        "p_value": float(p_val),
        "significant": bool(p_val < 0.05),
        "interpretation": "Your interpretation",
    }
    
    logger.info(f"Custom Test: {interpretation}")
    return result
```

### Add to Comparison

```python
# In compare_strategies()

custom_result = my_custom_test(returns1, returns2, strategy1_name, strategy2_name)
result["custom_test"] = custom_result
```

---

## Troubleshooting

### Error: "FileNotFoundError: results/signals_static.csv"
**Solution:** Run backtest with STRATEGY_MODE = "static" first

### Error: "Different lengths: 2975 vs 2974"
**Solution:** Dates don't align perfectly. Code automatically truncates to shorter length.

### p-value = 1.0 (No difference)
**Possible Causes:**
- Strategies are too similar
- Sample size too small
- High noise in data

**Solution:** 
- Try different strategies
- Use longer backtest period
- Reduce transaction costs

### All tests show no significance
**Possible Causes:**
- Strategy doesn't actually help
- Regime detection not working
- Model not trained properly

**Solution:**
- Check logs for errors
- Verify regime changes are detected
- Try different model hyperparameters

---

## Integration with Existing Code

### Update walk_forward_engine.py

No changes needed! The framework already generates the signals CSV files needed.

### Update performance_metrics.py

Optional: Add statistical tests to `compute_all_metrics()`

```python
# In analysis/performance_metrics.py

from analysis.statistical_tests import paired_ttest_returns

def compute_all_metrics(signals_path, equity_path):
    # ... existing code ...
    
    # Add statistical tests
    metrics["statistical_tests"] = {
        "paired_ttest": paired_ttest_returns(returns, returns)  # Compare to self as example
    }
    
    return metrics
```

---

## Research Paper Checklist

Before submitting your paper, ensure you have:

- [ ] Paired t-test comparing daily returns (p-value reported)
- [ ] Sharpe ratio decomposition (return vs volatility breakdown)
- [ ] Win rate significance test (hit ratio vs random)
- [ ] Maximum drawdown comparison
- [ ] Effect sizes reported (Cohen's d)
- [ ] Sample size reported (n observations)
- [ ] Multiple strategy comparisons (not just one)
- [ ] Buy-and-hold baseline included
- [ ] All p-values < 0.05 for claimed significance
- [ ] Limitations and caveats discussed

---

## Example: Complete Research Paper Section

```
4. EMPIRICAL RESULTS

4.1 Strategy Comparison

We compared three adaptation strategies (Static, Regime-Specific, Hybrid) 
against a buy-and-hold benchmark using walk-forward backtesting over 
2,975 trading days (2013-2025).

Table 1 presents summary statistics for each strategy...

4.2 Statistical Significance

To validate that observed differences are not due to chance, we conducted 
paired t-tests on daily returns. Results show that the Hybrid strategy 
significantly outperforms the Static strategy (t=2.12, p=0.034), with 
an average daily return advantage of +0.0036% (Cohen's d=0.157).

Sharpe ratio decomposition reveals that the improvement stems from both 
higher returns (+1.22% annualized) and lower volatility (-0.66% annualized), 
suggesting that regime awareness reduces downside risk without sacrificing 
upside potential.

The Hybrid strategy's hit ratio (52.34%) is significantly better than 
random guessing (50%, z=2.15, p=0.032), indicating genuine predictive 
power. Maximum drawdown analysis shows a 1.22% risk reduction compared 
to the Static strategy (-8.23% vs -9.45%).

Overall, these results provide strong statistical evidence that regime-aware 
adaptation strategies outperform static approaches...
```

---

## Next Steps

1. **Run the framework:** Follow Step 1-3 above
2. **Review results:** Check JSON, CSV, and TXT files
3. **Interpret findings:** Use this guide to understand outputs
4. **Write paper:** Use the checklist and example above
5. **Submit:** Include statistical significance evidence

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025
