import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# File path
file_path = "Fertility Indicators for Major States of General Marital Fertility Rate and Total Marital Fertility Rate from 2006 to 2013.csv"

# Since columns are not clean in the file, defining them manually
columns = [
    "State",
    "Years",
    "General Marital Fertility Rate (GMFR) - Total",
    "General Marital Fertility Rate (GMFR) - Rural",
    "General Marital Fertility Rate (GMFR) - Urban",
    "Total Marital Fertility Rate (TMFR) - Total",
    "Total Marital Fertility Rate (TMFR) - Rural",
    "Total Marital Fertility Rate (TMFR) - Urban"
]

# Reading fixed-width file (skip first broken row)
df = pd.read_fwf(
    file_path,
    skiprows=1,
    widths=[11] * 8,
    names=columns
)

# Convert important columns to numeric
clean_cols = [
    "Years",
    "General Marital Fertility Rate (GMFR) - Total",
    "General Marital Fertility Rate (GMFR) - Rural",
    "General Marital Fertility Rate (GMFR) - Urban"
]

for col in clean_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove rows where main data is missing
df = df.dropna(subset=clean_cols)

# Set style
sns.set_theme(style="whitegrid")

# Create figure
plt.figure(figsize=(20, 10))

# Plot 1: GMFR trends across states
ax1 = plt.subplot(1, 2, 1)

selected_states = [
    "Uttar Pradesh",
    "Bihar",
    "Rajasthan",
    "Madhya Pradesh",
    "Kerala",
    "Tamil Nadu"
]

sns.lineplot(
    x="Years",
    y="General Marital Fertility Rate (GMFR) - Total",
    hue="State",
    data=df[df["State"].isin(selected_states)],
    lw=3,
    marker="o",
    ax=ax1
)

ax1.set_title("GMFR Trends (2006-2013) for Selected Major States")
ax1.set_xticks(sorted(df["Years"].unique()))

# Plot 2: Rural vs Urban comparison (2013)
ax2 = plt.subplot(1, 2, 2)

# Filter only 2013 data
df_2013 = df[df["Years"] == 2013].copy()

# Convert wide → long format for plotting
df_2013_melt = df_2013.melt(
    id_vars=["State"],
    value_vars=[
        "General Marital Fertility Rate (GMFR) - Rural",
        "General Marital Fertility Rate (GMFR) - Urban"
    ],
    var_name="Area",
    value_name="GMFR"
)

# Clean Area names (Rural / Urban)
df_2013_melt["Area"] = df_2013_melt["Area"].str.split("-").str[-1].str.strip()

# Get top 10 states based on rural GMFR
top_states = df_2013.sort_values(
    "General Marital Fertility Rate (GMFR) - Rural",
    ascending=False
)["State"].head(10)

# Bar plot
sns.barplot(
    x="GMFR",
    y="State",
    hue="Area",
    data=df_2013_melt[df_2013_melt["State"].isin(top_states)],
    ax=ax2,
    palette="Set2"
)

ax2.set_title("Rural vs Urban GMFR in 2013 (Top 10 States)")

# Final layout
plt.tight_layout()
plt.show()
