"""
utils/data_loader.py
Handles CSV/Excel upload, validation, and preprocessing.
"""

import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO


REQUIRED_COLS = {"timestamp", "machine_id", "status"}
OPTIONAL_COLS = {"temperature", "load", "vibration"}
VALID_STATUSES = {"UP", "DOWN"}


def load_data(uploaded_file) -> tuple[pd.DataFrame | None, str | None]:
    """
    Load CSV or Excel file uploaded via Streamlit.
    Returns (dataframe, error_message). On success error_message is None.
    """
    try:
        fname = uploaded_file.name.lower()
        if fname.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif fname.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "Unsupported file type. Please upload a CSV or Excel file."
    except Exception as e:
        return None, f"Failed to read file: {e}"

    return validate_and_preprocess(df)


def validate_and_preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame | None, str | None]:
    """
    Validate required columns, clean data, parse types.
    Returns (clean_df, error_message).
    """
    # Normalise column names
    df.columns = [c.strip().lower() for c in df.columns]

    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        return None, f"Missing required column(s): {', '.join(sorted(missing))}"

    # Parse timestamp
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception:
        return None, "Could not parse 'timestamp' column. Ensure it is a valid date/time string."

    # Normalise status
    df["status"] = df["status"].astype(str).str.strip().str.upper()
    invalid_status = set(df["status"].unique()) - VALID_STATUSES
    if invalid_status:
        return None, (
            f"'status' column contains invalid values: {invalid_status}. "
            "Allowed values: UP, DOWN."
        )

    # Normalise machine_id
    df["machine_id"] = df["machine_id"].astype(str).str.strip()

    # Sort
    df = df.sort_values(["machine_id", "timestamp"]).reset_index(drop=True)

    # Handle optional sensor columns – fill missing with NaN
    for col in OPTIONAL_COLS:
        if col not in df.columns:
            df[col] = np.nan
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows where critical fields are null
    before = len(df)
    df = df.dropna(subset=["timestamp", "machine_id", "status"])
    dropped = before - len(df)

    return df, None if dropped == 0 else None  # silently drop bad rows, still success


def get_data_summary(df: pd.DataFrame) -> dict:
    """Return a quick summary dict for the sidebar / overview panel."""
    return {
        "total_records": len(df),
        "machines": sorted(df["machine_id"].unique().tolist()),
        "date_range": (df["timestamp"].min(), df["timestamp"].max()),
        "has_temperature": df["temperature"].notna().any(),
        "has_load": df["load"].notna().any(),
        "has_vibration": df["vibration"].notna().any(),
    }
