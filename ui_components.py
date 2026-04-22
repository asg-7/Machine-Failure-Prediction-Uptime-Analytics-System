"""
components/ui_components.py
Reusable Streamlit UI building blocks.
"""

import streamlit as st
import pandas as pd
from typing import Optional


RISK_BADGE = {
    "High":    ("🔴", "rgba(239, 68, 68, 0.15)", "#EF4444"),
    "Medium":  ("🟡", "rgba(245, 158, 11, 0.15)", "#F59E0B"),
    "Low":     ("🟢", "rgba(34, 197, 94, 0.15)", "#22C55E"),
    "Unknown": ("⚪", "rgba(148, 163, 184, 0.15)", "#94A3B8"),
}


def risk_badge_html(label: str) -> str:
    icon, bg, color = RISK_BADGE.get(label, RISK_BADGE["Unknown"])
    return (
        f'<span style="background:{bg};color:{color};padding:2px 10px;'
        f'border-radius:12px;font-weight:600;font-size:0.85em;">{icon} {label}</span>'
    )


def metric_card(title: str, value: str, delta: Optional[str] = None,
                color: str = "#6366F1") -> None:
    delta_html = (
        f'<div style="font-size:0.8em;opacity:0.7;margin-top:2px;">{delta}</div>'
        if delta else ""
    )
    st.markdown(
        f"""
        <div style="background:rgba(120,120,120,0.05);border-left:4px solid {color};
                    border-radius:8px;padding:16px 20px;margin-bottom:8px;
                    box-shadow:0 2px 4px rgba(0,0,0,0.02);">
            <div style="font-size:0.8em;opacity:0.7;text-transform:uppercase;
                        letter-spacing:0.05em;font-weight:600;">{title}</div>
            <div style="font-size:1.6em;font-weight:700;color:var(--text-color);">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_banner(message: str, level: str = "warning") -> None:
    """level: info | warning | error | success"""
    colors = {
        "info":    ("rgba(59, 130, 246, 0.1)", "#3B82F6", "ℹ️"),
        "warning": ("rgba(245, 158, 11, 0.1)", "#F59E0B", "⚠️"),
        "error":   ("rgba(239, 68, 68, 0.1)", "#EF4444", "🚨"),
        "success": ("rgba(34, 197, 94, 0.1)", "#22C55E", "✅"),
    }
    bg, border, icon = colors.get(level, colors["info"])
    st.markdown(
        f"""
        <div style="background:{bg};border-left:4px solid {border};
                    border-radius:8px;padding:14px 18px;margin:8px 0;
                    color:var(--text-color); animation: fadeIn 0.5s ease-in;">
            {icon} &nbsp; {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_prediction_card(row: pd.Series) -> None:
    """Render a single machine prediction card."""
    label = row.get("risk_label", "Unknown")
    icon, bg, color = RISK_BADGE.get(label, RISK_BADGE["Unknown"])
    ttf = row.get("remaining_ttf_hours")
    ttf_str = f"{ttf:.1f} h" if (ttf is not None and not pd.isna(ttf)) else "N/A"
    cur_run = row.get("current_run_hours", 0)
    pred_ttf = row.get("predicted_ttf_hours")
    pred_str = f"{pred_ttf:.1f} h" if (pred_ttf is not None and not pd.isna(pred_ttf)) else "N/A"
    conf = row.get("confidence", "N/A")
    failures = row.get("failure_count", 0)

    st.markdown(
        f"""
        <div style="background:rgba(120,120,120,0.05);border:1px solid rgba(120,120,120,0.1);
                    border-radius:12px;padding:20px;margin-bottom:12px;
                    box-shadow:0 4px 6px rgba(0,0,0,0.02);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:1.15em;font-weight:700;color:var(--text-color);letter-spacing:-0.5px;">
                    {row['machine_id']}
                </span>
                <span style="background:{bg};color:{color};padding:4px 12px;
                             border-radius:12px;font-weight:600;font-size:0.85em;
                             border:1px solid {color};">
                    {icon} {label} Risk
                </span>
            </div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);
                        gap:12px;margin-top:16px;">
                <div>
                    <div style="font-size:0.72em;opacity:0.6;font-weight:600;letter-spacing:0.5px;">REMAINING TTF</div>
                    <div style="font-size:1.2em;font-weight:700;color:var(--text-color);">{ttf_str}</div>
                </div>
                <div>
                    <div style="font-size:0.72em;opacity:0.6;font-weight:600;letter-spacing:0.5px;">PREDICTED CYCLE</div>
                    <div style="font-size:1.2em;font-weight:700;color:var(--text-color);">{pred_str}</div>
                </div>
                <div>
                    <div style="font-size:0.72em;opacity:0.6;font-weight:600;letter-spacing:0.5px;">FAILURES LOGGED</div>
                    <div style="font-size:1.2em;font-weight:700;color:var(--text-color);">{failures}</div>
                </div>
            </div>
            <div style="margin-top:16px;font-size:0.8em;opacity:0.5;font-weight:500;">
                Current run: {cur_run:.1f} h &nbsp;|&nbsp; Model confidence: {conf}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert_machines(predictions: pd.DataFrame) -> None:
    """Show alert banner for High/Medium risk machines."""
    high = predictions[predictions["risk_label"] == "High"]["machine_id"].tolist()
    medium = predictions[predictions["risk_label"] == "Medium"]["machine_id"].tolist()

    if high:
        alert_banner(
            f"<strong>CRITICAL:</strong> {', '.join(high)} — High failure risk. "
            "Schedule maintenance immediately.",
            level="error",
        )
    if medium:
        alert_banner(
            f"<strong>CAUTION:</strong> {', '.join(medium)} — Medium failure risk. "
            "Plan maintenance within next cycle.",
            level="warning",
        )
    if not high and not medium:
        alert_banner("All machines are currently in Low risk zone. ✅", level="success")


def section_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<p style="opacity:0.6;margin:0;font-size:0.95em;">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div style="margin:30px 0 16px 0; border-bottom: 1px solid rgba(120,120,120,0.1); padding-bottom: 8px;">
            <h3 style="margin:0;color:var(--text-color);letter-spacing:-0.5px;font-weight:700;">{title}</h3>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
