"""
utils/tsdpl_charts.py
All Plotly visualizations specific to TSDPL Kalinganagar dashboard.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


RISK_COLOR = {"Critical": "#DA1E28", "High": "#F1C21B", "Medium": "#0F62FE", "Low": "#24A148"}
STATUS_COLOR = {"ALARM": "#DA1E28", "WARNING": "#F1C21B", "Normal": "#24A148", "Scheduled": "#94A3B8", "Overdue": "#DA1E28", "Completed": "#24A148"}
SHIFT_COLORS = {"A - Morning": "#1192E8", "B - Afternoon": "#8A3FFC", "C - Night": "#002D9C"}
TREND_COLOR = {"Improving": "#24A148", "Worsening": "#DA1E28", "Stable": "#94A3B8"}

import plotly.io as pio
TSDPL_TEMPLATE = { 
    "layout": { 
        "paper_bgcolor": "#0b1120", 
        "plot_bgcolor": "#0d1f35", 
        "font": {"color": "#94a3b8", "family": "Inter, system-ui, sans-serif"}, 
        "colorway": ["#38bdf8", "#4ade80", "#fbbf24", "#f87171", "#c084fc"], 
        "xaxis": {"gridcolor": "#1e293b", "linecolor": "#1e3a5f", "tickcolor": "#475569"}, 
        "yaxis": {"gridcolor": "#1e293b", "linecolor": "#1e3a5f", "tickcolor": "#475569"}, 
        "legend": {"bgcolor": "#0d1f35", "bordercolor": "#1e3a5f", "borderwidth": 1}, 
        "hoverlabel": { "bgcolor": "#0d1526", "bordercolor": "#38bdf8", "font": {"color": "#f1f5f9"} } 
    } 
} 
pio.templates["tsdpl"] = pio.templates["plotly"].update(TSDPL_TEMPLATE) 
pio.templates.default = "tsdpl"


# ── 1. Tornado Chart: Shift vs Downtime ──────────────────────────────────────
def chart_shift_tornado(shift_mtbf: pd.DataFrame, machines: list = None) -> go.Figure:
    """
    Horizontal diverging bar (Tornado):
    Left = Night shift downtime, Right = Morning shift downtime.
    Highlights Cassette Leveller and Slitter Head.
    """
    if shift_mtbf.empty:
        return go.Figure().update_layout(title="No shift data available")

    if machines:
        df = shift_mtbf[shift_mtbf["machine_id"].isin(machines)].copy()
    else:
        # Default to key machines
        df = shift_mtbf[shift_mtbf["machine_id"].isin([
            "Cassette Leveller (HR-CTL)", "Slitter Head (HR Slitting)",
            "Flying Shear (HR-CTL)", "Recoiler (HR Slitting)",
            "Robotic Tool Setup (CR 2024)"
        ])].copy()

    pivot = df.pivot_table(
        index="machine_id", columns="shift", values="total_downtime_min", aggfunc="sum"
    ).fillna(0).reset_index()

    morning_col = "A - Morning" if "A - Morning" in pivot.columns else None
    night_col   = "C - Night"   if "C - Night"   in pivot.columns else None
    afternoon_col = "B - Afternoon" if "B - Afternoon" in pivot.columns else None

    fig = go.Figure()

    if morning_col:
        fig.add_trace(go.Bar(
            name="Morning (A)",
            x=pivot[morning_col],
            y=pivot["machine_id"],
            orientation="h",
            marker_color=SHIFT_COLORS["A - Morning"],
            text=pivot[morning_col].astype(int).astype(str) + " min",
            textposition="outside",
        ))
    if afternoon_col:
        fig.add_trace(go.Bar(
            name="Afternoon (B)",
            x=pivot[afternoon_col],
            y=pivot["machine_id"],
            orientation="h",
            marker_color=SHIFT_COLORS["B - Afternoon"],
            text=pivot[afternoon_col].astype(int).astype(str) + " min",
            textposition="outside",
        ))
    if night_col:
        fig.add_trace(go.Bar(
            name="Night (C)",
            x=-pivot[night_col],  # negative for tornado left side
            y=pivot["machine_id"],
            orientation="h",
            marker_color=SHIFT_COLORS["C - Night"],
            text=pivot[night_col].astype(int).astype(str) + " min",
            textposition="outside",
        ))

    max_val = max(
        pivot[morning_col].max() if morning_col else 0,
        pivot[night_col].max() if night_col else 0,
        pivot[afternoon_col].max() if afternoon_col else 0,
    ) * 1.3

    fig.update_layout(
        title="Tornado Chart: Downtime by Shift (Night ← | → Morning/Afternoon)",
        xaxis=dict(
            title="Downtime (min)",
            range=[-max_val, max_val],
            tickvals=list(range(int(-max_val), int(max_val)+1, max(1, int(max_val//4)))),
            ticktext=[str(abs(v)) for v in range(int(-max_val), int(max_val)+1, max(1, int(max_val//4)))],
            gridcolor="#E5E7EB",
        ),
        yaxis_title="Machine",
        barmode="overlay",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        legend=dict(orientation="h", y=1.08),
    )
    fig.add_vline(x=0, line_color="#1E293B", line_width=2)
    return fig


# ── 2. MTBF / MTTR Clustered Column by Shift ────────────────────────────────
def chart_mtbf_by_shift(shift_mtbf: pd.DataFrame, metric: str = "MTBF_hours") -> go.Figure:
    if shift_mtbf.empty:
        return go.Figure()

    fig = px.bar(
        shift_mtbf,
        x="machine_id",
        y=metric,
        color="shift",
        barmode="group",
        color_discrete_map=SHIFT_COLORS,
        title=f"{metric.replace('_', ' ')} by Machine & Shift",
        labels={"machine_id": "Machine", metric: metric.replace("_", " "), "shift": "Shift"},
        height=420,
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-35,
        yaxis=dict(gridcolor="#E5E7EB"),
        legend=dict(orientation="h", y=1.08),
    )
    return fig


# ── 3. Machine Health Scorecard Heatmap ─────────────────────────────────────
def chart_sensor_heatmap(scorecard_df: pd.DataFrame) -> go.Figure:
    if scorecard_df.empty:
        return go.Figure()

    status_num = {"Normal": 0, "WARNING": 1, "ALARM": 2}
    scorecard_df["status_num"] = scorecard_df["status"].map(status_num).fillna(0)

    pivot = scorecard_df.pivot_table(
        index="machine_id", columns="parameter", values="status_num", aggfunc="max"
    ).fillna(0)

    colorscale = [
        [0.0,  "#DCFCE7"],  # Normal – green
        [0.5,  "#FEF3C7"],  # Warning – yellow
        [1.0,  "#FEE2E2"],  # Alarm – red
    ]

    hover_text = []
    for m in pivot.index:
        row_hover = []
        for p in pivot.columns:
            if p in scorecard_df[scorecard_df["machine_id"] == m]["parameter"].values:
                row = scorecard_df[
                    (scorecard_df["machine_id"] == m) & (scorecard_df["parameter"] == p)
                ].iloc[0]
                row_hover.append(
                    f"<b>{p}</b><br>Value: {row['current_value']} {row['unit']}<br>"
                    f"Status: {row['status']}<br>Trend: {row['trend']}"
                )
            else:
                row_hover.append("N/A")
        hover_text.append(row_hover)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=colorscale,
        zmin=0, zmax=2,
        text=hover_text,
        hovertemplate="%{text}<extra></extra>",
        showscale=False,
    ))

    # Overlay text labels
    status_labels = {0: "✅", 1: "⚠️", 2: "🚨"}
    annotations = []
    for i, m in enumerate(pivot.index):
        for j, p in enumerate(pivot.columns):
            val = pivot.values[i][j]
            annotations.append(dict(
                x=j, y=i,
                text=status_labels.get(int(val), ""),
                showarrow=False,
                font=dict(size=16),
            ))

    fig.update_layout(
        title="Machine Health Scorecard (Sensor Status Heatmap)",
        xaxis=dict(tickangle=-35, title="Parameter"),
        yaxis_title="Machine",
        height=max(380, len(pivot.index) * 45),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=annotations,
    )
    return fig


# ── 4. Sensor Parameter Trend (single machine, single param) ────────────────
def chart_param_trend(sensor_df: pd.DataFrame, machine: str, param: str) -> go.Figure:
    data = sensor_df[
        (sensor_df["machine_id"] == machine) & (sensor_df["parameter"] == param)
    ].sort_values("timestamp")

    if data.empty:
        fig = go.Figure()
        fig.update_layout(title=f"No data: {machine} – {param}")
        return fig

    unit = data["unit"].iloc[0]
    ah = data["alarm_high"].iloc[0]
    al = data["alarm_low"].iloc[0]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["timestamp"], y=data["value"],
        mode="lines", name=param,
        line=dict(color="#0F62FE", width=2),
    ))
    # Rolling average
    roll = data["value"].rolling(6, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=data["timestamp"], y=roll,
        mode="lines", name="6-pt Rolling Avg",
        line=dict(color="#F1C21B", dash="dash", width=2),
    ))
    if ah:
        fig.add_hline(y=ah, line_dash="dash", line_color="#DA1E28",
                      annotation_text=f"Alarm High: {ah}", annotation_position="top right")
    if al:
        fig.add_hline(y=al, line_dash="dash", line_color="#DA1E28",
                      annotation_text=f"Alarm Low: {al}", annotation_position="bottom right")

    fig.update_layout(
        title=f"{param} – {machine}",
        xaxis_title="Time",
        yaxis_title=f"{param} ({unit})",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
        hovermode="x unified",
    )
    return fig


# ── 5. Failure Category Breakdown (Pie / Donut) ─────────────────────────────
def chart_failure_category_donut(downtime_log: pd.DataFrame, machine: str = None) -> go.Figure:
    df = downtime_log.copy()
    if machine:
        df = df[df["machine_id"] == machine]
    if df.empty:
        return go.Figure()

    cat_counts = df.groupby("failure_category")["downtime_minutes"].sum().reset_index()
    colors = {
        "Mechanical": "#DA1E28", 
        "Electrical": "#0F62FE",
        "Hydraulic/Pneumatic": "#8A3FFC", 
        "Performance Degradation": "#F1C21B", 
        "Intermittent": "#1192E8",
        "Surface Degradation": "#A56EFF",
        "Process": "#24A148", 
        "Planned": "#94A3B8"
    }
    c = [colors.get(c, "#CBD5E1") for c in cat_counts["failure_category"]]

    fig = go.Figure(go.Pie(
        labels=cat_counts["failure_category"],
        values=cat_counts["downtime_minutes"],
        hole=0.45,
        marker_colors=c,
    ))
    title = f"Downtime by Failure Category{f' – {machine}' if machine else ''}"
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
        legend=dict(orientation="h", y=-0.1),
    )
    return fig


# ── 6. Month-over-Month Grid ─────────────────────────────────────────────────
def chart_mom_grid(mom_df: pd.DataFrame) -> go.Figure:
    """
    3×2 subplot grid with bar pairs (this vs last month downtime).
    Color-coded by trend.
    """
    if mom_df.empty:
        return go.Figure()

    machines = mom_df["machine_id"].tolist()
    n = len(machines)
    cols = 3
    rows_n = (n + cols - 1) // cols

    subplot_titles = machines[:n]
    fig = make_subplots(
        rows=rows_n, cols=cols,
        subplot_titles=subplot_titles,
        vertical_spacing=0.18,
        horizontal_spacing=0.08,
    )

    for idx, (_, row) in enumerate(mom_df.iterrows()):
        r = idx // cols + 1
        c = idx % cols + 1
        LAST_MONTH_COLOR  = "#334155"
        IMPROVING_COLOR   = "#22c55e"
        WORSENING_COLOR   = "#ef4444"
        STABLE_COLOR      = "#38bdf8"
        
        if row["trend"] == "Improving":
            bar_color = IMPROVING_COLOR
        elif row["trend"] == "Worsening":
            bar_color = WORSENING_COLOR
        else:
            bar_color = STABLE_COLOR

        fig.add_trace(go.Bar(
            name="Last Month", x=["Last Month"],
            y=[row["last_month_downtime_min"]],
            marker_color=LAST_MONTH_COLOR,
            showlegend=(idx == 0),
        ), row=r, col=c)

        fig.add_trace(go.Bar(
            name="This Month", x=["This Month"],
            y=[row["this_month_downtime_min"]],
            marker_color=bar_color,
            showlegend=(idx == 0),
        ), row=r, col=c)

    fig.update_traces(marker_line_width=0)
    fig.update_layout(
        title="Month-over-Month Downtime Comparison per Machine",
        barmode="group",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=max(450, rows_n * 220),
        legend=dict(orientation="h", y=1.04),
        showlegend=True,
    )
    fig.update_yaxes(gridcolor="#E5E7EB")
    return fig


# ── 7. PM Completion Status Bar ──────────────────────────────────────────────
def chart_pm_status(pm_df: pd.DataFrame) -> go.Figure:
    if pm_df.empty:
        return go.Figure()

    status_counts = pm_df.groupby(["machine_id", "status"]).size().reset_index(name="count")
    colors = {"Completed": "#24A148", "Overdue": "#DA1E28", "Scheduled": "#0F62FE"}

    fig = px.bar(
        status_counts,
        x="machine_id",
        y="count",
        color="status",
        color_discrete_map=colors,
        barmode="stack",
        title="PM Task Status per Machine",
        labels={"machine_id": "Machine", "count": "Tasks", "status": "Status"},
        height=400,
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-35,
        yaxis=dict(gridcolor="#E5E7EB"),
        legend=dict(orientation="h", y=1.08),
    )
    return fig


# ── 8. Incident Timeline (Gantt-style) ──────────────────────────────────────
def chart_incident_timeline(downtime_log: pd.DataFrame, days_back: int = 14) -> go.Figure:
    if downtime_log.empty:
        return go.Figure()

    cutoff = pd.Timestamp.now() - pd.Timedelta(days=days_back)
    df = downtime_log[downtime_log["timestamp"] >= cutoff].copy()
    if df.empty:
        return go.Figure().update_layout(title="No incidents in this period")

    df["end_time"] = df["timestamp"] + pd.to_timedelta(df["downtime_minutes"], unit="m")

    category_color = {
        "Mechanical": "#DA1E28", 
        "Electrical": "#0F62FE",
        "Hydraulic/Pneumatic": "#8A3FFC", 
        "Performance Degradation": "#F1C21B", 
        "Intermittent": "#1192E8",
        "Surface Degradation": "#A56EFF",
        "Process": "#24A148", 
        "Planned": "#94A3B8"
    }

    fig = go.Figure()
    for _, row in df.iterrows():
        color = category_color.get(row["failure_category"], "#CBD5E1")
        fig.add_trace(go.Scatter(
            x=[row["timestamp"], row["end_time"]],
            y=[row["machine_id"], row["machine_id"]],
            mode="lines",
            line=dict(color=color, width=10),
            name=row["failure_category"],
            hovertemplate=(
                f"<b>{row['machine_id']}</b><br>"
                f"Code: {row['failure_code']}<br>"
                f"Desc: {row['failure_desc']}<br>"
                f"Duration: {row['downtime_minutes']} min<br>"
                f"Shift: {row['shift']}<extra></extra>"
            ),
            showlegend=False,
        ))

    # Legend proxies
    for cat, col in category_color.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines",
            line=dict(color=col, width=8),
            name=cat,
        ))

    fig.update_layout(
        title=f"Incident Timeline (Last {days_back} Days)",
        xaxis_title="Date/Time",
        yaxis_title="Machine",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=max(380, len(df["machine_id"].unique()) * 35 + 100),
        hovermode="closest",
        legend=dict(orientation="h", y=1.08),
    )
    return fig
