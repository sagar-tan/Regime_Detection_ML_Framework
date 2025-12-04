import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from analysis.utils_plot import colors, savefig

def plot_equity_curve(signals_path, equity_path, save_path):
    df_sig = pd.read_csv(signals_path, parse_dates=["Date"]).set_index("Date")
    df_eq = pd.read_csv(equity_path, parse_dates=["Date"]).set_index("Date")

    plt.figure(figsize=(12,6))
    plt.plot(df_eq.index, df_eq["Equity"], label="Model Equity", color=colors["equity"])

    # Optional: plot SPY buy-and-hold baseline
    spy = (df_sig["DayReturn"] + 1).cumprod()
    plt.plot(spy.index, spy.values, label="SPY Buy & Hold", color=colors["spy"], alpha=0.5)

    plt.title("Equity Curve")
    plt.ylabel("Equity")
    plt.xlabel("Date")
    plt.legend()
    savefig(save_path)

if __name__ == "__main__":
    plot_equity_curve(
        "results/signals_SPY.csv",
        "results/equity_curve_SPY.csv",
        "results/figures/equity_curve_SPY.png"
    )
