"""
utils/charts.py
All Plotly visualizations for the dashboard.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


RISK_COLORS = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#22C55E", "Unknown": "#94A3B8"}
PALETTE = px.colors.qualitative.Plotly


# ──────────────────────────────────────────────
# 1. Uptime vs Downtime Bar Chart
# ──────────────────────────────────────────────

def chart_uptime_downtime(uptime_df: pd.DataFrame) -> go.Figure:
    machines = uptime_df.index.tolist()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Uptime %",
        x=machines,
        y=uptime_df["uptime_pct"],
        marker_color="#22C55E",
        text=uptime_df["uptime_pct"].astype(str) + "%",
        textposition="inside",
    ))
    fig.add_trace(go.Bar(
        name="Downtime %",
        x=machines,
        y=uptime_df["downtime_pct"],
        marker_color="#EF4444",
        text=uptime_df["downtime_pct"].astype(str) + "%",
        textposition="inside",
    ))
    fig.update_layout(
        barmode="stack",
        title="Uptime vs Downtime per Machine",
        xaxis_title="Machine",
        yaxis_title="Percentage (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=380,
    )
    fig.update_yaxes(range=[0, 100], gridcolor="#E5E7EB")
    return fig


# ──────────────────────────────────────────────
# 2. Daily Uptime Trend Line
# ──────────────────────────────────────────────

def chart_daily_uptime_trend(daily_uptime: pd.DataFrame, selected_machines=None) -> go.Figure:
    if selected_machines:
        daily_uptime = daily_uptime[daily_uptime["machine_id"].isin(selected_machines)]

    fig = px.line(
        daily_uptime,
        x="date",
        y="uptime_pct",
        color="machine_id",
        title="Daily Uptime Trend",
        labels={"uptime_pct": "Uptime (%)", "date": "Date", "machine_id": "Machine"},
        color_discrete_sequence=PALETTE,
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=380,
        hovermode="x unified",
        yaxis=dict(range=[0, 105], gridcolor="#E5E7EB"),
    )
    fig.add_hline(y=90, line_dash="dash", line_color="#94A3B8",
                  annotation_text="90% target", annotation_position="bottom right")
    return fig


# ──────────────────────────────────────────────
# 3. Failure Frequency Bar
# ──────────────────────────────────────────────

def chart_failure_frequency(failure_patterns: pd.DataFrame) -> go.Figure:
    if failure_patterns.empty:
        fig = go.Figure()
        fig.update_layout(title="No failure events detected")
        return fig

    fp = failure_patterns.reset_index().sort_values("failure_count", ascending=True)
    fig = go.Figure(go.Bar(
        x=fp["failure_count"],
        y=fp["machine_id"],
        orientation="h",
        marker_color="#6366F1",
        text=fp["failure_count"],
        textposition="outside",
    ))
    fig.update_layout(
        title="Failure Frequency per Machine",
        xaxis_title="Number of Failures",
        yaxis_title="Machine",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=380,
        xaxis=dict(gridcolor="#E5E7EB"),
    )
    return fig


# ──────────────────────────────────────────────
# 4. Time-of-Day Failure Heatmap
# ──────────────────────────────────────────────

def chart_hourly_failure_trend(hourly_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=hourly_df["hour_of_day"],
        y=hourly_df["failure_count"],
        marker_color="#F59E0B",
    ))
    fig.update_layout(
        title="Failures by Hour of Day",
        xaxis=dict(
            title="Hour of Day",
            tickmode="array",
            tickvals=list(range(24)),
            ticktext=[f"{h:02d}:00" for h in range(24)],
            gridcolor="#E5E7EB",
        ),
        yaxis=dict(title="Failure Count", gridcolor="#E5E7EB"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
    )
    return fig


# ──────────────────────────────────────────────
# 5. Risk Ranking Gauge / Bar
# ──────────────────────────────────────────────

def chart_risk_ranking(predictions: pd.DataFrame) -> go.Figure:
    if predictions.empty:
        fig = go.Figure()
        fig.update_layout(title="No prediction data")
        return fig

    pred = predictions.sort_values("risk_value", ascending=True)
    colors = [RISK_COLORS.get(r, "#94A3B8") for r in pred["risk_label"]]

    fig = go.Figure(go.Bar(
        x=pred["risk_value"],
        y=pred["machine_id"],
        orientation="h",
        marker_color=colors,
        text=[f"{r} ({v})" for r, v in zip(pred["risk_label"], pred["risk_value"])],
        textposition="outside",
    ))
    fig.update_layout(
        title="Machine Risk Ranking",
        xaxis=dict(title="Risk Score (0-100)", range=[0, 120], gridcolor="#E5E7EB"),
        yaxis_title="Machine",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=380,
    )
    # Threshold lines
    fig.add_vline(x=40, line_dash="dot", line_color="#F59E0B", annotation_text="Medium")
    fig.add_vline(x=70, line_dash="dot", line_color="#EF4444", annotation_text="High")
    return fig


# ──────────────────────────────────────────────
# 6. TTF Prediction Chart
# ──────────────────────────────────────────────

def chart_ttf_prediction(predictions: pd.DataFrame) -> go.Figure:
    if predictions.empty or predictions["predicted_ttf_hours"].isna().all():
        fig = go.Figure()
        fig.update_layout(title="Insufficient data for TTF prediction")
        return fig

    pred = predictions.dropna(subset=["predicted_ttf_hours"]).sort_values(
        "remaining_ttf_hours", ascending=True
    )
    colors = [RISK_COLORS.get(r, "#94A3B8") for r in pred["risk_label"]]

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Bar(
        name="Already Run (h)",
        x=pred["current_run_hours"],
        y=pred["machine_id"],
        orientation="h",
        marker_color="#94A3B8",
    ))
    fig.add_trace(go.Bar(
        name="Remaining TTF (h)",
        x=pred["remaining_ttf_hours"].clip(lower=0),
        y=pred["machine_id"],
        orientation="h",
        marker_color=colors,
    ))
    fig.update_layout(
        barmode="stack",
        title="Predicted Time-to-Failure (TTF)",
        xaxis_title="Hours",
        yaxis_title="Machine",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=380,
        xaxis=dict(gridcolor="#E5E7EB"),
    )
    return fig


# ──────────────────────────────────────────────
# 7. Sensor Trend (optional)
# ──────────────────────────────────────────────

def chart_sensor_trend(df_machine: pd.DataFrame, sensor: str, machine_id: str) -> go.Figure:
    data = df_machine[["timestamp", sensor, "status"]].dropna(subset=[sensor])
    if data.empty:
        fig = go.Figure()
        fig.update_layout(title=f"No {sensor} data for {machine_id}")
        return fig

    up = data[data["status"] == "UP"]
    down = data[data["status"] == "DOWN"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=up["timestamp"], y=up[sensor],
        mode="lines", name="UP", line=dict(color="#22C55E", width=1),
    ))
    fig.add_trace(go.Scatter(
        x=down["timestamp"], y=down[sensor],
        mode="markers", name="DOWN (failure)", marker=dict(color="#EF4444", size=5),
    ))
    # Rolling mean
    data_sorted = data.sort_values("timestamp")
    roll = data_sorted[sensor].rolling(20, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=data_sorted["timestamp"], y=roll,
        mode="lines", name="Rolling Avg", line=dict(color="#6366F1", dash="dash", width=2),
    ))
    fig.update_layout(
        title=f"{sensor.title()} Trend – {machine_id}",
        xaxis_title="Time",
        yaxis_title=sensor.title(),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=300,
        hovermode="x unified",
    )
    return fig
