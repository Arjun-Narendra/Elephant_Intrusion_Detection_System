Elephant Intrusion Detection System (EIDS)

A seismic signal-based Elephant Intrusion Detection System that combines signal processing, a Rule-Based Decision-Making System (RBDMS), and Random Forest classification to analyze ground vibrations for wildlife intrusion monitoring.

Overview

Human–elephant conflict is a significant challenge in areas where human settlements and elephant habitats overlap. This project explores the use of ground-vibration signals captured using geophone sensors to identify elephant-related activity.

The system processes vibration signals, extracts meaningful signal features, applies rule-based decision logic, and uses a Random Forest classifier for data-driven classification. An MQTT-based receiver is also included as part of the intended real-time data-processing architecture.

System Architecture
Geophone Sensors
       |
       v
Ground-Vibration Signals
       |
       v
Windowing and Signal Processing
       |
       v
Feature Extraction
       |
       +--------------------------+
       |                          |
       v                          v
     RBDMS                Feature Dataset
       |                          |
       |                          v
       |                  Random Forest
       |                          |
       +------------+-------------+
                    |
                    v
          Classification Output
                    |
                    v
           MQTT-Based Receiver
                    |
                    v
             Alert / Logging

The diagram represents the overall project architecture. The rule-based and machine-learning stages serve distinct purposes, and their exact integration depends on the implementation used for inference.

Key Features
Seismic Signal Processing: Processes ground-vibration recordings for subsequent analysis.
Feature Engineering: Extracts compact numerical features from signal windows.
Rule-Based Decision-Making System (RBDMS): Uses explicit rules to interpret signal characteristics and identify event-like activity.
Random Forest Classification: Applies supervised machine learning to engineered signal features.
Feature Analysis: Supports examination of signal characteristics and class-wise feature distributions.
MQTT Integration: Includes a receiver designed to subscribe to incoming sensor messages.
Edge-Oriented Design: Uses a compact feature representation intended to support resource-conscious inference.
Dataset

The project uses a seismic ground-vibration dataset containing recordings associated with four classes:

Class	Samples
Elephant	164
Human	164
Bovid	164
Noise	164
Total	656

The dataset contains three signal channels per waveform. Each waveform was reported as having a shape of (3, 2048) during dataset exploration.

The consolidated technical report also documents a window configuration of approximately 10 seconds and 2,045 samples. These window dimensions should be verified against the final preprocessing implementation before reproducing the experiments.

Dataset note: Raw recordings and derived datasets are not included in this repository by default. Refer to the original dataset source and its licensing terms before obtaining or redistributing the data.

Signal Processing and Feature Extraction

The project explores signal preprocessing, waveform visualization, frequency analysis, and feature extraction to convert vibration signals into a compact representation suitable for classification.

Four primary features were selected for the RBDMS and Random Forest feature-based workflow.

Feature	Description	Purpose
STA/LTA	Short-Term Average / Long-Term Average ratio	Highlights transient changes relative to background activity.
Zero-Crossing Rate (ZCR)	Rate of waveform zero crossings	Describes waveform oscillation and sign-change behaviour.
Predominant Frequency	Frequency associated with the strongest spectral contribution	Represents dominant frequency characteristics.
RMS	Root Mean Square amplitude	Measures the overall strength of the vibration signal.

Together, these features describe complementary signal characteristics, including amplitude, transient behaviour, spectral content, and waveform structure.

Rule-Based Decision-Making System (RBDMS)

The RBDMS provides an interpretable, rule-oriented approach to evaluating signal features.

The project includes two development versions:

RBDMS v1: An earlier implementation of the rule-based feature analysis.
RBDMS v2: A subsequent implementation that organizes feature evidence and supports biological-event versus noise screening.

The rule-based approach provides explicit decision logic that can be inspected and compared with supervised classification results.

Random Forest Classification

Random Forest is used as the supervised machine-learning approach for the engineered feature dataset.

The training workflow involves:

Loading the engineered feature dataset and associated metadata.
Aligning samples with their corresponding labels.
Preparing the feature matrix and target labels.
Training the Random Forest classifier.
Evaluating the trained model on held-out data.
Saving model information and integrating the model into the inference workflow.

The model uses engineered numerical features rather than directly classifying the complete raw waveform.

Recorded Model Results

The project model information records the following test metrics:

Metric	Recorded value
Accuracy	72.73%
Weighted Precision	71.51%
Weighted Recall	72.73%
Weighted F1-score	71.86%

These values are recorded project results, not a guarantee of performance on new recordings or real-world deployments. The evaluation split, class-level metrics, and final training configuration should be verified before interpreting these results further.

## Repository Structure

The repository is organized around signal processing, feature extraction, rule-based decision-making, and machine-learning analysis.

```text
Elephant_Intrusion_Detection_System/
├── Signal Processing/
│   ├── elephant_dataset/          # Seismic waveform dataset
│   ├── EEDS_features_v2.csv       # Engineered signal features
│   ├── EEDS_features_initial.csv  # Initial feature dataset
│   ├── build_rbdms_v1.py           # Initial RBDMS implementation
│   ├── build_rbdms_v2.py           # Updated RBDMS implementation
│   └── ...                         # Analysis scripts and visualizations
├── .gitignore
├── LICENSE
└── README.md
```

*Note: This is a representative structure. Adjust file and folder names to match the contents actually committed to the repository.*

## My Contributions

My work focused on the signal-processing and feature-based analysis aspects of the project.

* **Signal Analysis:** Explored seismic waveform data and examined its time-domain and frequency-domain characteristics.
* **Feature Selection:** Analyzed signal features and focused on STA/LTA, Zero-Crossing Rate (ZCR), Predominant Frequency, and RMS for feature-based classification.
* **Rule-Based Decision-Making:** Worked on the development and analysis of the RBDMS, including its successive implementation versions.
* **Machine Learning:** Contributed to the feature-based Random Forest classification workflow and model evaluation.
* **Data Visualization:** Generated waveform and frequency-analysis visualizations to understand signal characteristics across different classes.

These contributions supported the development and evaluation of a feature-based approach to elephant intrusion detection using ground-vibration signals.

## Objective

The objective of this project is to explore a seismic signal-based approach for detecting elephant-related activity using ground-vibration data. By combining signal processing, selected statistical and frequency-domain features, rule-based decision-making, and Random Forest classification, the project aims to distinguish relevant biological events from background noise and support the development of wildlife intrusion monitoring and early-warning systems.
