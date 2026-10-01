import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import os

print("=" * 60)
print("FREQUENCY ANALYSIS PLOTTING")
print("=" * 60)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET = os.path.join(
    BASE_DIR,
    "..",
    "elephant_dataset"
)

OUTPUT_DIR = BASE_DIR

FS = 200

classes = [
    "elephant",
    "human",
    "bovid",
    "noise"
]

print("\nDataset:")
print(os.path.abspath(DATASET))

print("Dataset exists:", os.path.exists(DATASET))


# ============================================================
# PART 1 — SPECTROGRAM
# ============================================================

print("\nCreating spectrograms...")

fig, axes = plt.subplots(
    4,
    1,
    figsize=(14, 12)
)

for i, class_name in enumerate(classes):

    folder = os.path.join(
        DATASET,
        class_name
    )

    print(
        f"\nProcessing {class_name.upper()}"
    )

    print("Folder:", folder)
    print("Exists:", os.path.exists(folder))

    if not os.path.exists(folder):
        print("ERROR: folder not found")
        continue

    files = [
        f for f in os.listdir(folder)
        if f.lower().endswith(".npy")
    ]

    print("Number of files:", len(files))

    if len(files) == 0:
        print("No .npy files found!")
        continue

    # First waveform
    file = files[0]

    filepath = os.path.join(
        folder,
        file
    )

    print("Using:", file)

    waveform = np.load(filepath)

    print("Waveform shape:", waveform.shape)

    # Component 1
    x = waveform[0]

    # Remove DC
    x = x - np.mean(x)

    # --------------------------------------------------------
    # Spectrogram
    # --------------------------------------------------------

    frequencies, times, Sxx = signal.spectrogram(
        x,
        fs=FS,
        window="hann",
        nperseg=256,
        noverlap=128
    )

    # Convert to dB
    Sxx_dB = 10 * np.log10(
        Sxx + 1e-20
    )

    im = axes[i].pcolormesh(
        times,
        frequencies,
        Sxx_dB,
        shading="gouraud"
    )

    axes[i].set_title(
        class_name.upper()
    )

    axes[i].set_ylabel(
        "Frequency (Hz)"
    )

    axes[i].set_ylim(
        0,
        100
    )

    fig.colorbar(
        im,
        ax=axes[i],
        label="Power (dB)"
    )


axes[-1].set_xlabel(
    "Time (seconds)"
)

fig.suptitle(
    "Spectrogram Comparison - Component 1",
    fontsize=16
)

plt.tight_layout()

spectrogram_path = os.path.join(
    OUTPUT_DIR,
    "spectrogram_comparison.png"
)

plt.savefig(
    spectrogram_path,
    dpi=150
)

print("\nSpectrogram saved:")
print(spectrogram_path)

plt.show()


# ============================================================
# PART 2 — MEAN FREQUENCY
# ============================================================

print("\nCreating mean-frequency comparison...")

csv_file = os.path.join(
    OUTPUT_DIR,
    "frequency_features.csv"
)

print("CSV:", csv_file)

if not os.path.exists(csv_file):

    print("\nERROR:")
    print("frequency_features.csv was not found.")
    print("Run frequency_analysis.py first.")

else:

    df = pd.read_csv(csv_file)

    print(
        "CSV loaded successfully."
    )

    print(
        "Rows:",
        len(df)
    )

    # Average the three components
    mean_frequency = (
        df.groupby(
            ["file", "class"]
        )["mean_frequency_hz"]
        .mean()
        .reset_index()
    )

    data = []

    for class_name in classes:

        values = mean_frequency[
            mean_frequency["class"] == class_name
        ]["mean_frequency_hz"]

        data.append(values)

        print(
            f"{class_name}: "
            f"{len(values)} samples"
        )

    plt.figure(
        figsize=(10, 6)
    )

    plt.boxplot(
        data,
        labels=classes
    )

    plt.ylabel(
        "Mean Frequency (Hz)"
    )

    plt.xlabel(
        "Class"
    )

    plt.title(
        "Mean Frequency Comparison"
    )

    plt.grid(
        True,
        axis="y"
    )

    plt.tight_layout()

    mean_path = os.path.join(
        OUTPUT_DIR,
        "mean_frequency_comparison.png"
    )

    plt.savefig(
        mean_path,
        dpi=150
    )

    print("\nMean frequency plot saved:")
    print(mean_path)

    plt.show()


# ============================================================
# PART 3 — DOMINANT FREQUENCY
# ============================================================

print("\nCreating dominant-frequency comparison...")

if os.path.exists(csv_file):

    dominant_frequency = (
        df.groupby(
            ["file", "class"]
        )["dominant_frequency_hz"]
        .mean()
        .reset_index()
    )

    data = []

    for class_name in classes:

        values = dominant_frequency[
            dominant_frequency["class"] == class_name
        ]["dominant_frequency_hz"]

        data.append(values)

    plt.figure(
        figsize=(10, 6)
    )

    plt.boxplot(
        data,
        labels=classes
    )

    plt.ylabel(
        "Dominant Frequency (Hz)"
    )

    plt.xlabel(
        "Class"
    )

    plt.title(
        "Dominant Frequency Comparison"
    )

    plt.grid(
        True,
        axis="y"
    )

    plt.tight_layout()

    dominant_path = os.path.join(
        OUTPUT_DIR,
        "dominant_frequency_comparison.png"
    )

    plt.savefig(
        dominant_path,
        dpi=150
    )

    print("\nDominant frequency plot saved:")
    print(dominant_path)

    plt.show()


# ============================================================
# DONE
# ============================================================

print("\n" + "=" * 60)
print("PLOTTING COMPLETE")
print("=" * 60)