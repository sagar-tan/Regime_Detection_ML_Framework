import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

colors = {
    "equity": "#2979FF",
    "spy": "#000000",
    "regime_0": "#90CAF9",
    "regime_1": "#FF7043",
    "regime_2": "#66BB6A",
    "regime_3": "#AB47BC",
    "regime_4": "#FFA726",
}

def savefig(path):
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()
