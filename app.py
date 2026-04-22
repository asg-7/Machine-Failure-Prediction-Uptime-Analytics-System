"""
app.py
Machine Failure Prediction & Uptime Analytics System
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# ── path setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from utils.data_loader import load_data, get_data_summary
from utils.analytics import (
    compute_uptime_downtime,
    extract_failure_events,
    compute_failure_patterns,
    compute_hourly_failure_trend,
    compute_daily_uptime,
)
from utils.predictor import predict_all_machines, compute_sensor_anomaly_score
from utils.charts import (
    chart_uptime_downtime,
    chart_daily_uptime_trend,
    chart_failure_frequency,
    chart_hourly_failure_trend,
    chart_risk_ranking,
    chart_ttf_prediction,
    chart_sensor_trend,
)
from components.ui_components import (
    metric_card,
    alert_banner,
    render_prediction_card,
    render_alert_machines,
    section_header,
    risk_badge_html,
)


# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Machine Failure Analytics",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
    /* Modern Card Styles (Formal, Glass/Sleek) */
    .modern-card {
        background: rgba(120, 120, 120, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(120, 120, 120, 0.15);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        cursor: pointer;
        animation: slideUp 0.6s ease-out forwards;
        opacity: 0;
        height: 100%;
    }
    
    .modern-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
        border-color: rgba(120, 120, 120, 0.3);
        background: rgba(120, 120, 120, 0.08);
    }
    
    .modern-card h3 {
        font-weight: 600;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
        font-size: 1.3rem;
    }
    
    .modern-card p {
        opacity: 0.8;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 0;
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Staggered animation delays for the 4 cards */
    div[data-testid="column"]:nth-child(1) .modern-card { animation-delay: 0.1s; }
    div[data-testid="column"]:nth-child(2) .modern-card { animation-delay: 0.2s; }
    div[data-testid="column"]:nth-child(3) .modern-card { animation-delay: 0.3s; }
    div[data-testid="column"]:nth-child(4) .modern-card { animation-delay: 0.4s; }

    /* General Typography & Spacing enhancements */
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 700 !important; letter-spacing: -0.5px; }
    .stDataFrame { border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid rgba(120,120,120,0.1); }
    h1, h2, h3 { letter-spacing: -0.03em; }

    /* Tab visibility fix — force full readability on all themes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 2px solid rgba(120,120,120,0.2);
    }
    /* Force tab button and ALL children to use full opacity visible text */
    .stTabs [data-baseweb="tab"],
    .stTabs [data-baseweb="tab"] *,
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] div {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        color: rgba(200, 200, 200, 0.9) !important;
        opacity: 1 !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px !important;
        border-radius: 8px 8px 0 0 !important;
        transition: background 0.2s ease !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"]:hover,
    .stTabs [data-baseweb="tab"]:hover * {
        color: #ffffff !important;
        background: rgba(120,120,120,0.12) !important;
    }
    /* Active/selected tab — bright white text */
    .stTabs [aria-selected="true"],
    .stTabs [aria-selected="true"] *,
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] div {
        color: #ffffff !important;
        opacity: 1 !important;
    }
    /* Indigo active indicator bar */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #6366F1 !important;
        height: 3px !important;
        border-radius: 2px !important;
    }
    
</style>
""", unsafe_allow_html=True)


# ── session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "summary" not in st.session_state:
    st.session_state.summary = None


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Machine Failure Analytics")
    st.markdown("---")

    # File upload
    st.markdown("### 📂 Upload Data")
    uploaded = st.file_uploader(
        "CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Required columns: timestamp, machine_id, status (UP/DOWN). "
             "Optional: temperature, load, vibration",
    )

    if uploaded:
        with st.spinner("Loading data..."):
            df, err = load_data(uploaded)
        if err:
            st.error(f"❌ {err}")
            st.session_state.df = None
        else:
            st.session_state.df = df
            st.session_state.summary = get_data_summary(df)
            st.success(f"✅ Loaded {len(df):,} records")

    # Demo data
    st.markdown("---")
    if st.button("🎲 Load Demo Data", use_container_width=True):
        with st.spinner("Generating demo dataset..."):
            import tempfile, os
            from generate_sample_data import generate_sample_data
            _tmp_path = os.path.join(tempfile.gettempdir(), "demo.csv")
            df_demo = generate_sample_data(n_machines=6, days=45, output_path=_tmp_path)
            df_clean, _ = __import__("utils.data_loader", fromlist=["validate_and_preprocess"]).validate_and_preprocess(df_demo)
            st.session_state.df = df_clean
            st.session_state.summary = get_data_summary(df_clean)
            st.success("✅ Demo data loaded (6 machines, 45 days)")

    # Sidebar summary
    if st.session_state.summary:
        s = st.session_state.summary
        st.markdown("---")
        st.markdown("### 📊 Dataset Info")
        st.markdown(f"**Records:** {s['total_records']:,}")
        st.markdown(f"**Machines:** {len(s['machines'])}")
        st.markdown(f"**From:** {s['date_range'][0].strftime('%Y-%m-%d')}")
        st.markdown(f"**To:** {s['date_range'][1].strftime('%Y-%m-%d')}")

        sensors = []
        if s["has_temperature"]: sensors.append("🌡 Temp")
        if s["has_load"]: sensors.append("⚡ Load")
        if s["has_vibration"]: sensors.append("📳 Vibration")
        if sensors:
            st.markdown(f"**Sensors:** {', '.join(sensors)}")

        st.markdown("---")
        st.markdown("### 🔍 Machine Filter")
        all_machines = s["machines"]
        selected = st.multiselect(
            "Select machines",
            options=all_machines,
            default=all_machines,
            label_visibility="collapsed",
        )
        st.session_state.selected_machines = selected

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.75em;color:#94A3B8;text-align:center;">'
        'Machine Failure Analytics v1.0<br>Plant Operations Intelligence</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

if st.session_state.df is None:
    # ── Landing page ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:60px 20px 40px; animation: fadeIn 1s ease-in;">
        <div style="font-size:4rem; margin-bottom: 20px; text-shadow: 0 4px 12px rgba(0,0,0,0.1);">⚙️</div>
        <h1 style="margin:10px 0; font-weight: 700; letter-spacing: -1px;">Machine Failure Prediction</h1>
        <h3 style="opacity: 0.8; font-weight: 400; margin-bottom: 20px;">& Uptime Analytics System</h3>
        <p style="opacity: 0.6; max-width:600px; margin:0 auto; font-size: 1.1rem; line-height: 1.6;">
            Upload your plant data or load the demo dataset to get started.
            Predict failures, rank machine risk, and plan maintenance proactively.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="modern-card">
            <div style="font-size: 2.5rem; margin-bottom: 15px;">📊</div>
            <h3>Uptime Tracking</h3>
            <p>Detailed monitoring of machine availability and operational cycles.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="modern-card">
            <div style="font-size: 2.5rem; margin-bottom: 15px;">🔮</div>
            <h3>Failure Prediction</h3>
            <p>Estimate time-to-failure with regression models.</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="modern-card">
            <div style="font-size: 2.5rem; margin-bottom: 15px;">🎯</div>
            <h3>Risk Ranking</h3>
            <p>Low / Medium / High risk classification.</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="modern-card">
            <div style="font-size: 2.5rem; margin-bottom: 15px;">🚨</div>
            <h3>Smart Alerts</h3>
            <p>Highlight machines needing urgent attention.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    alert_banner(
        "👈 Upload a CSV/Excel file in the sidebar, or click <strong>Load Demo Data</strong> to explore.",
        level="info",
    )

    # CSV format guide
    with st.expander("📋 Expected CSV Format"):
        st.markdown("""
        | timestamp | machine_id | status | temperature | load | vibration |
        |-----------|------------|--------|-------------|------|-----------|
        | 2024-01-01 00:00:00 | MCH-001 | UP | 72.3 | 85.0 | 1.2 |
        | 2024-01-01 00:30:00 | MCH-001 | DOWN | 45.1 | 0 | 0.1 |

        - **timestamp** – datetime string (any standard format)
        - **machine_id** – unique machine identifier
        - **status** – `UP` or `DOWN`
        - **temperature, load, vibration** – optional sensor readings
        """)
    st.stop()


# ── Data is loaded — run analytics ───────────────────────────────────────────
df_all = st.session_state.df
selected_machines = st.session_state.get("selected_machines", df_all["machine_id"].unique().tolist())

# Filter by selection
df = df_all[df_all["machine_id"].isin(selected_machines)] if selected_machines else df_all

# Core computations (cached via st.cache_data pattern with hash)
@st.cache_data(show_spinner=False)
def run_analytics(df_hash, df):
    uptime_df = compute_uptime_downtime(df)
    failure_events = extract_failure_events(df)
    failure_patterns = compute_failure_patterns(failure_events)
    hourly_trend = compute_hourly_failure_trend(failure_events)
    daily_uptime = compute_daily_uptime(df)
    predictions = predict_all_machines(df, failure_events)
    return uptime_df, failure_events, failure_patterns, hourly_trend, daily_uptime, predictions

# Use a simple hash to trigger recompute on new data or selection
df_hash = (len(df), tuple(sorted(selected_machines)), df["timestamp"].max().isoformat())
uptime_df, failure_events, failure_patterns, hourly_trend, daily_uptime, predictions = run_analytics(df_hash, df)


# ── Tab layout ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "📈 Uptime Analysis",
    "💥 Failure Patterns",
    "🔮 Predictions & Risk",
    "🔬 Machine Drilldown",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 🏠 Operations Overview")

    # Alert banner
    render_alert_machines(predictions)
    st.markdown("")

    # KPI row
    total_records = len(df)
    avg_uptime = uptime_df["uptime_pct"].mean() if not uptime_df.empty else 0
    total_failures = len(failure_events)
    high_risk = len(predictions[predictions["risk_label"] == "High"]) if not predictions.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Records", f"{total_records:,}", color="#6366F1")
    with c2:
        metric_card("Avg Fleet Uptime", f"{avg_uptime:.1f}%",
                    delta="↑ Good" if avg_uptime >= 90 else "↓ Below 90% target",
                    color="#22C55E" if avg_uptime >= 90 else "#F59E0B")
    with c3:
        metric_card("Total Failures", str(total_failures), color="#EF4444")
    with c4:
        metric_card("High Risk Machines", str(high_risk),
                    color="#EF4444" if high_risk > 0 else "#22C55E")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row
    col1, col2 = st.columns(2)
    with col1:
        section_header("Uptime vs Downtime", "Stacked percentage per machine")
        st.plotly_chart(chart_uptime_downtime(uptime_df), use_container_width=True, key="overview_uptime")
    with col2:
        section_header("Machine Risk Ranking", "Current risk score (0–100)")
        st.plotly_chart(chart_risk_ranking(predictions), use_container_width=True, key="overview_risk")

    # Summary table
    section_header("Machine Summary Table")
    if not uptime_df.empty and not predictions.empty:
        summary_table = uptime_df[["uptime_pct", "downtime_hours", "uptime_hours"]].copy()
        pred_cols = predictions.set_index("machine_id")[
            ["failure_count", "predicted_ttf_hours", "remaining_ttf_hours", "risk_label", "risk_value"]
        ]
        summary_table = summary_table.join(pred_cols, how="left")
        summary_table["risk_label"] = summary_table["risk_label"].fillna("Unknown")

        def style_risk(val):
            styles = {
                "High":    "background-color:#EF4444;color:#ffffff;font-weight:600;border-radius:4px;",
                "Medium":  "background-color:#F59E0B;color:#ffffff;font-weight:600;border-radius:4px;",
                "Low":     "background-color:#22C55E;color:#ffffff;font-weight:600;border-radius:4px;",
                "Unknown": "color:inherit;",
            }
            return styles.get(val, "")

        styled = summary_table.style.map(style_risk, subset=["risk_label"])
        st.dataframe(styled, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — UPTIME ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 📈 Uptime & Downtime Analysis")

    if uptime_df.empty:
        alert_banner("No uptime data available for selected machines.", "warning")
    else:
        # Metrics
        best_machine = uptime_df["uptime_pct"].idxmax()
        worst_machine = uptime_df["uptime_pct"].idxmin()

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Best Performer", best_machine,
                        delta=f"{uptime_df.loc[best_machine,'uptime_pct']}% uptime",
                        color="#22C55E")
        with c2:
            metric_card("Needs Attention", worst_machine,
                        delta=f"{uptime_df.loc[worst_machine,'uptime_pct']}% uptime",
                        color="#EF4444")
        with c3:
            total_downtime_h = uptime_df["downtime_hours"].sum()
            metric_card("Total Downtime", f"{total_downtime_h:.0f} h",
                        delta="Across all selected machines", color="#F59E0B")

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            section_header("Uptime vs Downtime per Machine")
            st.plotly_chart(chart_uptime_downtime(uptime_df), use_container_width=True, key="uptime_downtime_chart")
        with col2:
            section_header("Daily Uptime Trend")
            st.plotly_chart(
                chart_daily_uptime_trend(daily_uptime, selected_machines),
                use_container_width=True,
                key="daily_uptime_trend"
            )

        section_header("Detailed Uptime Table")
        st.dataframe(
            uptime_df.reset_index().rename(columns={
                "machine_id": "Machine", "uptime_pct": "Uptime %",
                "downtime_pct": "Downtime %", "uptime_hours": "Uptime (h)",
                "downtime_hours": "Downtime (h)", "up_count": "UP Records",
                "down_count": "DOWN Records",
            }),
            use_container_width=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FAILURE PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 💥 Failure Pattern Detection")

    if failure_events.empty:
        alert_banner("No failure events (UP→DOWN transitions) detected in the selected data.", "info")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Total Failure Events", str(len(failure_events)), color="#EF4444")
        with c2:
            avg_rt = failure_events["runtime_before_failure_hours"].mean()
            metric_card("Avg Runtime Before Failure", f"{avg_rt:.1f} h", color="#F59E0B")
        with c3:
            most_failures = failure_events["machine_id"].value_counts().idxmax()
            metric_card("Most Failures", most_failures, color="#6366F1")

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            section_header("Failure Frequency per Machine")
            st.plotly_chart(chart_failure_frequency(failure_patterns), use_container_width=True, key="failure_freq")
        with col2:
            section_header("Failures by Hour of Day", "Identify peak failure windows")
            st.plotly_chart(chart_hourly_failure_trend(hourly_trend), use_container_width=True, key="failure_hourly")

        section_header("Failure Event Log")
        fe_display = failure_events.copy()
        fe_display["failure_time"] = fe_display["failure_time"].dt.strftime("%Y-%m-%d %H:%M")
        fe_display["runtime_before_failure_hours"] = fe_display["runtime_before_failure_hours"].round(2)
        st.dataframe(
            fe_display.rename(columns={
                "machine_id": "Machine", "failure_time": "Failure Time",
                "runtime_before_failure_hours": "Runtime Before Failure (h)",
                "hour_of_day": "Hour", "day_of_week": "Day",
            }),
            use_container_width=True,
        )

        if not failure_patterns.empty:
            section_header("Runtime Statistics per Machine")
            st.dataframe(failure_patterns.reset_index().rename(columns={
                "machine_id": "Machine", "failure_count": "Failures",
                "avg_runtime_h": "Avg Runtime (h)", "std_runtime_h": "Std Dev (h)",
                "min_runtime_h": "Min Runtime (h)", "max_runtime_h": "Max Runtime (h)",
                "most_common_failure_hour": "Peak Failure Hour",
            }), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PREDICTIONS & RISK
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 🔮 Failure Predictions & Risk Assessment")

    if predictions.empty:
        alert_banner("No predictions available.", "warning")
    else:
        render_alert_machines(predictions)
        st.markdown("")

        section_header("Risk Cards", "Real-time assessment per machine")
        cols_per_row = 2
        pred_rows = [
            predictions.iloc[i:i+cols_per_row]
            for i in range(0, len(predictions), cols_per_row)
        ]
        for row_df in pred_rows:
            cols = st.columns(cols_per_row)
            for col, (_, pred_row) in zip(cols, row_df.iterrows()):
                with col:
                    render_prediction_card(pred_row)

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            section_header("Risk Score Ranking")
            st.plotly_chart(chart_risk_ranking(predictions), use_container_width=True, key="risk_ranking_chart")
        with col2:
            section_header("Time-to-Failure Breakdown")
            st.plotly_chart(chart_ttf_prediction(predictions), use_container_width=True, key="ttf_breakdown")

        section_header("Full Prediction Table")
        pred_display = predictions.copy()
        pred_display["risk_label"] = pred_display["risk_label"]
        st.dataframe(
            pred_display.rename(columns={
                "machine_id": "Machine", "failure_count": "Failures",
                "avg_runtime_h": "Avg Runtime (h)", "predicted_ttf_hours": "Predicted TTF (h)",
                "current_run_hours": "Current Run (h)", "remaining_ttf_hours": "Remaining TTF (h)",
                "risk_label": "Risk Level", "risk_value": "Risk Score",
                "confidence": "Model Confidence",
            }),
            use_container_width=True,
        )

        # Maintenance planning insight
        section_header("💡 Maintenance Planning Insights")
        high_df = predictions[predictions["risk_label"] == "High"]
        med_df = predictions[predictions["risk_label"] == "Medium"]

        if not high_df.empty:
            machines_str = ", ".join(high_df["machine_id"].tolist())
            alert_banner(
                f"<strong>Immediate Action Required:</strong> {machines_str} should be inspected "
                "before next shift. Risk score ≥ 70.",
                level="error",
            )
        if not med_df.empty:
            machines_str = ", ".join(med_df["machine_id"].tolist())
            min_rem = med_df["remaining_ttf_hours"].min()
            alert_banner(
                f"<strong>Plan Within Next Cycle:</strong> {machines_str} — "
                f"shortest remaining TTF is {min_rem:.1f} h.",
                level="warning",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — MACHINE DRILLDOWN
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("## 🔬 Machine Drilldown")

    if not selected_machines:
        alert_banner("No machines selected.", "warning")
    else:
        chosen = st.selectbox("Select a machine to inspect:", options=selected_machines)
        df_m = df[df["machine_id"] == chosen]

        if df_m.empty:
            alert_banner(f"No data for {chosen}.", "warning")
        else:
            # Find prediction row
            pred_row = predictions[predictions["machine_id"] == chosen]

            # Machine stats header
            col_l, col_r = st.columns([2, 1])
            with col_l:
                section_header(f"Machine: {chosen}", f"{len(df_m):,} records")
            with col_r:
                if not pred_row.empty:
                    render_prediction_card(pred_row.iloc[0])

            # Sensor anomaly
            anomaly_score = compute_sensor_anomaly_score(df_m)
            if anomaly_score > 0:
                level = "error" if anomaly_score > 60 else ("warning" if anomaly_score > 30 else "success")
                alert_banner(
                    f"Sensor Anomaly Score: <strong>{anomaly_score:.1f}/100</strong> — "
                    f"{'Significant deviation from baseline' if anomaly_score > 30 else 'Normal range'}",
                    level=level,
                )

            # Sensor charts
            sensors_available = [
                s for s in ["temperature", "load", "vibration"]
                if df_m[s].notna().any()
            ]

            if sensors_available:
                section_header("Sensor Trends")
                sensor_choice = st.radio(
                    "Sensor", sensors_available,
                    horizontal=True, label_visibility="collapsed",
                )
                st.plotly_chart(
                    chart_sensor_trend(df_m, sensor_choice, chosen),
                    use_container_width=True,
                    key="sensor_trend_chart"
                )

            # Failure events for this machine
            fe_m = failure_events[failure_events["machine_id"] == chosen] if not failure_events.empty else pd.DataFrame()
            section_header(f"Failure Events ({len(fe_m)} total)")
            if fe_m.empty:
                alert_banner("No failure events recorded for this machine.", "info")
            else:
                fe_m_display = fe_m.copy()
                fe_m_display["failure_time"] = fe_m_display["failure_time"].dt.strftime("%Y-%m-%d %H:%M")
                st.dataframe(fe_m_display.drop(columns=["machine_id"]), use_container_width=True)

            # Raw data preview
            with st.expander("📄 Raw Data Preview (last 200 rows)"):
                st.dataframe(df_m.tail(200), use_container_width=True)
