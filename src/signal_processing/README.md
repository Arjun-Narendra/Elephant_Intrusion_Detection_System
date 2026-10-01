# Signal Processing

## Overview

This directory contains scripts for exploring and analysing seismic signals used in the Elephant Intrusion Detection System.

Signal analysis helps investigate the characteristics of different event classes and supports the selection and interpretation of features for downstream classification.

## Analysis Objectives

The signal-processing workflow may include:

* Inspecting seismic waveform data.
* Comparing signals from different event classes.
* Analysing frequency-domain characteristics.
* Visualising waveform and frequency information.
* Supporting the investigation of features used by the RBDMS and Random Forest pipeline.

## Frequency Analysis

The `frequency_analysis/` subdirectory contains scripts associated with frequency analysis and signal visualisation.

Depending on the available files, these scripts may generate frequency plots, mean-frequency comparisons, or spectrogram visualisations.

## Before Using the Scripts

1. Identify the dataset file or directory required by the selected script.
2. Confirm the expected data format and directory structure.
3. Check whether the script uses a relative path or a machine-specific absolute path.
4. Verify that the input data is accessible from the script's execution directory.
5. Review the required Python libraries.
6. Check the output directory and filename before generating plots.

## Path Considerations

Some analysis scripts may expect dataset files to be located relative to the script, while others may contain paths from the original development environment.

For example, a script containing an absolute Windows path must be updated to match the location of the dataset on the current computer.

## Outputs

Depending on the script, outputs may include waveform visualisations, frequency-analysis plots, mean-frequency comparisons, and spectrograms.

The exact outputs depend on the individual script.

## Note

This directory is intended for signal inspection and analysis. The presence of an analysis script does not imply that it is directly compatible with every dataset layout or execution environment.
