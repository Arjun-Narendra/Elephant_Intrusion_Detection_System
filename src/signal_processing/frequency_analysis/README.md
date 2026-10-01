# Frequency Analysis

## Overview

This directory contains scripts for analysing the frequency characteristics of seismic signals in the Elephant Intrusion Detection System project.

Frequency-domain analysis helps examine how signal energy is distributed across frequencies and how signal characteristics vary between event classes.

## Purpose

The scripts in this directory may be used to:

* Examine the frequency characteristics of seismic recordings.
* Compare signals belonging to different classes.
* Visualise frequency distributions and spectral information.
* Generate plots to support dataset exploration and feature analysis.

## Before Running a Script

* Identify the exact input dataset required by the script.
* Check whether the input is a waveform file, a directory of recordings, or a CSV file.
* Confirm the expected filename and directory structure.
* Inspect any hardcoded paths and update them if necessary.
* Verify that the required Python libraries are installed.
* Check where the script saves its output.

## Input and Output

**Input:** The dataset files expected by the individual analysis script.

**Output:** Frequency-analysis visualisations or numerical summaries, depending on the script.

Input formats and output filenames may differ between scripts. Refer to the source code when a requirement is not documented here.

## Important

Run these scripts from an environment where the expected dataset paths are valid. Scripts originally developed on another computer may require path adjustments before use.
