import pandas as pd
import matplotlib.pyplot as plt
import os

# ============================================================
# LOAD DATA
# ============================================================

csv_file = "frequency_features.csv"

df = pd.read_csv(csv_file)

print("CSV loaded")
print("Rows:", len(df))

# ============================================================
# AVERAGE THE 3 COMPONENTS
# ============================================================

mean_frequency = (
    df.groupby(["file", "class"])["mean_frequency_hz"]
    .mean()
    .reset_index()
)

classes = ["elephant", "human", "bovid", "noise"]

data = []

print("\nNumber of recordings:")

for class_name in classes:

    values = mean_frequency[
        mean_frequency["class"] == class_name
    ]["mean_frequency_hz"]

    data.append(values)

    print(
        f"{class_name:10s}: "
        f"{len(values)} recordings"
    )

# ============================================================
# PRINT STATISTICS
# ============================================================

print("\nMean-frequency statistics:")

for class_name in classes:

    values = mean_frequency[
        mean_frequency["class"] == class_name
    ]["mean_frequency_hz"]

    print(
        f"\n{class_name.upper()}"
    )

    print(
        f"  Mean   : {values.mean():.2f} Hz"
    )

    print(
        f"  Median : {values.median():.2f} Hz"
    )

    print(
        f"  Min    : {values.min():.2f} Hz"
    )

    print(
        f"  Max    : {values.max():.2f} Hz"
    )

# ============================================================
# BOX PLOT
# ============================================================

plt.figure(figsize=(10, 6))

plt.boxplot(
    data,
    tick_labels=classes,
    showmeans=True
)

plt.ylabel(
    "Mean Frequency (Hz)"
)

plt.xlabel(
    "Class"
)

plt.title(
    "Mean Frequency Distribution"
)

plt.grid(
    True,
    axis="y",
    alpha=0.3
)

plt.tight_layout()

# Save
plt.savefig(
    "mean_frequency_all_classes.png",
    dpi=200
)

plt.show()

print(
    "\nPlot saved as:"
    "\nmean_frequency_all_classes.png"
)