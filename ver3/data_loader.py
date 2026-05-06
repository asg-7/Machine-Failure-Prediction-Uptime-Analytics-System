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

# MAPPING dictionary to translate TSDPL headers into standard keys
COLUMN_MAPPING = {
    "timestamp": ["DATE", "Date", "date", "Month", "MONTH", "month", "Sl No", "SL NO", "sl_no", "Period", "PERIOD", "timestamp"],
    "machine_id": ["EQUIPMENT", "Equipment", "equipment", "Work Centre", "WORK CENTRE", "work_centre", "Machine", "MACHINE", "machine", "machine_id", "AREA", "Area", "area", "Asset", "ASSET"],
    "duration_min": ["UNPLANNED B/D \n(Min.)", "UNPLANNED B/D (Min.)", "Time (Min)", "TIME (MIN)", "Min", "MIN", "Minutes", "DOWNTIME (MIN)", "Downtime (Min)", "downtime_minutes", "Duration", "DURATION", "B/D HOURS", "BD HOURS", "HOURS", "Downtime Hours", "DOWNTIME (HRS)", "Duration (Hrs)", "HRS"],
    "failure_category": ["failure_category", "Category", "CATEGORY", "category"],
    "status": ["status", "Status", "STATUS"]
}

def _fuzzy_map_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """Fuzzy mapping of columns using COLUMN_MAPPING. Returns mapped df and boolean indicating if hours were detected."""
    hours_detected = False
    rename_map = {}
    for std_col, aliases in COLUMN_MAPPING.items():
        for alias in aliases:
            norm_alias = alias.lower().replace("\n", " ").strip()
            for raw_col in df.columns:
                norm_raw = str(raw_col).lower().replace("\n", " ").strip()
                if norm_raw == norm_alias:
                    rename_map[raw_col] = std_col
                    if std_col == "duration_min" and any(h in norm_raw for h in ["hour", "hrs", "hr", "b/d hours"]):
                        hours_detected = True
                    break
    return df.rename(columns=rename_map), hours_detected

def load_data(uploaded_file) -> tuple[pd.DataFrame | None, str | None]:
    """
    Load CSV or Excel file uploaded via Streamlit.
    Implements Heuristic Anchor Search and Fuzzy Mapping.
    Returns (dataframe, error_message). On success error_message is None.
    """
    try:
        fname = uploaded_file.name.lower()
        if fname.endswith(".csv"):
            try:
                raw_df = pd.read_csv(uploaded_file, header=None)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                raw_df = pd.read_csv(uploaded_file, header=None, encoding="latin-1")
        elif fname.endswith((".xlsx", ".xls")):
            raw_df = pd.read_excel(uploaded_file, header=None)
        else:
            return None, "Unsupported file type. Please upload a CSV or Excel file."
            
        # Heuristic Anchor Search
        cleaned = raw_df.replace(r"^\s*$", np.nan, regex=True)
        # Find where the table actually starts
        try:
            start_idx = cleaned.dropna(thresh=3).index[0]
        except IndexError:
            return None, "Could not locate a valid data table in the file."
            
        # Set columns and drop metadata rows
        df = cleaned.iloc[start_idx + 1:].copy()
        df.columns = cleaned.iloc[start_idx].fillna("").astype(str).tolist()
        df = df.dropna(how="all").reset_index(drop=True)
        
        # Fuzzy Mapping
        df, hours_detected = _fuzzy_map_columns(df)
        
        # If this is a standard UP/DOWN file, process it normally
        if set(["timestamp", "machine_id", "status"]).issubset(df.columns):
            return validate_and_preprocess(df)
            
        # If this is a messy downtime record, process it for QIP
        if "duration_min" in df.columns and "timestamp" in df.columns and "machine_id" in df.columns:
            # Parse timestamp
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True)
            df = df.dropna(subset=["timestamp"])
            
            # Unit detection to convert Hours to Minutes automatically
            df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce").fillna(0)
            if hours_detected:
                df["duration_min"] = df["duration_min"] * 60
                
            df["machine_id"] = df["machine_id"].astype(str).str.strip()
            df = df[df["duration_min"] > 0].reset_index(drop=True)
            return df, None
            
        # Fallback to standard validation if mapping didn't find specific QIP columns
        return validate_and_preprocess(df)
        
    except Exception as e:
        return None, f"Failed to read file: {e}"


def validate_and_preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame | None, str | None]:
    """
    Validate required columns, clean data, parse types.
    Returns (clean_df, error_message).
    """
    # Normalise column names
    df.columns = [str(c).strip().lower() for c in df.columns]

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
    # Handle the case where the df might be a QIP messy file without UP/DOWN statuses
    has_temp = "temperature" in df.columns and df["temperature"].notna().any()
    has_load = "load" in df.columns and df["load"].notna().any()
    has_vib = "vibration" in df.columns and df["vibration"].notna().any()
    
    return {
        "total_records": len(df),
        "machines": sorted(df["machine_id"].unique().tolist()) if "machine_id" in df.columns else [],
        "date_range": (df["timestamp"].min(), df["timestamp"].max()) if "timestamp" in df.columns else (None, None),
        "has_temperature": has_temp,
        "has_load": has_load,
        "has_vibration": has_vib,
    }
