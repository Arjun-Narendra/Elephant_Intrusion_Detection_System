import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import os
import random

# ============================================================
# SETTINGS
# ============================================================

DATASET_PATH = r"C:\Users\arjun\Downloads\EEDS\elephant_dataset"

CLASSES = [
    "elephant",
    "human",
    "bovid",
    "noise"
]

# Number of signals from each class
N_SIGNALS = 4

# Sampling frequency
FS = 200

# Component to analyze
COMPONENT = 0       # 0 = Component 1
                    # 1 = Component 2
                    # 2 = Component 3

# Maximum frequency to display
MAX_FREQ = 100

# ============================================================
# START
# ============================================================

print("=" * 60)
print("MULTIPLE SPECTROGRAM ANALYSIS")
print("=" * 60)

print(f"Dataset: {DATASET_PATH}")
print(f"Sampling frequency: {FS} Hz")
print(f"Nyquist frequency: {FS/2} Hz")
print(f"Component: {COMPONENT + 1}")

# ============================================================
# PROCESS EACH CLASS
# ============================================================

for class_name in CLASSES:

    folder = os.path.join(DATASET_PATH, class_name)

    files = [
        f for f in os.listdir(folder)
        if f.endswith(".npy")
    ]

    # Randomly select signals
    random.seed(42)

    if len(files) > N_SIGNALS:
        selected_files = random.sample(files, N_SIGNALS)
    else:
        selected_files = files

    print("\n" + "=" * 60)
    print(class_name.upper())
    print("=" * 60)

    # ========================================================
    # CREATE FIGURE
    # ========================================================

    fig, axes = plt.subplots(
        N_SIGNALS,
        1,
        figsize=(12, 10)
    )

    # If only one signal
    if N_SIGNALS == 1:
        axes = [axes]

    # ========================================================
    # PROCESS SIGNALS
    # ========================================================

    for i, filename in enumerate(selected_files):

        filepath = os.path.join(folder, filename)

        signal = np.load(filepath)

        # Shape should be (3, 2048)
        print(
            f"{filename:25s} "
            f"Shape={signal.shape}"
        )

        # Select component
        x = signal[COMPONENT]

        # ====================================================
        # SPECTROGRAM
        # ====================================================

        frequencies, times, Sxx = spectrogram(
            x,
            fs=FS,
            nperseg=256,
            noverlap=128
        )

        # Convert to dB
        Sxx_dB = 10 * np.log10(
            Sxx + 1e-20
        )

        # ====================================================
        # FREQUENCY ANALYSIS
        # ====================================================

        # Average power at each frequency
        frequency_power = np.mean(
            Sxx,
            axis=1
        )

        # Dominant frequency
        dominant_index = np.argmax(
            frequency_power
        )

        dominant_frequency = frequencies[
            dominant_index
        ]

        # Frequencies containing significant energy
        threshold = (
            np.max(frequency_power) * 0.10
        )

        significant_freqs = frequencies[
            frequency_power >= threshold
        ]

        if len(significant_freqs) > 0:

            freq_min = significant_freqs.min()
            freq_max = significant_freqs.max()

        else:

            freq_min = 0
            freq_max = 0

        print(
            f"   Dominant frequency: "
            f"{dominant_frequency:.2f} Hz"
        )

        print(
            f"   Significant range: "
            f"{freq_min:.2f} - "
            f"{freq_max:.2f} Hz"
        )

        # ====================================================
        # LIMIT DISPLAY TO 0-100 Hz
        # ====================================================

        mask = frequencies <= MAX_FREQ

        frequencies_plot = frequencies[mask]
        Sxx_plot = Sxx_dB[mask, :]

        # ====================================================
        # PLOT
        # ====================================================

        mesh = axes[i].pcolormesh(
            times,
            frequencies_plot,
            Sxx_plot,
            shading="gouraud"
        )

        axes[i].set_ylim(
            0,
            MAX_FREQ
        )

        axes[i].set_ylabel(
            "Frequency (Hz)"
        )

        axes[i].set_title(
            filename
            + f" | Dominant = "
            + f"{dominant_frequency:.1f} Hz"
        )

        fig.colorbar(
            mesh,
            ax=axes[i],
            label="Power (dB)"
        )

    axes[-1].set_xlabel(
        "Time (seconds)"
    )

    fig.suptitle(
        f"{class_name.upper()} - "
        f"{N_SIGNALS} Spectrograms - "
        f"Component {COMPONENT + 1}",
        fontsize=16
    )

    plt.tight_layout()

    # ========================================================
    # SAVE
    # ========================================================

    output_file = (
        f"spectrogram_{class_name}_"
        f"component_{COMPONENT + 1}.png"
    )

    plt.savefig(
        output_file,
        dpi=200
    )

    print(
        f"\nSaved: {output_file}"
    )

    plt.show()