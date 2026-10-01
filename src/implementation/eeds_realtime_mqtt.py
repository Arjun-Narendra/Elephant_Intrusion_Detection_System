"""
EEDS REAL-TIME MQTT -> SIGNAL PROCESSING -> RBDMS -> RANDOM FOREST

Place this file in the same folder as:
    EEDS_RandomForest_Baseline.pkl
    EEDS_selected_features.json       (recommended)
or:
    selected_features.json

Install dependencies once:
    pip install paho-mqtt numpy scipy pandas scikit-learn joblib

Run:
    python eeds_realtime_mqtt.py

Expected MQTT payload from ESP32:
{
  "node": "NODE_02",
  "firstSample": 1,
  "lastSample": 200,
  "count": 200,
  "x": [...],
  "y": [...],
  "z": [...]
}

The ESP32 sketch currently publishes 200 samples per packet at 200 Hz.
This program builds a 2048-sample window for each node.
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from collections import defaultdict
from pathlib import Path
from threading import Lock

import joblib
import numpy as np
import paho.mqtt.client as mqtt
from scipy.signal import welch


# ============================================================
# USER CONFIGURATION
# ============================================================

BROKER = "broker.hivemq.com"
PORT = 1883
MQTT_TOPIC = "elephant/nodes/#"

FS = 200                         # ESP32 sampling rate
PACKET_SIZE = 200
WINDOW_SIZE = 2048               # RF/RBDMS processing window
NODE_TIMEOUT_SECONDS = 60

MODEL_FILE = "EEDS_RandomForest_Baseline.pkl"
SELECTED_FEATURES_FILE = "EEDS_selected_features.json"

# RBDMS V2 thresholds supplied in the project code
STA_MAX = 9.70535
ZCR_MIN = 32.6953
ZCR_MAX = 101.377
FREQ_MIN = 11.3281
FREQ_MAX = 23.4375
RMS_MIN = 1.07576e-10

# Set this to True only if your RBDMS thresholds were calculated
# from unit-standard-deviation-normalized signals.
NORMALIZE_CHANNELS_FOR_FEATURES = False

# The RBDMS currently uses a 3-out-of-4 score per channel,
# and at least 2 of 3 channels must pass.
MIN_PARAMETER_SCORE_PER_CHANNEL = 3
MIN_PASSING_CHANNELS = 2


# ============================================================
# GLOBAL STATE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / MODEL_FILE
FEATURES_PATH = BASE_DIR / SELECTED_FEATURES_FILE

rf_model = None
selected_features = None

node_buffers = defaultdict(lambda: {
    "x": [],
    "y": [],
    "z": [],
    "last_seen": 0.0,
})
buffer_lock = Lock()


# ============================================================
# FILE / MODEL LOADING
# ============================================================

def load_selected_features():
    """Load the exact feature order used during RF training."""
    candidate_files = [
        BASE_DIR / SELECTED_FEATURES_FILE,
        BASE_DIR / "selected_features.json",
    ]

    for path in candidate_files:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                features = data
            elif isinstance(data, dict):
                features = (
                    data.get("selected_features")
                    or data.get("features")
                    or data.get("feature_names")
                )
            else:
                features = None

            if features:
                print(f"[MODEL] Selected features loaded from: {path.name}")
                print(f"[MODEL] Number of selected features: {len(features)}")
                return list(features)

    print("[MODEL] No selected-feature JSON found.")
    print("[MODEL] The program will try to use model.feature_names_in_.")
    return None


def load_model():
    global rf_model, selected_features

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"RF model not found: {MODEL_PATH}\n"
            f"Place {MODEL_FILE} beside this Python file."
        )

    rf_model = joblib.load(MODEL_PATH)
    selected_features = load_selected_features()

    if selected_features is None:
        model_features = getattr(rf_model, "feature_names_in_", None)
        if model_features is not None:
            selected_features = list(model_features)
            print("[MODEL] Feature order loaded from model.feature_names_in_.")

    if selected_features is None:
        raise FileNotFoundError(
            "Could not determine RF feature names. Place "
            "EEDS_selected_features.json or selected_features.json "
            "beside this Python file."
        )

    print(f"[MODEL] RF model loaded: {MODEL_PATH.name}")
    print("[MODEL] RF feature order:")
    for i, name in enumerate(selected_features, 1):
        print(f"        {i:02d}. {name}")


# ============================================================
# SIGNAL PROCESSING
# ============================================================

def calculate_rms(signal: np.ndarray) -> float:
    signal = np.asarray(signal, dtype=float)
    return float(np.sqrt(np.mean(signal ** 2)))


def calculate_zcr(signal: np.ndarray) -> float:
    """
    ZCR expressed as crossings per second.
    This matches the RBDMS receiver's duration-based approach.
    """
    signal = np.asarray(signal, dtype=float)
    if len(signal) < 2:
        return 0.0

    crossings = np.sum(np.diff(np.signbit(signal)) != 0)
    duration_seconds = len(signal) / FS

    if duration_seconds <= 0:
        return 0.0

    return float(crossings / duration_seconds)


def calculate_predominant_frequency(signal: np.ndarray) -> float:
    signal = np.asarray(signal, dtype=float)

    if len(signal) < 4:
        return 0.0

    signal = signal - np.mean(signal)

    frequencies, power = welch(
        signal,
        fs=FS,
        nperseg=min(512, len(signal)),
    )

    # Ignore DC
    valid = frequencies > 0
    if not np.any(valid):
        return 0.0

    valid_frequencies = frequencies[valid]
    valid_power = power[valid]

    return float(valid_frequencies[np.argmax(valid_power)])


def calculate_sta_lta(signal: np.ndarray) -> float:
    """
    Maximum STA/LTA ratio using:
        STA = 0.25 seconds
        LTA = 2.0 seconds

    This follows the RBDMS V2 receiver implementation.
    """
    signal = np.asarray(signal, dtype=float)

    sta_samples = max(1, int(0.25 * FS))
    lta_samples = max(sta_samples + 1, int(2.0 * FS))

    if len(signal) < lta_samples:
        return 0.0

    energy = signal ** 2
    max_ratio = 0.0

    for i in range(lta_samples, len(energy) + 1):
        sta = np.mean(energy[i - sta_samples:i])
        lta = np.mean(energy[i - lta_samples:i])

        if lta > 1e-20:
            ratio = sta / lta
            if ratio > max_ratio:
                max_ratio = ratio

    return float(max_ratio)


def prepare_channel(signal):
    signal = np.asarray(signal, dtype=float)
    signal = signal[np.isfinite(signal)]

    if len(signal) == 0:
        return np.zeros(WINDOW_SIZE, dtype=float)

    # Remove DC component before feature extraction
    signal = signal - np.mean(signal)

    if NORMALIZE_CHANNELS_FOR_FEATURES:
        std = np.std(signal)
        if std > 1e-12:
            signal = signal / std

    return signal


def extract_channel_features(signal):
    signal = prepare_channel(signal)

    return {
        "STA_LTA": calculate_sta_lta(signal),
        "RMS": calculate_rms(signal),
        "ZCR": calculate_zcr(signal),
        "Predominant_Frequency": calculate_predominant_frequency(signal),
    }


def extract_window_features(window):
    """
    window shape:
        (3, WINDOW_SIZE)

    Output names:
        CH1_STA_LTA, CH1_RMS, CH1_ZCR, CH1_Predominant_Frequency, ...
    """
    if np.asarray(window).shape != (3, WINDOW_SIZE):
        raise ValueError(
            f"Expected window shape (3, {WINDOW_SIZE}), "
            f"received {np.asarray(window).shape}"
        )

    result = {}

    for channel_index, channel_name in enumerate(("CH1", "CH2", "CH3")):
        channel_features = extract_channel_features(window[channel_index])

        for feature_name, value in channel_features.items():
            result[f"{channel_name}_{feature_name}"] = float(value)

    return result


# ============================================================
# RBDMS V2
# ============================================================

def score_channel(features, channel_name):
    sta_lta = features[f"{channel_name}_STA_LTA"]
    rms = features[f"{channel_name}_RMS"]
    zcr = features[f"{channel_name}_ZCR"]
    frequency = features[f"{channel_name}_Predominant_Frequency"]

    score = 0
    reasons = []

    if sta_lta <= STA_MAX:
        score += 1
        reasons.append("STA/LTA=PASS")
    else:
        reasons.append("STA/LTA=FAIL")

    if ZCR_MIN <= zcr <= ZCR_MAX:
        score += 1
        reasons.append("ZCR=PASS")
    else:
        reasons.append("ZCR=FAIL")

    if FREQ_MIN <= frequency <= FREQ_MAX:
        score += 1
        reasons.append("FREQ=PASS")
    else:
        reasons.append("FREQ=FAIL")

    if rms >= RMS_MIN:
        score += 1
        reasons.append("RMS=PASS")
    else:
        reasons.append("RMS=FAIL")

    passed = score >= MIN_PARAMETER_SCORE_PER_CHANNEL
    return score, passed, reasons


def apply_rbdms(features):
    channel_results = {}
    passing_channels = 0

    for channel_name in ("CH1", "CH2", "CH3"):
        score, passed, reasons = score_channel(features, channel_name)
        channel_results[channel_name] = {
            "score": score,
            "passed": passed,
            "reasons": reasons,
        }

        if passed:
            passing_channels += 1

    accepted = passing_channels >= MIN_PASSING_CHANNELS
    return accepted, channel_results, passing_channels


# ============================================================
# RANDOM FOREST
# ============================================================

def make_rf_input(feature_dict):
    missing = [name for name in selected_features if name not in feature_dict]

    if missing:
        raise KeyError(
            "The following RF features are missing from the live extractor: "
            + ", ".join(missing)
        )

    return np.array(
        [[feature_dict[name] for name in selected_features]],
        dtype=float,
    )


def run_random_forest(feature_dict):
    X = make_rf_input(feature_dict)

    prediction = rf_model.predict(X)[0]

    probabilities = None
    if hasattr(rf_model, "predict_proba"):
        probabilities = rf_model.predict_proba(X)[0]

    return prediction, probabilities


# ============================================================
# TERMINAL OUTPUT
# ============================================================

def print_feature_summary(features):
    print("\n[FEATURES]")
    for channel in ("CH1", "CH2", "CH3"):
        print(
            f"  {channel}: "
            f"STA/LTA={features[channel + '_STA_LTA']:.4f}, "
            f"RMS={features[channel + '_RMS']:.6e}, "
            f"ZCR={features[channel + '_ZCR']:.4f}, "
            f"Freq={features[channel + '_Predominant_Frequency']:.4f} Hz"
        )


def process_complete_window(node_id, window):
    try:
        print("\n" + "=" * 72)
        print(f"[PROCESSING] Node={node_id} | Samples={WINDOW_SIZE}")

        features = extract_window_features(window)
        print_feature_summary(features)

        accepted, channel_results, passing_channels = apply_rbdms(features)

        print("\n[RBDMS]")
        for channel_name, result in channel_results.items():
            status = "PASS" if result["passed"] else "FAIL"
            print(
                f"  {channel_name}: {result['score']}/4 "
                f"-> {status} | " + ", ".join(result["reasons"])
            )

        print(
            f"  Overall RBDMS: "
            f"{'ACCEPT' if accepted else 'REJECT'} "
            f"({passing_channels}/3 channels passed)"
        )

        if not accepted:
            print("[RF] SKIPPED because RBDMS rejected this window.")
            print("=" * 72)
            return

        prediction, probabilities = run_random_forest(features)

        print("\n[RANDOM FOREST]")
        print(f"  Prediction: {prediction}")

        if probabilities is not None:
            classes = getattr(rf_model, "classes_", range(len(probabilities)))
            for label, probability in zip(classes, probabilities):
                print(f"  Probability[{label}]: {probability:.4f}")

        print(f"\n[FINAL RESULT] Node={node_id} -> {prediction}")
        print("=" * 72)

    except Exception as exc:
        print(f"\n[ERROR] Could not process window from {node_id}: {exc}")
        traceback.print_exc()


# ============================================================
# MQTT BUFFER MANAGEMENT
# ============================================================

def clean_old_nodes():
    now = time.time()
    with buffer_lock:
        expired = [
            node_id
            for node_id, data in node_buffers.items()
            if now - data["last_seen"] > NODE_TIMEOUT_SECONDS
        ]

        for node_id in expired:
            del node_buffers[node_id]
            print(f"[BUFFER] Removed inactive node: {node_id}")


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"[MQTT] Connected to {BROKER}:{PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"[MQTT] Subscribed to: {MQTT_TOPIC}")
        print("[SYSTEM] Waiting for ESP32 data...\n")
    else:
        print(f"[MQTT] Connection failed. Reason code: {reason_code}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties=None):
    print(f"[MQTT] Disconnected. Reason code: {reason_code}")


def get_payload_array(payload, *names):
    for name in names:
        if name in payload:
            value = payload[name]
            if isinstance(value, list):
                return value
    return None


def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))

        # Ignore non-waveform metadata messages
        node_id = payload.get("node_id") or payload.get("node")
        if not node_id:
            return

        x = get_payload_array(payload, "x", "wave_x")
        y = get_payload_array(payload, "y", "wave_y")
        z = get_payload_array(payload, "z", "wave_z")

        if x is None or y is None or z is None:
            return

        count = min(len(x), len(y), len(z))
        if count == 0:
            return

        x = np.asarray(x[:count], dtype=float)
        y = np.asarray(y[:count], dtype=float)
        z = np.asarray(z[:count], dtype=float)

        if not (
            np.all(np.isfinite(x))
            and np.all(np.isfinite(y))
            and np.all(np.isfinite(z))
        ):
            print(f"[MQTT] Ignored non-finite packet from {node_id}")
            return

        with buffer_lock:
            data = node_buffers[node_id]
            data["x"].extend(x.tolist())
            data["y"].extend(y.tolist())
            data["z"].extend(z.tolist())
            data["last_seen"] = time.time()

            current_size = len(data["x"])
            print(
                f"[MQTT] {node_id}: received {count} samples | "
                f"buffer={current_size}/{WINDOW_SIZE}"
            )

            if current_size < WINDOW_SIZE:
                return

            # Take exactly one complete window
            window = np.array([
                data["x"][:WINDOW_SIZE],
                data["y"][:WINDOW_SIZE],
                data["z"][:WINDOW_SIZE],
            ], dtype=float)

            # Remove the processed samples; retain any extra samples
            data["x"] = data["x"][WINDOW_SIZE:]
            data["y"] = data["y"][WINDOW_SIZE:]
            data["z"] = data["z"][WINDOW_SIZE:]

        # Process outside the lock
        process_complete_window(str(node_id), window)

    except json.JSONDecodeError:
        print("[MQTT] Ignored non-JSON message.")
    except Exception as exc:
        print(f"[MQTT] Message handling error: {exc}")
        traceback.print_exc()


# ============================================================
# MAIN
# ============================================================

def create_mqtt_client():
    # Compatible with newer and older Paho MQTT versions
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    return client


def main():
    print("=" * 72)
    print("EEDS REAL-TIME ELEPHANT INTRUSION DETECTION")
    print("MQTT -> Signal Processing -> RBDMS -> Random Forest")
    print("=" * 72)

    print(f"[CONFIG] Broker: {BROKER}:{PORT}")
    print(f"[CONFIG] Topic: {MQTT_TOPIC}")
    print(f"[CONFIG] Sampling rate: {FS} Hz")
    print(f"[CONFIG] Processing window: {WINDOW_SIZE} samples")
    print(f"[CONFIG] Feature normalization: {NORMALIZE_CHANNELS_FOR_FEATURES}")

    load_model()

    client = create_mqtt_client()

    try:
        print("\n[MQTT] Connecting...")
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()

        while True:
            clean_old_nodes()
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n[STOP] Stopping EEDS receiver...")
    except Exception as exc:
        print(f"\n[FATAL] {exc}")
        traceback.print_exc()
    finally:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass

        print("[SYSTEM] EEDS receiver stopped.")


if __name__ == "__main__":
    main()
