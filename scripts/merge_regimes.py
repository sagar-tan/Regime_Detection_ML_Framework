import pandas as pd
from pathlib import Path

f_base = Path("data/processed/features_merged.csv")
f_hmm  = Path("data/processed/features_with_hmm_SPY.csv")
f_cp   = Path("data/processed/features_with_cp_SPY.csv")

df_base = pd.read_csv(f_base, parse_dates=["Date"]).set_index("Date")
df_hmm  = pd.read_csv(f_hmm, parse_dates=["Date"]).set_index("Date")
df_cp   = pd.read_csv(f_cp, parse_dates=["Date"]).set_index("Date")

# Extract only the new regime columns
hmm_col = [c for c in df_hmm.columns if "HMM_Regime" in c]
cp_col  = [c for c in df_cp.columns if "CP_Regime" in c]

df_final = df_base.copy()

# Attach HMM regime
for col in hmm_col:
    df_final[col] = df_hmm[col]

# Attach CP regime
for col in cp_col:
    df_final[col] = df_cp[col]

out = Path("data/processed/features_final_SPY.csv")
df_final.reset_index().to_csv(out, index=False)

print("Merged final file saved to:", out)
