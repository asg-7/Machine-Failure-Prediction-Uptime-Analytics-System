"""
utils/analytics.py
Uptime/Downtime engine and failure pattern detection.
"""

import pandas as pd
import numpy as np
from typing import Optional


# ──────────────────────────────────────────────
# 1. Uptime / Downtime Engine
# ──────────────────────────────────────────────

def compute_uptime_downtime(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each machine compute:
      - total_records, up_count, down_count
      - uptime_pct, downtime_pct
      - approx_uptime_hours, approx_downtime_hours  (assumes uniform record interval)
    Returns a DataFrame indexed by machine_id.
    """
    results = []
    for machine, grp in df.groupby("machine_id"):
        total = len(grp)
        up = (grp["status"] == "UP").sum()
        down = (grp["status"] == "DOWN").sum()
        up_pct = round(100 * up / total, 2) if total else 0
        down_pct = round(100 * down / total, 2) if total else 0

        # Estimate hours using median interval between consecutive records
        grp_sorted = grp.sort_values("timestamp")
        deltas = grp_sorted["timestamp"].diff().dropna()
        if len(deltas):
            median_interval_h = deltas.median().total_seconds() / 3600
        else:
            median_interval_h = 0

        uptime_h = round(up * median_interval_h, 2)
        downtime_h = round(down * median_interval_h, 2)

        results.append({
            "machine_id": machine,
            "total_records": total,
            "up_count": up,
            "down_count": down,
            "uptime_pct": up_pct,
            "downtime_pct": down_pct,
            "uptime_hours": uptime_h,
            "downtime_hours": downtime_h,
        })

    return pd.DataFrame(results).set_index("machine_id")


# ──────────────────────────────────────────────
# 2. Failure Event Extraction
# ──────────────────────────────────────────────

def extract_failure_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect transitions UP → DOWN for each machine.
    Returns DataFrame of failure events with:
      machine_id, failure_time, runtime_before_failure_hours, hour_of_day
    """
    events = []
    for machine, grp in df.groupby("machine_id"):
        grp = grp.sort_values("timestamp").reset_index(drop=True)
        # Track when machine was last seen UP
        last_up_time: Optional[pd.Timestamp] = None

        for i, row in grp.iterrows():
            if row["status"] == "UP":
                if last_up_time is None:
                    last_up_time = row["timestamp"]
            elif row["status"] == "DOWN":
                if last_up_time is not None:
                    runtime_h = (row["timestamp"] - last_up_time).total_seconds() / 3600
                    events.append({
                        "machine_id": machine,
                        "failure_time": row["timestamp"],
                        "runtime_before_failure_hours": round(runtime_h, 3),
                        "hour_of_day": row["timestamp"].hour,
                        "day_of_week": row["timestamp"].day_name(),
                    })
                    last_up_time = None  # reset until next UP run

    return pd.DataFrame(events) if events else pd.DataFrame(
        columns=["machine_id", "failure_time", "runtime_before_failure_hours",
                 "hour_of_day", "day_of_week"]
    )


# ──────────────────────────────────────────────
# 3. Failure Pattern Statistics
# ──────────────────────────────────────────────

def compute_failure_patterns(failure_events: pd.DataFrame) -> pd.DataFrame:
    """
    Per-machine stats:
      failure_count, avg_runtime_before_failure, std_runtime,
      min_runtime, max_runtime, most_common_failure_hour
    """
    if failure_events.empty:
        return pd.DataFrame()

    rows = []
    for machine, grp in failure_events.groupby("machine_id"):
        rt = grp["runtime_before_failure_hours"]
        hour_mode = grp["hour_of_day"].mode()
        rows.append({
            "machine_id": machine,
            "failure_count": len(grp),
            "avg_runtime_h": round(rt.mean(), 2),
            "std_runtime_h": round(rt.std(), 2) if len(rt) > 1 else 0.0,
            "min_runtime_h": round(rt.min(), 2),
            "max_runtime_h": round(rt.max(), 2),
            "most_common_failure_hour": int(hour_mode.iloc[0]) if len(hour_mode) else None,
        })

    return pd.DataFrame(rows).set_index("machine_id")


# ──────────────────────────────────────────────
# 4. Time-of-Day Trend
# ──────────────────────────────────────────────

def compute_hourly_failure_trend(failure_events: pd.DataFrame) -> pd.DataFrame:
    """
    Returns count of failures per hour-of-day across all machines.
    """
    if failure_events.empty:
        return pd.DataFrame({"hour_of_day": range(24), "failure_count": [0] * 24})

    trend = (
        failure_events.groupby("hour_of_day")
        .size()
        .reindex(range(24), fill_value=0)
        .reset_index()
    )
    trend.columns = ["hour_of_day", "failure_count"]
    return trend


# ──────────────────────────────────────────────
# 5. Rolling Uptime (for trend chart)
# ──────────────────────────────────────────────

def compute_daily_uptime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Daily uptime % per machine, suitable for a time-series line chart.
    """
    df2 = df.copy()
    df2["date"] = df2["timestamp"].dt.date
    df2["is_up"] = (df2["status"] == "UP").astype(int)

    daily = (
        df2.groupby(["machine_id", "date"])["is_up"]
        .mean()
        .mul(100)
        .round(2)
        .reset_index()
    )
    daily.columns = ["machine_id", "date", "uptime_pct"]
    daily["date"] = pd.to_datetime(daily["date"])
    return daily
