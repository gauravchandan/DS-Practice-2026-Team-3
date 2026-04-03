import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Path to the dataset
file_path = "District, Sex Ratio_2001_Rural, Sex Ratio_2001_Urban, Sex Ratio_2001_Total, Sex Ratio_2011_Rural.csv"

# Manually fixing column names (since original file is messy)
columns = [
    "District",
    "Sex Ratio_2001_Rural",
    "Sex Ratio_2001_Urban",
    "Sex Ratio_2001_Total",
    "Sex Ratio_2011_Rural",
    "Sex Ratio_2011_Urban",
    "Sex Ratio_2011_Total",
    "Decadal Change in percentage 2001_2011"
]

# Reading file as fixed-width format and skipping the broken first row
df = pd.read_fwf(
    file_path,
    skiprows=1,
    widths=[11] * 8,
    names=columns
)

# Converting important columns to numeric (invalid values → NaN)
numeric_cols = [
    "Sex Ratio_2001_Total",
    "Sex Ratio_2011_Total",
    "Decadal Change in percentage 2001_2011"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Set plotting style
sns.set_theme(style="darkgrid")

# Create subplots
fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Plot 1: Violin plot (2001 vs 2011)
melted_df = df.melt(
    id_vars=["District"],
    value_vars=["Sex Ratio_2001_Total", "Sex Ratio_2011_Total"],
    var_name="Year",
    value_name="Ratio"
)

# Extract year from column names
melted_df["Year"] = melted_df["Year"].astype(str).str.extract(r"(\d{4})")

sns.violinplot(
    x="Year",
    y="Ratio",
    data=melted_df,
    ax=axes[0],
    palette="muted",
    inner="quartile"
)

axes[0].set_title("Violin Plot: Total Sex Ratio (2001 vs 2011)")

# Plot 2: Scatter plot (district comparison)
sns.scatterplot(
    x="Sex Ratio_2001_Total",
    y="Sex Ratio_2011_Total",
    data=df,
    ax=axes[1],
    alpha=0.5,
    color="purple"
)

# Reference line (y = x)
axes[1].plot([700, 1200], [700, 1200], linestyle="--", color="red")
axes[1].set_title("District Shift: 2001 vs 2011 (Above Red Line = Improved)")

# Plot 3: Histogram (decadal change)
sns.histplot(
    df["Decadal Change in percentage 2001_2011"].dropna(),
    bins=30,
    ax=axes[2],
    color="orange",
    kde=True
)

axes[2].axvline(0, linestyle="--", color="black")
axes[2].set_title("Distribution of Decadal Change (%)")

# Final layout
plt.tight_layout()
plt.show()