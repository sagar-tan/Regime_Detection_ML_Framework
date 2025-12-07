import pandas as pd
from scipy.stats import ttest_rel
import numpy as np

def load_pnl(path):
    df = pd.read_csv(path, parse_dates=["Date"])
    return df["PnL"].values

def sharpe(x):
    return np.mean(x) / (np.std(x) + 1e-9)

if __name__ == "__main__":  
    static = load_pnl("results/signals_static.csv")
    hybrid = load_pnl("results/signals_hybrid.csv")
    regime = load_pnl("results/signals_regime_specific.csv")

    # 1. Paired t-tests
    t_hyb_stat = ttest_rel(hybrid, static)
    t_reg_stat = ttest_rel(regime, static)
    t_hyb_reg  = ttest_rel(hybrid, regime)

    # 2. Sharpe ratios
    sh_static = sharpe(static)
    sh_hybrid = sharpe(hybrid)
    sh_regime = sharpe(regime)

    print("\n===== T-TEST RESULTS =====")
    
    print("Hybrid vs Static:", t_hyb_stat)
    print("Regime vs Static:", t_reg_stat)
    print("Hybrid vs Regime:", t_hyb_reg)

    print("\n===== SHARPE RATIOS =====")

    print(f"Static: {sh_static:.4f}")
    print(f"Regime: {sh_regime:.4f}")
    print(f"Hybrid: {sh_hybrid:.4f}")
