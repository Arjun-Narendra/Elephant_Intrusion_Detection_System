import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ============================================================
# SETTINGS
# ============================================================

CSV_FILE = "EEDS_features_v2.csv"

TEST_SIZE = 0.20
RANDOM_STATE = 42

CHANNELS = [1, 2, 3]


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(CSV_FILE)

print()
print("========================================")
print("        EEDS RBDMS VERSION 2")
print("========================================")

print("\nDataset:", df.shape)

print("\nClass distribution:")
print(df["Class"].value_counts())


# ============================================================
# TARGET
#
# 1 = Biological event
# 0 = Noise
# ============================================================

df["Target"] = (
    df["Class"] != "noise"
).astype(int)


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
# HELPER
# ============================================================

def channel_values(data, feature):

    values = []

    for ch in CHANNELS:

        values.extend(
            data[
                f"CH{ch}_{feature}"
            ].values
        )

    return np.asarray(values)


# ============================================================
# TRAINING DISTRIBUTIONS
# ============================================================

biological = train_df[
    train_df["Target"] == 1
]

noise = train_df[
    train_df["Target"] == 0
]


print()
print("========================================")
print("TRAINING DISTRIBUTIONS")
print("========================================")


features = [
    "STA_LTA",
    "ZCR",
    "Predominant_Frequency",
    "RMS"
]

for feature in features:

    bio = channel_values(
        biological,
        feature
    )

    noi = channel_values(
        noise,
        feature
    )

    print(f"\n{feature}")

    print(
        " Biological median:",
        np.median(bio)
    )

    print(
        " Biological Q25:",
        np.percentile(bio, 25)
    )

    print(
        " Biological Q75:",
        np.percentile(bio, 75)
    )

    print(
        " Noise median:",
        np.median(noi)
    )

    print(
        " Noise Q25:",
        np.percentile(noi, 25)
    )

    print(
        " Noise Q75:",
        np.percentile(noi, 75)
    )


# ============================================================
# RBDMS RULES
# ============================================================

def parameter_score(row, channel, rule):

    score = 0

    # --------------------------------------------------------
    # STA/LTA
    # --------------------------------------------------------

    sta = row[
        f"CH{channel}_STA_LTA"
    ]

    if sta <= rule["STA_MAX"]:
        score += 1


    # --------------------------------------------------------
    # ZCR
    # --------------------------------------------------------

    zcr = row[
        f"CH{channel}_ZCR"
    ]

    if (
        rule["ZCR_MIN"]
        <= zcr
        <= rule["ZCR_MAX"]
    ):
        score += 1


    # --------------------------------------------------------
    # Frequency
    # --------------------------------------------------------

    freq = row[
        f"CH{channel}_Predominant_Frequency"
    ]

    if (
        rule["FREQ_MIN"]
        <= freq
        <= rule["FREQ_MAX"]
    ):
        score += 1


    # --------------------------------------------------------
    # RMS
    # --------------------------------------------------------

    rms = row[
        f"CH{channel}_RMS"
    ]

    if rms >= rule["RMS_MIN"]:
        score += 1


    return score


# ============================================================
# APPLY RBDMS
# ============================================================

def run_rbdms(data, rule):

    predictions = []

    for _, row in data.iterrows():

        channel_scores = []

        for ch in CHANNELS:

            score = parameter_score(
                row,
                ch,
                rule
            )

            channel_scores.append(score)


        # ----------------------------------------------------
        # Channel decision
        #
        # At least 3 of 4 parameters must pass
        # ----------------------------------------------------

        channel_events = [
            score >= 3
            for score in channel_scores
        ]


        # ----------------------------------------------------
        # 2 OUT OF 3 CHANNEL VOTING
        # ----------------------------------------------------

        event = (
            sum(channel_events) >= 2
        )

        predictions.append(
            int(event)
        )

    return np.asarray(predictions)


# ============================================================
# GENERATE CANDIDATE THRESHOLDS
# ============================================================

bio_sta = channel_values(
    biological,
    "STA_LTA"
)

bio_zcr = channel_values(
    biological,
    "ZCR"
)

bio_freq = channel_values(
    biological,
    "Predominant_Frequency"
)

bio_rms = channel_values(
    biological,
    "RMS"
)


noise_sta = channel_values(
    noise,
    "STA_LTA"
)

noise_zcr = channel_values(
    noise,
    "ZCR"
)

noise_freq = channel_values(
    noise,
    "Predominant_Frequency"
)

noise_rms = channel_values(
    noise,
    "RMS"
)


# ============================================================
# THRESHOLD CANDIDATES
# ============================================================

sta_candidates = [
    np.percentile(
        bio_sta,
        p
    )
    for p in [75, 80, 85, 90, 92, 95]
]


zcr_min_candidates = [
    np.percentile(
        bio_zcr,
        p
    )
    for p in [5, 10, 15, 20, 25]
]


zcr_max_candidates = [
    np.percentile(
        bio_zcr,
        p
    )
    for p in [75, 80, 85, 90, 95]
]


freq_min_candidates = [
    np.percentile(
        bio_freq,
        p
    )
    for p in [5, 10, 15, 20]
]


freq_max_candidates = [
    np.percentile(
        bio_freq,
        p
    )
    for p in [75, 80, 85, 90, 95]
]


rms_min_candidates = [
    np.percentile(
        bio_rms,
        p
    )
    for p in [5, 10, 15, 20, 25, 30]
]


# ============================================================
# SEARCH FOR BEST RBDMS
# ============================================================

print()
print("========================================")
print("SEARCHING RBDMS V2")
print("========================================")


best_rules = []


for sta_max in sta_candidates:

    for zcr_min in zcr_min_candidates:

        for zcr_max in zcr_max_candidates:

            if zcr_max <= zcr_min:
                continue

            for freq_min in freq_min_candidates:

                for freq_max in freq_max_candidates:

                    if freq_max <= freq_min:
                        continue

                    for rms_min in rms_min_candidates:

                        rule = {

                            "STA_MAX":
                                sta_max,

                            "ZCR_MIN":
                                zcr_min,

                            "ZCR_MAX":
                                zcr_max,

                            "FREQ_MIN":
                                freq_min,

                            "FREQ_MAX":
                                freq_max,

                            "RMS_MIN":
                                rms_min
                        }


                        pred = run_rbdms(
                            train_df,
                            rule
                        )

                        actual = train_df[
                            "Target"
                        ].values


                        precision = precision_score(
                            actual,
                            pred,
                            zero_division=0
                        )

                        recall = recall_score(
                            actual,
                            pred,
                            zero_division=0
                        )

                        f1 = f1_score(
                            actual,
                            pred,
                            zero_division=0
                        )


                        # ------------------------------------------------
                        # False alarm rate
                        # ------------------------------------------------

                        noise_mask = (
                            actual == 0
                        )

                        false_alarms = np.sum(
                            pred[noise_mask] == 1
                        )

                        total_noise = np.sum(
                            noise_mask
                        )

                        false_alarm_rate = (
                            false_alarms
                            / total_noise
                        )


                        # ------------------------------------------------
                        # We want:
                        #
                        # High recall
                        # High precision
                        # Low false alarms
                        #
                        # Minimum biological recall = 80%
                        # ------------------------------------------------

                        if recall >= 0.80:

                            objective = (
                                0.45 * precision
                                +
                                0.35 * recall
                                +
                                0.20 * (1 - false_alarm_rate)
                            )

                            best_rules.append(
                                (
                                    objective,
                                    precision,
                                    recall,
                                    f1,
                                    false_alarm_rate,
                                    rule
                                )
                            )


# ============================================================
# SORT RESULTS
# ============================================================

best_rules.sort(
    key=lambda x: x[0],
    reverse=True
)


if len(best_rules) == 0:

    print()
    print(
        "No rule satisfied the "
        "minimum recall requirement."
    )

    print(
        "RBDMS v2 needs a wider search."
    )

    raise SystemExit


best = best_rules[0]


# ============================================================
# DISPLAY BEST RULE
# ============================================================

print()
print("========================================")
print("BEST RBDMS V2")
print("========================================")

print(
    f"\nTraining Precision : {best[1]:.4f}"
)

print(
    f"Training Recall    : {best[2]:.4f}"
)

print(
    f"Training F1        : {best[3]:.4f}"
)

print(
    f"Training FAR       : {best[4]:.4f}"
)


print("\nThresholds:")

for key, value in best[5].items():

    print(
        f"{key:12s}: {value:.6g}"
    )


# ============================================================
# TEST SET
# ============================================================

test_prediction = run_rbdms(
    test_df,
    best[5]
)

test_actual = test_df[
    "Target"
].values


test_accuracy = accuracy_score(
    test_actual,
    test_prediction
)

test_precision = precision_score(
    test_actual,
    test_prediction,
    zero_division=0
)

test_recall = recall_score(
    test_actual,
    test_prediction,
    zero_division=0
)

test_f1 = f1_score(
    test_actual,
    test_prediction,
    zero_division=0
)


# ============================================================
# FALSE ALARM RATE
# ============================================================

noise_mask = (
    test_actual == 0
)

false_alarms = np.sum(
    test_prediction[noise_mask] == 1
)

total_noise = np.sum(
    noise_mask
)

test_far = (
    false_alarms / total_noise
)


# ============================================================
# RESULTS
# ============================================================

print()
print("========================================")
print("RBDMS V2 TEST RESULTS")
print("========================================")

print(
    f"\nAccuracy          : "
    f"{test_accuracy:.4f}"
)

print(
    f"Precision         : "
    f"{test_precision:.4f}"
)

print(
    f"Recall            : "
    f"{test_recall:.4f}"
)

print(
    f"F1-score          : "
    f"{test_f1:.4f}"
)

print(
    f"False Alarm Rate  : "
    f"{test_far:.4f}"
)

print(
    f"False alarms      : "
    f"{false_alarms}/{total_noise}"
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    test_actual,
    test_prediction
)

print("\nConfusion Matrix:")

print(
    "                 Predicted"
)

print(
    "              Noise   Event"
)

print(
    f"Actual Noise   {cm[0,0]:5d} "
    f" {cm[0,1]:5d}"
)

print(
    f"       Event   {cm[1,0]:5d} "
    f" {cm[1,1]:5d}"
)


# ============================================================
# SAVE RESULTS
# ============================================================

results = test_df[
    ["File", "Class"]
].copy()

results[
    "RBDMS_Event"
] = test_prediction

results[
    "RBDMS_Decision"
] = np.where(
    test_prediction == 1,
    "PASS_TO_RF",
    "REJECT"
)

results.to_csv(
    "RBDMS_v2_test_results.csv",
    index=False
)


# ============================================================
# TOP 10 CANDIDATE RULES
# ============================================================

top_rules = []

for item in best_rules[:10]:

    objective, precision, recall, f1, far, rule = item

    top_rules.append({

        "Objective": objective,

        "Precision": precision,

        "Recall": recall,

        "F1": f1,

        "False_Alarm_Rate": far,

        **rule
    })


pd.DataFrame(
    top_rules
).to_csv(
    "RBDMS_v2_candidate_rules.csv",
    index=False
)


print()
print("Saved:")
print("  RBDMS_v2_test_results.csv")
print("  RBDMS_v2_candidate_rules.csv")

print()
print("========================================")
print("RBDMS V2 COMPLETE")
print("========================================")