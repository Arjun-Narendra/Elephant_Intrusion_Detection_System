# Random Forest Classification

## Overview

This directory contains the source code and supporting files associated with Random Forest classification in the Elephant Intrusion Detection System (EIDS).

The Random Forest model is used to classify seismic events based on extracted signal features. It complements the Rule-Based Decision-Making System (RBDMS) in the project's feature-based event detection workflow.

## Input Dataset

The classification workflow uses the processed feature dataset available in the repository's `datasets/` directory.

* `EEDS_features_v2.csv` — Contains extracted signal features used for feature-based analysis and classification.
* `metadata.csv` — Contains supporting metadata associated with the dataset.

The actual input requirements depend on the individual script.

## Features

The project investigates the following signal features:

* **STA/LTA:** Represents the ratio between short-term and long-term signal averages.
* **Zero Crossing Rate (ZCR):** Measures the frequency of sign changes in a signal.
* **Predominant Frequency:** Represents the dominant frequency component of the signal.
* **RMS:** Represents the effective magnitude of a signal.

The columns used by the classifier must match those expected by the training or evaluation script.

## Classification Workflow

The general workflow consists of:

1. Loading the extracted feature dataset.
2. Preparing the input features and class labels.
3. Performing the data preparation required by the model.
4. Training or loading the Random Forest classifier.
5. Evaluating the model using the metrics implemented in the script.
6. Saving the trained model or related outputs when supported.

Refer to the source code for the exact processing and evaluation steps.

## Before Using the Scripts

* Confirm that the required CSV files are available.
* Check the expected feature columns and target labels.
* Verify the dataset paths specified in the script.
* Check for hardcoded paths such as `/content/`, which may be specific to Google Colab.
* Ensure that the required Python libraries are installed.
* Confirm the output locations for trained models, configuration files, and evaluation results.

## Outputs

Depending on the script, outputs may include a trained Random Forest model, evaluation metrics, classification results, and supporting configuration files.

## Relationship to the Implementation

The trained model may be used by the implementation scripts for inference. Ensure that the model file, feature configuration, and any associated metadata are compatible with the implementation being used.

## Note

This directory documents the Random Forest classification component. Actual execution requirements and outputs should be verified against the corresponding source files.
