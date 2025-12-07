import pandas as pd
df = pd.read_csv("data/processed/features_final_SPY.csv")

print(df["SPY_HMM_Regime"].value_counts())
print(df["SPY_CP_Regime"].value_counts())
print(df[["SPY_HMM_Regime","SPY_CP_Regime"]].head(30))
print(df[["SPY_HMM_Regime","SPY_CP_Regime"]].tail(30))
