import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# SETTINGS
# ============================================================

CSV_FILE = "EEDS_features_v2.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.20

CHANNELS = [1, 2, 3]

# Features used by RBDMS
FEATURES = [
    "STA_LTA",
    "ZCR",
    "Predominant_Frequency",
    "RMS"
]


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(CSV_FILE)

print("\n========================================")
print("       EEDS RBDMS v1")
print("========================================")

print("\nDataset shape:", df.shape)

print("\nClass distribution:")
print(df["Class"].value_counts())


# ============================================================
# CREATE BINARY TARGET
#
# Biological classes = EVENT
# Noise = NO EVENT
# ============================================================

df["Target"] = (
    df["Class"] != "noise"
).astype(int)

print("\nTarget:")
print("1 = Biological event")
print("0 = Noise")


# ============================================================
# CREATE CHANNEL-AVERAGED FEATURES
#
# We first create a robust summary for each channel.
# The RBDMS itself will still perform 2/3 channel voting.
# ============================================================

for feature in FEATURES:

    channel_columns = [
        f"CH{ch}_{feature}"
        for ch in CHANNELS
    ]

    df[f"Mean_{feature}"] = df[
        channel_columns
    ].mean(axis=1)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

train_df, test_df = train_test_split(
    df,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=df["Class"]
)

print("\nTraining samples:", len(train_df))
print("Testing samples :", len(test_df))


# ============================================================
# THRESHOLD SEARCH
# ============================================================

def percentile_range(values):

    values = np.asarray(values)

    return {
        "q10": np.percentile(values, 10),
        "q25": np.percentile(values, 25),
        "q50": np.percentile(values, 50),
        "q75": np.percentile(values, 75),
        "q90": np.percentile(values, 90)
    }


# ============================================================
# DISPLAY TRAINING DISTRIBUTIONS
# ============================================================

print("\n========================================")
print("TRAINING DISTRIBUTIONS")
print("========================================")

for feature in FEATURES:

    values = train_df[
        f"Mean_{feature}"
    ]

    stats = percentile_range(values)

    print(f"\n{feature}")

    for key, value in stats.items():
        print(f"{key:>4}: {value:.6g}")


# ============================================================
# CHANNEL RULE
# ============================================================

def channel_passes(
    row,
    channel,
    thresholds
):
    """
    Determine whether one channel looks like
    a biological seismic event.

    The conditions are intentionally multi-parameter.

    We require:

      1. STA/LTA not to be abnormally high
      2. ZCR within learned range
      3. Frequency within learned range
      4. RMS above learned minimum

    At least 3 of 4 conditions must pass.
    """

    score = 0

    # --------------------------------------------
    # STA/LTA
    # --------------------------------------------

    sta_lta = row[
        f"CH{channel}_STA_LTA"
    ]

    if sta_lta <= thresholds["STA_LTA_MAX"]:
        score += 1

    # --------------------------------------------
    # ZCR
    # --------------------------------------------

    zcr = row[
        f"CH{channel}_ZCR"
    ]

    if (
        thresholds["ZCR_MIN"]
        <= zcr
        <= thresholds["ZCR_MAX"]
    ):
        score += 1

    # --------------------------------------------
    # Predominant frequency
    # --------------------------------------------

    freq = row[
        f"CH{channel}_Predominant_Frequency"
    ]

    if (
        thresholds["FREQ_MIN"]
        <= freq
        <= thresholds["FREQ_MAX"]
    ):
        score += 1

    # --------------------------------------------
    # RMS
    # --------------------------------------------

    rms = row[
        f"CH{channel}_RMS"
    ]

    if rms >= thresholds["RMS_MIN"]:
        score += 1

    # At least 3 parameters must agree
    return score >= 3


# ============================================================
# AUTOMATIC THRESHOLD SEARCH
# ============================================================

print("\n========================================")
print("SEARCHING FOR RBDMS THRESHOLDS")
print("========================================")


# Candidate percentile values
percentiles = [10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90]


def get_channel_values(data, feature):

    values = []

    for ch in CHANNELS:

        values.extend(
            data[
                f"CH{ch}_{feature}"
            ].values
        )

    return np.asarray(values)


# Training biological and noise distributions

biological_train = train_df[
    train_df["Target"] == 1
]

noise_train = train_df[
    train_df["Target"] == 0
]


# ------------------------------------------------------------
# Build candidate threshold ranges
# ------------------------------------------------------------

zcr_values = get_channel_values(
    biological_train,
    "ZCR"
)

freq_values = get_channel_values(
    biological_train,
    "Predominant_Frequency"
)

rms_values = get_channel_values(
    biological_train,
    "RMS"
)

noise_sta_values = get_channel_values(
    noise_train,
    "STA_LTA"
)

biological_sta_values = get_channel_values(
    biological_train,
    "STA_LTA"
)


zcr_candidates = [
    np.percentile(zcr_values, p)
    for p in percentiles
]

freq_low_candidates = [
    np.percentile(freq_values, p)
    for p in [5, 10, 15, 20, 25]
]

freq_high_candidates = [
    np.percentile(freq_values, p)
    for p in [75, 80, 85, 90, 95]
]

rms_candidates = [
    np.percentile(rms_values, p)
    for p in [10, 20, 25, 30, 40, 50]
]

sta_candidates = [
    np.percentile(
        biological_sta_values,
        p
    )
    for p in [75, 80, 85, 90, 95]
]


# ============================================================
# SEARCH
# ============================================================

best_result = None


for zcr_low in zcr_candidates:

    for zcr_high in zcr_candidates:

        if zcr_high <= zcr_low:
            continue

        for freq_low in freq_low_candidates:

            for freq_high in freq_high_candidates:

                if freq_high <= freq_low:
                    continue

                for rms_min in rms_candidates:

                    for sta_max in sta_candidates:

                        thresholds = {

                            "STA_LTA_MAX":
                                sta_max,

                            "ZCR_MIN":
                                zcr_low,

                            "ZCR_MAX":
                                zcr_high,

                            "FREQ_MIN":
                                freq_low,

                            "FREQ_MAX":
                                freq_high,

                            "RMS_MIN":
                                rms_min
                        }

                        predictions = []

                        actual = []

                        for _, row in train_df.iterrows():

                            channel_results = []

                            for ch in CHANNELS:

                                result = channel_passes(
                                    row,
                                    ch,
                                    thresholds
                                )

                                channel_results.append(
                                    result
                                )

                            # 2-out-of-3 voting
                            event = (
                                sum(channel_results)
                                >= 2
                            )

                            predictions.append(
                                int(event)
                            )

                            actual.append(
                                int(row["Target"])
                            )

                        f1 = f1_score(
                            actual,
                            predictions,
                            zero_division=0
                        )

                        if (
                            best_result is None
                            or f1 >
                            best_result["f1"]
                        ):

                            best_result = {

                                "f1": f1,

                                "thresholds":
                                    thresholds
                            }


# ============================================================
# BEST RBDMS
# ============================================================

print("\n========================================")
print("BEST RBDMS v1 THRESHOLDS")
print("========================================")

print(
    f"\nTraining F1: "
    f"{best_result['f1']:.4f}"
)

for key, value in (
    best_result["thresholds"].items()
):

    print(
        f"{key:20s}: {value:.6g}"
    )


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def run_rbdms(data, thresholds):

    predictions = []

    for _, row in data.iterrows():

        channel_results = []

        for ch in CHANNELS:

            result = channel_passes(
                row,
                ch,
                thresholds
            )

            channel_results.append(
                result
            )

        # 2 out of 3 channels
        event = (
            sum(channel_results)
            >= 2
        )

        predictions.append(
            int(event)
        )

    return np.asarray(predictions)


# ============================================================
# TEST SET EVALUATION
# ============================================================

test_predictions = run_rbdms(
    test_df,
    best_result["thresholds"]
)

test_actual = test_df[
    "Target"
].values


accuracy = accuracy_score(
    test_actual,
    test_predictions
)

precision = precision_score(
    test_actual,
    test_predictions,
    zero_division=0
)

recall = recall_score(
    test_actual,
    test_predictions,
    zero_division=0
)

f1 = f1_score(
    test_actual,
    test_predictions,
    zero_division=0
)


# ============================================================
# RESULTS
# ============================================================

print("\n========================================")
print("RBDMS v1 TEST RESULTS")
print("========================================")

print(
    f"\nAccuracy : {accuracy:.4f}"
)

print(
    f"Precision: {precision:.4f}"
)

print(
    f"Recall   : {recall:.4f}"
)

print(
    f"F1-score : {f1:.4f}"
)


print("\nConfusion Matrix:")
print(
    confusion_matrix(
        test_actual,
        test_predictions
    )
)


print("\nClassification Report:")
print(
    classification_report(
        test_actual,
        test_predictions,
        target_names=[
            "Noise",
            "Biological Event"
        ],
        zero_division=0
    )
)


# ============================================================
# CLASS-WISE RESULT
# ============================================================

test_result = test_df[
    ["File", "Class"]
].copy()

test_result[
    "RBDMS_Event"
] = test_predictions

test_result[
    "RBDMS_Decision"
] = np.where(
    test_predictions == 1,
    "PASS_TO_RF",
    "REJECT"
)


output_file = (
    "RBDMS_v1_test_results.csv"
)

test_result.to_csv(
    output_file,
    index=False
)


print(
    f"\nResults saved to: "
    f"{output_file}"
)

print("\n========================================")
print("RBDMS v1 COMPLETE")
print("========================================")