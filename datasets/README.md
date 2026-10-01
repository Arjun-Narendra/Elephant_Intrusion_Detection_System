# Dataset Files

## Overview

This directory contains the processed feature dataset and metadata used in the Elephant Intrusion Detection System (EIDS) project.

These files support feature-based analysis, the Rule-Based Decision-Making System (RBDMS), and Random Forest classification.

## Files

### 1. `EEDS_features_v2.csv`

Contains the extracted signal features used in the feature-based processing and classification workflow.

The project investigates features such as:

* **STA/LTA** — Short-Term Average to Long-Term Average ratio.
* **ZCR** — Zero Crossing Rate.
* **Predominant Frequency** — Dominant frequency component of a signal.
* **RMS** — Root Mean Square amplitude.

The CSV may also contain additional extracted features and class labels. Refer to the file's actual columns when using it.

**Purpose:** Supports feature analysis, RBDMS processing, and Random Forest model development.

### 2. `metadata.csv`

Contains metadata associated with the dataset.

**Purpose:** Provides supporting information for understanding or identifying dataset records. Refer to the actual column names to determine which metadata fields are available and how they correspond to the feature dataset.

## Dataset Classes

The project dataset was previously described as containing four classes:

| Class     | Number of Recordings |
| --------- | -------------------: |
| Elephant  |                  164 |
| Human     |                  164 |
| Bovid     |                  164 |
| Noise     |                  164 |
| **Total** |              **656** |

These counts describe the dataset used during project development; verify them against the uploaded CSV files before treating them as the current file counts.

## How These Files Are Used

The files support the following workflow:

1. Load the extracted features required by the selected processing script.
2. Use relevant signal features in the RBDMS workflow.
3. Prepare the feature data and labels for Random Forest classification.
4. Use metadata when required to interpret or associate dataset records.

The exact input requirements depend on the individual source script.

## Before Using the Files

* Check the CSV column names and data types.
* Confirm the class labels and target column expected by the script.
* Verify the file paths used in the source code.
* Ensure that the metadata and feature records correspond correctly.
* Check the dataset's original source, attribution requirements, and redistribution permissions.

## Data Availability

This directory contains the feature dataset and metadata, not the original raw seismic waveform recordings.

Please refer to the original dataset source and its applicable terms for information about data provenance and permitted use.
