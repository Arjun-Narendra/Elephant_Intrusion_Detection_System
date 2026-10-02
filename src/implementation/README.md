# EIDS Implementation

## Overview

This directory contains the implementation files associated with the Elephant Intrusion Detection System (EIDS).

It includes files used to support the deployment or execution of the feature-based classification workflow, including the Random Forest model and its associated configuration files where provided.

## Files

The directory may contain the following files:

| File                             | Purpose                                                           |
| -------------------------------- | ----------------------------------------------------------------- |
| `eeds_realtime_mqtt.py`          | Python script associated with the real-time MQTT-based workflow.  |
| `EEDS_RandomForest_Baseline.pkl` | Saved Random Forest model used by the implementation, if present. |
| `EEDS_model_info.json`           | Model-related information or configuration, if present.           |
| `EEDS_selected_features.json`    | Information about the selected input features, if present.        |

Check the actual files in this directory to confirm their availability and contents.

## Implementation Workflow

The intended workflow is:

1. Obtain seismic feature data from the relevant upstream processing stage.
2. Load the saved Random Forest model and required configuration files.
3. Prepare the input features in the format expected by the model.
4. Perform classification using the loaded model.
5. Use the MQTT-related workflow to handle messages, where configured.
6. Review the resulting classification output and any associated logs.

The exact sequence depends on the script and its configuration.

## MQTT Communication

The `eeds_realtime_mqtt.py` script is associated with the MQTT-based implementation.

Before using it, inspect the source code to identify:

* The MQTT broker address and port.
* The expected topic names.
* The input message format.
* The required model and configuration paths.
* The format and destination of classification outputs.

Ensure that the broker and other required services are available and configured appropriately before execution.

## Model and Configuration Files

The implementation may depend on a saved Random Forest model and JSON configuration files.

Keep the required files in the locations expected by the script. If a model or configuration file is moved or renamed, update the corresponding references in the source code.

The input features must be consistent with those used during model training.

## Before Using the Implementation

* Verify that all required model and configuration files are present.
* Check the file paths used by the implementation script.
* Review the MQTT broker and topic configuration.
* Confirm the expected input data format.
* Ensure that the required Python libraries are available.
* Check the output and logging configuration.
* Verify that the model and feature configuration correspond to the intended classifier.

## Limitations

The implementation depends on compatible model files, input data, configuration settings, and MQTT connectivity where applicable.

The presence of implementation files does not by itself establish that a complete live deployment is configured or operational.

## Note

This directory documents the available implementation components. Refer to the source code and configuration files for the exact execution requirements.
