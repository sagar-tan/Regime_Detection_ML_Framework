import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from analysis.utils_plot import savefig

def plot_transition_windows(signals_path, save_path, window=20):
    df = pd.read_csv(signals_path, parse_dates=["Date"]).set_index("Date")
    df["RegimePrev"] = df["Regime"].shift(1)

    transition_dates = df[df["Regime"] != df["RegimePrev"]].index

    curves = []

    for date in transition_dates:
        idx = df.index.get_loc(date)
        start = max(0, idx - window)
        end = min(len(df)-1, idx + window)

        segment = df.iloc[start:end]["DayReturn"].values
        if len(segment) == (window*2):
            curves.append(segment)

    if len(curves) == 0:
        print("No valid transitions found.")
        return

    curves = np.array(curves)
    mean_curve = curves.mean(axis=0)

    x = np.arange(-window, window)

    plt.figure(figsize=(12,6))
    plt.axvline(0, color='red', linewidth=2, label="Regime Change")
    plt.plot(x, mean_curve, label="Avg Return Around Regime Shift")
    plt.title("Average Returns ± Window Around Regime Flip")
    plt.xlabel("Days Relative to Transition")
    plt.ylabel("Avg Daily Return")
    plt.legend()

    savefig(save_path)

if __name__ == "__main__":
    plot_transition_windows(
        "results/signals_SPY.csv",
        "results/figures/transition_window_SPY.png"
    )
