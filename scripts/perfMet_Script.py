from analysis.performance_metrics import compute_all_metrics

metrics = compute_all_metrics(
    "results/signals_SPY.csv",
    "results/equity_curve_SPY.csv"
)

print(metrics)
