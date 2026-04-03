import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

# File path
file_path = "Total Fertility Rate India 2011.csv"

# Reading raw file manually (since formatting is not clean)
with open(file_path, "r") as f:
    lines = f.readlines()

# Extract years from first row
years = [int(y) for y in re.findall(r"\b(19\d\d|20\d\d)\b", lines[0])]

data = []

# Parse each line
for line in lines[1:]:
    if not line.strip():
        continue

    match = re.match(r"\s*(\d+)\s*([A-Za-z0-9&\s]+?)([0-9][\d\.\s]*)$", line)

    if match:
        state = match.group(2).strip()
        values = match.group(3).split()

        row = {"State": state}

        for i, year in enumerate(years):
            # If value missing → keep it as 0.0
            if i < len(values) and values[i].replace(".", "", 1).isdigit():
                row[year] = float(values[i])
            else:
                row[year] = 0.0

        data.append(row)

# Create DataFrame
df = pd.DataFrame(data).set_index("State")

# Heatmap
plt.figure(figsize=(12, 8))

sns.heatmap(
    df,
    cmap="YlOrRd",
    vmin=0,
    cbar_kws={
        "label": "TFR",
        "ticks": [0, 1, 2, 3, 4, 5, 6]
    }
)

plt.title("Heatmap: Historical Total Fertility Rate by State (1971-2010)")
plt.xlabel("Year")
plt.ylabel("State")
plt.show()

# Line Plot
plt.figure(figsize=(12, 6))

states_to_plot = ["All India", "Kerala", "Uttar Prade", "Bihar"]

for state in states_to_plot:
    if state in df.index:
        # Replace 0 with NaN so plot doesn't break visually
        safe_values = df.loc[state].replace(0.0, float("nan"))
        plt.plot(df.columns, safe_values, marker="o", label=state)

plt.title("Total Fertility Rate Trend")
plt.xlabel("Year")
plt.ylabel("Total Fertility Rate")
plt.legend()
plt.grid(True)
plt.show()