# 🏭 Machine Failure Prediction & Uptime Analytics
**An enterprise-grade predictive maintenance dashboard for plant engineers and operations teams**

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32.2-red) ![Pandas](https://img.shields.io/badge/Pandas-2.0.3-green) ![scikit--learn](https://img.shields.io/badge/scikit--learn-1.3.0-orange) ![Plotly](https://img.shields.io/badge/Plotly-5.18.0-purple) ![License: Proprietary](https://img.shields.io/badge/License-Proprietary-lightgrey)

**Plant:** TSDPL Kalinganagar, Jajpur Road, Odisha &nbsp;|&nbsp; **Last Updated:** May 2026

> Moves plant operations from reactive to predictive maintenance — no cloud infrastructure, no complex ML pipelines.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Version History](#version-history)
3. [What's New in v3.0](#whats-new-in-v30)
4. [Quick Start](#quick-start)
5. [Dashboard Navigation](#dashboard-navigation)
6. [File Structure](#file-structure)
7. [Input Data Format](#input-data-format)
8. [How It Works](#how-it-works)
9. [Module Reference](#module-reference)
10. [Configuration Reference](#configuration-reference)
11. [UI and Design System](#ui-and-design-system)
12. [Roadmap](#roadmap)
13. [Known Limitations](#known-limitations)

---

## 🔍 Overview

A dual-mode **12-tab Streamlit dashboard** built for plant engineers, maintenance technicians, and operations managers. Upload any CSV/Excel of machine UP/DOWN status and get actionable fleet intelligence immediately — no data science background required.

| Capability | Details |
|---|---|
| 📂 Data ingestion | Upload any CSV/Excel time-series of machine UP/DOWN status |
| 🧹 Messy file normalizer | Auto-detects header row, maps alias columns, handles mixed date formats & duration units |
| 📊 Uptime engine | Compute uptime %, downtime hours, and efficiency per machine |
| 🔍 Failure detection | Detect UP→DOWN transitions, time-of-day trends, and flapping behaviour |
| 🔮 TTF prediction | Predict Time-to-Failure and assign 0–100 risk scores via moving average + linear regression |
| 🏭 TSDPL-specific | Shift analytics, PM checklist, sensor scorecards, month-over-month comparison, composite Health Score |
| 💚 Advanced failure modes | Performance degradation, intermittent flapping, and surface wear indices |
| 📊 QIP Analysis | Before/after MTBF·MTTR comparison with delta cards, grouped bar chart, and narrative verdict |
| 🧰 Equipment Health Intelligence | Per-equipment MTBF/MTTR vs configurable targets, composite severity scoring, Critical/Warning/Normal ranking |

---

## 📦 Version History

| Version | Highlights |
|---|---|
| v1.0 | 5-tab generic dashboard — upload, uptime, failure detection, TTF prediction, drilldown |
| v1.1 | Fixed `pd.to_datetime()` deprecation (`infer_datetime_format` removed in Pandas 2.x) |
| v2.0 | TSDPL Kalinganagar edition — 5 new tabs, 4 new modules, 11 machines, 22 failure codes, shift roster, PM checklist, health scorecard, MoM comparison |
| v2.1 | Dark high-contrast UI overhaul, advanced failure modes, Health Score tab, loading transitions |
| v2.2 | Real-world messy file normalizer (`utils/messy_loader.py`), QIP Analysis tab, security-hardened upload validation |
| v3.0 | Equipment MTBF/MTTR vs target thresholds, underperformer severity ranking, Health Scorecard extension, `config.toml` selectbox fix, nuclear-depth sidebar CSS |

---

## ✨ What's New in v3.0

### 🧰 Equipment Health & Underperformer Intelligence

A new analytics layer surfaces which equipment is failing to meet plant targets — no manual threshold tracking required.

**`EQUIPMENT_THRESHOLDS`** in `utils/tsdpl_constants.py` defines acceptable MTBF (min hours) and MTTR (max minutes) per equipment. **`UNDERPERFORMER_WEIGHTS`** controls the composite severity score: `mtbf_gap_pct` (0.45), `mttr_excess_pct` (0.35), `breakdown_count` (0.20). Change these values to update plant targets without touching any analytics code.

Two new analytics functions power this: `compute_equipment_mtbf_mttr()` derives per-equipment MTBF, MTTR, and availability directly from the Breakdown Excel file, while `flag_underperforming_equipment()` computes the composite severity score and assigns Critical / Warning / Normal health status.

The **Health Scorecard tab** now displays colour-coded MTBF/MTTR bars with target markers and a horizontal severity ranking chart whenever Breakdown Excel data is uploaded — no additional file needed.

### 🎨 Config & Theming Fix

`secondaryBackgroundColor` in `config.toml` changed from `#1A2C3E` to `#FFFFFF`. Streamlit injects this value as an inline style on every widget div — a dark value makes selectbox text invisible even with CSS `!important`. The sidebar stays dark navy via targeted CSS overrides with nuclear-depth `!important` rules on every inner element of the uploader dropzone.

> ⚠️ **Do not revert `secondaryBackgroundColor` to a dark value** — it will break main-area selectboxes. The sidebar is kept dark entirely through CSS.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd TSDPL-Kalinganagar-Dashboard

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard
streamlit run app_version2.py
```

App opens at `http://localhost:8501`

**`requirements.txt`:**
```
streamlit==1.32.2
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
plotly==5.18.0
openpyxl==3.1.2
```

> ⚠️ Python 3.11+ recommended. The app uses `str | None` union syntax (PEP 604).

### First-Time Use

1. **Upload data** via the left sidebar, **OR**
2. Click **🎲 Generic Demo** to load synthetic UP/DOWN data, **OR**
3. Click **🏭 TSDPL Demo** to load 90 days of plant-specific demo data.

### Sidebar Upload Options

| Section | File Type | Purpose |
|---|---|---|
| **📂 Upload Generic Data** | CSV / Excel | Standard `timestamp`, `machine_id`, `status` format |
| **🔬 Upload Real-World Data** | CSV / Excel | Messy exports with metadata rows, mixed headers, inconsistent dates |
| **⚙️ Maintenance Delay Analysis** | `.xlsx` (multi-file) | Breakdown sheets → also powers Equipment Health Scorecard |

---

## 🗺️ Dashboard Navigation

### Generic Tabs — work with any uploaded CSV/Excel

| Tab | Title | What you get |
|---|---|---|
| 1 | 🏠 Overview | KPI cards, alert banners, uptime vs downtime chart, risk ranking, summary table |
| 2 | 📈 Uptime Analysis | Stacked bar chart, daily trend line, detailed uptime table |
| 3 | 💥 Failure Patterns | Frequency bar chart, hour-of-day chart, failure event log |
| 4 | 🔮 Predictions & Risk | Risk cards per machine, TTF bar chart, maintenance planning insights |
| 5 | 🔬 Machine Drilldown | Sensor trend chart, anomaly score, per-machine failure log, raw data preview |

### TSDPL Tabs — Kalinganagar plant-specific

| Tab | Title | Core Feature |
|---|---|---|
| 6 | 📋 Shift Roster | TBL_SHIFT_ROSTER_LOG with incident overlay, master roster viewer, XLOOKUP formula |
| 7 | 📊 Shift Analytics | Tornado chart, MTBF/MTTR clustered bars, OEE pivot, night shift root-cause insight |
| 8 | 🔧 PM Checklist | LOTO compliance banner, overdue/completed colour rows, PM status chart, incident timeline |
| 9 | 🌡️ Health Scorecard | Sensor alarm heatmap, parameter trend drilldown, **equipment MTBF/MTTR vs targets, underperformer severity ranking** |
| 10 | 💚 Health Score | Composite 0–100 gauge per machine, sub-score breakdown table |
| 11 | 📅 Month-over-Month | MoM grid chart, MTBF scorecard cards, DAX + Excel formula reference, failure code glossary |
| 12 | 📊 QIP Analysis | Before/after MTBF/MTTR comparison with delta cards, grouped bar chart, narrative verdict |

### Quick-Find Guide

| Goal | Where to go |
|---|---|
| Explore generic prediction features | 🎲 Generic Demo → Tabs 1–5 |
| Explore TSDPL plant dashboard | 🏭 TSDPL Demo → Tabs 6–11 |
| Upload real plant data (UP/DOWN format) | Sidebar uploader → Tabs 1–5 respond automatically |
| Upload a messy real-world maintenance export | Sidebar → 🔬 Upload Real-World Data |
| Run a QIP before/after MTBF comparison | Tab 12 → QIP Analysis |
| View who was on duty at a failure | Tab 6 → filter Incidents: "Y - Only Incidents" |
| See which shift causes most downtime | Tab 7 → Tornado Chart |
| Find overdue LOTO tasks | Tab 8 → red LOTO banner + status filter "Overdue" |
| Check which sensor is drifting | Tab 9 → Heatmap → Parameter Trend Drilldown |
| See equipment MTBF vs plant targets | Tab 9 → Equipment Health section (requires Breakdown Excel upload) |
| View composite machine health | Tab 10 → Health Score gauges |
| Present MTBF scorecard to management | Tab 11 → MoM scorecard cards |

---

## 🗂️ File Structure

```
TSDPL-Kalinganagar-Dashboard/
│
├── .streamlit/
│   └── config.toml              # Global theme config (Tata Blue, secondaryBg=#FFFFFF)
│
├── app_version2.py              # 🚀 Main entry point — 12-tab Streamlit app
│
├── components/
│   └── ui_components.py         # Reusable UI (metric cards, alerts, prediction cards, health cards)
│
├── utils/
│   ├── analytics.py             # Generic uptime/downtime engine + failure pattern detection
│   ├── charts.py                # Plotly visualizations for generic data (tabs 1–5)
│   ├── data_loader.py           # CSV/Excel upload, validation, heuristic header search, fuzzy mapping
│   ├── messy_loader.py          # Real-world messy export normalizer (metadata rows, mixed dates)
│   ├── predictor.py             # TTF prediction engine (LinearRegression + moving average)
│   ├── breakdown_loader.py      # Breakdown Excel parser (handles \xa0, merged headers, pivot sheets)
│   ├── tsdpl_constants.py       # Domain constants, EQUIPMENT_THRESHOLDS, UNDERPERFORMER_WEIGHTS
│   ├── tsdpl_demo_data.py       # Synthetic data generator for TSDPL demo mode
│   ├── tsdpl_analytics.py       # MTBF/MTTR, OEE, MoM, sensor scorecard, equipment severity scoring
│   └── tsdpl_charts.py          # TSDPL Plotly charts (tornado, heatmap, MTBF/MTTR bars, severity rank)
│
├── requirements.txt             # Pinned Python dependencies
├── CHANGELOG.md                 # Development changelog
└── README.md                    # ⬅️ This file
```

---

## 📂 Input Data Format

### Generic UP/DOWN Format (Tabs 1–5)

| Column | Type | Required | Description |
|---|---|---|---|
| `timestamp` | datetime | ✅ | Event timestamp — any format parseable by `pd.to_datetime()` |
| `machine_id` | string | ✅ | Any non-null identifier |
| `status` | string | ✅ | `UP` or `DOWN` (case-insensitive) |
| `temperature` | float | ❌ | Sensor reading (°C) |
| `load` | float | ❌ | Sensor reading (%) |
| `vibration` | float | ❌ | Sensor reading (mm/s) |

### Messy Maintenance Export Format (Tab 12 — QIP Analysis)

`normalize_maintenance_data()` accepts files with any of these column variations and normalises to four standard columns:

| Standard Column | Accepted Aliases |
|---|---|
| `Date` | `DATE`, `Date`, `Month`, `MONTH`, `Sl No`, `Period`, `timestamp` |
| `Duration_Min` | `UNPLANNED B/D (Min.)`, `Downtime Hours`, `B/D HOURS`, `HRS`, `HOURS`, `Duration`, `Min` |
| `Equipment` | `EQUIPMENT`, `Work Centre`, `Machine`, `AREA`, `Asset`, `machine_id` |
| `Reason` | `BRIEF DESCRIPTION`, `Description`, `Failure Reason`, `Remarks`, `Root Cause` |

Files may have any number of metadata rows above the real header. Duration columns in hours are detected by column name and automatically converted to minutes.

### Breakdown Excel Format (⚙️ Maintenance Delay Analysis + Health Scorecard)

Handles `Monthly BD Sheet`, `pivot`, and `PARETO` sheets. Key columns: `AREA`, `EQUIPMENT`, `UNPLANNED B/D (Min.)` / `(Hr.)`, `BRIEF DESCRIPTION OF MAJOR UNPLANNED BREAKDOWNS`.

> 🆕 **The same Breakdown Excel also drives the Equipment MTBF/MTTR and Underperformer Severity Ranking charts in the Health Scorecard tab.** No extra upload required.

---

## 🧠 How It Works

### 1. Data Processing
Cleans and validates the upload, parses timestamps, uppercases status values, and coerces sensor columns to numeric.

### 2. Failure Detection
Identifies UP→DOWN transitions as failure events and calculates runtime before each failure, the hour-of-day it occurred, and whether it qualifies as a short/flapping event (< 30 min).

### 3. Analytics Engine
Computes per-machine uptime/downtime percentages, failure frequency, hourly failure distribution, daily uptime trends, and a 7-day rolling flapping score.

### 4. Prediction Engine

The TTF prediction runs in six steps:

```
Step 1 — Moving Average TTF     mean of last min(5, n) inter-failure runtimes
Step 2 — Linear Regression      predict next interval using failure index as X
Step 3 — Weighted Combination   w_lr = clamp(R², 0.2, 0.7)
Step 4 — Remaining TTF          combined_ttf − current_run_hours
Step 5 — Risk Score             clamp(ratio × 100 + cv_penalty, 0, 100)
Step 6 — Risk Label             High ≥ 70  |  Medium ≥ 40  |  Low < 40
```

### 5. Health Score
Composite 0–100 score per machine combining: runtime risk (prediction engine), sensor anomaly score (Z-score deviation of recent 10% UP readings vs baseline), flapping score (short DOWN events in rolling 7-day window), and PM compliance.

### 6. Messy File Normalizer
The `normalize_maintenance_data()` pipeline runs in six steps:

```
Step 1 — _read_raw()          Read CSV/Excel with no assumed header (header=None)
Step 2 — _extract_table()     Find first row with ≥3 non-null values = real header
Step 3 — _map_columns()       Fuzzy alias matching → Date / Duration_Min / Equipment / Reason
Step 4 — _parse_dates()       pd.to_datetime(dayfirst=True) + apostrophe-strip second pass
Step 5 — _parse_duration()    pd.to_numeric(errors='coerce') + ×60 if hours column detected
Step 6 — _final_clean()       Drop null Duration/Equipment rows, zero-duration rows, reset index
```

### 7. Equipment Severity Scoring (v3.0)

```
mtbf_gap_pct    = max(0, (target_mtbf − actual_mtbf) / target_mtbf)
mttr_excess_pct = max(0, (actual_mttr − target_mttr) / target_mttr)
breakdown_count = normalised event count across fleet

severity_score  = (0.45 × mtbf_gap_pct) + (0.35 × mttr_excess_pct) + (0.20 × breakdown_count)
```

Thresholds: **Critical** ≥ 0.6 · **Warning** ≥ 0.3 · **Normal** < 0.3

---

## 📖 Module Reference

### `utils/data_loader.py`

| Function | Returns | Description |
|---|---|---|
| `load_data(uploaded_file)` | `(df, error)` | Reads CSV or Excel; `error` is None on success |
| `validate_and_preprocess(df)` | `df` | Normalises columns, parses timestamps, coerces sensors |
| `get_data_summary(df)` | `dict` | `{total_records, machines, date_range, has_temperature, ...}` |

### `utils/analytics.py`

| Function | Description |
|---|---|
| `compute_uptime_downtime(df)` | Per-machine `uptime_pct`, `downtime_hours` |
| `extract_failure_events(df)` | Detects UP→DOWN transitions; returns `failure_time`, `runtime_before_failure_hours`, `hour_of_day` |
| `compute_failure_patterns(fe)` | Aggregates `failure_count`, `avg/std/min/max_runtime_h`, `most_common_failure_hour` |
| `compute_hourly_failure_trend(fe)` | Failure count by hour-of-day (0–23), always 24 rows |
| `compute_daily_uptime(df)` | Daily uptime percentage per machine |
| `compute_flapping_score(fe)` | Count of DOWN events < 30 min per machine in rolling 7-day window |

### `utils/predictor.py`

| Function | Description |
|---|---|
| `predict_machine(fe, df)` | Single-machine prediction dict |
| `predict_all_machines(df, fe)` | Fleet-wide predictions sorted by `risk_value` descending |
| `compute_sensor_anomaly_score(df)` | Z-score deviation of recent 10% UP readings vs baseline, capped at 100 |
| `compute_health_score(risk, anomaly, flapping, pm)` | Composite 0–100 score |

### `utils/messy_loader.py`

| Function | Description |
|---|---|
| `normalize_maintenance_data(uploaded_file)` | Public API — reads any messy CSV/Excel, returns `(clean_df, error)` |
| `compute_mtbf_mttr_from_norm(df, period_mask)` | Computes MTBF, MTTR, failure count, downtime for a given time window |

> To add a new column alias — edit `COLUMN_ALIASES` in `messy_loader.py`. No other files need to change.

### `utils/breakdown_loader.py`

Sheet auto-detection (`Monthly BD Sheet`, `pivot`, `PARETO`), deep column name cleaning, dynamic column resolution by fuzzy keyword matching, multi-file merge support (concatenates WCTL-1 + WCTL-2 + Slit), and fallback computation if pivot/Pareto sheets are corrupted.

### `utils/tsdpl_analytics.py`

| Function | Metric |
|---|---|
| `compute_mtbf_mttr(dl)` | Per-machine MTBF (h), MTTR (min), availability % |
| `compute_shift_mtbf_mttr(dl)` | Machine × Shift breakdown |
| `compute_oee_loss(dl)` | OEE availability loss % with category split |
| `compute_mom_comparison(dl)` | This month vs last month trend arrows |
| `compute_sensor_scorecard(sr)` | 24-hour alarm/warning/normal status per parameter |
| `compute_equipment_mtbf_mttr(raw_df)` | **(v3.0)** Per-equipment MTBF, MTTR, availability from Breakdown Excel |
| `flag_underperforming_equipment(df)` | **(v3.0)** Composite severity score + Critical/Warning/Normal health status |

### `utils/tsdpl_charts.py`

| Function | Chart Type |
|---|---|
| `chart_shift_tornado()` | Diverging horizontal bar — Night on negative X, Morning/Afternoon on positive |
| `chart_mtbf_by_shift()` | Grouped column chart — metric switchable between MTBF / MTTR / downtime |
| `chart_sensor_heatmap()` | Heatmap with ✅ / ⚠️ / 🚨 emoji overlays |
| `chart_param_trend()` | Time-series with alarm threshold lines |
| `chart_failure_category_donut()` | Donut pie by failure category |
| `chart_mom_grid()` | 3×N subplot bar grid |
| `chart_pm_status()` | Stacked bar (Completed / Overdue / Scheduled) |
| `chart_incident_timeline()` | Gantt-style scatter timeline |
| `chart_qip_comparison()` | Grouped bar (baseline vs improvement) |
| `chart_equipment_mtbf_mttr()` | **(v3.0)** MTBF/MTTR bars with target markers, colour-coded pass/fail |
| `chart_underperformer_ranking()` | **(v3.0)** Horizontal severity ranking chart with threshold reference lines |

### `components/ui_components.py`

| Function | Description |
|---|---|
| `metric_card(title, value, delta, color)` | Left-bordered KPI card with delta indicator |
| `alert_banner(message, level)` | Full-width coloured banner — levels: `info` / `warning` / `error` / `success` |
| `render_prediction_card(row)` | 3-column risk card: risk label, TTF, confidence |
| `render_alert_machines(predictions)` | Fleet risk banner based on highest-risk machine |
| `section_header(title, subtitle)` | H3 + subtitle with consistent spacing |
| `render_equipment_health_card(eq)` | **(v3.0)** Equipment health KPI card with severity badge |

---

## ⚙️ Configuration Reference

### Risk Score Thresholds

| Score | Label | Colour |
|---|---|---|
| 0–39 | 🟢 Low | `#22C55E` |
| 40–69 | 🟡 Medium | `#F59E0B` |
| 70–100 | 🔴 High | `#EF4444` |

### Machine Criticality

| Criticality | Machines |
|---|---|
| Critical | Cassette Leveller (HR-CTL), Slitter Head (HR Slitting), Skin Pass Mill (CR) |
| High | Uncoiler (HR-CTL), Flying Shear (HR-CTL), Recoiler (HR Slitting), Robotic Tool Setup (CR) |
| Medium | Air Cushion Stacker, Tension Bridle, Scrap Chopper, Inspection & Parting Line |

### Failure Code Taxonomy

| Prefix | Category |
|---|---|
| ME-xx | Mechanical |
| EE-xx | Electrical |
| HY-xx | Hydraulic |
| PR-xx | Process |
| PL-xx | Planned |

### Equipment Targets (v3.0)

Defined in `EQUIPMENT_THRESHOLDS` in `utils/tsdpl_constants.py`. Edit values here — no other code changes needed:

```python
EQUIPMENT_THRESHOLDS = {
    "STACKER":      {"mtbf_min_hrs": 200, "mttr_max_min": 30},
    "FLYING SHEAR": {"mtbf_min_hrs": 350, "mttr_max_min": 15},
    # ... add equipment as needed
}

UNDERPERFORMER_WEIGHTS = {
    "mtbf_gap_pct":    0.45,   # increase if MTBF gap should count more
    "mttr_excess_pct": 0.35,   # increase for heavier penalty on slow recovery
    "breakdown_count": 0.20    # increase if event frequency matters more
}
```

### PM Frequency Map

| Frequency | Hours |
|---|---|
| Per Coil | 8 |
| Per Coil Batch | 16 |
| Shift / Daily | 8 / 24 |
| Weekly | 168 |
| Monthly | 720 |
| Quarterly | 2,160 |

---

## 🎨 UI and Design System

### Color Palette

| Role | Hex | Usage |
|---|---|---|
| Main area background | `#F4F7F9` | Outer content shell |
| Sidebar background | `#1A2C3E` | Dark navy sidebar |
| Uploader dropzone | `#0D1B2A` | File upload areas in sidebar |
| Accent blue | `#0080C7` | Tata Blue — active tabs, headers, buttons |
| Success green | `#22C55E` | High uptime, Low risk |
| Warning amber | `#F59E0B` | Medium risk, open alerts |
| Danger red | `#EF4444` | High risk, critical alerts |
| Text primary | `#1A2C3E` | Values, machine names |
| Text secondary | `#5C6F87` | Labels, chart subtitles |
| Widget backgrounds | `#FFFFFF` | Selectboxes, inputs (via `config.toml`) |

### Theming Architecture

Theming is applied in two layers:

**Layer 1 — `.streamlit/config.toml`** (framework defaults):
```toml
primaryColor             = "#0080C7"
backgroundColor          = "#F4F7F9"
secondaryBackgroundColor = "#FFFFFF"   # ⚠️ Must stay light — see note below
textColor                = "#1A2C3E"
font                     = "sans serif"
```

**Layer 2 — Inline CSS** in `app_version2.py` (targeted overrides via `st.markdown`):
- Sidebar `#1A2C3E` background with forced `#FFFFFF` text on all children
- Uploader dropzone forced to `#0D1B2A` at every inner element level (beats inline style injection)
- Tab bar white background, Tata Blue active state
- Metric card animation (`fadeSlideUp`)
- Selectbox/multiselect backgrounds forced white with dark text

> ⚠️ **`secondaryBackgroundColor` must remain `#FFFFFF`** — Streamlit injects it as an inline style on every widget control div. A dark value makes dropdown text invisible even against CSS `!important` rules. The sidebar stays dark entirely through CSS overrides.

> ⚠️ **Do not use `st.components.v1.html()`** for JS injection — it creates an iframe that captures click events and breaks buttons.

---

## 🗺️ Roadmap

| Feature | Priority | Complexity | Notes |
|---|---|---|---|
| Weibull survival analysis (RUL model) | 🔴 High | Medium | `lifelines` library; handles machines with no recent failures via shape parameter β |
| Isolation Forest anomaly detection | 🔴 High | Low | Multivariate sensor anomaly; feeds directly into health score |
| Sensor-weighted composite risk score | 🔴 High | Low | Anomaly score already computed — merge into `risk_value` |
| Work Order PDF export | 🔴 High | Medium | `fpdf2`; per-machine work order from high-risk card |
| SQLite backend + incremental append | 🟡 Medium | Medium | Zero infrastructure; deduplicated by timestamp + machine_id |
| FMEA RPN table | 🟡 Medium | Low | Severity × Occurrence × Detectability mapped from failure code taxonomy |
| MTTR by technician + repeat failure rate | 🟡 Medium | Low | Flag machines failing within 48h of repair |
| Shift handover one-page PDF | 🟡 Medium | Low | Auto-generated at shift change: at-risk machines, open PM, recent failures |
| Date range sidebar filter | 🟡 Medium | Low | Applied across all 12 tabs |
| Messy loader: editable alias UI | 🟡 Medium | Low | Let users define column mappings in-app |
| Power BI `.pbix` template | 🔵 Low | High | DAX measures already documented in Tab 11 |

---

## ⚠️ Known Limitations

**TTF model requires 2+ failure events per machine.** Machines with 0 or 1 failures receive a static fallback risk score (10 or 35 respectively).

**Long-runtime machines are under-risk-scored.** A machine UP for a long time with no historical failures reads Low risk even if statistically overdue. A no-failure-but-long-runtime penalty is not yet implemented.

**Sensor anomaly score is not yet merged into `risk_value`.** Both signals are shown separately; full fusion is on the roadmap.

**Shift roster is generated, not editable.** There is no in-app form to log actual shift assignments or mark a repair as complete.

**Single-file upload only (generic tabs).** Each upload replaces the previous dataset. Incremental append is planned via SQLite backend.

**Flapping threshold is fixed at 30 minutes.** Should be configurable per machine type but is currently hardcoded.

**Messy loader requires at least one matched column per standard name.** Files missing any of `Date`, `Duration`, `Equipment`, or `Reason` will return an error listing which columns could not be found.

**QIP MTBF is span-based, not operational-hours-based.** Period hours are computed from first to last event timestamp, not from actual production calendar hours.

**Equipment Health charts require Breakdown Excel upload.** If `breakdown_data` is None, the MTBF/MTTR and severity ranking charts in the Health Scorecard tab will not appear.

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| UI / Frontend | Streamlit 1.32.2 |
| Data processing | Pandas 2.0.3, NumPy 1.24.3 |
| Visualisation | Plotly 5.18.0 (custom `tsdpl` template) |
| Modelling | Moving average + linear regression (scikit-learn 1.3.0) |
| Excel I/O | OpenPyXL 3.1.2 |
| Styling | CSS injection via `st.markdown` + `.streamlit/config.toml` |
| Language | Python 3.11+ |

---

## 🔒 Security Hardening

| Control | Implementation |
|---|---|
| Input Validation | `validate_machine_id()` — regex whitelist `[a-zA-Z0-9_\-\s()/.]{1,100}` |
| Numeric Bounds | `validate_numeric_input()` — min/max guards |
| HTML Sanitization | `sanitize_html_string()` — strips `<script>` tags and `on*=` event handlers |
| File Upload Guards | `validate_file_upload()` — 50MB limit, extension whitelist (`csv`, `xlsx`, `xls`) |
| Audit Logging | Python `logging` at `WARNING` level for rejected uploads and processing errors |
| No Debug Exposure | All exceptions caught and sanitized; no stack traces leaked to UI |
| Dependency Pinning | All packages pinned in `requirements.txt` |

---

## 🐛 Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: utils` | Running from wrong directory | Run from project root; `sys.path.insert(0, ...)` handles relative imports |
| `Could not locate a valid data table` | Metadata rows above header | Use 🔬 Upload Real-World Data instead of generic uploader |
| `Only UP, DOWN allowed` | Status values like `Running`, `Stopped` | Normalize statuses in source file or extend `VALID_STATUSES` in `data_loader.py` |
| Breakdown tab empty after upload | No `AREA` or `EQUIPMENT` column detected | Verify Excel has `Monthly BD Sheet` tab with correct headers |
| Equipment Health charts missing | `breakdown_data` is None | Upload via ⚙️ Maintenance Delay Analysis |
| Main-area selectboxes invisible | `secondaryBackgroundColor` was dark | Changed to `#FFFFFF` in `config.toml` — do not revert |
| Sidebar upload area invisible | `secondaryBackgroundColor` injects white inline on inner divs | Nuclear-depth CSS forces `#0D1B2A` on all inner elements |
| Plotly charts not rendering | Browser WebGL disabled | Enable hardware acceleration in browser settings |
| File picker pre-fills "(streamlit)" | Browser/OS caches window title | Known Streamlit limitation |
| `components.html()` breaks buttons | Injected iframe captures click events | Do not use `st.components.v1.html()` for invisible JS |

---

<p align="center">
  <strong>TSDPL Kalinganagar v3.0</strong> · Jajpur Road, Odisha<br>
  <sub>Predictive maintenance · Shift analytics · Sensor health · Equipment intelligence</sub>
</p>
