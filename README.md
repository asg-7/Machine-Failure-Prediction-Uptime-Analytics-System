# 🏭 Machine Failure Prediction & Uptime Analytics
A locally-runnable predictive maintenance dashboard for plant engineers and operations teams

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red) ![Pandas](https://img.shields.io/badge/Pandas-2.x-green) ![scikit--learn](https://img.shields.io/badge/scikit--learn-latest-orange) ![Plotly](https://img.shields.io/badge/Plotly-latest-purple) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow) ![Version](https://img.shields.io/badge/Version-2.2-brightgreen)

**Plant: TSDPL Kalinganagar, Jajpur Road, Odisha** &nbsp;|&nbsp; **Last Updated: April 2026**

> Moves plant operations from reactive to predictive maintenance — no cloud infrastructure, no complex ML pipelines.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Version History](#-version-history)
- [Whats New in v2.2](#-whats-new-in-v22)
- [Quick Start](#-quick-start)
- [Dashboard Navigation](#️-dashboard-navigation)
- [File Structure](#️-file-structure)
- [Input Data Format](#-input-data-format)
- [How It Works](#-how-it-works)
- [Module Reference](#-module-reference)
- [Configuration Reference](#️-configuration-reference)
- [UI and Design System](#-ui-and-design-system)
- [Roadmap](#️-roadmap)
- [Known Limitations](#️-known-limitations)
- [Contributing](#-contributing)

---

## 🔍 Overview
A dual-mode **11-tab** Streamlit dashboard built for plant engineers, maintenance technicians, and operations managers. Upload any CSV/Excel of machine UP/DOWN status and get actionable fleet intelligence immediately — no data science background required.

**v2.2** adds a complete real-world data ingestion pipeline — handling messy factory exports with pivoted headers, inconsistent column names, and mixed date formats — plus a QIP (Quality Improvement Project) before/after analysis tab for presenting MTBF/MTTR improvement results to management.

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

---

## 📦 Version History

| Version | Highlights |
|---|---|
| v1.0 | 5-tab generic dashboard — upload, uptime, failure detection, TTF prediction, drilldown |
| v1.1 | Fixed `pd.to_datetime()` deprecation (`infer_datetime_format` removed in Pandas 2.x) |
| v2.0 | TSDPL Kalinganagar edition — 5 new tabs, 4 new modules, 11 machines, 22 failure codes, shift roster, PM checklist, health scorecard, MoM comparison |
| v2.1 | Dark high-contrast UI overhaul, advanced failure modes, Health Score tab, loading transitions |
| v2.2 | Real-world messy file normalizer (`utils/messy_loader.py`), QIP Analysis tab, security-hardened upload validation |

---

## ✨ Whats New in v2.2

### 🧹 Real-World Messy File Normalizer
A new standalone module `utils/messy_loader.py` handles the messy CSV/Excel exports that real factory managers actually produce:

- **Smart header detection** — automatically skips metadata rows (titles, report dates, plant names) and finds the real header row as the first row with ≥ 3 non-null values
- **Column alias mapping engine** — a central `COLUMN_ALIASES` dictionary maps every known variant of `Date`, `Duration_Min`, `Equipment`, and `Reason` found across different file sources. New aliases can be added in one place with no other code changes
- **Robust date parsing** — `pd.to_datetime(dayfirst=True)` covers ISO, DD.MM.YYYY, and European formats; a second pass strips apostrophes to handle `Sept'25` / `Sep'25` style strings
- **Duration unit detection** — automatically detects whether the duration column is in minutes or hours (by inspecting column name substrings like `HOURS`, `HRS`) and converts to minutes. Always stores `Duration_Min` as a numeric minute value
- **Unnamed column cleanup** — drops all `Unnamed:` and entirely-empty columns produced by Excel merged-cell formatting
- **UTF-8 / latin-1 fallback** — Windows-exported CSVs with special characters are handled automatically

### 📊 QIP Analysis Tab (Tab 12)
A new **📊 QIP Analysis** tab for presenting before/after maintenance improvement results:

- Equipment filter to focus on specific machines
- Two independent date pickers — **Baseline Period** and **Improvement Period**
- Computed metrics for each period: MTBF (hours), MTTR (minutes), failure count, total downtime
- Delta cards with directional colour coding (green = improved, red = worsened)
- Grouped bar chart comparing all four metrics side by side
- Auto-generated narrative verdict: `🟢 Both improved / 🟡 Mixed / 🔴 Neither improved`
- Raw data expanders for baseline and improvement windows for audit traceability

### 🔒 Security-Hardened Upload Pipeline
The existing upload path and the new messy uploader share the same `validate_file_upload()` guard:

- 50 MB file size cap
- Allowlist of extensions: `csv`, `xlsx`, `xls`
- UTF-8 magic-byte check for CSV files
- Detailed errors logged server-side; only safe messages shown to the user

### 🗂️ Sidebar — Second Upload Section
A clearly separated **🔬 Upload Real-World Data** section added below the existing clean-format uploader. It uploads into its own session state key (`normalized_df`) so it never interferes with the existing generic tabs (1–5) or TSDPL tabs (6–11).

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Setup
```bash
# 1. Clone the repository
git clone https://github.com/asg-7/Machine-Failure-Prediction-Uptime-Analytics-System.git
cd Machine-Failure-Prediction-Uptime-Analytics-System

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Generate a sample CSV for the generic demo
python generate_sample_data.py

# 4. Launch the dashboard
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## 🗺️ Dashboard Navigation

The dashboard runs in two modes — click **🎲 Generic Demo** for tabs 1–5 (works with any CSV upload), **🏭 TSDPL Demo** for tabs 6–11 (pre-loaded Kalinganagar plant data), or upload a real-world messy file for the **📊 QIP Analysis** tab.

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
| 9 | 🌡️ Health Scorecard | Sensor alarm heatmap, operational limits table, parameter trend drilldown, flapping score |
| 10 | 💚 Health Score | Composite 0–100 gauge per machine, sub-score breakdown table |
| 11 | 📅 Month-over-Month | MoM grid chart, MTBF scorecard cards, DAX + Excel formula reference, failure code glossary |

### New in v2.2

| Tab | Title | Core Feature |
|---|---|---|
| 12 | 📊 QIP Analysis | Upload messy file → select baseline & improvement periods → MTBF/MTTR delta cards + chart + verdict |

### Quick-find guide

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
| View composite machine health | Tab 10 → Health Score gauges |
| Present MTBF scorecard to management | Tab 11 → MoM scorecard cards |

---

## 🗂️ File Structure

```
machine_failure_app/
│
├── app.py                          # Main entry — 12-tab dual-mode dashboard (v2.2)
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
│   ├── tsdpl_charts.py             # 8 Plotly charts for tabs 6–11
│   └── messy_loader.py             # ✨ NEW v2.2 — real-world file normalizer + QIP helpers
│
└── components/
    ├── __init__.py
    └── ui_components.py            # Reusable Streamlit HTML/CSS components
```

| File | Lines |
|---|---|
| app.py | ~720 |
| utils/tsdpl_charts.py | 416 |
| utils/tsdpl_constants.py | 272 |
| utils/tsdpl_demo_data.py | 303 |
| utils/tsdpl_analytics.py | 237 |
| utils/charts.py | 260 |
| utils/predictor.py | 199 |
| utils/analytics.py | 166 |
| utils/messy_loader.py | ~230 ✨ new |
| utils/data_loader.py | 93 |
| components/ui_components.py | 148 |
| **Total** | **~3,050** |

---

## 📂 Input Data Format

### Generic uploader (Tabs 1–5) — clean UP/DOWN format

Upload a CSV or Excel file with the following structure:

| timestamp | machine_id | status | temperature | load | vibration |
|---|---|---|---|---|---|
| 2024-01-01 00:00 | MCH-001 | UP | 72.3 | 85 | 1.2 |
| 2024-01-01 00:30 | MCH-001 | DOWN | 45.1 | 0 | 0.1 |

**Required columns:**

| Column | Type | Notes |
|---|---|---|
| timestamp | datetime string | Any format parseable by `pd.to_datetime()` |
| machine_id | string | Any non-null identifier |
| status | string | `UP` or `DOWN` (case-insensitive) |

**Optional columns** — enable sensor trend charts and anomaly scoring:

| Column | Type |
|---|---|
| temperature | numeric |
| load | numeric |
| vibration | numeric |

Invalid values in optional columns are coerced to `NaN` rather than causing an error.

### Messy uploader (Tab 12 — QIP Analysis) — any real-world format

The `normalize_maintenance_data()` function accepts files with any of these variations and normalises them to four standard columns:

| Standard Column | Accepted Aliases |
|---|---|
| `Date` | `DATE`, `Date`, `Month`, `MONTH`, `Sl No`, `Period` |
| `Duration_Min` | `UNPLANNED B/D (Min.)`, `Time (Min)`, `Min`, `B/D HOURS`, `Downtime Hours`, `Duration`, `HRS` |
| `Equipment` | `EQUIPMENT`, `Work Centre`, `Machine`, `AREA`, `Asset` |
| `Reason` | `BRIEF DESCRIPTION`, `Description`, `Desc`, `Failure Reason`, `Remarks`, `Root Cause` |

Files may have any number of metadata rows above the real header — the normalizer finds the header automatically. Duration columns in hours are detected by column name and converted to minutes automatically.

---

## 🧠 How It Works

### 1. Data Processing
Cleans and validates the upload, parses timestamps, uppercases status values, and coerces sensor columns to numeric.

### 2. Failure Detection
Identifies UP → DOWN transitions as failure events and calculates runtime before each failure, the hour-of-day it occurred, and whether it qualifies as a short/flapping event (< 30 min).

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

### 5. Health Score (v2.1)
Composite 0–100 score per machine, combining four signals:

| Signal | Source |
|---|---|
| Runtime risk | Prediction engine above |
| Sensor anomaly score | Z-score deviation of recent 10% UP readings vs baseline, capped at 100 |
| Flapping score | Count of short DOWN events in the rolling 7-day window |
| PM compliance | Based on maintenance record age and overdue flags |

### 6. Messy File Normalizer (v2.2)
The `normalize_maintenance_data()` pipeline runs in six steps:

```
Step 1 — _read_raw()          Read CSV/Excel with no assumed header (header=None)
Step 2 — _extract_table()     Find first row with ≥3 non-null values = real header; discard metadata above
Step 3 — _map_columns()       Fuzzy alias matching → Date / Duration_Min / Equipment / Reason
Step 4 — _parse_dates()       pd.to_datetime(dayfirst=True) + apostrophe-strip second pass
Step 5 — _parse_duration()    pd.to_numeric(errors='coerce') + ×60 if hours column detected
Step 6 — _final_clean()       Drop null Duration/Equipment rows, zero-duration rows, reset index
```

### 7. QIP MTBF/MTTR Computation (v2.2)
`compute_mtbf_mttr_from_norm()` computes per-period metrics from any normalised DataFrame:

```
period_hours    = (date_max − date_min).total_seconds() / 3600
uptime_hours    = period_hours − (total_downtime_min / 60)
MTBF (hours)    = uptime_hours / failure_count
MTTR (minutes)  = total_downtime_min / failure_count
```

---

## 📖 Module Reference

### utils/data_loader.py

| Function | Returns | Description |
|---|---|---|
| `load_data(uploaded_file)` | `(df, error)` | Reads CSV or Excel. `error` is `None` on success |
| `validate_and_preprocess(df)` | `df` | Normalises columns, parses timestamps, coerces sensors |
| `get_data_summary(df)` | `dict` | `{total_records, machines, date_range, has_temperature, has_load, has_vibration}` |

### utils/analytics.py

| Function | Description |
|---|---|
| `compute_uptime_downtime(df)` | Per-machine `uptime_pct`, `downtime_pct`, `uptime_hours`, `downtime_hours` |
| `extract_failure_events(df)` | Detects UP→DOWN transitions; returns `failure_time`, `runtime_before_failure_hours`, `hour_of_day` |
| `compute_failure_patterns(failure_events)` | Aggregates `failure_count`, `avg/std/min/max_runtime_h`, `most_common_failure_hour` |
| `compute_hourly_failure_trend(failure_events)` | Failure count by hour-of-day (0–23), always 24 rows |
| `compute_daily_uptime(df)` | Daily uptime percentage per machine |
| `compute_flapping_score(failure_events)` | Count of DOWN events < 30 min per machine in rolling 7-day window (v2.1) |

### utils/predictor.py

| Function | Description |
|---|---|
| `predict_machine(failure_events_machine, df_machine)` | Single-machine prediction dict |
| `predict_all_machines(df, failure_events)` | Fleet-wide predictions sorted by `risk_value` descending |
| `compute_sensor_anomaly_score(df_machine)` | Z-score deviation of recent 10% UP readings vs baseline, capped at 100 |
| `compute_health_score(risk_value, anomaly_score, flapping_score, pm_compliance)` | Composite 0–100 score (v2.1) |

### utils/messy_loader.py ✨ new in v2.2

| Function | Description |
|---|---|
| `normalize_maintenance_data(uploaded_file)` | Public API — reads any messy CSV/Excel, returns `(clean_df, error)` |
| `_read_raw(uploaded_file)` | Reads file with `header=None`; UTF-8 with latin-1 fallback for CSV |
| `_extract_table(raw_df)` | Locates header row (first row with ≥3 non-null values), strips metadata |
| `_map_columns(data_df)` | Alias matching → standard names; detects hours-denominated duration columns |
| `_parse_dates(df)` | `pd.to_datetime(dayfirst=True)` + apostrophe-strip second pass; drops NaT rows |
| `_parse_duration(df, hours_col)` | Coerces to numeric; multiplies by 60 if hours column detected; clips negatives |
| `_final_clean(df)` | Drops null Duration/Equipment, zero-duration rows; strips whitespace |
| `compute_mtbf_mttr_from_norm(df, period_mask)` | Computes MTBF, MTTR, failure count, downtime for a given time window mask |

**To add a new column alias** — edit `COLUMN_ALIASES` in `messy_loader.py`. No other files need to change.

### utils/tsdpl_analytics.py

| Function | Description |
|---|---|
| `compute_mtbf_mttr(downtime_log)` | Per-machine `MTBF_hours`, `MTTR_min`, `availability_pct` |
| `compute_shift_mtbf_mttr(downtime_log)` | Same metrics grouped by `(machine_id, shift)` |
| `compute_oee_loss(downtime_log)` | Per `(machine_id, shift)`: OEE availability loss and downtime by category |
| `compute_mom_comparison(downtime_log)` | Per machine: trend (Improving/Worsening/Stable), delta downtime, top failure mode |
| `compute_sensor_scorecard(sensor_df)` | Per `(machine_id, parameter)`: status (Normal/WARNING/ALARM), trend arrow |

MoM trend thresholds: Improving if `mtbf_this / mtbf_last > 1.05` · Worsening if `< 0.95` · Stable otherwise.

### utils/tsdpl_charts.py

| Function | Chart Type |
|---|---|
| `chart_shift_tornado` | Diverging horizontal bar — Night on negative X, Morning/Afternoon on positive |
| `chart_mtbf_by_shift` | Grouped vertical bar — metric switchable between MTBF / MTTR / downtime |
| `chart_sensor_heatmap` | Heatmap with ✅ / ⚠️ / 🚨 emoji overlays |
| `chart_param_trend` | Scatter + rolling average + alarm threshold lines |
| `chart_failure_category_donut` | Donut pie by failure category |
| `chart_mom_grid` | 3×N subplot bar grid — last month slate, this month trend-coloured |
| `chart_pm_status` | Stacked bar by status (Completed / Overdue / Scheduled) |
| `chart_incident_timeline` | Gantt-style scatter — each incident a thick line from start to start + duration |

All charts apply the `"tsdpl"` Plotly template automatically.

### components/ui_components.py

| Function | Description |
|---|---|
| `risk_badge_html(label)` | Inline `<span>` badge coloured by risk label |
| `metric_card(title, value, delta, color)` | Left-bordered card with large value and optional delta |
| `alert_banner(message, level)` | Full-width coloured banner — levels: `info / warning / error / success` |
| `render_prediction_card(row)` | 3-column machine prediction card: risk, TTF, confidence |
| `render_alert_machines(predictions)` | Error/warning/success banner based on fleet risk state |
| `section_header(title, subtitle)` | H3 + subtitle with consistent spacing |

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

### PM Frequency Map

| Frequency | Hours |
|---|---|
| Per Coil | 8 |
| Per Coil Batch | 16 |
| Shift | 8 |
| Daily | 24 |
| Weekly | 168 |
| Monthly | 720 |
| Quarterly | 2,160 |

### Messy Loader — Column Alias Map (v2.2)

| Standard Column | Accepted Aliases |
|---|---|
| `Date` | `DATE`, `Date`, `date`, `Month`, `MONTH`, `Sl No`, `Period` |
| `Duration_Min` | `UNPLANNED B/D (Min.)`, `Time (Min)`, `Min`, `B/D HOURS`, `Downtime Hours`, `Duration`, `HRS`, `HOURS` |
| `Equipment` | `EQUIPMENT`, `Work Centre`, `Machine`, `AREA`, `Asset`, `machine_id` |
| `Reason` | `BRIEF DESCRIPTION`, `Description`, `Desc`, `Failure Reason`, `Remarks`, `Root Cause` |

---

## 🎨 UI and Design System

### Color Palette

| Role | Hex | Usage |
|---|---|---|
| App background | `#0b1120` | Outermost shell |
| Card background | `#0d1f35` | KPI cards, chart containers |
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
    background: #0d1526; border-radius: 8px; padding: 3px; gap: 2px;
    overflow-x: auto; overflow-y: hidden;
    flex-wrap: nowrap; scrollbar-width: none;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] {
    border-radius: 6px; color: #64748b;
    font-size: clamp(13px, 1.1vw, 16px) !important;
    font-weight: 500 !important; padding: 8px 14px !important;
    white-space: nowrap;
}
.stTabs [aria-selected="true"]  { background: #1e3a5f !important; color: #f1f5f9 !important; }
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

```python
import plotly.io as pio

pio.templates["tsdpl"] = pio.templates["plotly"].update({
    "layout": {
        "paper_bgcolor": "#0b1120",
        "plot_bgcolor":  "#0d1f35",
        "font":          {"color": "#94a3b8", "family": "Inter, system-ui, sans-serif"},
        "colorway":      ["#38bdf8", "#4ade80", "#fbbf24", "#f87171", "#c084fc"],
        "xaxis": {"gridcolor": "#1e293b", "linecolor": "#1e3a5f", "tickcolor": "#475569"},
        "yaxis": {"gridcolor": "#1e293b", "linecolor": "#1e3a5f", "tickcolor": "#475569"},
        "legend":     {"bgcolor": "#0d1f35", "bordercolor": "#1e3a5f", "borderwidth": 1},
        "hoverlabel": {"bgcolor": "#0d1526", "bordercolor": "#38bdf8", "font": {"color": "#f1f5f9"}}
    }
})
pio.templates.default = "tsdpl"
```

---

## 🗺️ Roadmap

| Feature | Priority | Complexity | Notes |
|---|---|---|---|
| Weibull survival analysis (RUL model) | 🔴 High | Medium | `lifelines` library; handles machines with no recent failures via shape parameter β |
| Isolation Forest anomaly detection | 🔴 High | Low | Multivariate sensor anomaly; feeds directly into health score |
| Sensor-weighted composite risk score | 🔴 High | Low | Anomaly score already computed — merge into `risk_value` |
| Work Order PDF export | 🔴 High | Medium | `fpdf2`; per-machine work order generated from high-risk card |
| SQLite backend + incremental append | 🟡 Medium | Medium | Zero infrastructure; deduplicated by `timestamp + machine_id` |
| FMEA RPN table | 🟡 Medium | Low | Severity × Occurrence × Detectability mapped from failure_code taxonomy |
| MTTR by technician + repeat failure rate | 🟡 Medium | Low | Accountability KPI; flag machines failing within 48h of repair |
| Shift handover one-page PDF | 🟡 Medium | Low | Auto-generated at shift change: at-risk machines, open PM, recent failures |
| Date range sidebar filter | 🟡 Medium | Low | Applied across all 12 tabs |
| Configurable flapping threshold | 🟡 Medium | Low | Currently hardcoded at 30 min — should be per machine type |
| Messy loader: editable alias UI | 🟡 Medium | Low | Let users define column mappings in-app without editing `messy_loader.py` |
| Power BI .pbix template | 🔵 Low | High | DAX measures already documented in Tab 11 |
| Comparative period selector | 🔵 Low | Medium | Any two custom date windows, not just calendar months |

---

## ⚠️ Known Limitations

- **TTF model requires 2+ failure events per machine.** Machines with 0 or 1 failures receive a static fallback risk score (10 or 35 respectively).
- **Long-runtime machines are under-risk-scored.** A machine UP for a long time with no historical failures reads Low risk even if statistically overdue. A no-failure-but-long-runtime penalty is not yet implemented.
- **Sensor anomaly score is not yet merged into `risk_value`.** Both signals are shown separately in v2.1; full fusion is on the roadmap.
- **Shift roster is generated, not editable.** There is no in-app form to log actual shift assignments or mark a repair as complete.
- **Single-file upload only (generic tabs).** Each upload replaces the previous dataset. Incremental append is planned via SQLite backend.
- **Flapping threshold is fixed at 30 minutes.** This should be configurable per machine type but is currently hardcoded.
- **Messy loader requires at least one matched column per standard name.** Files missing any of Date, Duration, Equipment, or Reason will return an error listing which columns could not be found.
- **QIP MTBF is span-based, not operational-hours-based.** Period hours are computed from first to last event timestamp, not from actual production calendar hours.

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| UI / Frontend | Streamlit |
| Data processing | Pandas 2.x, NumPy |
| Visualisation | Plotly (custom `tsdpl` dark template) |
| Modelling | Statistical heuristics — moving average + linear regression |
| Styling | Custom CSS injection via `st.markdown` |

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a pull request

---

## 📜 License

This project is licensed under the MIT License — see `LICENSE` for details.

---

## 👤 Author

**Anubhav Sengupta** &nbsp; GitHub [@asg-7](https://github.com/asg-7) · anubhavsengupta618@gmail.com

> ⭐ If this dashboard helped you, drop a star — it really helps!

---

*TSDPL Kalinganagar Maintenance Dashboard · v2.2 · April 2026*
