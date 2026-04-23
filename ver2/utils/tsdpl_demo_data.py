"""
utils/tsdpl_demo_data.py
Generates realistic TSDPL-specific demo datasets:
  - Downtime incident log (with shift, failure codes, machine)
  - PM checklist log (task completion timestamps)
  - Shift roster incident log
  - Sensor readings per machine
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from utils.tsdpl_constants import (
    MACHINES, FAILURE_CODES, SHIFTS, SHIFT_CODES, MASTER_ROSTER,
    FAILURE_CODE_LIST, get_shift_from_hour, LINES, PM_FREQUENCY_HOURS
)

random.seed(7)
np.random.seed(7)

# ── Night shift more failure prone for slitter (domain knowledge) ─────────────
MACHINE_SHIFT_FAILURE_WEIGHTS = {
    "Slitter Head (HR Slitting)":    {"A - Morning": 1.0, "B - Afternoon": 1.2, "C - Night": 2.0},
    "Cassette Leveller (HR-CTL)":    {"A - Morning": 1.0, "B - Afternoon": 1.1, "C - Night": 1.6},
    "Flying Shear (HR-CTL)":         {"A - Morning": 1.0, "B - Afternoon": 1.0, "C - Night": 1.3},
    "Recoiler (HR Slitting)":        {"A - Morning": 1.0, "B - Afternoon": 1.1, "C - Night": 1.8},
    "Robotic Tool Setup (CR 2024)":  {"A - Morning": 1.5, "B - Afternoon": 1.0, "C - Night": 1.0},
}


def generate_downtime_log(days: int = 90) -> pd.DataFrame:
    """
    Returns a downtime incident log:
    timestamp, machine_id, line, zone, shift, failure_code, failure_category,
    failure_desc, downtime_minutes, repaired_by, remarks
    """
    start = datetime.now() - timedelta(days=days)
    records = []

    machine_list = list(MACHINES.keys())
    # Base failures per machine per day
    machine_daily_rate = {
        m: random.uniform(0.05, 0.25) for m in machine_list
    }

    current = start
    while current < datetime.now():
        for machine in machine_list:
            rate = machine_daily_rate[machine]
            shift = get_shift_from_hour(current.hour)
            # Apply shift weight
            weight = MACHINE_SHIFT_FAILURE_WEIGHTS.get(machine, {}).get(shift, 1.0)
            if random.random() < rate * weight * (8 / 24):  # 8h shift slice
                # Pick a relevant failure code
                machine_codes = [
                    k for k, v in FAILURE_CODES.items()
                    if v["machine"] == machine or v["machine"] == "All"
                ]
                if not machine_codes:
                    machine_codes = FAILURE_CODE_LIST
                code = random.choice(machine_codes)
                fc = FAILURE_CODES[code]

                # Find repair tech for this shift
                tech = next(
                    (r["name"] for r in MASTER_ROSTER
                     if r["shift"] == shift and r["role"] == "Maint. Tech"), "On-Call Tech"
                )
                supervisor = next(
                    (r["name"] for r in MASTER_ROSTER
                     if r["shift"] == shift and r["role"] == "Supervisor"), "Shift Supervisor"
                )

                downtime = int(np.random.lognormal(mean=3.5, sigma=0.8))
                downtime = min(max(downtime, 5), 480)  # 5 min to 8 hours

                records.append({
                    "timestamp": current + timedelta(minutes=random.randint(0, 479)),
                    "machine_id": machine,
                    "line": MACHINES[machine]["line"],
                    "zone": MACHINES[machine]["zone"],
                    "shift": shift,
                    "failure_code": code,
                    "failure_category": fc["category"],
                    "failure_desc": fc["desc"],
                    "downtime_minutes": downtime,
                    "repaired_by": tech,
                    "supervisor": supervisor,
                    "remarks": "",
                })

        current += timedelta(hours=8)  # step by shift

    df = pd.DataFrame(records).sort_values("timestamp").reset_index(drop=True)
    return df


def generate_shift_roster_log(downtime_log: pd.DataFrame) -> pd.DataFrame:
    """
    Creates TBL_SHIFT_ROSTER_LOG — one entry per shift×line×zone per day,
    with incident flag where downtime occurred.
    """
    start = downtime_log["timestamp"].min().date() if not downtime_log.empty else \
            (datetime.now() - timedelta(days=30)).date()
    end = datetime.now().date()

    rows = []
    d = start
    while d <= end:
        for shift_name in SHIFT_CODES:
            for line, zones in {
                "HR-CTL Line": ["Entry (Uncoiler)", "Mid (Cassette Leveller)", "Exit (Flying Shear / Stacker)"],
                "HR Slitting Line": ["Entry (Uncoiler/Bridle)", "Mid (Slitter Head)", "Exit (Recoiler / Scrap Chopper)"],
                "CR Processing Facility": ["Entry (Skin Pass Mill)", "Mid (Inspection)", "Exit (Parting Line)"],
            }.items():
                for zone in zones:
                    # Lookup operator from master roster
                    operator = next(
                        (r["name"] for r in MASTER_ROSTER
                         if r["shift"] == shift_name and r["line"] == line
                         and (r["zone"] == zone or r["zone"] == "All")
                         and r["role"] == "Operator"), "Standby Operator"
                    )
                    supervisor = next(
                        (r["name"] for r in MASTER_ROSTER
                         if r["shift"] == shift_name and r["role"] == "Supervisor"), "On-Call Supervisor"
                    )
                    tech = next(
                        (r["name"] for r in MASTER_ROSTER
                         if r["shift"] == shift_name and r["role"] == "Maint. Tech"), "On-Call Tech"
                    )

                    # Check for incidents
                    shift_start_map = {"A - Morning": 6, "B - Afternoon": 14, "C - Night": 22}
                    sh = shift_start_map.get(shift_name, 6)
                    day_dt = datetime.combine(d, datetime.min.time())
                    shift_start_dt = day_dt + timedelta(hours=sh)
                    shift_end_dt = shift_start_dt + timedelta(hours=8)

                    if not downtime_log.empty:
                        incidents = downtime_log[
                            (downtime_log["timestamp"] >= shift_start_dt) &
                            (downtime_log["timestamp"] < shift_end_dt) &
                            (downtime_log["line"] == line) &
                            (downtime_log["zone"] == zone)
                        ]
                        incident_flag = "Y" if len(incidents) > 0 else "N"
                        incident_ts = incidents["timestamp"].min().strftime("%H:%M") \
                            if len(incidents) > 0 else ""
                        incident_code = incidents["failure_code"].iloc[0] \
                            if len(incidents) > 0 else ""
                    else:
                        incident_flag, incident_ts, incident_code = "N", "", ""

                    rows.append({
                        "date": d.strftime("%Y-%m-%d"),
                        "shift": shift_name,
                        "line": line,
                        "zone": zone,
                        "operator_name": operator,
                        "supervisor_name": supervisor,
                        "maint_tech_oncall": tech,
                        "incident_logged": incident_flag,
                        "incident_timestamp": incident_ts,
                        "failure_code": incident_code,
                    })
        d += timedelta(days=1)

    return pd.DataFrame(rows)


def generate_pm_checklist_log(days: int = 90) -> pd.DataFrame:
    """
    Simulates PM task completion log with some overdue tasks.
    """
    records = []
    now = datetime.now()
    start = now - timedelta(days=days)

    for machine_name, machine_data in MACHINES.items():
        for task_info in machine_data["pm_tasks"]:
            freq_h = PM_FREQUENCY_HOURS.get(task_info["frequency"], 24)
            current = start
            while current < now:
                # Simulate occasional missed/delayed tasks
                delay_h = 0
                if random.random() < 0.12:  # 12% chance overdue
                    delay_h = random.randint(2, freq_h)

                completed_at = current + timedelta(hours=freq_h + delay_h)
                if completed_at > now:
                    # Future scheduled task
                    records.append({
                        "machine_id": machine_name,
                        "task": task_info["task"],
                        "category": task_info["category"],
                        "frequency": task_info["frequency"],
                        "scheduled_date": current.strftime("%Y-%m-%d %H:%M"),
                        "completed_date": "",
                        "status": "Overdue" if current < now else "Scheduled",
                        "technician": random.choice(
                            [r["name"] for r in MASTER_ROSTER if r["role"] == "Maint. Tech"]
                        ),
                        "loto_required": task_info.get("loto", False),
                        "remarks": "",
                    })
                else:
                    tech = random.choice(
                        [r["name"] for r in MASTER_ROSTER if r["role"] == "Maint. Tech"]
                    )
                    records.append({
                        "machine_id": machine_name,
                        "task": task_info["task"],
                        "category": task_info["category"],
                        "frequency": task_info["frequency"],
                        "scheduled_date": current.strftime("%Y-%m-%d %H:%M"),
                        "completed_date": completed_at.strftime("%Y-%m-%d %H:%M"),
                        "status": "Overdue" if delay_h > 0 else "Completed",
                        "technician": tech,
                        "loto_required": task_info.get("loto", False),
                        "remarks": "Completed with delay" if delay_h > 0 else "",
                    })
                current += timedelta(hours=freq_h)

    return pd.DataFrame(records)


def generate_sensor_readings(days: int = 90) -> pd.DataFrame:
    """
    Time-series sensor readings per machine. Simulates degradation trends.
    """
    records = []
    now = datetime.now()
    start = now - timedelta(days=days)
    step_h = 4  # every 4 hours

    for machine_name, machine_data in MACHINES.items():
        params = machine_data["params"]
        current = start
        # Simulate gradual degradation in last 20% of time window
        degrade_start = start + timedelta(days=int(days * 0.8))

        while current <= now:
            for param_name, param_cfg in params.items():
                lo, hi = param_cfg["normal_range"]
                base = lo + (hi - lo) * 0.5
                noise = (hi - lo) * 0.08

                # Degradation ramp
                if current > degrade_start and param_cfg.get("alarm_high"):
                    progress = (current - degrade_start).total_seconds() / \
                               (now - degrade_start + timedelta(seconds=1)).total_seconds()
                    ramp = (param_cfg["alarm_high"] - hi) * progress * 0.7
                else:
                    ramp = 0

                value = base + ramp + np.random.normal(0, noise)

                # Clamp to reasonable bounds
                if param_cfg.get("alarm_high"):
                    value = min(value, param_cfg["alarm_high"] * 1.05)
                if param_cfg.get("alarm_low"):
                    value = max(value, param_cfg["alarm_low"] * 0.95)

                in_alarm = False
                if param_cfg.get("alarm_high") and value > param_cfg["alarm_high"]:
                    in_alarm = True
                if param_cfg.get("alarm_low") and value < param_cfg["alarm_low"]:
                    in_alarm = True

                records.append({
                    "timestamp": current,
                    "machine_id": machine_name,
                    "line": machine_data["line"],
                    "parameter": param_name,
                    "value": round(value, 3),
                    "unit": param_cfg["unit"],
                    "alarm_high": param_cfg.get("alarm_high"),
                    "alarm_low": param_cfg.get("alarm_low"),
                    "in_alarm": in_alarm,
                    "shift": get_shift_from_hour(current.hour),
                })
            current += timedelta(hours=step_h)

    return pd.DataFrame(records)


# ── Cached session loader ────────────────────────────────────────────────────
_cache: dict = {}

def get_tsdpl_data(days: int = 90) -> dict:
    """Returns all TSDPL datasets, cached in memory."""
    global _cache
    if not _cache:
        downtime = generate_downtime_log(days)
        _cache = {
            "downtime_log":    downtime,
            "shift_roster":    generate_shift_roster_log(downtime),
            "pm_checklist":    generate_pm_checklist_log(days),
            "sensor_readings": generate_sensor_readings(days),
        }
    return _cache
