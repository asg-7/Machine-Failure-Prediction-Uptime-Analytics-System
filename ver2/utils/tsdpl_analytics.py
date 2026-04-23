"""
utils/tsdpl_analytics.py
MTBF / MTTR / OEE / Shift analytics / Month-over-Month calculations
for TSDPL Kalinganagar.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.tsdpl_constants import SHIFT_CODES, MACHINES, LINES


# ── MTBF per machine per shift ────────────────────────────────────────────────
def compute_mtbf_mttr(downtime_log: pd.DataFrame, observation_hours: float = None) -> pd.DataFrame:
    """
    Returns per-machine:
      failure_count, total_downtime_min, MTTR_min, MTBF_hours
    observation_hours: total window in hours (default: full log span)
    """
    if downtime_log.empty:
        return pd.DataFrame()

    if observation_hours is None:
        span = (downtime_log["timestamp"].max() - downtime_log["timestamp"].min())
        observation_hours = max(span.total_seconds() / 3600, 1)

    rows = []
    for machine, grp in downtime_log.groupby("machine_id"):
        n = len(grp)
        total_dt = grp["downtime_minutes"].sum()
        mttr = round(total_dt / n, 1) if n > 0 else 0.0
        uptime_h = max(observation_hours - total_dt / 60, 1)
        mtbf = round(uptime_h / max(n, 1), 2)
        rows.append({
            "machine_id": machine,
            "failure_count": n,
            "total_downtime_min": int(total_dt),
            "MTTR_min": mttr,
            "MTBF_hours": mtbf,
            "availability_pct": round(100 * (observation_hours * 60 - total_dt) / (observation_hours * 60), 2),
        })

    return pd.DataFrame(rows).sort_values("MTBF_hours").reset_index(drop=True)


def compute_shift_mtbf_mttr(downtime_log: pd.DataFrame) -> pd.DataFrame:
    """
    Returns MTBF / MTTR broken down by shift AND machine.
    Used for Tornado Chart data and shift comparison.
    """
    if downtime_log.empty:
        return pd.DataFrame()

    rows = []
    for (machine, shift), grp in downtime_log.groupby(["machine_id", "shift"]):
        n = len(grp)
        total_dt = grp["downtime_minutes"].sum()
        mttr = round(total_dt / n, 1) if n > 0 else 0.0
        # Approx observation = 8h per shift per unique date
        dates = grp["timestamp"].dt.date.nunique()
        obs_h = dates * 8
        mtbf = round(max(obs_h - total_dt / 60, 1) / max(n, 1), 2)
        rows.append({
            "machine_id": machine,
            "shift": shift,
            "failure_count": n,
            "total_downtime_min": int(total_dt),
            "MTTR_min": mttr,
            "MTBF_hours": mtbf,
        })

    return pd.DataFrame(rows)


def compute_oee_loss(downtime_log: pd.DataFrame, total_shift_hours: float = 8.0) -> pd.DataFrame:
    """
    Approximate OEE Availability Loss % per machine per shift.
    Loss = total_downtime_min / (total_shifts × shift_hours × 60)
    """
    if downtime_log.empty:
        return pd.DataFrame()

    rows = []
    for (machine, shift), grp in downtime_log.groupby(["machine_id", "shift"]):
        n_shifts = grp["timestamp"].dt.date.nunique()
        available_min = n_shifts * total_shift_hours * 60
        lost_min = grp["downtime_minutes"].sum()
        oee_loss_pct = round(100 * lost_min / max(available_min, 1), 2)

        # Split by category
        mech_min = grp[grp["failure_category"] == "Mechanical"]["downtime_minutes"].sum()
        elec_min = grp[grp["failure_category"] == "Electrical"]["downtime_minutes"].sum()
        hyd_min  = grp[grp["failure_category"] == "Hydraulic"]["downtime_minutes"].sum()
        proc_min = grp[grp["failure_category"] == "Process"]["downtime_minutes"].sum()

        rows.append({
            "machine_id": machine,
            "shift": shift,
            "oee_avail_loss_pct": oee_loss_pct,
            "mech_downtime_min": int(mech_min),
            "elec_downtime_min": int(elec_min),
            "hydraulic_downtime_min": int(hyd_min),
            "process_downtime_min": int(proc_min),
            "total_downtime_min": int(lost_min),
        })

    return pd.DataFrame(rows)


# ── Month-over-Month comparison ───────────────────────────────────────────────
def compute_mom_comparison(downtime_log: pd.DataFrame) -> pd.DataFrame:
    """
    For each machine:
      this_month_downtime_min, last_month_downtime_min,
      this_month_failures,  last_month_failures,
      mtbf_this, mtbf_last,
      trend (Improving / Worsening / Stable),
      top_failure_mode (desc)
    """
    if downtime_log.empty:
        return pd.DataFrame()

    now = datetime.now()
    this_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_start = (this_start - timedelta(days=1)).replace(day=1)
    last_end = this_start

    log = downtime_log.copy()
    log["timestamp"] = pd.to_datetime(log["timestamp"])

    this_month = log[log["timestamp"] >= this_start]
    last_month = log[(log["timestamp"] >= last_start) & (log["timestamp"] < last_end)]

    machines = log["machine_id"].unique()
    rows = []
    for machine in machines:
        tm = this_month[this_month["machine_id"] == machine]
        lm = last_month[last_month["machine_id"] == machine]

        tm_dt = tm["downtime_minutes"].sum()
        lm_dt = lm["downtime_minutes"].sum()
        tm_n = len(tm)
        lm_n = len(lm)

        # MTBF approximation
        days_this = max((now - this_start).days, 1)
        days_last = max((last_end - last_start).days, 1)

        mtbf_this = round((days_this * 24 - tm_dt / 60) / max(tm_n, 1), 2)
        mtbf_last = round((days_last * 24 - lm_dt / 60) / max(lm_n, 1), 2)

        # Trend: higher MTBF is better
        if tm_n == 0 and lm_n == 0:
            trend = "Stable"
        elif mtbf_this > mtbf_last * 1.05:
            trend = "Improving"
        elif mtbf_this < mtbf_last * 0.95:
            trend = "Worsening"
        else:
            trend = "Stable"

        # Top failure mode (short label)
        if not tm.empty:
            top = tm["failure_desc"].value_counts().idxmax()
            # Shorten to ~2 words
            short_label = " ".join(top.split()[:2])
        else:
            short_label = "None"

        rows.append({
            "machine_id": machine,
            "this_month_failures": tm_n,
            "last_month_failures": lm_n,
            "this_month_downtime_min": int(tm_dt),
            "last_month_downtime_min": int(lm_dt),
            "mtbf_this_month_h": mtbf_this,
            "mtbf_last_month_h": mtbf_last,
            "trend": trend,
            "top_failure_mode": short_label,
            "delta_downtime_min": int(tm_dt - lm_dt),
        })

    return pd.DataFrame(rows)


# ── Sensor Health Scorecard ───────────────────────────────────────────────────
def compute_sensor_scorecard(sensor_df: pd.DataFrame, lookback_hours: int = 24) -> pd.DataFrame:
    """
    For each machine+parameter, compute:
      current_value (last reading), alarm_high, alarm_low,
      alarm_status, trend (last 6 readings)
    """
    if sensor_df.empty:
        return pd.DataFrame()

    cutoff = sensor_df["timestamp"].max() - timedelta(hours=lookback_hours)
    recent = sensor_df[sensor_df["timestamp"] >= cutoff]

    rows = []
    for (machine, param), grp in recent.groupby(["machine_id", "parameter"]):
        grp_sorted = grp.sort_values("timestamp")
        last_val = grp_sorted["value"].iloc[-1]
        ah = grp_sorted["alarm_high"].iloc[-1]
        al = grp_sorted["alarm_low"].iloc[-1]
        unit = grp_sorted["unit"].iloc[-1]

        # Trend
        if len(grp_sorted) >= 3:
            recent_vals = grp_sorted["value"].values[-6:]
            slope = np.polyfit(range(len(recent_vals)), recent_vals, 1)[0]
            trend_dir = "↑ Rising" if slope > 0.01 else ("↓ Falling" if slope < -0.01 else "→ Stable")
        else:
            trend_dir = "→ Stable"

        # Status
        if (ah and last_val > ah) or (al and last_val < al):
            status = "ALARM"
        else:
            normal_lo, normal_hi = MACHINES.get(machine, {}).get(
                "params", {}).get(param, {}).get("normal_range", (None, None))
            if normal_hi and last_val > normal_hi * 0.9:
                status = "WARNING"
            else:
                status = "Normal"

        rows.append({
            "machine_id": machine,
            "parameter": param,
            "unit": unit,
            "current_value": round(last_val, 3),
            "alarm_high": ah,
            "alarm_low": al,
            "status": status,
            "trend": trend_dir,
        })

    return pd.DataFrame(rows)
