import pandas as pd

s = pd.read_csv("results/signals_static.csv")["Signal"]
r = pd.read_csv("results/signals_regime_specific.csv")["Signal"]
h = pd.read_csv("results/signals_hybrid.csv")["Signal"]

print("Static vs Regime-Specific:", (s != r).sum())
print("Static vs Hybrid:", (s != h).sum())
print("Regime-Specific vs Hybrid:", (r != h).sum())
