from analysis.plot_equity import plot_equity_curve
from analysis.plot_regimes import plot_regime_timeline
from analysis.plot_transitions import plot_transition_windows

def generate_all():
    plot_equity_curve(
        "results/signals_SPY.csv",
        "results/equity_curve_SPY.csv",
        "results/figures/equity_curve_SPY.png"
    )

    plot_regime_timeline(
        "data/processed/features_final_SPY.csv",
        "results/figures/hmm_timeline_SPY.png"
    )

    plot_transition_windows( 
        "results/signals_SPY.csv",
        "results/figures/transition_window_SPY.png"
    )

if __name__ == "__main__":
    generate_all()
