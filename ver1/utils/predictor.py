"""
utils/predictor.py
Simple failure prediction using moving averages + linear regression.
Outputs: predicted_ttf_hours, risk_score (Low / Medium / High), risk_value (0-100)
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Optional


# ──────────────────────────────────────────────
# Helper: time since last failure
# ──────────────────────────────────────────────

def _time_since_last_failure(df_machine: pd.DataFrame) -> Optional[float]:
    """Hours since most recent DOWN event."""
    downs = df_machine[df_machine["status"] == "DOWN"]["timestamp"]
    if downs.empty:
        return None
    last_down = downs.max()
    last_record = df_machine["timestamp"].max()
    return (last_record - last_down).total_seconds() / 3600


def _current_run_hours(df_machine: pd.DataFrame) -> float:
    """Hours the machine has been continuously UP until the last record."""
    grp = df_machine.sort_values("timestamp")
    # Walk backwards until we hit a DOWN
    hours = 0.0
    prev_ts = None
    for _, row in grp[::-1].iterrows():
        if row["status"] == "DOWN":
            break
        if prev_ts is not None:
            hours += (prev_ts - row["timestamp"]).total_seconds() / 3600
        prev_ts = row["timestamp"]
    return round(hours, 3)


# ──────────────────────────────────────────────
# Core Prediction
# ──────────────────────────────────────────────

def predict_machine(
    failure_events_machine: pd.DataFrame,
    df_machine: pd.DataFrame,
    window: int = 5,
) -> dict:
    """
    Predict TTF and risk for a single machine.

    Strategy:
      1. Moving average of recent inter-failure runtimes → baseline TTF
      2. Linear regression on failure intervals → trend TTF
      3. Combined estimate = weighted average of both
      4. Current runtime already accumulated → remaining TTF
      5. Risk = normalize remaining TTF against combined estimate
    """
    result = {
        "machine_id": df_machine["machine_id"].iloc[0] if len(df_machine) else "Unknown",
        "failure_count": 0,
        "avg_runtime_h": None,
        "predicted_ttf_hours": None,
        "current_run_hours": 0.0,
        "remaining_ttf_hours": None,
        "risk_label": "Unknown",
        "risk_value": 0,
        "confidence": "Low",
    }

    if failure_events_machine.empty or len(failure_events_machine) < 2:
        result["failure_count"] = len(failure_events_machine)
        result["risk_label"] = "Low" if failure_events_machine.empty else "Medium"
        result["risk_value"] = 10 if failure_events_machine.empty else 35
        result["confidence"] = "Low (insufficient data)"
        return result

    runtimes = failure_events_machine["runtime_before_failure_hours"].values
    n = len(runtimes)
    result["failure_count"] = n
    result["avg_runtime_h"] = round(float(np.mean(runtimes)), 2)

    # --- Moving average TTF ---
    recent = runtimes[-min(window, n):]
    ma_ttf = float(np.mean(recent))

    # --- Linear regression on failure intervals ---
    X = np.arange(n).reshape(-1, 1)
    y = runtimes
    lr = LinearRegression()
    lr.fit(X, y)
    lr_ttf = float(lr.predict([[n]])[0])  # predict next interval
    lr_ttf = max(lr_ttf, 1.0)  # floor at 1 hour

    # --- Combined ---
    # Weight: regression gets more weight if trend is clear (R² > 0.4)
    ss_res = np.sum((y - lr.predict(X)) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    w_lr = min(0.7, max(0.2, r2))
    combined_ttf = (1 - w_lr) * ma_ttf + w_lr * lr_ttf
    combined_ttf = round(max(combined_ttf, 1.0), 2)

    result["predicted_ttf_hours"] = combined_ttf
    result["confidence"] = "High" if r2 > 0.5 else ("Medium" if r2 > 0.2 else "Low")

    # --- Current run & remaining ---
    current_run = _current_run_hours(df_machine)
    result["current_run_hours"] = round(current_run, 2)

    remaining = combined_ttf - current_run
    result["remaining_ttf_hours"] = round(remaining, 2)

    # --- Risk Score (0-100) ---
    ratio = current_run / combined_ttf if combined_ttf > 0 else 1.0
    # ratio close to 1 means high risk
    risk_value = int(min(100, max(0, ratio * 100)))

    # Std-based penalty: high variance → higher risk
    if n > 2:
        cv = np.std(runtimes) / np.mean(runtimes) if np.mean(runtimes) > 0 else 0
        risk_value = int(min(100, risk_value + cv * 15))

    result["risk_value"] = risk_value

    if risk_value >= 70:
        result["risk_label"] = "High"
    elif risk_value >= 40:
        result["risk_label"] = "Medium"
    else:
        result["risk_label"] = "Low"

    return result


def predict_all_machines(
    df: pd.DataFrame,
    failure_events: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run prediction for every machine in df.
    Returns a DataFrame with one row per machine.
    """
    rows = []
    for machine in df["machine_id"].unique():
        df_m = df[df["machine_id"] == machine]
        fe_m = (
            failure_events[failure_events["machine_id"] == machine]
            if not failure_events.empty
            else pd.DataFrame()
        )
        rows.append(predict_machine(fe_m, df_m))

    pred_df = pd.DataFrame(rows)
    if not pred_df.empty:
        pred_df = pred_df.sort_values("risk_value", ascending=False).reset_index(drop=True)
    return pred_df


# ──────────────────────────────────────────────
# Sensor anomaly helper (optional enrichment)
# ──────────────────────────────────────────────

def compute_sensor_anomaly_score(df_machine: pd.DataFrame) -> float:
    """
    Returns a 0-100 anomaly score based on how far recent sensor readings
    deviate from the machine's historical baseline (z-score approach).
    Returns 0 if sensors not available.
    """
    sensors = ["temperature", "load", "vibration"]
    available = [s for s in sensors if df_machine[s].notna().sum() > 10]
    if not available:
        return 0.0

    up_data = df_machine[df_machine["status"] == "UP"]
    if len(up_data) < 20:
        return 0.0

    recent_n = max(1, int(len(up_data) * 0.1))  # last 10%
    baseline = up_data.iloc[:-recent_n]
    recent = up_data.iloc[-recent_n:]

    z_scores = []
    for s in available:
        mu = baseline[s].mean()
        sigma = baseline[s].std()
        if sigma > 0:
            recent_mean = recent[s].mean()
            z = abs((recent_mean - mu) / sigma)
            z_scores.append(z)

    if not z_scores:
        return 0.0

    avg_z = np.mean(z_scores)
    # cap at 3 sigma → 100%
    return round(min(100, avg_z / 3 * 100), 1)
