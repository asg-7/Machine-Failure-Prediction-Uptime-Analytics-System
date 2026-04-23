# Machine Failure Prediction & Uptime Analytics System
## Complete Project Revision — v1.0 → v2.0

**Project:** Machine Failure Prediction & Uptime Analytics System  
**Plant:** TSDPL Kalinganagar, Jajpur Road, Odisha  
**Stack:** Python · Pandas · NumPy · scikit-learn · Plotly · Streamlit  
**Last Updated:** April 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Version History Summary](#2-version-history-summary)
3. [v1.0 — Initial Build](#3-v10--initial-build)
4. [v1.1 — Bug Fix: Timestamp Parsing](#4-v11--bug-fix-timestamp-parsing)
5. [v2.0 — TSDPL Kalinganagar Edition](#5-v20--tsdpl-kalinganagar-edition)
6. [Complete File Structure](#6-complete-file-structure)
7. [Module Reference](#7-module-reference)
8. [Data Contracts](#8-data-contracts)
9. [Configuration Reference](#9-configuration-reference)
10. [How to Run](#10-how-to-run)
11. [Known Limitations & Future Work](#11-known-limitations--future-work)

---

## 1. Project Overview

A lightweight, locally-runnable plant maintenance dashboard that moves operations from **reactive** to **predictive** maintenance. Built for plant engineers, maintenance teams, and operations managers who need actionable intelligence without heavy cloud infrastructure or complex ML pipelines.

**Core capabilities:**
- Upload any CSV/Excel time-series of machine UP/DOWN status
- Compute uptime, downtime, efficiency percentages
- Detect failure patterns and time-of-day trends
- Predict time-to-failure (TTF) and assign risk scores using moving averages + linear regression
- TSDPL-specific: shift-based analytics, PM checklist, sensor scorecards, month-over-month comparison

---

## 2. Version History Summary

| Version | Date | Description |
|---------|------|-------------|
| v1.0 | Initial | 5-tab generic dashboard — data upload, uptime engine, failure detection, TTF prediction, drilldown |
| v1.1 | Patch | Fixed `pd.to_datetime()` deprecation (`infer_datetime_format` removed in Pandas 2.x) |
| v2.0 | Current | TSDPL Kalinganagar edition — 5 new tabs, 4 new modules, 11 machines, 22 failure codes, shift roster, PM checklist, health scorecard, MoM comparison |

---

## 3. v1.0 — Initial Build

### What Was Built

A 5-tab Streamlit application satisfying the original PRD. Generic — works with any plant's CSV data.

### Files Created

```
machine_failure_app/
├── app.py                      (original 5-tab version)
├── requirements.txt
├── generate_sample_data.py
├── sample_data.csv             (auto-generated, 5 machines, 60 days)
├── utils/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── analytics.py
│   ├── predictor.py
│   └── charts.py
└── components/
    ├── __init__.py
    └── ui_components.py
```

### Tab Layout — v1.0

| Tab | Title | Content |
|-----|-------|---------|
| 1 | 🏠 Overview | KPI cards, alert banners, uptime vs downtime chart, risk ranking chart, summary table |
| 2 | 📈 Uptime Analysis | Stacked bar chart, daily trend line, detailed uptime table |
| 3 | 💥 Failure Patterns | Frequency bar chart, hour-of-day chart, failure event log |
| 4 | 🔮 Predictions & Risk | Risk cards per machine, TTF bar chart, maintenance planning insights |
| 5 | 🔬 Machine Drilldown | Sensor trend chart, anomaly score, per-machine failure log, raw data preview |

### Sidebar — v1.0

- CSV / Excel file uploader
- **🎲 Load Demo Data** button (generates 6 machines, 45-day synthetic dataset)
- Dataset info panel (record count, date range, sensor availability)
- Machine multiselect filter (applied across all tabs)

---

### `utils/data_loader.py` — v1.0

**Purpose:** File upload handling, validation, and preprocessing pipeline.

**Constants:**
```python
REQUIRED_COLS  = {"timestamp", "machine_id", "status"}
OPTIONAL_COLS  = {"temperature", "load", "vibration"}
VALID_STATUSES = {"UP", "DOWN"}
```

**Functions:**

| Function | Signature | Description |
|----------|-----------|-------------|
| `load_data` | `(uploaded_file) → (DataFrame\|None, str\|None)` | Reads CSV or Excel from Streamlit uploader. Returns `(df, error)` tuple — error is `None` on success. |
| `validate_and_preprocess` | `(df) → (DataFrame\|None, str\|None)` | Normalises column names to lowercase, parses timestamp, uppercases status, coerces sensor columns to numeric, drops null-critical rows silently. |
| `get_data_summary` | `(df) → dict` | Returns `{total_records, machines, date_range, has_temperature, has_load, has_vibration}` for sidebar display. |

**Validation rules:**
1. All three required columns must be present (case-insensitive match after strip)
2. `timestamp` must be parseable by `pd.to_datetime()`
3. `status` values must be strictly `UP` or `DOWN` after uppercasing
4. Optional sensor columns are created as `NaN` if absent; coerced to numeric if present
5. Rows with null `timestamp`, `machine_id`, or `status` are silently dropped

---

### `utils/analytics.py` — v1.0

**Purpose:** Core uptime/downtime engine and failure pattern detection. Pure Pandas — no ML.

**Functions:**

| Function | Returns | Description |
|----------|---------|-------------|
| `compute_uptime_downtime(df)` | `DataFrame` indexed by `machine_id` | Per-machine: `total_records`, `up_count`, `down_count`, `uptime_pct`, `downtime_pct`, `uptime_hours`, `downtime_hours`. Hour estimates use median inter-record interval × record count. |
| `extract_failure_events(df)` | `DataFrame` | Detects UP→DOWN transitions per machine. Columns: `machine_id`, `failure_time`, `runtime_before_failure_hours`, `hour_of_day`, `day_of_week`. Resets `last_up_time` on each DOWN event to avoid double-counting. |
| `compute_failure_patterns(failure_events)` | `DataFrame` indexed by `machine_id` | Aggregates `failure_count`, `avg_runtime_h`, `std_runtime_h`, `min_runtime_h`, `max_runtime_h`, `most_common_failure_hour`. Returns empty DataFrame if no events. |
| `compute_hourly_failure_trend(failure_events)` | `DataFrame` | Failure count by hour-of-day (0–23), always 24 rows via `reindex`. |
| `compute_daily_uptime(df)` | `DataFrame` | Daily uptime percentage per machine. Columns: `machine_id`, `date`, `uptime_pct`. Used for the daily trend line chart. |

---

### `utils/predictor.py` — v1.0

**Purpose:** Time-to-failure prediction and 0–100 risk scoring using simple interpretable models.

**Private helpers:**

| Function | Returns | Description |
|----------|---------|-------------|
| `_time_since_last_failure(df_machine)` | `float\|None` | Hours from most recent DOWN event to last record. |
| `_current_run_hours(df_machine)` | `float` | Walks backwards through sorted records until first DOWN, accumulates continuous UP duration. |

**Public functions:**

| Function | Returns | Description |
|----------|---------|-------------|
| `predict_machine(failure_events_machine, df_machine, window=5)` | `dict` | Single-machine prediction. Returns keys: `machine_id`, `failure_count`, `avg_runtime_h`, `predicted_ttf_hours`, `current_run_hours`, `remaining_ttf_hours`, `risk_label`, `risk_value`, `confidence`. |
| `predict_all_machines(df, failure_events)` | `DataFrame` | Runs `predict_machine` for all unique `machine_id` values, returns sorted by `risk_value` descending. |
| `compute_sensor_anomaly_score(df_machine)` | `float` | Z-score deviation of recent 10% of UP readings vs baseline. Capped at 100. Returns 0 if sensors unavailable or fewer than 20 UP records. |

**Prediction algorithm detail:**

```
Step 1: Moving Average TTF
  recent_window = last min(5, n) inter-failure runtimes
  ma_ttf = mean(recent_window)

Step 2: Linear Regression TTF
  X = failure index [0..n-1], y = runtime_before_failure_hours
  lr_ttf = model.predict([n])  ← predict next interval
  lr_ttf floored at 1.0 hours

Step 3: Weighted Combination
  R² of regression → regression weight w_lr = clamp(R², 0.2, 0.7)
  combined_ttf = (1 - w_lr) × ma_ttf + w_lr × lr_ttf

Step 4: Remaining TTF
  remaining_ttf = combined_ttf - current_run_hours

Step 5: Risk Score (0–100)
  ratio = current_run_hours / combined_ttf
  risk_value = clamp(ratio × 100, 0, 100)
  + CV penalty: += cv × 15  (where cv = std/mean of runtimes)
  risk_value capped at 100

Step 6: Risk Label
  risk_value ≥ 70 → "High"
  risk_value ≥ 40 → "Medium"
  risk_value  < 40 → "Low"
```

**Confidence levels:**
- `High` if R² > 0.5
- `Medium` if R² > 0.2
- `Low` otherwise (including insufficient data)

---

### `utils/charts.py` — v1.0

**Purpose:** All Plotly visualisations for the generic tabs. Each function returns a `go.Figure` — never calls `st.plotly_chart()` directly (separation of concerns).

| Function | Chart Type | Key Parameters |
|----------|-----------|----------------|
| `chart_uptime_downtime(uptime_df)` | Stacked bar | X: machine, Y: %, Series: Uptime (green) / Downtime (red) |
| `chart_daily_uptime_trend(daily_uptime, selected_machines)` | Line chart | X: date, Y: uptime%, Color: machine. Dashed 90% target line. |
| `chart_failure_frequency(failure_patterns)` | Horizontal bar | X: count, Y: machine, sorted ascending |
| `chart_hourly_failure_trend(hourly_df)` | Vertical bar | X: hour-of-day (00:00–23:00), Y: failure count |
| `chart_risk_ranking(predictions)` | Horizontal bar | X: risk score 0–100, Y: machine, colour-coded by label. Dotted thresholds at 40 and 70. |
| `chart_ttf_prediction(predictions)` | Stacked horizontal bar | Segment 1: current_run_hours (grey), Segment 2: remaining_ttf_hours (risk colour) |
| `chart_sensor_trend(df_machine, sensor, machine_id)` | Scatter + line | UP points in green line, DOWN points as red markers, 20-pt rolling average in purple dashes |

---

### `components/ui_components.py` — v1.0

**Purpose:** Reusable HTML/CSS Streamlit components. All render via `st.markdown(..., unsafe_allow_html=True)`.

| Function | Description |
|----------|-------------|
| `risk_badge_html(label)` | Returns inline HTML `<span>` badge coloured by risk label. |
| `metric_card(title, value, delta, color)` | Left-bordered card with title, large value, optional delta line. Default colour `#6366F1`. |
| `alert_banner(message, level)` | Full-width coloured banner. Levels: `info` (blue), `warning` (amber), `error` (red), `success` (green). Supports HTML in message. |
| `render_prediction_card(row)` | 3-column grid card for a single machine prediction. Shows risk badge, remaining TTF, predicted cycle, failure count, current run, confidence. |
| `render_alert_machines(predictions)` | Reads full predictions DataFrame. Renders error banner for High risk machines, warning banner for Medium. Success banner if all Low. |
| `section_header(title, subtitle)` | H3 + optional subtitle paragraph with consistent spacing. |

---

### `generate_sample_data.py` — v1.0

**Purpose:** Standalone script to generate realistic synthetic UP/DOWN time-series CSV.

**Usage:**
```bash
python generate_sample_data.py          # creates sample_data.csv (5 machines, 60 days)
```

**Parameters:**
- `n_machines` — number of machines (default 5)
- `days` — observation window (default 60)
- `output_path` — output CSV path

**Realism features:**
- Each machine has a randomised base failure probability (`0.01–0.06` per hour)
- Downtime durations: log-normal distribution, `60–480` minutes
- Temperature, load, vibration: Gaussian noise around per-machine baselines
- Random seed `42` for reproducibility

---

## 4. v1.1 — Bug Fix: Timestamp Parsing

### Problem

```
AssertionError: Loader error: Could not parse 'timestamp' column.
```

Pandas 2.x removed the `infer_datetime_format` parameter from `pd.to_datetime()`. The v1.0 code passed it explicitly.

### Fix — `utils/data_loader.py`

```python
# BEFORE (v1.0) — raises TypeError in Pandas 2.x
df["timestamp"] = pd.to_datetime(df["timestamp"], infer_datetime_format=True)

# AFTER (v1.1) — works across Pandas 2.x
df["timestamp"] = pd.to_datetime(df["timestamp"])
```

`pd.to_datetime()` already infers format automatically since Pandas 2.0; the parameter was redundant.

**Files changed:** `utils/data_loader.py` (1 line)

---

## 5. v2.0 — TSDPL Kalinganagar Edition

### What Changed

v2.0 is a domain-specific extension layered on top of v1.0/v1.1. The original 5 tabs are **unchanged and fully operational**. Five new tabs were added targeting TSDPL Kalinganagar's three processing lines using a separate data pipeline that does not interfere with the generic upload path.

### New Files

```
machine_failure_app/
└── utils/
    ├── tsdpl_constants.py      ← new
    ├── tsdpl_demo_data.py      ← new
    ├── tsdpl_analytics.py      ← new
    └── tsdpl_charts.py         ← new
```

`app.py` was fully rewritten to support the dual-mode sidebar and 10-tab layout while preserving the original render functions unchanged inside `render_generic()`.

### New Sidebar Buttons

| Button | Action |
|--------|--------|
| **🎲 Generic Demo** | Same as v1.0 — 6 machines, 45 days, UP/DOWN format |
| **🏭 TSDPL Demo** | Generates 90-day TSDPL-specific downtime log, shift roster, PM log, sensor readings |

Both datasets can be loaded simultaneously. Generic tabs 1–5 respond to Generic Demo. TSDPL tabs 6–10 respond to TSDPL Demo.

---

### New Tab Layout — v2.0

| Tab | Title | Core Feature |
|-----|-------|-------------|
| 6 | 📋 Shift Roster | TBL_SHIFT_ROSTER_LOG with incident overlay, master roster viewer, XLOOKUP formula |
| 7 | 📊 Shift Analytics | Tornado chart, MTBF/MTTR clustered bars, OEE pivot, night shift root-cause insight |
| 8 | 🔧 PM Checklist | LOTO compliance banner, overdue/completed colour rows, PM status chart, incident timeline |
| 9 | 🌡️ Health Scorecard | Sensor alarm heatmap, operational limits table, parameter trend drilldown |
| 10 | 📅 Month-over-Month | MoM grid chart, MTBF scorecard cards, DAX + Excel formula reference, failure code glossary |

---

### `utils/tsdpl_constants.py` — v2.0

**Purpose:** Single source of truth for all TSDPL domain data. Everything else imports from here — no hardcoded values in other modules.

#### Shift Configuration

```python
SHIFTS = {
    "A - Morning":   {"start": "06:00", "end": "14:00"},
    "B - Afternoon": {"start": "14:00", "end": "22:00"},
    "C - Night":     {"start": "22:00", "end": "06:00"},
}
```

**`get_shift_from_hour(hour: int) → str`** — maps any integer hour (0–23) to a shift code string.

#### Machine Registry

11 machines across 3 lines. Each entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `line` | str | `"HR-CTL Line"` / `"HR Slitting Line"` / `"CR Processing Facility"` |
| `zone` | str | Entry / Mid / Exit zone label |
| `criticality` | str | `"Critical"` / `"High"` / `"Medium"` |
| `params` | dict | Sensor parameter configs (see below) |
| `pm_tasks` | list | Preventive maintenance tasks (see below) |

**Criticality breakdown:**

| Machine | Line | Criticality |
|---------|------|-------------|
| Cassette Leveller (HR-CTL) | HR-CTL | Critical |
| Slitter Head (HR Slitting) | HR Slitting | Critical |
| Skin Pass Mill (CR) | CR | Critical |
| Uncoiler (HR-CTL) | HR-CTL | High |
| Flying Shear (HR-CTL) | HR-CTL | High |
| Recoiler (HR Slitting) | HR Slitting | High |
| Robotic Tool Setup (CR 2024) | CR | High |
| Air Cushion Stacker (HR-CTL) | HR-CTL | Medium |
| Tension Bridle (HR Slitting) | HR Slitting | Medium |
| Scrap Chopper (HR Slitting) | HR Slitting | Medium |
| Inspection & Parting Line (CR) | CR | Medium |

**Sensor parameter config format:**
```python
"Roller Bearing Temp (°C)": {
    "unit": "°C",
    "alarm_high": 75,
    "alarm_low": None,
    "normal_range": (20, 65),
}
```

27 total sensor parameters monitored across 11 machines.

**PM task config format:**
```python
{
    "task": "Leveller Roll Scale/Buildup Inspection",
    "frequency": "Shift",
    "category": "Mechanical",
    "loto": True,          # optional — triggers LOTO banner in Tab 8
}
```

30 total PM tasks. 6 require LOTO. Frequency options: `Per Coil`, `Per Coil Batch`, `Shift`, `Daily`, `Weekly`, `Monthly`, `Quarterly`.

#### Failure Code Registry

22 failure codes across 5 categories:

| Category | Codes | Example |
|----------|-------|---------|
| Mechanical | ME-01 to ME-09 | ME-01: Leveller Roll Spalling |
| Electrical | EE-01 to EE-05 | EE-04: Flying Shear Encoder Fault |
| Hydraulic | HY-01 to HY-03 | HY-02: Mandrel Expansion Slippage |
| Process | PR-01 to PR-03 | PR-01: Strip Breakage |
| Planned | PL-01 to PL-02 | PL-01: Planned Knife Change |

Each code: `{"desc": str, "category": str, "machine": str}`.

#### Master Roster

24 personnel, 3 shifts × 8 per shift:

| Role | Count per Shift | Description |
|------|----------------|-------------|
| Operator | 6 | One per zone per line |
| Supervisor | 1 | Covers all lines |
| Maint. Tech | 1 | On-call for all lines |

---

### `utils/tsdpl_demo_data.py` — v2.0

**Purpose:** Generates all four TSDPL-specific demo datasets. Cached in module-level `_cache` dict to avoid regenerating on every Streamlit rerun.

**Entry point:**
```python
get_tsdpl_data(days=90) → {
    "downtime_log":    DataFrame,
    "shift_roster":    DataFrame,
    "pm_checklist":    DataFrame,
    "sensor_readings": DataFrame,
}
```

#### `generate_downtime_log(days=90)` → DataFrame

Columns: `timestamp`, `machine_id`, `line`, `zone`, `shift`, `failure_code`, `failure_category`, `failure_desc`, `downtime_minutes`, `repaired_by`, `supervisor`, `remarks`

**Realism features:**
- Each machine has a base daily failure rate (`0.05–0.25`)
- Shift-weighted failure multipliers per machine (defined in `MACHINE_SHIFT_FAILURE_WEIGHTS`):
  - Night shift multiplier for Slitter Head: **2.0×** (encodes domain knowledge)
  - Night shift for Cassette Leveller: **1.6×**
  - Morning shift for Robotic Setup: **1.5×** (setup activity highest in morning)
- Downtime duration: log-normal, clamped to `5–480` minutes
- Failure codes randomly selected from machine-relevant subset of the registry
- Repaired by / Supervisor auto-populated from Master Roster by shift match

#### `generate_shift_roster_log(downtime_log)` → DataFrame

Creates TBL_SHIFT_ROSTER_LOG. One row per `date × shift × line × zone`.

Columns: `date`, `shift`, `line`, `zone`, `operator_name`, `supervisor_name`, `maint_tech_oncall`, `incident_logged`, `incident_timestamp`, `failure_code`

Logic: for each slot, queries `downtime_log` for matching `timestamp range + line + zone`. Sets `incident_logged = "Y"` if any incidents found and populates `incident_timestamp` and `failure_code` from the earliest match.

#### `generate_pm_checklist_log(days=90)` → DataFrame

Columns: `machine_id`, `task`, `category`, `frequency`, `scheduled_date`, `completed_date`, `status`, `technician`, `loto_required`, `remarks`

Logic: iterates every task × scheduled occurrence in the window. 12% of tasks get a random delay (`2 hrs` to `freq_hours`). Delayed tasks become `"Overdue"` with `"Completed with delay"` remark.

#### `generate_sensor_readings(days=90)` → DataFrame

Columns: `timestamp`, `machine_id`, `line`, `parameter`, `value`, `unit`, `alarm_high`, `alarm_low`, `in_alarm`, `shift`

Step: 4-hour intervals. For each parameter: Gaussian noise around midpoint of normal range. In the last 20% of the time window, a linear degradation ramp pushes values toward the `alarm_high` threshold (simulating wear). Alarm flag set where value exceeds alarm bounds.

---

### `utils/tsdpl_analytics.py` — v2.0

**Purpose:** All TSDPL-specific KPI calculations. Pure Pandas/NumPy — no Streamlit imports.

| Function | Returns | Description |
|----------|---------|-------------|
| `compute_mtbf_mttr(downtime_log, observation_hours)` | DataFrame | Per-machine: `failure_count`, `total_downtime_min`, `MTTR_min`, `MTBF_hours`, `availability_pct`. Observation window defaults to full log span. |
| `compute_shift_mtbf_mttr(downtime_log)` | DataFrame | Same metrics grouped by `(machine_id, shift)`. Uses `dates × 8h` as per-shift observation window. |
| `compute_oee_loss(downtime_log, total_shift_hours=8.0)` | DataFrame | Per `(machine_id, shift)`: `oee_avail_loss_pct`, `mech_downtime_min`, `elec_downtime_min`, `hydraulic_downtime_min`, `process_downtime_min`. |
| `compute_mom_comparison(downtime_log)` | DataFrame | Per machine: `this/last_month_failures`, `this/last_month_downtime_min`, `mtbf_this/last_month_h`, `trend` (Improving/Worsening/Stable), `top_failure_mode`, `delta_downtime_min`. |
| `compute_sensor_scorecard(sensor_df, lookback_hours=24)` | DataFrame | Per `(machine_id, parameter)`: `current_value`, `unit`, `alarm_high/low`, `status` (Normal/WARNING/ALARM), `trend` (↑ Rising / ↓ Falling / → Stable from 6-point slope). |

**MoM trend thresholds:**
- `Improving` if `mtbf_this / mtbf_last > 1.05`
- `Worsening` if `mtbf_this / mtbf_last < 0.95`
- `Stable` otherwise

---

### `utils/tsdpl_charts.py` — v2.0

**Purpose:** All Plotly visualisations for TSDPL tabs 6–10.

| Function | Chart Type | Description |
|----------|-----------|-------------|
| `chart_shift_tornado(shift_mtbf, machines)` | Diverging horizontal bar | Night (C) on negative X-axis (left), Morning (A) and Afternoon (B) on positive X-axis (right). Machine names on Y-axis. |
| `chart_mtbf_by_shift(shift_mtbf, metric)` | Grouped vertical bar | X: machine, Y: selected metric, grouped by shift. Metric switchable between `MTBF_hours`, `MTTR_min`, `total_downtime_min`. |
| `chart_sensor_heatmap(scorecard_df)` | Heatmap + emoji overlays | Rows: machines, Columns: parameters. Colour scale: green (Normal) → yellow (WARNING) → red (ALARM). Emoji overlay: ✅ / ⚠️ / 🚨. |
| `chart_param_trend(sensor_df, machine, param)` | Scatter + line | Raw values, 6-point rolling average, alarm_high and alarm_low as dashed horizontal lines. |
| `chart_failure_category_donut(downtime_log, machine)` | Donut pie | Downtime minutes by failure category. Optionally filtered to single machine. |
| `chart_mom_grid(mom_df)` | 3×N subplot bar grid | Each subplot: two bars (last month grey, this month colour-coded by trend). |
| `chart_pm_status(pm_df)` | Stacked vertical bar | X: machine, Y: task count, stacked by status (green/red/purple). |
| `chart_incident_timeline(downtime_log, days_back=14)` | Gantt-style scatter lines | Each incident: a thick coloured line from start to `start + downtime_minutes`. Colour by failure category. Hover shows code, description, duration, shift. |

**Colour maps:**
```python
SHIFT_COLORS = {
    "A - Morning":   "#6366F1",  # indigo
    "B - Afternoon": "#F59E0B",  # amber
    "C - Night":     "#1E293B",  # dark slate
}
TREND_COLOR = {
    "Improving": "#22C55E",
    "Worsening": "#EF4444",
    "Stable":    "#94A3B8",
}
```

---

### `app.py` — v2.0 Changes

The original render logic was refactored into two isolated functions:

```python
def render_generic(df_all):
    # Handles tabs 1–5 using st.session_state.df
    # Unchanged logic from v1.0 wrapped in a function

def render_tsdpl(tsdpl):
    # Handles tabs 6–10 using st.session_state.tsdpl_data
    # New TSDPL-specific logic
```

**Execution flow:**
```python
# Bottom of app.py
if st.session_state.df is not None:
    render_generic(st.session_state.df)
else:
    # show info banners on tabs 1–5

if st.session_state.tsdpl_loaded:
    render_tsdpl(st.session_state.tsdpl_data)
else:
    # show info banners on tabs 6–10
```

This means both data modes can be active simultaneously, and loading one does not reset the other.

**Tab 6 — Shift Roster additions:**
- `st.expander` master roster viewer with copy-paste XLOOKUP formula:
  ```excel
  =XLOOKUP(1,
    (MasterRoster[Shift]=[@Shift])*(MasterRoster[Line]=[@Line])
    *(MasterRoster[Zone]=[@Zone])*(MasterRoster[Role]="Operator"),
    MasterRoster[Name], "Standby")
  ```
- Three-way filter: Line, Shift, Incident flag
- Row-level red highlighting for incident shifts
- Incident count per operator aggregation table

**Tab 8 — PM Checklist additions:**
- LOTO compliance banner fires when `loto_required=True AND status="Overdue"`, citing TSDPL SOP-SAFE-04
- `st.expander` with ready-to-use Excel formulas:
  - Conditional formatting formula for overdue detection
  - Machine Status data validation dropdown list
  - MTBF array formula
- Status icons mapped: `✅ Completed`, `🔴 Overdue`, `📅 Scheduled`

**Tab 10 — Month-over-Month additions:**
- DAX measures for Power BI (This Month, Last Month, MoM Trend Arrow)
- Excel array formulas for rolling 30-day and prior 30-day windows
- Full failure code glossary (ME/EE/HY/PR/PL series) with category colour coding

---

## 6. Complete File Structure

```
machine_failure_app/
│
├── app.py                          # Main entry point — 10-tab dual-mode dashboard
├── requirements.txt                # Python dependencies
├── generate_sample_data.py         # Generic synthetic data generator
├── sample_data.csv                 # Pre-generated (5 machines, 60 days)
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py              # Upload, validate, preprocess (generic)
│   ├── analytics.py                # Uptime engine + failure pattern detection (generic)
│   ├── predictor.py                # TTF prediction + risk scoring (generic)
│   ├── charts.py                   # 7 Plotly charts for tabs 1–5 (generic)
│   ├── tsdpl_constants.py          # TSDPL domain data — machines, codes, roster, limits
│   ├── tsdpl_demo_data.py          # TSDPL synthetic data generators
│   ├── tsdpl_analytics.py          # MTBF, MTTR, OEE, MoM, sensor scorecard
│   └── tsdpl_charts.py             # 8 Plotly charts for tabs 6–10 (TSDPL)
│
└── components/
    ├── __init__.py
    └── ui_components.py            # Reusable Streamlit HTML/CSS components
```

**Line count by file:**

| File | Lines |
|------|-------|
| `app.py` | 601 |
| `utils/tsdpl_charts.py` | 416 |
| `utils/tsdpl_constants.py` | 272 |
| `utils/tsdpl_demo_data.py` | 303 |
| `utils/tsdpl_analytics.py` | 237 |
| `utils/charts.py` | 260 |
| `utils/predictor.py` | 199 |
| `utils/analytics.py` | 166 |
| `utils/data_loader.py` | 93 |
| `components/ui_components.py` | 148 |
| **Total** | **~2,700** |

---

## 7. Module Reference

### Import Map

```
app.py
 ├── utils.data_loader        → load_data, get_data_summary
 ├── utils.analytics          → compute_uptime_downtime, extract_failure_events,
 │                               compute_failure_patterns, compute_hourly_failure_trend,
 │                               compute_daily_uptime
 ├── utils.predictor          → predict_all_machines, compute_sensor_anomaly_score
 ├── utils.charts             → chart_uptime_downtime, chart_daily_uptime_trend,
 │                               chart_failure_frequency, chart_hourly_failure_trend,
 │                               chart_risk_ranking, chart_ttf_prediction, chart_sensor_trend
 ├── components.ui_components → metric_card, alert_banner, render_prediction_card,
 │                               render_alert_machines, section_header, risk_badge_html
 ├── utils.tsdpl_constants    → MACHINES, MACHINE_NAMES, FAILURE_CODES, LINES,
 │                               SHIFT_CODES, MASTER_ROSTER, get_shift_from_hour
 ├── utils.tsdpl_demo_data    → get_tsdpl_data
 ├── utils.tsdpl_analytics    → compute_mtbf_mttr, compute_shift_mtbf_mttr,
 │                               compute_oee_loss, compute_mom_comparison,
 │                               compute_sensor_scorecard
 └── utils.tsdpl_charts       → chart_shift_tornado, chart_mtbf_by_shift,
                                 chart_sensor_heatmap, chart_param_trend,
                                 chart_failure_category_donut, chart_mom_grid,
                                 chart_pm_status, chart_incident_timeline
```

### Caching Strategy

Both render functions use `@st.cache_data` with a manual hash key:

```python
# Generic (tabs 1–5)
df_hash = (len(df), tuple(sorted(selected_machines)), df["timestamp"].max().isoformat())

# TSDPL (tabs 6–10)
dl_hash = len(downtime_log)
```

TSDPL demo data itself is cached at module level in `tsdpl_demo_data._cache` (plain dict) so the 90-day generation runs only once per session regardless of reruns.

---

## 8. Data Contracts

### Generic Input Schema (CSV/Excel upload)

| Column | Required | Type | Constraints |
|--------|----------|------|-------------|
| `timestamp` | ✅ | datetime string | Any standard format parseable by `pd.to_datetime()` |
| `machine_id` | ✅ | string | Any non-null identifier |
| `status` | ✅ | string | Must be `UP` or `DOWN` (case-insensitive) |
| `temperature` | Optional | numeric | Any float; coerced to NaN on invalid |
| `load` | Optional | numeric | Any float; coerced to NaN on invalid |
| `vibration` | Optional | numeric | Any float; coerced to NaN on invalid |

### TSDPL Downtime Log Schema

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime | Failure event time |
| `machine_id` | str | One of 11 TSDPL machine names |
| `line` | str | Processing line |
| `zone` | str | Entry / Mid / Exit zone |
| `shift` | str | A - Morning / B - Afternoon / C - Night |
| `failure_code` | str | ME-xx / EE-xx / HY-xx / PR-xx / PL-xx |
| `failure_category` | str | Mechanical / Electrical / Hydraulic / Process / Planned |
| `failure_desc` | str | Human-readable description |
| `downtime_minutes` | int | Duration of downtime |
| `repaired_by` | str | Maintenance technician name |
| `supervisor` | str | Shift supervisor name |
| `remarks` | str | Free text |

### Prediction Output Schema

| Column | Type | Description |
|--------|------|-------------|
| `machine_id` | str | Machine identifier |
| `failure_count` | int | Total failures in dataset |
| `avg_runtime_h` | float | Average runtime between failures |
| `predicted_ttf_hours` | float\|None | Predicted full cycle duration |
| `current_run_hours` | float | Hours UP since last failure |
| `remaining_ttf_hours` | float\|None | Predicted hours until next failure |
| `risk_label` | str | `Low` / `Medium` / `High` / `Unknown` |
| `risk_value` | int | 0–100 continuous risk score |
| `confidence` | str | `High` / `Medium` / `Low` / `Low (insufficient data)` |

---

## 9. Configuration Reference

### PM Frequency → Hours Map

| Frequency Label | Hours |
|----------------|-------|
| Per Coil | 8 |
| Per Coil Batch | 16 |
| Shift | 8 |
| Daily | 24 |
| Weekly | 168 |
| Monthly | 720 |
| Quarterly | 2,160 |

### Machine Status Dropdown Options

```
Running
Planned Stop
Breakdown - Mechanical
Breakdown - Electrical
Breakdown - Hydraulic
Breakdown - Process
PM In Progress
Idle / No Production
```

### Risk Score Thresholds

| Score Range | Label | Colour |
|------------|-------|--------|
| 0–39 | Low | `#22C55E` (green) |
| 40–69 | Medium | `#F59E0B` (amber) |
| 70–100 | High | `#EF4444` (red) |

---

## 10. How to Run

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Generate sample CSV for manual upload
python generate_sample_data.py

# 3. Launch dashboard
streamlit run app.py
```

App opens at **http://localhost:8501**

### Quick Start Guide

| Goal | Action |
|------|--------|
| Explore generic prediction features | Click **🎲 Generic Demo** → use tabs 1–5 |
| Explore TSDPL plant dashboard | Click **🏭 TSDPL Demo** → use tabs 6–10 |
| Upload real plant data (UP/DOWN format) | Use sidebar uploader → tabs 1–5 respond automatically |
| View who was on duty at a failure | Tab 6 → filter Incidents: "Y - Only Incidents" |
| See which shift causes most downtime | Tab 7 → Tornado Chart |
| Find overdue LOTO tasks | Tab 8 → red LOTO banner (if any) + status filter "Overdue" |
| Check which sensor is drifting | Tab 9 → Heatmap → Parameter Trend Drilldown |
| Present to management | Tab 10 → MTBF scorecard cards |

---

## 11. Known Limitations & Future Work

### Current Limitations

- **TTF model requires ≥2 failure events** per machine to produce a prediction. Machines with 0 or 1 failures get a static fallback risk score (10 or 35).
- **Long-runtime machines under-risk-scored:** if a machine has been UP for a very long time with no historical failures in the data, the risk score will read Low even though it may be overdue. A "no-failure-but-long-runtime" penalty is not yet implemented.
- **Sensor anomaly score is computed but not fed back into the risk score.** The two signals (runtime-based risk and sensor-based anomaly) are shown separately but not combined.
- **Shift roster is generated, not editable.** There is no in-app form to log actual shift assignments or mark a repair as complete.
- **Single-file upload only.** Each upload replaces the previous dataset. Incremental append (deduplicated by `timestamp + machine_id`) is not yet supported.

### Planned Improvements

| Feature | Priority | Complexity |
|---------|----------|-----------|
| Sensor-weighted risk score (merge anomaly score into risk_value) | High | Low |
| Maintenance log form (log repair, reset current_run counter) | High | Medium |
| Multi-file incremental append with deduplication | Medium | Medium |
| MTBF / MTTR export to Excel with formatted report | Medium | Low |
| Date range sidebar filter for all analyses | Medium | Low |
| Failure reason tagging (`failure_reason` optional column) | Low | Low |
| Comparative period selector (any two date windows, not just calendar months) | Low | Medium |
| Power BI `.pbix` template file generation | Low | High |

---

*Document generated from codebase audit — TSDPL Kalinganagar Maintenance Dashboard v2.0*
