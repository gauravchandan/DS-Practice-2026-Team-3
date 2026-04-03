import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
FIG_DIR = os.path.join(os.path.dirname(__file__), "report", "figs")
os.makedirs(FIG_DIR, exist_ok=True)

print("Plot 1: Life Expectancy")
df_wb = pd.read_csv(os.path.join(DATA_DIR, "WorldBank_Final.csv")).replace('..', np.nan)
df_wb_melt = df_wb.melt(id_vars=['Series Name'], var_name='YearRaw', value_name='Value')
df_wb_melt['Year'] = df_wb_melt['YearRaw'].str.extract(r'(\d{4})').astype(float)
df_wb_melt['Value'] = pd.to_numeric(df_wb_melt['Value'], errors='coerce')
df_wb_melt['Value'] = df_wb_melt.groupby('Series Name')['Value'].transform(lambda x: x.interpolate(limit_direction='both'))
df_wb_wide = df_wb_melt.dropna(subset=['Year']).pivot(index='Year', columns='Series Name', values='Value').reset_index()

plt.figure(figsize=(10, 6))
plt.plot(df_wb_wide['Year'], df_wb_wide["Life expectancy at birth, female (years)"], label='Female Life Exp.', color='crimson')
plt.plot(df_wb_wide['Year'], df_wb_wide["Life expectancy at birth, male (years)"], label='Male Life Exp.', color='royalblue')
plt.title("Life Expectancy (1960-2025)")
plt.xlabel("Year")
plt.ylabel("Age (years)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(os.path.join(FIG_DIR, "life_expectancy.pdf"), bbox_inches='tight')
plt.close()

print("Plot 2: TFR vs MCPR")
df_mcpr = pd.read_csv(os.path.join(DATA_DIR, "tfr_mcpr_2011.csv"))
df_mcpr = df_mcpr[~df_mcpr['State'].str.upper().isin(['INDIA', 'ALL INDIA'])]
plt.figure(figsize=(8, 6))
plt.scatter(df_mcpr['MCPR_Pct'], df_mcpr['TFR_2011'], color='purple', alpha=0.7)
plt.axhline(y=2.1, color='red', linestyle='--', label='Replacement Level (2.1)')
plt.title("Total Fertility Rate vs Modern Contraceptive Prevalence Rate")
plt.xlabel("MCPR (%)")
plt.ylabel("Total Fertility Rate (TFR)")
for i, row in df_mcpr.iterrows():
    plt.text(row['MCPR_Pct'], row['TFR_2011'], row['State'], fontsize=8)
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(os.path.join(FIG_DIR, "tfr_vs_mcpr.pdf"), bbox_inches='tight')
plt.close()

print("Plot 3: Crude Birth vs Death Rate")
plt.figure(figsize=(10, 6))
plt.plot(df_wb_wide['Year'], df_wb_wide["Birth rate, crude (per 1,000 people)"], label='Crude Birth Rate', color='forestgreen')
plt.plot(df_wb_wide['Year'], df_wb_wide["Death rate, crude (per 1,000 people)"], label='Crude Death Rate', color='crimson')
plt.title("Crude Birth Rate vs Crude Death Rate")
plt.xlabel("Year")
plt.ylabel("Rate (per 1,000 people)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(os.path.join(FIG_DIR, "crude_rates.pdf"), bbox_inches='tight')
plt.close()

print("Done")
