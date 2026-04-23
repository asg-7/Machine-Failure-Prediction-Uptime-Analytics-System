"""
app.py  —  TSDPL Kalinganagar Maintenance & Operations Dashboard
10-Tab Streamlit App   |   Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
import random
import time
from datetime import datetime, timedelta

def generate_inline_demo_data(n_machines=6, days=45):
    """Generate synthetic UP/DOWN time-series data with sensors."""
    np.random.seed(42)
    machines = [f"Machine_{i:02d}" for i in range(1, n_machines+1)]
    start_date = datetime.now() - timedelta(days=days)
    timestamps = pd.date_range(start=start_date, end=datetime.now(), freq='15min')
    
    records = []
    for ts in timestamps:
        for machine in machines:
            prob_down = 0.03
            status = 'DOWN' if np.random.random() < prob_down else 'UP'
            records.append({
                'timestamp': ts,
                'machine_id': machine,
                'status': status,
                'temperature': round(np.random.normal(65, 8), 1),
                'load': round(np.random.normal(75, 12), 1),
                'vibration': round(np.random.normal(0.4, 0.15), 2)
            })
    df = pd.DataFrame(records)
    df['status'] = df['status'].str.upper()
    return df

sys.path.insert(0, os.path.dirname(__file__))

from utils.data_loader import load_data, get_data_summary
from utils.analytics import (
    compute_uptime_downtime, extract_failure_events,
    compute_failure_patterns, compute_hourly_failure_trend, compute_daily_uptime,
)
from utils.predictor import predict_all_machines, compute_sensor_anomaly_score
from utils.charts import (
    chart_uptime_downtime, chart_daily_uptime_trend, chart_failure_frequency,
    chart_hourly_failure_trend, chart_risk_ranking, chart_ttf_prediction, chart_sensor_trend,
)
from components.ui_components import (
    metric_card, alert_banner, render_prediction_card,
    render_alert_machines, section_header,
)
from utils.tsdpl_constants import (
    MACHINES, MACHINE_NAMES, FAILURE_CODES, LINES,
    SHIFT_CODES, MASTER_ROSTER, get_shift_from_hour,
)
from utils.tsdpl_demo_data import get_tsdpl_data
from utils.tsdpl_analytics import (
    compute_mtbf_mttr, compute_shift_mtbf_mttr,
    compute_oee_loss, compute_mom_comparison, compute_sensor_scorecard,
)
from utils.tsdpl_charts import (
    chart_shift_tornado, chart_mtbf_by_shift, chart_sensor_heatmap,
    chart_param_trend, chart_failure_category_donut, chart_mom_grid,
    chart_pm_status, chart_incident_timeline,
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TSDPL Kalinganagar | Maintenance Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── App shell ─────────────────────────────── */
[data-testid="stAppViewContainer"] { background-color: #0b1120; color: #e2e8f0; }
[data-testid="stSidebar"] { background-color: #0d1526; border-right: 1px solid #1e2d45; }
.main .block-container { 
    overflow-y: auto !important; 
    max-height: none !important;
    height: auto !important; 
}

/* ── Cards / metrics ────────────────────────── */
[data-testid="stMetric"] { background: #0d1f35; border: 1px solid #1e3a5f; border-radius: 8px; padding: 12px 16px; }
[data-testid="stMetricLabel"] { color: #64748b; font-size: 11px; }
[data-testid="stMetricValue"] { color: #f1f5f9; }

/* ── Tab bar — always readable ──────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    padding: 4px 6px;
    background: #0d1526;
    border-radius: 8px;
}

.stTabs [data-baseweb="tab"] {
    font-size: clamp(13px, 1.1vw, 16px) !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
    color: #94a3b8 !important;
    border-radius: 6px;
    white-space: nowrap;
    min-width: fit-content;
}

.stTabs [aria-selected="true"] {
    background: #1e3a5f !important;
    color: #f1f5f9 !important;
}

.stTabs [aria-selected="false"]:hover {
    background: #172135 !important;
    color: #cbd5e1 !important;
}

/* ── Force tab bar to scroll horizontally instead of wrapping ── */
.stTabs [data-baseweb="tab-list"] {
    overflow-x: auto !important;
    overflow-y: hidden !important;
    flex-wrap: nowrap !important;
    scrollbar-width: none;          /* Firefox */
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
    display: none;                  /* Chrome/Safari */
}

/* ── Buttons ────────────────────────────────── */
.stButton > button { background: #1e3a5f; color: #38bdf8; border: 1px solid #1e3a5f; border-radius: 6px; font-weight: 500; transition: background 0.15s, transform 0.1s; }
.stButton > button:hover { background: #174a7a; transform: translateY(-1px); }

/* ── Alert / info boxes ─────────────────────── */
[data-testid="stAlert"][kind="error"] { background: #3f0d0d; border: 1px solid #7f1d1d; color: #fca5a5; border-radius: 6px; }
[data-testid="stAlert"][kind="warning"] { background: #422006; border: 1px solid #7c2d12; color: #fdba74; border-radius: 6px; }
[data-testid="stAlert"][kind="success"] { background: #052e16; border: 1px solid #166534; color: #86efac; border-radius: 6px; }

/* ── Table ──────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid #1e3a5f; border-radius: 8px; }
thead th { background: #0d1526 !important; color: #64748b !important; }
tbody tr:hover td { background: #172135 !important; }

/* ── Slide-in animation for cards ───────────── */
@keyframes fadeSlideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
[data-testid="stMetric"] { animation: fadeSlideUp 0.35s ease-out both; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
for key, default in [
    ("df", None), ("summary", None), ("selected_machines", []),
    ("tsdpl_data", None), ("tsdpl_loaded", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 TSDPL Kalinganagar")
    st.markdown("##### Maintenance & Operations Dashboard")
    st.markdown("---")
    
    st.markdown("### 📂 Upload Generic Data")
    uploaded = st.file_uploader("CSV / Excel (UP/DOWN format)", type=["csv","xlsx","xls"])
    if uploaded:
        df, err = load_data(uploaded)
        if err:
            st.error(f"❌ {err}")
        else:
            st.session_state.df = df
            st.session_state.summary = get_data_summary(df)
            st.success(f"✅ {len(df):,} records loaded")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 Generic Demo", use_container_width=True):
            df_raw = generate_inline_demo_data(n_machines=6, days=45)
            from utils.data_loader import validate_and_preprocess
            df_clean, _ = validate_and_preprocess(df_raw)
            st.session_state.df = df_clean
            st.session_state.summary = get_data_summary(df_clean)
            st.success("Generic demo data loaded.")
    with col2:
        if st.button("🏭 TSDPL Demo", use_container_width=True):
            with st.spinner("Generating 90-day TSDPL data…"):
                try:
                    from utils.tsdpl_demo_data import get_tsdpl_data
                    st.session_state.tsdpl_data = get_tsdpl_data(days=90)
                    st.session_state.tsdpl_loaded = True
                    st.success("TSDPL dataset loaded.")
                except Exception as e:
                    st.error(f"TSDPL demo failed: {e}")
    
    # Temporary debug: show import paths
    if st.checkbox("Show debug info"):
        st.write("Current directory:", os.getcwd())
        st.write("sys.path:", sys.path)
        st.write("tsdpl_demo_data exists?", os.path.exists("utils/tsdpl_demo_data.py"))
    
    if st.session_state.summary:
        s = st.session_state.summary
        st.markdown("---")
        st.markdown("### 📊 Generic Dataset")
        st.caption(f"{s['total_records']:,} records · {len(s['machines'])} machines")
        st.caption(f"{s['date_range'][0].strftime('%d %b')} → {s['date_range'][1].strftime('%d %b %Y')}")
        st.markdown("#### Machine Filter")
        sel = st.multiselect("", s["machines"], default=s["machines"], label_visibility="collapsed")
        st.session_state.selected_machines = sel

    if st.session_state.tsdpl_loaded:
        dl = st.session_state.tsdpl_data["downtime_log"]
        st.markdown("---")
        st.markdown("### 🏭 TSDPL Dataset")
        st.caption(f"{len(dl):,} incidents · {dl['machine_id'].nunique()} machines")
        st.caption(f"{dl['timestamp'].min().strftime('%d %b')} → {dl['timestamp'].max().strftime('%d %b %Y')}")

    st.markdown("---")
    st.markdown('<div style="font-size:.72em;color:#94A3B8;text-align:center;">TSDPL Kalinganagar v2.0<br>Jajpur Road, Odisha</div>', unsafe_allow_html=True)


# ── Landing ───────────────────────────────────────────────────────────────────
if not st.session_state.tsdpl_loaded and st.session_state.df is None:
    st.markdown("""
    <div style="background-color: #0F62FE; padding: 20px; border-radius: 12px; 
                color: white; text-align: center; margin: 2rem 0;">
        <h2 style="color: white; margin-bottom: 8px;">🏭 Welcome to TSDPL Kalinganagar</h2>
        <p style="font-size: 1.1rem; color: #E0E0E0;">
            Upload a machine log file or click <strong style="color: white;">🎲 Generic Demo</strong> 
            or <strong style="color: white;">🏭 TSDPL Demo</strong> to start monitoring.
        </p>
        <p style="color: #F1C21B; margin-top: 12px;">
            ⚡ Predictive maintenance · Shift analytics · Sensor health
        </p>
    </div>
    """, unsafe_allow_html=True)
    tiles = [
        ("📋","Shift Roster","Log who was on duty at every failure"),
        ("📊","Shift Analytics","MTBF/MTTR/OEE by shift, Tornado chart"),
        ("🔮","Failure Prediction","TTF + risk ranking for all machines"),
        ("🔧","PM Checklist","Overdue alerts, LOTO reminders"),
        ("🌡️","Health Scorecard","Sensor alarm heatmap"),
        ("📅","Month-over-Month","MTBF trend vs last month"),
    ]
    for row_start in range(0, 6, 3):
        cols = st.columns(3)
        for col, (icon, title, desc) in zip(cols, tiles[row_start:row_start+3]):
            with col:
                st.markdown(f"""<div style="background:#0d1f35;border: 1px solid #1e3a5f;border-radius:10px;padding:18px;text-align:center;margin-bottom:8px">
                <div style="font-size:2em">{icon}</div><strong style="color: #e2e8f0;">{title}</strong>
                <p style="color:#94a3b8;font-size:.85em;margin-top:6px">{desc}</p></div>""", unsafe_allow_html=True)
    st.stop()


# ── Tabs ──────────────────────────────────────────────────────────────────────
(tab_ov, tab_up, tab_fa, tab_pr, tab_dr,
 tab_ro, tab_sa, tab_pm_tab, tab_sc, tab_mm) = st.tabs([
    "🏠 Overview","📈 Uptime","💥 Failures","🔮 Predictions","🔬 Drilldown",
    "📋 Shift Roster","📊 Shift Analytics","🔧 PM Checklist","🌡️ Health Scorecard","📅 Month-over-Month",
])


# ═══════════════════════════════════════════════════════════════════════════════
# GENERIC TABS 1–5
# ═══════════════════════════════════════════════════════════════════════════════
def render_generic(df_all):
    sel = st.session_state.get("selected_machines", df_all["machine_id"].unique().tolist())
    df = df_all[df_all["machine_id"].isin(sel)] if sel else df_all

    @st.cache_data(show_spinner=False)
    def run(h, _df):
        ut = compute_uptime_downtime(_df)
        fe = extract_failure_events(_df)
        fp = compute_failure_patterns(fe)
        ht = compute_hourly_failure_trend(fe)
        du = compute_daily_uptime(_df)
        pr = predict_all_machines(_df, fe)
        return ut, fe, fp, ht, du, pr

    h = (len(df), tuple(sorted(sel)), df["timestamp"].max().isoformat())
    ut, fe, fp, ht, du, pr = run(h, df)

    with tab_ov:
        st.markdown("## 🏠 Operations Overview")
        render_alert_machines(pr)
        c1,c2,c3,c4 = st.columns(4)
        avg_up = ut["uptime_pct"].mean() if not ut.empty else 0
        high_r = len(pr[pr["risk_label"]=="High"]) if not pr.empty else 0
        with c1: metric_card("Total Records", f"{len(df):,}")
        with c2: metric_card("Avg Uptime", f"{avg_up:.1f}%", color="#22C55E" if avg_up>=90 else "#F59E0B")
        with c3: metric_card("Total Failures", str(len(fe)), color="#EF4444")
        with c4: metric_card("High Risk", str(high_r), color="#EF4444" if high_r>0 else "#22C55E")
        col1,col2 = st.columns(2)
        # Locate these lines around Line 186-188:
        col1, col2 = st.columns(2)
        with col1: 
            st.plotly_chart(chart_uptime_downtime(ut), use_container_width=True, key="overview_uptime_chart")
        with col2: 
            st.plotly_chart(chart_risk_ranking(pr), use_container_width=True, key="overview_risk_chart")
            tbl = ut[["uptime_pct","downtime_hours","uptime_hours"]].join(
                pr.set_index("machine_id")[["failure_count","predicted_ttf_hours","remaining_ttf_hours","risk_label","risk_value"]],how="left")
            st.dataframe(tbl, use_container_width=True)

    with tab_up:
        st.markdown("## 📈 Uptime & Downtime Analysis")
        if not ut.empty:
            best,worst = ut["uptime_pct"].idxmax(), ut["uptime_pct"].idxmin()
            c1,c2,c3 = st.columns(3)
            with c1: metric_card("Best Performer", best, delta=f"{ut.loc[best,'uptime_pct']}%", color="#22C55E")
            with c2: metric_card("Needs Attention", worst, delta=f"{ut.loc[worst,'uptime_pct']}%", color="#EF4444")
            with c3: metric_card("Total Downtime", f"{ut['downtime_hours'].sum():.0f} h", color="#F59E0B")
            c1,c2 = st.columns(2)
           # Update these lines in your tab_up section:
        with c1: 
            st.plotly_chart(chart_uptime_downtime(ut), use_container_width=True, key="uptime_tab_main_chart")
        with c2: 
            st.plotly_chart(chart_daily_uptime_trend(du, sel), use_container_width=True, key="uptime_tab_trend_chart")
            st.dataframe(ut.reset_index(), use_container_width=True)

    with tab_fa:
        st.markdown("## 💥 Failure Pattern Detection")
        if not fe.empty:
            c1,c2,c3 = st.columns(3)
            with c1: metric_card("Total Failures", str(len(fe)), color="#EF4444")
            with c2: metric_card("Avg Runtime Before Failure", f"{fe['runtime_before_failure_hours'].mean():.1f} h")
            with c3: metric_card("Most Failures", fe["machine_id"].value_counts().idxmax())
            c1,c2 = st.columns(2)
            with c1: st.plotly_chart(chart_failure_frequency(fp), use_container_width=True)
            with c2: st.plotly_chart(chart_hourly_failure_trend(ht), use_container_width=True)
            fe_d = fe.copy(); fe_d["failure_time"] = fe_d["failure_time"].dt.strftime("%Y-%m-%d %H:%M")
            st.dataframe(fe_d, use_container_width=True)
        else:
            alert_banner("No failure events detected.", "info")

    with tab_pr:
        st.markdown("## 🔮 Failure Predictions & Risk")
        if not pr.empty:
            render_alert_machines(pr)
            for chunk in [pr.iloc[i:i+2] for i in range(0, len(pr), 2)]:
                cols = st.columns(2)
                for col, (_, row) in zip(cols, chunk.iterrows()):
                    with col: render_prediction_card(row)
            c1,c2 = st.columns(2)
            with c1: st.plotly_chart(chart_risk_ranking(pr), use_container_width=True)
            with c2: st.plotly_chart(chart_ttf_prediction(pr), use_container_width=True)
            st.dataframe(pr, use_container_width=True)

    with tab_dr:
        st.markdown("## 🔬 Machine Drilldown")
        if sel:
            chosen = st.selectbox("Select machine:", sel)
            df_m = df[df["machine_id"]==chosen]
            pr_row = pr[pr["machine_id"]==chosen]
            c1,c2 = st.columns([2,1])
            with c1: section_header(f"Machine: {chosen}", f"{len(df_m):,} records")
            with c2:
                if not pr_row.empty: render_prediction_card(pr_row.iloc[0])
            sensors = [s for s in ["temperature","load","vibration"] if df_m[s].notna().any()]
            if sensors:
                sc = st.radio("Sensor:", sensors, horizontal=True)
                st.plotly_chart(chart_sensor_trend(df_m, sc, chosen), use_container_width=True)
            fe_m = fe[fe["machine_id"]==chosen] if not fe.empty else pd.DataFrame()
            section_header(f"Failure Events ({len(fe_m)})")
            if fe_m.empty: alert_banner("No failures recorded.", "info")
            else: st.dataframe(fe_m.drop(columns=["machine_id"]), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TSDPL TABS 6–10
# ═══════════════════════════════════════════════════════════════════════════════
def render_tsdpl(tsdpl):
    dl   = tsdpl["downtime_log"]
    sr   = tsdpl["shift_roster"]
    pm   = tsdpl["pm_checklist"]
    sens = tsdpl["sensor_readings"]

    @st.cache_data(show_spinner=False)
    def compute(_h, _dl, _sens):
        return (compute_mtbf_mttr(_dl), compute_shift_mtbf_mttr(_dl),
                compute_oee_loss(_dl), compute_mom_comparison(_dl),
                compute_sensor_scorecard(_sens))

    mtbf_df, shift_mtbf, oee_df, mom_df, scorecard = compute(len(dl), dl, sens)

    # ── TAB 6: SHIFT ROSTER ───────────────────────────────────────────────────
    with tab_ro:
        st.markdown("## 📋 Shift Roster & Incident Duty Planner")
        st.caption("TBL_SHIFT_ROSTER_LOG — who was on duty at the time of each failure event.")

        with st.expander("👥 Master Roster"):
            st.dataframe(pd.DataFrame(MASTER_ROSTER), use_container_width=True)
            st.code("""=XLOOKUP(1,
  (MasterRoster[Shift]=[@Shift])*(MasterRoster[Line]=[@Line])
  *(MasterRoster[Zone]=[@Zone])*(MasterRoster[Role]="Operator"),
  MasterRoster[Name], "Standby")""", language="excel")

        c1,c2,c3 = st.columns(3)
        with c1: lines_sel = st.multiselect("Line:", LINES, default=LINES, key="r_line")
        with c2: shifts_sel = st.multiselect("Shift:", SHIFT_CODES, default=SHIFT_CODES, key="r_shift")
        with c3: inc_f = st.selectbox("Incidents:", ["All","Y - Only Incidents","N - No Incident"], key="r_inc")

        rv = sr.copy()
        if lines_sel:  rv = rv[rv["line"].isin(lines_sel)]
        if shifts_sel: rv = rv[rv["shift"].isin(shifts_sel)]
        if inc_f == "Y - Only Incidents": rv = rv[rv["incident_logged"]=="Y"]
        elif inc_f == "N - No Incident":  rv = rv[rv["incident_logged"]=="N"]

        total_s = len(rv); inc_s = (rv["incident_logged"]=="Y").sum()
        c1,c2,c3 = st.columns(3)
        with c1: metric_card("Shift Slots", f"{total_s:,}")
        with c2: metric_card("With Incidents", str(inc_s), color="#EF4444")
        with c3: metric_card("Incident Rate", f"{100*inc_s/max(total_s,1):.1f}%", color="#F59E0B")

        def color_inc(row):
            return ["background-color:#FEE2E2"]*len(row) if row["incident_logged"]=="Y" else [""]*len(row)

        st.dataframe(rv.style.apply(color_inc,axis=1), use_container_width=True, height=460)

        section_header("Incident Count by Operator")
        inc_df = sr[sr["incident_logged"]=="Y"]
        if not inc_df.empty:
            st.dataframe(inc_df.groupby("operator_name").size().reset_index(name="incident_count")
                         .sort_values("incident_count",ascending=False), use_container_width=True)


    # ── TAB 7: SHIFT ANALYTICS ────────────────────────────────────────────────
    with tab_sa:
        st.markdown("## 📊 Shift Performance Analytics")
        st.caption("MTBF · MTTR · OEE Loss by Shift")

        if shift_mtbf.empty:
            alert_banner("No shift data.", "warning")
        else:
            c1,c2,c3 = st.columns(3)
            for col,sh,clr in zip([c1,c2,c3], SHIFT_CODES, ["#6366F1","#F59E0B","#1E293B"]):
                with col:
                    sd = shift_mtbf[shift_mtbf["shift"]==sh]
                    metric_card(sh, f"{int(sd['total_downtime_min'].sum()):,} min",
                                delta=f"Avg MTBF: {sd['MTBF_hours'].mean():.1f} h", color=clr)

            section_header("Tornado Chart — Downtime by Shift",
                           "Night (C) plotted left · Morning (A) plotted right")
            mach_opts = dl["machine_id"].unique().tolist()
            default_tornado = [m for m in [
                "Cassette Leveller (HR-CTL)","Slitter Head (HR Slitting)",
                "Flying Shear (HR-CTL)","Recoiler (HR Slitting)"] if m in mach_opts]
            tornado_sel = st.multiselect("Machines:", mach_opts, default=default_tornado, key="tornado")
            st.plotly_chart(chart_shift_tornado(shift_mtbf, tornado_sel), use_container_width=True)

            c1,c2 = st.columns(2)
            with c1:
                section_header("MTBF/MTTR by Machine & Shift")
                metric_c = st.radio("Metric:", ["MTBF_hours","MTTR_min","total_downtime_min"],
                                    horizontal=True, key="sm")
                st.plotly_chart(chart_mtbf_by_shift(shift_mtbf, metric_c), use_container_width=True)
            with c2:
                section_header("Failure Category Mix")
                line_f = st.selectbox("Line:", ["All"]+LINES, key="sa_lf")
                dl_f = dl if line_f=="All" else dl[dl["line"]==line_f]
                st.plotly_chart(chart_failure_category_donut(dl_f), use_container_width=True)

            section_header("OEE Availability Loss % (pivot: machine × shift)")
            oee_piv = oee_df.pivot_table(
                index="machine_id", columns="shift", values="oee_avail_loss_pct", aggfunc="mean"
            ).fillna(0).round(2)
            st.dataframe(oee_piv.style.background_gradient(cmap="RdYlGn_r",axis=None), use_container_width=True)

            section_header("💡 Why Night Shift Typically Shows Higher Slitter Downtime")
            st.markdown("""
- **Reduced supervision density** during 22:00–06:00 increases time-to-detect knife wear.
- **End-of-shift fatigue** (04:00–06:00) raises manual re-threading errors → strip breakage.
- **Thermal contraction** in unheated bays causes Cassette Leveller roll gap drift on cold nights.
- **Knife change deferrals** across Night shift handover → more coils run on degraded blades.
- **Recommendation:** Mandate per-coil knife inspection sign-off on Night shift; add Cassette Leveller ΔT alarm from 22:00.
            """)

            section_header("Full Shift Downtime Table")
            st.dataframe(shift_mtbf.sort_values("total_downtime_min",ascending=False), use_container_width=True)


    # ── TAB 8: PM CHECKLIST ───────────────────────────────────────────────────
    with tab_pm_tab:
        st.markdown("## 🔧 Digital PM Checklist")
        st.caption("Preventive Maintenance log with overdue alerts and LOTO compliance reminders.")

        pm_view = pm.copy()
        loto_overdue = pm_view[(pm_view["loto_required"]==True)&(pm_view["status"]=="Overdue")]
        if not loto_overdue.empty:
            alert_banner(
                f"⚠️ <strong>LOTO COMPLIANCE ALERT:</strong> Overdue LOTO tasks on: "
                f"{', '.join(loto_overdue['machine_id'].unique())}. "
                "Do NOT begin work without completing Lockout/Tagout procedure per TSDPL SOP-SAFE-04.",
                "error",
            )

        c1,c2,c3 = st.columns(3)
        with c1: pm_m = st.selectbox("Machine:", ["All"]+MACHINE_NAMES, key="pm_m")
        with c2: pm_st = st.multiselect("Status:", ["Completed","Overdue","Scheduled"],
                                         default=["Completed","Overdue","Scheduled"], key="pm_st")
        with c3: pm_ct = st.multiselect("Category:", ["Mechanical","Electrical","Hydraulic"],
                                         default=["Mechanical","Electrical","Hydraulic"], key="pm_ct")

        if pm_m!="All": pm_view = pm_view[pm_view["machine_id"]==pm_m]
        if pm_st: pm_view = pm_view[pm_view["status"].isin(pm_st)]
        if pm_ct: pm_view = pm_view[pm_view["category"].isin(pm_ct)]

        c1,c2,c3,c4 = st.columns(4)
        with c1: metric_card("Total Tasks", str(len(pm_view)))
        with c2: metric_card("Completed", str((pm_view["status"]=="Completed").sum()), color="#22C55E")
        with c3: metric_card("Overdue",   str((pm_view["status"]=="Overdue").sum()),   color="#EF4444")
        with c4: metric_card("LOTO Required", str(int(pm_view["loto_required"].sum())), color="#F59E0B")

        c1,c2 = st.columns(2)
        with c1: st.plotly_chart(chart_pm_status(pm), use_container_width=True)
        with c2: st.plotly_chart(chart_incident_timeline(dl, 14), use_container_width=True)

        section_header("PM Task Log")
        disp = pm_view.copy()
        disp["loto_required"] = disp["loto_required"].map({True:"🔒 YES", False:"—"})
        disp["status"] = disp["status"].map({"Completed":"✅ Completed","Overdue":"🔴 Overdue","Scheduled":"📅 Scheduled"}).fillna(disp["status"])

        def style_pm(row):
            if "Overdue" in str(row["status"]): return ["background-color:#FEE2E2"]*len(row)
            if "Completed" in str(row["status"]): return ["background-color:#F0FDF4"]*len(row)
            return [""]*len(row)

        st.dataframe(disp.style.apply(style_pm,axis=1), use_container_width=True, height=460)

        with st.expander("📐 Excel Formulas — Conditional Formatting & Validation"):
            st.markdown("""
**Overdue → RED (apply to A2:J500):**
```excel
=AND($F2<>"", $G2="", TODAY()-DATEVALUE($F2)>1)
```
*(F = scheduled_date, G = completed_date)*

**Completed → GREEN:**
```excel
=$H2="Completed"
```
**Machine Status Dropdown (Data Validation list):**
```
Running, Planned Stop, Breakdown - Mechanical, Breakdown - Electrical,
Breakdown - Hydraulic, Breakdown - Process, PM In Progress, Idle / No Production
```
**MTBF Array Formula:**
```excel
=(COUNTIF(TBL_DOWNTIME[Date],"<="&TODAY())*8*24 - SUMIF(TBL_DOWNTIME[machine_id],A2,TBL_DOWNTIME[downtime_minutes])/60)
/ COUNTIF(TBL_DOWNTIME[machine_id],A2)
```
            """)


    # ── TAB 9: HEALTH SCORECARD ───────────────────────────────────────────────
    with tab_sc:
        st.markdown("## 🌡️ Machine Health Scorecard")
        st.caption("Sensor parameter alarm status across all TSDPL machines — last 24 hours.")

        if scorecard.empty:
            alert_banner("No sensor data.", "warning")
        else:
            alarms   = scorecard[scorecard["status"]=="ALARM"]
            warnings = scorecard[scorecard["status"]=="WARNING"]

            if not alarms.empty:
                alarm_str = "; ".join(f"{r['machine_id']} / {r['parameter']} = {r['current_value']} {r['unit']}"
                                       for _, r in alarms.iterrows())
                alert_banner(f"🚨 <strong>ACTIVE ALARMS ({len(alarms)}):</strong> {alarm_str}", "error")
            if not warnings.empty:
                warn_str = "; ".join(f"{r['machine_id']} / {r['parameter']}" for _, r in warnings.iterrows())
                alert_banner(f"⚠️ <strong>WARNINGS ({len(warnings)}):</strong> {warn_str}", "warning")

            c1,c2,c3 = st.columns(3)
            with c1: metric_card("Parameters Monitored", str(len(scorecard)))
            with c2: metric_card("In Alarm", str(len(alarms)), color="#EF4444")
            with c3: metric_card("In Warning", str(len(warnings)), color="#F59E0B")

            section_header("Sensor Status Heatmap", "✅ Normal · ⚠️ Warning · 🚨 Alarm")
            st.plotly_chart(chart_sensor_heatmap(scorecard), use_container_width=True)

            section_header("Operational Limit Configuration Table")
            lim_rows = []
            for m, md in MACHINES.items():
                for p, cfg in md["params"].items():
                    lim_rows.append({"Machine":m,"Line":md["line"],"Criticality":md["criticality"],
                                     "Parameter":p,"Unit":cfg["unit"],
                                     "Normal Lo":cfg["normal_range"][0],"Normal Hi":cfg["normal_range"][1],
                                     "Alarm High":cfg.get("alarm_high","—"),"Alarm Low":cfg.get("alarm_low","—")})
            crit_map = {"Critical":"background-color:#FEE2E2","High":"background-color:#FEF3C7","Medium":"background-color:#EFF6FF"}
            lim_df = pd.DataFrame(lim_rows)
            st.dataframe(lim_df.style.map(lambda v: crit_map.get(v,""), subset=["Criticality"]),
                         use_container_width=True)

            section_header("Parameter Trend Drilldown")
            c1,c2 = st.columns(2)
            with c1: sc_m = st.selectbox("Machine:", scorecard["machine_id"].unique(), key="sc_m")
            with c2:
                sc_ps = scorecard[scorecard["machine_id"]==sc_m]["parameter"].tolist()
                sc_p = st.selectbox("Parameter:", sc_ps, key="sc_p")
            st.plotly_chart(chart_param_trend(sens, sc_m, sc_p), use_container_width=True)

            with st.expander("📋 Full Scorecard Table"):
                def color_s(val):
                    return {"ALARM":"background-color:#FEE2E2","WARNING":"background-color:#FEF3C7","Normal":"background-color:#F0FDF4"}.get(val,"")
                st.dataframe(scorecard.style.map(color_s, subset=["status"]), use_container_width=True)


    # ── TAB 10: MONTH-OVER-MONTH ──────────────────────────────────────────────
    with tab_mm:
        st.markdown("## 📅 Month-over-Month Executive Summary")
        st.markdown(
            "<p style='color: #94a3b8; font-size: 13px; margin-top: -8px;'>"
            "MTBF trend, downtime delta, top failure mode per machine vs last month.</p>",
            unsafe_allow_html=True
        )

        if mom_df.empty:
            alert_banner("Insufficient data for MoM comparison.", "warning")
        else:
            imp = (mom_df["trend"]=="Improving").sum()
            wor = (mom_df["trend"]=="Worsening").sum()
            sta = (mom_df["trend"]=="Stable").sum()
            delta_total = mom_df["delta_downtime_min"].sum()

            def mom_kpi_card(label, value, border_color):
                return f"""
                <div style="border-left: 4px solid {border_color}; padding: 14px 20px;
                            background: #0d1f35; border-radius: 6px;
                            border-top: 1px solid #1e3a5f; border-right: 1px solid #1e3a5f;
                            border-bottom: 1px solid #1e3a5f;">
                  <p style="color: #64748b; font-size: 10px; letter-spacing: 0.08em;
                            text-transform: uppercase; margin: 0 0 6px;">{label}</p>
                  <p style="color: #f1f5f9; font-size: 30px; font-weight: 700;
                            margin: 0; line-height: 1;">{value}</p>
                </div>
                """

            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(mom_kpi_card("IMPROVING", str(imp), "#22c55e"), unsafe_allow_html=True)
            with c2: st.markdown(mom_kpi_card("WORSENING", str(wor), "#ef4444"), unsafe_allow_html=True)
            with c3: st.markdown(mom_kpi_card("STABLE", str(sta), "#38bdf8"), unsafe_allow_html=True)
            with c4:
                fleet_val = f"{'▲' if delta_total>0 else '▼'} {abs(delta_total):,} min"
                st.markdown(mom_kpi_card("FLEET Δ DOWNTIME", fleet_val, "#f59e0b"), unsafe_allow_html=True)

            section_header("Downtime Comparison Grid")
            st.plotly_chart(chart_mom_grid(mom_df), use_container_width=True)

            section_header("Machine MTBF Scorecards")
            for chunk_s in range(0, len(mom_df), 3):
                chunk = mom_df.iloc[chunk_s:chunk_s+3]
                cols = st.columns(3)
                for col, (_, row) in zip(cols, chunk.iterrows()):
                    with col:
                        t = row["trend"]
                        ti = "🟢" if t=="Improving" else ("🔴" if t=="Worsening" else "⚪")
                        bg = "#F0FDF4" if t=="Improving" else ("#FEF2F2" if t=="Worsening" else "#F8FAFC")
                        bd = "#22C55E" if t=="Improving" else ("#EF4444" if t=="Worsening" else "#E2E8F0")
                        st.markdown(f"""<div style="background:{bg};border:1px solid {bd};border-radius:10px;
                        padding:14px;margin-bottom:10px">
                        <div style="font-weight:700;font-size:.85em;color:#1E293B;margin-bottom:8px">{row['machine_id']}</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:.78em">
                        <div><span style="color:#64748B">MTBF This</span><br><strong>{row['mtbf_this_month_h']:.1f} h</strong></div>
                        <div><span style="color:#64748B">MTBF Last</span><br><strong>{row['mtbf_last_month_h']:.1f} h</strong></div>
                        <div><span style="color:#64748B">Failures</span><br><strong>{row['this_month_failures']}</strong>
                             <span style="color:#94A3B8"> vs {row['last_month_failures']}</span></div>
                        <div><span style="color:#64748B">Top Failure</span><br><strong>{row['top_failure_mode']}</strong></div>
                        </div><div style="margin-top:8px;font-size:.88em">{ti} {t}</div></div>""",
                        unsafe_allow_html=True)

            with st.expander("📋 Full MoM Data Table"):
                st.dataframe(mom_df, use_container_width=True)

            with st.expander("📐 Power BI DAX + Excel Formulas"):
                st.markdown("""
**DAX — This Month Downtime:**
```dax
This Month Downtime =
CALCULATE(SUM(DowntimeLog[downtime_minutes]), DATESMTD(DowntimeLog[timestamp]))
```
**DAX — Last Month Downtime:**
```dax
Last Month Downtime =
CALCULATE(SUM(DowntimeLog[downtime_minutes]),
  DATEADD(DATESMTD(LASTDATE(DowntimeLog[timestamp])), -1, MONTH))
```
**DAX — MoM Trend Arrow:**
```dax
MoM Trend =
VAR Curr = [This Month Downtime]  VAR Prev = [Last Month Downtime]
RETURN IF(Prev=0,"Stable", IF(Curr/Prev<0.95,"▲ Improving", IF(Curr/Prev>1.05,"▼ Worsening","→ Stable")))
```
**Excel — Rolling 30-day Downtime:**
```excel
=SUMPRODUCT((TBL_DOWNTIME[machine_id]=A2)*(TBL_DOWNTIME[timestamp]>=TODAY()-30)*TBL_DOWNTIME[downtime_minutes])
```
**Excel — Prior 30-day Window:**
```excel
=SUMPRODUCT((TBL_DOWNTIME[machine_id]=A2)*(TBL_DOWNTIME[timestamp]>=TODAY()-60)*(TBL_DOWNTIME[timestamp]<TODAY()-30)*TBL_DOWNTIME[downtime_minutes])
```
                """)

            section_header("📖 Failure Code Glossary — TSDPL Kalinganagar")
            gloss = pd.DataFrame([
                {"Code":k,"Description":v["desc"],"Category":v["category"],"Primary Machine":v["machine"]}
                for k,v in FAILURE_CODES.items()
            ])
            cat_bg = {"Mechanical":"background-color:#FEF2F2","Electrical":"background-color:#EFF6FF",
                      "Hydraulic":"background-color:#FFFBEB","Process":"background-color:#F0FDF4","Planned":"background-color:#F8FAFC"}
            st.dataframe(gloss.style.map(lambda v: cat_bg.get(v,""), subset=["Category"]),
                         use_container_width=True)


# ── Render ────────────────────────────────────────────────────────────────────
if st.session_state.df is not None:
    render_generic(st.session_state.df)
else:
    for t, lbl in zip([tab_ov,tab_up,tab_fa,tab_pr,tab_dr],
                      ["Overview","Uptime","Failures","Predictions","Drilldown"]):
        with t:
            alert_banner(f"Upload a CSV or click <strong>🎲 Generic Demo</strong> to use the {lbl} tab.","info")

if st.session_state.tsdpl_loaded:
    render_tsdpl(st.session_state.tsdpl_data)
else:
    for t, lbl in zip([tab_ro,tab_sa,tab_pm_tab,tab_sc,tab_mm],
                      ["Shift Roster","Shift Analytics","PM Checklist","Health Scorecard","Month-over-Month"]):
        with t:
            alert_banner(f"Click <strong>🏭 TSDPL Demo</strong> in the sidebar to use the {lbl} tab.","info")
