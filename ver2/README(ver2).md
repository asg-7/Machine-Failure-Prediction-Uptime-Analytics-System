# 🏭 Machine Failure Prediction & Uptime Analytics System

**Plant:** TSDPL Kalinganagar, Jajpur Road, Odisha  
**Stack:** Python · Pandas · NumPy · scikit-learn · Plotly · Streamlit  
**Version:** 2.0 — TSDPL Kalinganagar Edition  
**Last Updated:** April 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Version History](#2-version-history)
3. [Quick Start](#3-quick-start)
4. [File Structure](#4-file-structure)
5. [Tab Reference](#5-tab-reference)
6. [Module Reference](#6-module-reference)
7. [Data Contracts](#7-data-contracts)
8. [Configuration Reference](#8-configuration-reference)
9. [UI & Design System](#9-ui--design-system)
10. [Roadmap & Future Work](#10-roadmap--future-work)
11. [Known Limitations](#11-known-limitations)

---

## 1. Project Overview

A lightweight, locally-runnable plant maintenance dashboard that moves operations from **reactive** to **predictive** maintenance. Built for plant engineers, maintenance teams, and operations managers who need actionable intelligence without heavy cloud infrastructure or complex ML pipelines.

**Core capabilities:**

- Upload any CSV/Excel time-series of machine UP/DOWN status
- Compute uptime, downtime, and efficiency percentages
- Detect failure patterns and time-of-day trends
- Predict time-to-failure (TTF) and assign 0–100 risk scores using moving averages + linear regression
- TSDPL-specific: shift-based analytics, PM checklist, sensor scorecards, month-over-month comparison
- Advanced failure mode detection: Performance Degradation, Intermittent Failures, Surface Degradation
- Composite Health Score tab aggregating sensor anomaly, runtime risk, and flapping metrics

---

## 2. Version History

| Version | Description |
|---------|-------------|
| v1.0 | 5-tab generic dashboard — data upload, uptime engine, failure detection, TTF prediction, drilldown |
| v1.1 | Fixed `pd.to_datetime()` deprecation (`infer_datetime_format` removed in Pandas 2.x) |
| v2.0 | TSDPL Kalinganagar edition — 5 new tabs, 4 new modules, 11 machines, 22 failure codes, shift roster, PM checklist, health scorecard, MoM comparison |
| v2.1 | Color system overhaul (dark high-contrast theme), advanced failure modes, Health Score tab, tab bar responsiveness, loading transitions |

### v2.1 Changes (April 2026)

**Color & UI Overhaul**

- Full dark theme applied via Streamlit CSS injection targeting `data-testid` selectors
- Three-tier contrast hierarchy: `#f1f5f9` for values, `#94a3b8` for labels, `#64748b` for supporting text
- Consistent left-border color coding on all KPI cards: green (improving), red (worsening), blue (stable), amber (fleet delta)
- Tab bar uses `clamp(13px, 1.1vw, 16px)` font sizing — readable at all zoom levels
- Tab bar scrolls horizontally on narrow viewports (`flex-wrap: nowrap`, `overflow-x: auto`)
- Unified `TSDPL_TEMPLATE` registered in `plotly.io` — all charts inherit dark background, grid, hover, and colorway automatically

**Loading Transitions**

- `st.spinner()` wraps `predict_all_machines()` and `compute_sensor_scorecard()`
- `st.progress()` increments per machine during heavy fleet-wide computations
- `st.empty()` placeholder + skeleton pattern for Weibull fit (roadmap)
- `fadeSlideUp` CSS animation on metric cards (`opacity 0→1`, `translateY 10px→0`, `0.35s ease-out`)

**Advanced Failure Modes**

- Performance Degradation: sensor health index computed as deviation from normal operating range; soft amber alert triggered when index exceeds threshold
- Intermittent / Flapping: short DOWN events (< 30 min) counted per rolling 7-day window; "flapping score" surfaced as a dedicated metric
- Surface Degradation: maintenance record age and equipment runtime combined into a wear index; PM overdue flag escalated when wear index crosses criticality threshold

**Health Score Tab**

- Composite 0–100 score per machine aggregating: runtime-based risk (from `predictor.py`), sensor anomaly score (Z-score deviation), flapping frequency, and PM compliance
- Colour-coded gauge per machine (green / amber / red)
- Drill-down table shows sub-score breakdown

**Month-over-Month Tab — Contrast Fix**

- `Last Month` bars changed from washed-out `#808080` to high-contrast `#334155` (slate-700)
- `Stable` trend colour changed from invisible gray to `#38bdf8` (sky-400)
- KPI card background deepened to `#0d1f35`; value text raised to `#f1f5f9`
- Sub-label text raised from ~40% opacity to `#94a3b8`
- `FLEET Δ DOWNTIME` card border corrected to amber `#f59e0b`

---

## 3. Quick Start

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

### Navigation Guide

| Goal | Action |
|------|--------|
| Explore generic prediction features | Click **🎲 Generic Demo** → use tabs 1–5 |
| Explore TSDPL plant dashboard | Click **🏭 TSDPL Demo** → use tabs 6–10 |
| Upload real plant data (UP/DOWN format) | Use sidebar uploader → tabs 1–5 respond automatically |
| View who was on duty at a failure | Tab 6 → filter Incidents: "Y - Only Incidents" |
| See which shift causes most downtime | Tab 7 → Tornado Chart |
| Find overdue LOTO tasks | Tab 8 → red LOTO banner + status filter "Overdue" |
| Check which sensor is drifting | Tab 9 → Heatmap → Parameter Trend Drilldown |
| View composite machine health | Tab 10 → Health Score gauges |
| Present to management | Tab 11 → MoM MTBF scorecard cards |

---

## 4. File Structure

```
machine_failure_app/
│
├── app.py                          # Main entry — 10-tab dual-mode dashboard
├── requirements.txt
├── generate_sample_data.py         # Generic synthetic data generator
├── sample_data.csv                 # Pre-generated (5 machines, 60 days)
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py              # Upload, validate, preprocess (generic)
│   ├── analytics.py                # Uptime engine + failure pattern detection
│   ├── predictor.py                # TTF prediction + risk scoring + flapping score
│   ├── charts.py                   # 7 Plotly charts for tabs 1–5
│   ├── tsdpl_constants.py          # Domain data — machines, codes, roster, limits
│   ├── tsdpl_demo_data.py          # TSDPL synthetic data generators
│   ├── tsdpl_analytics.py          # MTBF, MTTR, OEE, MoM, sensor scorecard
│   └── tsdpl_charts.py             # 8 Plotly charts for tabs 6–10
│
└── components/
    ├── __init__.py
    └── ui_components.py            # Reusable Streamlit HTML/CSS components
```

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

## 5. Tab Reference

### Generic Tabs (work with any CSV upload)

| Tab | Title | Content |
|-----|-------|---------|
| 1 | 🏠 Overview | KPI cards, alert banners, uptime vs downtime chart, risk ranking, summary table |
| 2 | 📈 Uptime Analysis | Stacked bar chart, daily trend line, detailed uptime table |
| 3 | 💥 Failure Patterns | Frequency bar chart, hour-of-day chart, failure event log |
| 4 | 🔮 Predictions & Risk | Risk cards per machine, TTF bar chart, maintenance planning insights |
| 5 | 🔬 Machine Drilldown | Sensor trend chart, anomaly score, per-machine failure log, raw data preview |

### TSDPL Tabs (TSDPL Demo data required)

| Tab | Title | Core Feature |
|-----|-------|-------------|
| 6 | 📋 Shift Roster | TBL_SHIFT_ROSTER_LOG with incident overlay, master roster viewer, XLOOKUP formula |
| 7 | 📊 Shift Analytics | Tornado chart, MTBF/MTTR clustered bars, OEE pivot, night shift root-cause insight |
| 8 | 🔧 PM Checklist | LOTO compliance banner, overdue/completed colour rows, PM status chart, incident timeline |
| 9 | 🌡️ Health Scorecard | Sensor alarm heatmap, operational limits table, parameter trend drilldown, flapping score |
| 10 | 💚 Health Score | Composite 0–100 gauge per machine, sub-score breakdown table, performance/flapping/wear indices |
| 11 | 📅 Month-over-Month | MoM grid chart, MTBF scorecard cards, DAX + Excel formula reference, failure code glossary |

---

## 6. Module Reference

### `utils/data_loader.py`

**Purpose:** File upload handling, validation, and preprocessing pipeline.

```python
REQUIRED_COLS  = {"timestamp", "machine_id", "status"}
OPTIONAL_COLS  = {"temperature", "load", "vibration"}
VALID_STATUSES = {"UP", "DOWN"}
```

| Function | Description |
|----------|-------------|
| `load_data(uploaded_file)` | Reads CSV or Excel. Returns `(df, error)` tuple — error is `None` on success. |
| `validate_and_preprocess(df)` | Normalises columns, parses timestamp, uppercases status, coerces sensors to numeric. |
| `get_data_summary(df)` | Returns `{total_records, machines, date_range, has_temperature, has_load, has_vibration}`. |

### `utils/analytics.py`

**Purpose:** Core uptime/downtime engine and failure pattern detection. Pure Pandas.

| Function | Description |
|----------|-------------|
| `compute_uptime_downtime(df)` | Per-machine: `uptime_pct`, `downtime_pct`, `uptime_hours`, `downtime_hours`. |
| `extract_failure_events(df)` | Detects UP→DOWN transitions. Returns `failure_time`, `runtime_before_failure_hours`, `hour_of_day`. |
| `compute_failure_patterns(failure_events)` | Aggregates `failure_count`, `avg/std/min/max_runtime_h`, `most_common_failure_hour`. |
| `compute_hourly_failure_trend(failure_events)` | Failure count by hour-of-day (0–23), always 24 rows. |
| `compute_daily_uptime(df)` | Daily uptime percentage per machine. |
| `compute_flapping_score(failure_events)` | Count of DOWN events < 30 min per machine in rolling 7-day window. New in v2.1. |

### `utils/predictor.py`

**Purpose:** TTF prediction, 0–100 risk scoring, sensor anomaly, and health score aggregation.

**Prediction algorithm:**

```
Step 1: Moving Average TTF   — mean of last min(5, n) inter-failure runtimes
Step 2: Linear Regression    — predict next interval using failure index as X
Step 3: Weighted Combination — w_lr = clamp(R², 0.2, 0.7)
Step 4: Remaining TTF        — combined_ttf − current_run_hours
Step 5: Risk Score           — clamp(ratio × 100 + cv_penalty, 0, 100)
Step 6: Risk Label           — High ≥ 70 | Medium ≥ 40 | Low < 40
```

| Function | Description |
|----------|-------------|
| `predict_machine(failure_events_machine, df_machine)` | Single-machine prediction dict. |
| `predict_all_machines(df, failure_events)` | Fleet-wide predictions, sorted by `risk_value` descending. |
| `compute_sensor_anomaly_score(df_machine)` | Z-score deviation of recent 10% of UP readings vs baseline. Capped at 100. |
| `compute_health_score(risk_value, anomaly_score, flapping_score, pm_compliance)` | Composite 0–100 score. New in v2.1. |

### `utils/tsdpl_analytics.py`

| Function | Description |
|----------|-------------|
| `compute_mtbf_mttr(downtime_log)` | Per-machine: `MTBF_hours`, `MTTR_min`, `availability_pct`. |
| `compute_shift_mtbf_mttr(downtime_log)` | Same metrics grouped by `(machine_id, shift)`. |
| `compute_oee_loss(downtime_log)` | Per `(machine_id, shift)`: OEE availability loss and downtime by category. |
| `compute_mom_comparison(downtime_log)` | Per machine: trend (Improving/Worsening/Stable), delta downtime, top failure mode. |
| `compute_sensor_scorecard(sensor_df)` | Per `(machine_id, parameter)`: status (Normal/WARNING/ALARM), trend arrow. |

**MoM trend thresholds:** Improving if `mtbf_this / mtbf_last > 1.05` · Worsening if `< 0.95` · Stable otherwise.

### `utils/tsdpl_charts.py`

| Function | Chart Type |
|----------|-----------|
| `chart_shift_tornado` | Diverging horizontal bar — Night on negative X, Morning/Afternoon on positive |
| `chart_mtbf_by_shift` | Grouped vertical bar — metric switchable between MTBF/MTTR/downtime |
| `chart_sensor_heatmap` | Heatmap with ✅ / ⚠️ / 🚨 emoji overlays |
| `chart_param_trend` | Scatter + rolling average + alarm threshold lines |
| `chart_failure_category_donut` | Donut pie by failure category |
| `chart_mom_grid` | 3×N subplot bar grid — last month slate, this month trend-coloured |
| `chart_pm_status` | Stacked bar by status (Completed / Overdue / Scheduled) |
| `chart_incident_timeline` | Gantt-style scatter — each incident a thick line from start to start+duration |

All charts apply the `"tsdpl"` Plotly template automatically.

### `components/ui_components.py`

| Function | Description |
|----------|-------------|
| `risk_badge_html(label)` | Inline `<span>` badge coloured by risk label. |
| `metric_card(title, value, delta, color)` | Left-bordered card with large value and optional delta. |
| `alert_banner(message, level)` | Full-width coloured banner. Levels: `info / warning / error / success`. |
| `render_prediction_card(row)` | 3-column machine prediction card — risk, TTF, confidence. |
| `render_alert_machines(predictions)` | Error/warning/success banner based on fleet risk state. |
| `section_header(title, subtitle)` | H3 + subtitle with consistent spacing. |

---

## 7. Data Contracts

### Generic Input Schema (CSV/Excel upload)

| Column | Required | Type | Constraints |
|--------|----------|------|-------------|
| `timestamp` | ✅ | datetime string | Any format parseable by `pd.to_datetime()` |
| `machine_id` | ✅ | string | Any non-null identifier |
| `status` | ✅ | string | `UP` or `DOWN` (case-insensitive) |
| `temperature` | Optional | numeric | Coerced to NaN on invalid |
| `load` | Optional | numeric | Coerced to NaN on invalid |
| `vibration` | Optional | numeric | Coerced to NaN on invalid |

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
| `risk_label` | str | `Low / Medium / High / Unknown` |
| `risk_value` | int | 0–100 continuous risk score |
| `confidence` | str | `High / Medium / Low / Low (insufficient data)` |
| `flapping_score` | int | Count of short DOWN events in rolling 7-day window. New in v2.1. |
| `health_score` | int | Composite 0–100 score. New in v2.1. |

---

## 8. Configuration Reference

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

### Risk Score Thresholds

| Score Range | Label | Colour |
|------------|-------|--------|
| 0–39 | Low | `#22C55E` |
| 40–69 | Medium | `#F59E0B` |
| 70–100 | High | `#EF4444` |

### Machine Criticality

| Criticality | Machines |
|------------|---------|
| Critical | Cassette Leveller (HR-CTL), Slitter Head (HR Slitting), Skin Pass Mill (CR) |
| High | Uncoiler (HR-CTL), Flying Shear (HR-CTL), Recoiler (HR Slitting), Robotic Tool Setup (CR) |
| Medium | Air Cushion Stacker, Tension Bridle, Scrap Chopper, Inspection & Parting Line |

### Failure Code Taxonomy

| Prefix | Category |
|--------|---------|
| `ME-xx` | Mechanical |
| `EE-xx` | Electrical |
| `HY-xx` | Hydraulic |
| `PR-xx` | Process |
| `PL-xx` | Planned |

---

## 9. UI & Design System

### Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| App background | `#0b1120` | Outermost shell |
| Card background | `#0d1f35` | KPI cards, chart boxes |
| Border | `#1e3a5f` | All card borders, dividers |
| Accent blue | `#38bdf8` | Active nav, headers, links |
| Success green | `#22c55e` | High uptime, Low risk |
| Warning amber | `#f59e0b` | Medium risk, open alerts |
| Danger red | `#ef4444` | High risk, critical alerts |
| Purple | `#c084fc` | Shift B annotation, Weibull curve |
| Text primary | `#f1f5f9` | Values, machine names |
| Text secondary | `#94a3b8` | Labels, chart subtitles |
| Text muted | `#64748b` | KPI sub-labels, timestamps |

### Streamlit CSS Injection

Add the following block near the top of `app.py` after imports:

```python
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0b1120; color: #e2e8f0; }
[data-testid="stSidebar"] { background-color: #0d1526; border-right: 1px solid #1e2d45; }

[data-testid="stMetric"] {
    background: #0d1f35; border: 1px solid #1e3a5f;
    border-radius: 8px; padding: 12px 16px;
    animation: fadeSlideUp 0.35s ease-out both;
}
[data-testid="stMetricLabel"] { color: #64748b; font-size: 11px; }
[data-testid="stMetricValue"] { color: #f1f5f9; }

.stTabs [data-baseweb="tab-list"] {
    background: #0d1526; border-radius: 8px;
    padding: 3px; gap: 2px;
    overflow-x: auto; overflow-y: hidden;
    flex-wrap: nowrap; scrollbar-width: none;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    border-radius: 6px; color: #64748b;
    font-size: clamp(13px, 1.1vw, 16px) !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
    white-space: nowrap;
}
.stTabs [aria-selected="true"] { background: #1e3a5f !important; color: #f1f5f9 !important; }
.stTabs [aria-selected="false"]:hover { background: #172135 !important; color: #cbd5e1 !important; }

.stButton > button {
    background: #1e3a5f; color: #38bdf8;
    border: 1px solid #1e3a5f; border-radius: 6px;
    font-weight: 500; transition: background 0.15s, transform 0.1s;
}
.stButton > button:hover { background: #174a7a; transform: translateY(-1px); }

[data-testid="stAlert"][kind="error"]   { background: #3f0d0d; border: 1px solid #7f1d1d; color: #fca5a5; }
[data-testid="stAlert"][kind="warning"] { background: #422006; border: 1px solid #7c2d12; color: #fdba74; }
[data-testid="stAlert"][kind="success"] { background: #052e16; border: 1px solid #166534; color: #86efac; }

[data-testid="stDataFrame"] { border: 1px solid #1e3a5f; border-radius: 8px; }
thead th { background: #0d1526 !important; color: #64748b !important; }
tbody tr:hover td { background: #172135 !important; }

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)
```

### Plotly Template

Add to `utils/tsdpl_charts.py` (top of file, runs once on import):

```python
import plotly.io as pio

TSDPL_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "#0b1120",
        "plot_bgcolor":  "#0d1f35",
        "font":          {"color": "#94a3b8", "family": "Inter, system-ui, sans-serif"},
        "colorway":      ["#38bdf8", "#4ade80", "#fbbf24", "#f87171", "#c084fc"],
        "xaxis": {"gridcolor": "#1e293b", "linecolor": "#1e3a5f", "tickcolor": "#475569"},
        "yaxis": {"gridcolor": "#1e293b", "linecolor": "#1e3a5f", "tickcolor": "#475569"},
        "legend": {"bgcolor": "#0d1f35", "bordercolor": "#1e3a5f", "borderwidth": 1},
        "hoverlabel": {"bgcolor": "#0d1526", "bordercolor": "#38bdf8", "font": {"color": "#f1f5f9"}}
    }
}

pio.templates["tsdpl"] = pio.templates["plotly"].update(TSDPL_TEMPLATE)
pio.templates.default = "tsdpl"
```

### Loading Transitions

```python
# Quick operations (< 2s)
with st.spinner("Calculating risk scores..."):
    predictions = predict_all_machines(df, failure_events)

# Heavy fleet-wide compute — progress bar
progress = st.progress(0)
results = []
for i, machine in enumerate(machines):
    results.append(predict_machine(...))
    progress.progress((i + 1) / len(machines))
progress.empty()

# Placeholder skeleton while data loads
placeholder = st.empty()
placeholder.markdown('<div class="skeleton-loader">Loading...</div>', unsafe_allow_html=True)
# ... compute ...
placeholder.empty()
# render real content
```

---

## 10. Roadmap & Future Work

| Feature | Priority | Complexity | Notes |
|---------|----------|-----------|-------|
| Weibull survival analysis (RUL model) | High | Medium | `lifelines` library; handles machines with no recent failures via shape parameter β |
| Isolation Forest anomaly detection | High | Low | Multivariate sensor anomaly; feeds into health score |
| Work Order PDF export | High | Medium | `fpdf2`; generates per-machine work order from high-risk card |
| SQLite backend + incremental data append | Medium | Medium | Zero infrastructure; deduplicated by `timestamp + machine_id` |
| FMEA RPN table (Severity × Occurrence × Detectability) | Medium | Low | Maps `failure_code` taxonomy to RPN per failure type |
| MTTR by technician + repeat failure rate | Medium | Low | Accountability KPI; flag machine failing within 48h of repair |
| Shift handover one-page PDF | Medium | Low | Auto-generated at shift change; machines at risk, open PM, recent failures |
| Sensor-weighted composite risk score | High | Low | Already computed separately — merge anomaly into `risk_value` |
| Date range sidebar filter | Medium | Low | Applied across all 11 tabs |
| Power BI `.pbix` template | Low | High | DAX measures already documented in Tab 11 |
| Comparative period selector | Low | Medium | Any two custom date windows, not just calendar months |

---

## 11. Known Limitations

- **TTF model requires ≥ 2 failure events** per machine. Machines with 0 or 1 failures receive a static fallback risk score (10 or 35).
- **Long-runtime machines are under-risk-scored.** A machine UP for a very long time with no historical failures reads Low risk even if overdue. A no-failure-but-long-runtime penalty is not yet implemented.
- **Sensor anomaly score is not yet merged into `risk_value`.** The two signals are shown separately in v2.1; full fusion is planned (see roadmap).
- **Shift roster is generated, not editable.** There is no in-app form to log actual shift assignments or mark a repair as complete.
- **Single-file upload only.** Each upload replaces the previous dataset. Incremental append is planned via SQLite backend.
- **Flapping score uses a fixed 30-minute threshold** for classifying a DOWN event as "short". This should be configurable per machine type.

---

*TSDPL Kalinganagar Maintenance Dashboard v2.1 — April 2026*
