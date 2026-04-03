import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

# File path
file_path = "State wise TFR and MCPR 2011.csv"

# Reading file manually because CSV formatting is broken
with open(file_path, "r") as f:
    lines = f.readlines()

data = []

# Skipping first two rows (header + India total)
for line in lines[2:]:
    # Pattern: index → state → TFR → MCPR
    match = re.match(r"\s*\d+\s*([a-zA-Z\s]+)\s+([\d\.]+)\s+([\d\.]+)", line)

    if match:
        state = match.group(1).strip()
        tfr = float(match.group(2))
        mcpr = float(match.group(3))

        data.append({
            "States/UT": state,
            "TFR": tfr,
            "MCPR (%)": mcpr
        })

# Creating DataFrame
df = pd.DataFrame(data)

# Plotting 
sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# Plot 1: MCPR vs TFR (with regression line)
sns.regplot(
    x="MCPR (%)",
    y="TFR",
    data=df,
    ax=axes[0],
    scatter_kws={"s": 80, "alpha": 0.6},
    line_kws={"color": "red"}
)

axes[0].set_title("Correlation: MCPR vs TFR (with Trendline)")

# Plot 2: Top 10 states by TFR
top_states = df.sort_values("TFR", ascending=False).head(10)

sns.barplot(
    x="TFR",
    y="States/UT",
    data=top_states,
    ax=axes[1],
    palette="OrRd_r"
)

axes[1].set_title("Top 10 States with Highest TFR")

# Plot 3: MCPR distribution
sns.kdeplot(
    df["MCPR (%)"],
    fill=True,
    ax=axes[2],
    color="teal",
    alpha=0.5
)

axes[2].set_title("Density Distribution of Contraceptive Prevalence")
axes[2].set_xlabel("MCPR (%)")

# Final layout
plt.tight_layout()
plt.show()
