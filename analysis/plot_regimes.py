import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from analysis.utils_plot import colors, savefig

def plot_regime_timeline(features_path, save_path):
    df = pd.read_csv(features_path, parse_dates=["Date"]).set_index("Date")

    price = df["SPY_Close"]
    hmm = df["SPY_HMM_Regime"]
    cp = df["SPY_CP_Regime"]

    plt.figure(figsize=(14,6))
    plt.plot(price.index, price.values, label="SPY Price", color=colors["spy"])

    # Regime color shading
    for regime in sorted(hmm.unique()):
        mask = hmm == regime
        plt.scatter(price.index[mask], price.values[mask],
                    s=6, label=f"HMM Regime {regime}")

    plt.title("HMM Regime Timeline")
    plt.xlabel("Date"); plt.ylabel("Price")
    plt.legend(markerscale=3)
    savefig(save_path)

if __name__ == "__main__":
    plot_regime_timeline(
        "data/processed/features_final_SPY.csv",
        "results/figures/hmm_timeline_SPY.png"
    )
