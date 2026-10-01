# Dataset Documentation

This directory contains dataset resources used in the Elephant Intrusion Detection System (EIDS) for seismic signal analysis and feature-based classification.

## Dataset Overview

The project uses ground-vibration recordings associated with four classes: elephant, human, bovid, and noise. These recordings are explored to understand signal characteristics and develop a feature-based approach to wildlife intrusion monitoring.

## Dataset Organization

```text
datasets/
├── elephant/                   # Elephant-associated recordings
├── human/                      # Human-associated recordings
├── bovid/                      # Bovid-associated recordings
├── noise/                      # Background noise recordings
├── metadata.csv                # Dataset metadata
├── EEDS_features_v2.csv        # Engineered feature dataset
└── EEDS_features_initial.csv   # Initial feature dataset
```

*The directory structure above describes the intended organization. Keep only files that are actually present in the repository, and use the exact filenames committed to GitHub.*

## Class Distribution

The dataset explored during project development contains 656 recordings distributed equally across four classes.

| Class     | Number of recordings |
| --------- | -------------------: |
| Elephant  |                  164 |
| Human     |                  164 |
| Bovid     |                  164 |
| Noise     |                  164 |
| **Total** |              **656** |

## Signal Format

During dataset exploration, each waveform was represented by three signal channels, with 2,048 samples per channel.

* **Signal type:** Ground-vibration / seismic waveform
* **Number of channels:** 3
* **Samples per channel:** 2,048
* **Sampling frequency:** Approximately 200 Hz, as reported during dataset exploration

These details describe the dataset examined during development. Verify them against the source dataset and preprocessing scripts before using them as definitive specifications.

## Feature Dataset

The directory also includes CSV files containing engineered signal features.

* **`EEDS_features_v2.csv`:** Feature dataset used in the later feature-based workflow.
* **`EEDS_features_initial.csv`:** Initial feature dataset retained for reference, if included.
* **`metadata.csv`:** Metadata associated with the dataset, used to identify or organize recordings and their labels.

The feature-based workflow focuses on four primary features:

* Short-Term Average / Long-Term Average (STA/LTA)
* Zero-Crossing Rate (ZCR)
* Predominant Frequency
* Root Mean Square (RMS)

These features describe different aspects of signal behaviour and are used in rule-based analysis and Random Forest classification.

## Data Usage

The dataset supports signal visualization, frequency analysis, feature extraction, rule-based decision-making, and machine-learning experiments.

The dataset and feature files should be used consistently with the corresponding metadata and preprocessing workflow to maintain the correct association between recordings, features, and labels.

## Data Availability and Licensing

Before redistributing or publishing the raw recordings, metadata, or derived feature files, verify the original dataset's licence, attribution requirements, and permission to share.

If the source dataset cannot be redistributed, retain only this documentation and provide an appropriate reference to the original source, where permitted.

## Notes

* The number of recordings and signal dimensions reflect the dataset examined during project development.
* Feature CSV files may contain derived information from the raw recordings.
* The presence of a feature file does not by itself guarantee that the associated model can be reproduced without the corresponding preprocessing and training workflow.
