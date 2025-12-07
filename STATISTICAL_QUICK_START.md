# Statistical Significance - Quick Start Guide

**TL;DR:** 3 steps to prove your strategy isn't just lucky

---

## The Problem You're Solving

```
❌ WEAK: "Strategy A made 10%, Strategy B made 8%"
✅ STRONG: "Strategy A significantly outperforms Strategy B (p=0.034)"
```

Reviewers want p-values < 0.05 to believe you.

---

## 3-Step Quick Start

### Step 1: Generate Strategy Results (10 minutes)

Run backtest 3 times with different strategies:

```bash
# 1a. Static Strategy
# Edit: backtest/walk_forward_engine.py, line 44
STRATEGY_MODE = "static"
python backtest/walk_forward_engine.py
mv results/signals_SPY.csv results/signals_static.csv

# 1b. Regime-Specific Strategy
# Edit: backtest/walk_forward_engine.py, line 44
STRATEGY_MODE = "regime_specific"
python backtest/walk_forward_engine.py
mv results/signals_SPY.csv results/signals_regime_specific.csv

# 1c. Hybrid Strategy
# Edit: backtest/walk_forward_engine.py, line 44
STRATEGY_MODE = "hybrid"
python backtest/walk_forward_engine.py
# Keep as is
```

### Step 2: Generate Buy-and-Hold Baseline (1 minute)

```bash
python scripts/buy_and_hold_baseline.py
```

Creates `results/signals_bah.csv` - your benchmark.

### Step 3: Run Statistical Comparison (1 minute)

```bash
python scripts/statistical_comparison.py
```

Generates:
- `results/statistical_comparison.json` - Detailed results
- `results/strategy_summary.csv` - Metrics table
- `results/statistical_report.txt` - Formatted report

**Total time: ~15 minutes**

---

## What You Get

### Console Output (Immediate)
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

CONCLUSION:
  STRONG EVIDENCE FOR PUBLICATION ✓
  ✓ Statistically significant daily return difference (p < 0.05)
  ✓ Meaningful Sharpe ratio improvement (>0.1)
  ✓ Win rate significantly better than random (p < 0.05)
  ✓ Significant risk reduction in max drawdown (>2%)
```

### CSV Output
```
Strategy,Total Return (%),Ann. Return (%),Sharpe Ratio,Max Drawdown (%)
Static,23.45,12.23,0.7761,-9.45
Regime-Specific,25.67,13.45,0.9034,-8.12
Hybrid,26.78,14.12,0.9345,-8.23
Buy-and-Hold,18.90,10.12,0.6234,-12.34
```

### JSON Output
```json
{
  "Hybrid vs Static": {
    "paired_ttest": {
      "p_value": 0.0342,
      "significant": true,
      "mean_diff": 0.000234,
      "effect_size": 0.1567
    },
    "sharpe_decomposition": {
      "sharpe_diff": 0.1111,
      "improvement_source": "Both Higher Return & Lower Volatility"
    }
  }
}
```

---

## Key Metrics Explained

### 1. P-Value (Most Important)
```
p < 0.05  → ✓ SIGNIFICANT (claim this in your paper!)
p >= 0.05 → ✗ NOT significant (don't claim it)
```

**Example:**
- p = 0.034 → "Statistically significant (p=0.034)"
- p = 0.23 → "Not statistically significant (p=0.23)"

### 2. Effect Size (Cohen's d)
```
0.2 = small effect
0.5 = medium effect
0.8 = large effect
```

**Example:**
- d = 0.157 → Small but real effect
- d = 0.5 → Medium effect (good!)

### 3. Sharpe Ratio Improvement
```
Source: "Both Higher Return & Lower Volatility" → BEST ✓✓
Source: "Higher Return" → Good ✓
Source: "Lower Volatility" → Risk reduction ✓
```

### 4. Win Rate
```
Hit Ratio > 50% AND p < 0.05 → ✓ Better than random
Hit Ratio < 50% AND p < 0.05 → ✗ Worse than random
Hit Ratio ≈ 50% OR p >= 0.05 → ✗ Same as random
```

### 5. Maximum Drawdown
```
Positive dd_diff → Strategy 1 has lower drawdown (better) ✓
Negative dd_diff → Strategy 1 has higher drawdown (worse) ✗
```

---

## For Your Research Paper

### Copy-Paste Template

```
We compared three adaptation strategies using walk-forward backtesting 
over 2,975 trading days. Paired t-tests on daily returns show that the 
Hybrid strategy significantly outperforms the Static strategy 
(t=2.12, p=0.034), with an average daily return advantage of +0.0036% 
(Cohen's d=0.157).

Sharpe ratio decomposition reveals that the improvement stems from both 
higher returns (+1.22% annualized) and lower volatility (-0.66% annualized). 
The Hybrid strategy's hit ratio (52.34%) is significantly better than 
random guessing (50%, z=2.15, p=0.032). Maximum drawdown analysis shows 
a 1.22% risk reduction compared to the Static strategy (-8.23% vs -9.45%).

Overall, these results provide strong statistical evidence that regime-aware 
adaptation strategies outperform static approaches across multiple dimensions.
```

---

## Common Questions

### Q: What if p-value is 0.06?
**A:** Not significant. You can't claim it in your paper. Try:
- Longer backtest period
- Different model hyperparameters
- Different regime detection method

### Q: What if all tests show no significance?
**A:** Your strategy might not actually help. Check:
- Are regimes being detected? (Check logs)
- Is model retraining? (Check logs)
- Try different assets or time periods

### Q: Can I cherry-pick results?
**A:** No! Report all comparisons, even if not significant. Reviewers will ask.

### Q: What about multiple comparisons problem?
**A:** If comparing 6 strategies, use Bonferroni correction:
```python
alpha = 0.05 / 6  # Adjusted threshold
```

### Q: How many observations do I need?
**A:** More is better. With 2,975 daily returns, you have plenty.

---

## Files Created

```
analysis/
└── statistical_tests.py              # Core tests (450+ lines)

scripts/
├── statistical_comparison.py         # Main script (300+ lines)
└── buy_and_hold_baseline.py         # Baseline generator (150+ lines)

Documentation/
├── STATISTICAL_SIGNIFICANCE.md       # Detailed guide (500+ lines)
├── IMPLEMENTATION_SUMMARY.md         # What was done
└── STATISTICAL_QUICK_START.md       # This file
```

---

## Checklist Before Submitting Paper

- [ ] Paired t-test run (p-value reported)
- [ ] Sharpe decomposition done (return vs vol breakdown)
- [ ] Win rate test run (hit ratio vs random)
- [ ] Max drawdown compared
- [ ] Effect sizes reported (Cohen's d)
- [ ] Sample size reported (n=2975)
- [ ] Multiple strategies compared (not just one)
- [ ] Buy-and-hold baseline included
- [ ] All claimed significance has p < 0.05
- [ ] Limitations discussed

---

## Example Claims You Can Make

### ✓ GOOD (With Statistical Evidence)
- "Strategy A significantly outperforms Strategy B (p=0.034)"
- "Improvement driven by both higher returns and lower volatility"
- "Hit rate significantly better than random (p=0.032)"
- "Risk reduction of 1.22% in maximum drawdown"

### ✗ BAD (Without Statistical Evidence)
- "Strategy A is better" (no p-value)
- "Strategy A made 10%, B made 8%" (no significance test)
- "Our model predicts better" (no hit rate test)
- "Lower drawdown" (no comparison)

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "FileNotFoundError: signals_static.csv" | Run backtest with STRATEGY_MODE="static" |
| "p-value = 1.0" | Strategies too similar or sample too small |
| "All tests not significant" | Strategy might not help; check logs |
| "Different lengths error" | Normal; code handles it automatically |

---

## Next Steps

1. **Read:** `STATISTICAL_SIGNIFICANCE.md` for detailed guide
2. **Run:** 3 backtests with different strategies
3. **Generate:** Buy-and-hold baseline
4. **Compare:** Run statistical comparison
5. **Write:** Use template for paper

---

## One-Liner Commands

```bash
# Generate baseline
python scripts/buy_and_hold_baseline.py

# Run comparison
python scripts/statistical_comparison.py

# View results
cat results/statistical_report.txt
```

---

## Key Insight

**The magic number is 0.05**

If p-value < 0.05 → You have statistical significance ✓  
If p-value >= 0.05 → You don't → Don't claim it ✗

That's it!

---

**Ready to prove your strategy isn't just lucky?**

Start with Step 1 above. You'll have results in 15 minutes.

---

*For detailed explanations, see: STATISTICAL_SIGNIFICANCE.md*  
*For implementation details, see: IMPLEMENTATION_SUMMARY.md*
