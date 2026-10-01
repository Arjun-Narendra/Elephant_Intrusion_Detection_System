# Elephant Intrusion Detection System (EIDS)

A seismic signal-based approach to elephant intrusion detection using signal processing, a Rule-Based Decision-Making System (RBDMS), and Random Forest classification.

## Overview

Human–elephant conflict is a major challenge in regions where human settlements overlap with elephant habitats. This project explores the use of ground-vibration signals to identify elephant-related activity and support wildlife intrusion monitoring.

The system analyzes seismic waveform data, extracts relevant signal features, and applies rule-based and machine-learning techniques for classification. An MQTT-based receiver is also included to support sensor-message reception within the intended monitoring architecture.

## Objective

To explore a signal-processing and machine-learning approach for identifying elephant-related ground vibrations and distinguishing relevant biological activity from background noise, contributing to the development of wildlife monitoring and early-warning systems.

## System Architecture

```text
     Seismic Sensors
            |
            v
   Ground-Vibration Data
            |
            v
   Signal Preprocessing
            |
            v
     Feature Extraction
            |
            v
   Feature-Based Analysis
            |
       +----+----+
       |         |
       v         v
     RBDMS   Random Forest
       |         |
       +----+----+
            |
            v
   Classification Results
            |
            v
   Monitoring / Communication
       (MQTT Receiver)
```

*The diagram provides a high-level view of the project workflow. The RBDMS and Random Forest represent distinct rule-based and supervised-learning approaches; their precise interaction depends on the inference implementation.*

## Key Features

* **Seismic Signal Analysis:** Processes ground-vibration waveforms for further analysis.
* **Feature Engineering:** Converts waveform data into numerical features suitable for classification.
* **Rule-Based Decision-Making:** Uses explicit decision rules to screen signal activity.
* **Random Forest Classification:** Applies supervised learning to engineered signal features.
* **Signal Visualization:** Supports waveform and frequency-domain analysis across different event classes.
* **MQTT Communication:** Includes a receiver for incoming sensor messages.
* **Edge-Oriented Approach:** Explores feature-based processing suitable for resource-conscious deployment.

## Dataset

The project uses the Elephant Earthquake Detection System (EEDS) seismic waveform dataset, containing recordings from four classes.

| Class     | Number of recordings |
| --------- | -------------------: |
| Elephant  |                  164 |
| Human     |                  164 |
| Bovid     |                  164 |
| Noise     |                  164 |
| **Total** |              **656** |

During dataset exploration, each waveform was represented by three signal channels with 2,048 samples per channel, at a sampling rate of approximately 200 Hz.

*Dataset availability and redistribution are subject to the original dataset's access conditions and licence. Raw data is not included by default.*

## Signal Processing and Feature Extraction

Signal processing is used to examine waveform characteristics and derive numerical features for subsequent analysis.

The feature-based workflow focuses on four complementary signal characteristics:

| Feature                      | Purpose                                                              |
| ---------------------------- | -------------------------------------------------------------------- |
| **STA/LTA**                  | Highlights transient changes relative to background signal activity. |
| **Zero-Crossing Rate (ZCR)** | Describes waveform oscillation through zero crossings.               |
| **Predominant Frequency**    | Represents the dominant spectral characteristics of a signal.        |
| **Root Mean Square (RMS)**   | Measures the overall magnitude of the vibration signal.              |

Together, these features represent transient behaviour, waveform structure, frequency characteristics, and signal amplitude.

## Rule-Based Decision-Making System (RBDMS)

The RBDMS uses explicit rules to interpret extracted signal features and support event screening.

The project includes two development versions:

* **RBDMS v1:** Initial implementation of the rule-based analysis.
* **RBDMS v2:** Updated implementation supporting biological-event versus noise screening.

This approach provides interpretable decision logic that can be examined alongside machine-learning-based analysis.

## Random Forest Classification

Random Forest is used as a supervised machine-learning approach for the engineered feature dataset.

The workflow includes preparing the feature dataset, associating samples with their labels, training the classifier, and evaluating its predictions on held-out data.

Unlike an end-to-end waveform model, this approach uses extracted numerical features as its input representation.

### Recorded Evaluation Results

The project records the following evaluation metrics:

| Metric             | Recorded result |
| ------------------ | --------------: |
| Accuracy           |          72.73% |
| Weighted Precision |          71.51% |
| Weighted Recall    |          72.73% |
| Weighted F1-score  |          71.86% |

These are recorded project results. They should be interpreted in the context of the evaluation split and training configuration, and do not establish performance under real-world deployment conditions.

## Repository Structure

The repository contains scripts and resources related to signal analysis, feature extraction, and rule-based processing.

```text
Elephant_Intrusion_Detection_System/
├── Signal Processing/
│   ├── elephant_dataset/
│   ├── EIDS_features_v2.csv
│   ├── EIDS_features_initial.csv
│   ├── build_rbdms_v1.py
│   ├── build_rbdms_v2.py
│   ├── plot_dataset.py
│   ├── plot_frequency_analysis.py
│   └── ...
├── .gitignore
├── LICENSE
└── README.md
```

*The structure above is illustrative. Update it to reflect the actual files and folders committed to the repository.*

## My Contributions

My contributions focused on signal analysis and the feature-based processing workflow.

* **Signal Analysis:** Explored seismic waveform data and examined its time-domain and frequency-domain characteristics.
* **Feature Selection:** Analyzed signal features and worked with STA/LTA, ZCR, Predominant Frequency, and RMS for feature-based analysis.
* **RBDMS Development:** Contributed to the development and analysis of rule-based decision-making implementations.
* **Machine Learning:** Worked on the feature-based Random Forest classification workflow and model evaluation.
* **Data Visualization:** Generated waveform and frequency-analysis plots to examine signal characteristics across different classes.

These activities contributed to the analysis and development of the seismic signal-based detection approach.

## Limitations and Future Scope

* Validate the approach across different sensor locations and environmental conditions.
* Improve robustness against background vibrations and environmental noise.
* Evaluate classification performance on additional recordings.
* Further validate real-time communication and monitoring under practical deployment conditions.

## Technologies Used

* **Programming:** Python
* **Signal Processing:** Waveform and frequency analysis
* **Feature Engineering:** STA/LTA, ZCR, Predominant Frequency, RMS
* **Machine Learning:** Random Forest
* **Decision Logic:** Rule-Based Decision-Making System
* **Communication:** MQTT

## Project Status

The project covers seismic signal analysis, feature engineering, rule-based screening, and Random Forest classification. Further validation is needed to establish the reliability of the complete system under real-world operating conditions.

## Author

**Arjun Narendra Kumar**

GitHub: [@Arjun-Narendra](https://github.com/Arjun-Narendra)
