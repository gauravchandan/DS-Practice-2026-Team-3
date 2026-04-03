import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Dataset path
file_path = "Fertility (%) - DLHS IV.csv"

# Column names are messy in file, so defining them manually
columns = [
    "States",
    "Districts",
    "Fertility (%) - Births to women aged 15-19 years out of total births3",
    "Fertility (%) - Women aged 20-24 years reporting birth order of 2 & above",
    "Fertility (%) - Women aged 15-49 years who reported birth order of 3 & above",
    "Fertility (%) - Women with two children wanting no more children",
    "Fertility (%) - Mean no. of children ever born to women age 40-49 years"
]

# Reading as fixed-width file (first row is broken, so skipping it)
df = pd.read_fwf(
    file_path,
    skiprows=1,
    widths=[11] * 7,
    names=columns
)

# Getting all fertility-related columns
fertility_cols = [col for col in df.columns if "Fertility (%)" in col]

# Convert them to numeric (invalid values → NaN)
for col in fertility_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Short names (just for cleaner plotting)
rename_map = {
    "Fertility (%) - Births to women aged 15-19 years out of total births3": "Teen (15-19) Births",
    "Fertility (%) - Women aged 20-24 years reporting birth order of 2 & above": "20-24yr, Birth Order 2+",
    "Fertility (%) - Women aged 15-49 years who reported birth order of 3 & above": "15-49yr, Birth Order 3+",
    "Fertility (%) - Women with two children wanting no more children": "Want no more (2 kids)",
    "Fertility (%) - Mean no. of children ever born to women age 40-49 years": "Mean Children (40-49yr)"
}

df_numeric = df[fertility_cols].rename(columns=rename_map)

# Plot style
sns.set_theme(style="white")

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(20, 8))

# Plot 1: Correlation Heatmap 
corr_matrix = df_numeric.corr()

sns.heatmap(
    corr_matrix,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    ax=axes[0],
    vmin=-1,
    vmax=1,
    linewidths=0.5
)

axes[0].set_title("Correlation Heatmap of all DLHS Fertility Indicators", fontsize=14)

# Plot 2: Hexbin Density 
x_col = "Teen (15-19) Births"
y_col = "15-49yr, Birth Order 3+"

# Drop missing values only for required columns
df_clean = df_numeric.dropna(subset=[x_col, y_col])

axes[1].hexbin(
    df_clean[x_col],
    df_clean[y_col],
    gridsize=20,
    cmap="Blues",
    mincnt=1
)

axes[1].set_title("Density: Teen Births vs High Birth Orders")
axes[1].set_xlabel("Percentage of Teen Births (Age 15-19)")
axes[1].set_ylabel("Percentage of Women with 3+ Births (Age 15-49)")

# Final adjustments
plt.tight_layout()
plt.show()