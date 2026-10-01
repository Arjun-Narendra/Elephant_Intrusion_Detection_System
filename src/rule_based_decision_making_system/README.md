# Rule-Based Decision-Making System (RBDMS)

## Overview

This directory contains scripts associated with the Rule-Based Decision-Making System developed for the Elephant Intrusion Detection System project.

The RBDMS uses signal features and predefined decision rules to help distinguish biological events from background noise.

## Feature-Based Analysis

The selected features investigated in the project include:

* **STA/LTA** — Helps identify changes in short-term signal activity relative to longer-term activity.
* **Zero Crossing Rate (ZCR)** — Describes the frequency of sign changes in the waveform.
* **Predominant Frequency** — Describes the dominant frequency component of the signal.
* **RMS** — Represents the effective signal magnitude.

The role of each feature depends on the decision rules implemented in the corresponding script.

## Available Scripts

* `build_rbdms_v1.py` — First version of the RBDMS feature-processing workflow.
* `build_rbdms_v2.py` — Updated version of the RBDMS workflow.

Check the source files to confirm their exact processing steps and outputs.

## Before Running the Scripts

1. Locate the feature CSV file required by the selected script.
2. Confirm that the file contains the expected feature columns and labels.
3. Check the configured CSV filename and input path.
4. Verify that the script is being run from the expected working directory.
5. Confirm the required Python dependencies.
6. Review the output files before using them in subsequent stages.

## Input

The scripts are associated with the extracted feature dataset, including `EEDS_features_v2.csv` where required by the selected version.

The exact input requirements should be verified in each script.

## Output

Outputs depend on the script version and may include processed feature data, decision-rule results, or information used in subsequent classification stages.

## Important

The RBDMS and Random Forest are separate components of the overall workflow. Check the data format expected by each component before passing results between them.

A README documents the expected workflow but does not modify hardcoded paths or the decision rules in the source code.
