"""
utils/messy_loader.py  —  Messy real-world CSV/Excel normalizer
TSDPL Kalinganagar Maintenance Dashboard  |  v1.0  |  April 2026

PURPOSE
-------
Factory maintenance exports are never clean.  This module handles:
  - Pivoted headers with metadata rows above the real header
  - Inconsistent column names across different file sources
  - Mixed date formats  (2025-09-03 / 01.08.2025 / Sept'25 etc.)
  - Duration expressed in minutes OR hours depending on the file
  - Merged / unnamed Excel columns that must be dropped
  - Completely empty rows and columns

The output is always a tidy 4-column DataFrame:
    Date          (datetime64[ns])
    Duration_Min  (float64, always minutes)
    Equipment     (str)
    Reason        (str)

USAGE
-----
    from utils.messy_loader import normalize_maintenance_data
    df, error = normalize_maintenance_data(uploaded_file)
    if error:
        st.error(error)
    else:
        # df is ready — feed into MTBF/MTTR functions
"""

import io
import logging
import pandas as pd
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Column alias mapping ──────────────────────────────────────────────────────
# Maps every known alias found in TSDPL / plant files → our standard name.
# Add new aliases here as new file variants are encountered — no other changes
# needed anywhere else in the codebase.

COLUMN_ALIASES: dict[str, list[str]] = {
    "Date": [
        "DATE", "Date", "date", "Month", "MONTH", "month",
        "Sl No", "SL NO", "sl_no", "Period", "PERIOD",
    ],
    "Duration_Min": [
        # minutes variants
        "UNPLANNED B/D \n(Min.)", "UNPLANNED B/D (Min.)",
        "Time (Min)", "TIME (MIN)", "Min", "MIN", "Minutes",
        "DOWNTIME (MIN)", "Downtime (Min)", "downtime_minutes",
        "Duration", "DURATION",
        # hours variants — detected at runtime to trigger ×60 conversion
        "B/D HOURS", "BD HOURS", "HOURS", "Downtime Hours",
        "DOWNTIME (HRS)", "Duration (Hrs)", "HRS",
    ],
    "Equipment": [
        "EQUIPMENT", "Equipment", "equipment",
        "Work Centre", "WORK CENTRE", "work_centre",
        "Machine", "MACHINE", "machine", "machine_id",
        "AREA", "Area", "area", "Asset", "ASSET",
    ],
    "Reason": [
        "BRIEF DESCRIPTION", "Brief Description",
        "Description", "DESCRIPTION", "description",
        "Desc", "DESC", "desc",
        "Failure Reason", "FAILURE REASON", "failure_reason",
        "Remarks", "REMARKS", "remarks",
        "Root Cause", "ROOT CAUSE",
    ],
}

# Hour-denominated aliases — if the matched column name contains any of these
# substrings (case-insensitive), the values are treated as hours → ×60.
HOURS_INDICATORS = ["hour", "hrs", "hr", "b/d hours", "bd hours"]


# ── Public API ────────────────────────────────────────────────────────────────

def normalize_maintenance_data(uploaded_file) -> tuple[pd.DataFrame, str | None]:
    """
    Read a messy CSV or Excel maintenance export and return a clean DataFrame.

    Parameters
    ----------
    uploaded_file : Streamlit UploadedFile
        Raw file object from st.file_uploader().

    Returns
    -------
    (df, error)
        df    — clean 4-column DataFrame on success; empty DataFrame on failure.
        error — None on success; human-readable error string on failure.
    """
    try:
        # ── Step 1: Read the raw file without assuming any header ─────────────
        raw_df, error = _read_raw(uploaded_file)
        if error:
            return pd.DataFrame(), error

        # ── Step 2: Find the real header row and extract the data table ───────
        data_df, error = _extract_table(raw_df)
        if error:
            return pd.DataFrame(), error

        # ── Step 3: Map inconsistent column names → standard names ────────────
        standard_df, hours_col_detected, error = _map_columns(data_df)
        if error:
            return pd.DataFrame(), error

        # ── Step 4: Normalise the Date column → datetime, drop unparseable ────
        standard_df = _parse_dates(standard_df)

        # ── Step 5: Normalise Duration_Min → numeric minutes ─────────────────
        standard_df = _parse_duration(standard_df, hours_col_detected)

        # ── Step 6: Drop rows that are still useless after cleaning ───────────
        standard_df = _final_clean(standard_df)

        if standard_df.empty:
            return pd.DataFrame(), "File parsed but no valid rows remained after cleaning."

        logger.info(
            "normalize_maintenance_data: %d rows loaded from %s",
            len(standard_df), getattr(uploaded_file, "name", "unknown"),
        )
        return standard_df, None

    except Exception as exc:
        logger.error("normalize_maintenance_data failed: %s", exc, exc_info=True)
        return pd.DataFrame(), f"Unexpected error while parsing file: {type(exc).__name__}"


# ── Internal helpers ──────────────────────────────────────────────────────────

def _read_raw(uploaded_file) -> tuple[pd.DataFrame, str | None]:
    """Read CSV or Excel into a headerless DataFrame (all strings, no parsing)."""
    name = getattr(uploaded_file, "name", "").lower()
    ext  = Path(name).suffix.lstrip(".")

    try:
        if ext in ("xlsx", "xls"):
            # Read without a header so metadata rows are preserved as data rows.
            df = pd.read_excel(uploaded_file, header=None, dtype=str)
        else:
            # Attempt UTF-8, fall back to latin-1 for Windows-exported CSVs.
            try:
                df = pd.read_csv(uploaded_file, header=None, dtype=str, encoding="utf-8")
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, header=None, dtype=str, encoding="latin-1")
    except Exception as exc:
        return pd.DataFrame(), f"Could not open file: {exc}"

    return df, None


def _extract_table(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, str | None]:
    """
    Locate the real header row — defined as the first row that has
    at least 3 non-null, non-empty values.  Everything above it is metadata.
    """
    # Replace completely empty strings with NaN so dropna works correctly.
    cleaned = raw_df.replace(r"^\s*$", np.nan, regex=True)

    # Find first row index that has >= 3 non-null values.
    non_null_counts = cleaned.notna().sum(axis=1)
    candidate_rows  = non_null_counts[non_null_counts >= 3]

    if candidate_rows.empty:
        return pd.DataFrame(), (
            "Could not locate a header row. "
            "The file may be empty or have too many metadata rows."
        )

    header_row_idx = candidate_rows.index[0]

    # Use that row as column names; everything below it is data.
    col_names = cleaned.iloc[header_row_idx].fillna("").astype(str).tolist()

    # Deduplicate blank/Unnamed column names to avoid pandas confusion.
    seen: dict[str, int] = {}
    deduped = []
    for c in col_names:
        key = c.strip() if c.strip() else "Unnamed"
        seen[key] = seen.get(key, 0) + 1
        deduped.append(key if seen[key] == 1 else f"{key}_{seen[key]}")

    data_df = cleaned.iloc[header_row_idx + 1:].copy()
    data_df.columns = deduped
    data_df = data_df.reset_index(drop=True)

    # Drop columns that are entirely empty or named "Unnamed*".
    useful_cols = [c for c in data_df.columns if not c.startswith("Unnamed")]
    data_df = data_df[useful_cols]

    # Drop entirely-NaN rows.
    data_df = data_df.dropna(how="all")

    return data_df, None


def _map_columns(
    data_df: pd.DataFrame,
) -> tuple[pd.DataFrame, bool, str | None]:
    """
    Map raw column names → standard names using COLUMN_ALIASES.

    Returns (standard_df, hours_col_detected, error).
    hours_col_detected is True when the Duration column name implies hours.
    """
    col_lookup: dict[str, str] = {}   # raw_name → standard_name
    hours_col_detected = False

    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            # Normalise both sides for a fuzzy match.
            norm_alias = alias.lower().replace("\n", " ").strip()
            for raw_col in data_df.columns:
                norm_raw = raw_col.lower().replace("\n", " ").strip()
                if norm_raw == norm_alias:
                    col_lookup[raw_col] = standard_name
                    # Check if this Duration column is hours-denominated.
                    if standard_name == "Duration_Min":
                        if any(h in norm_raw for h in HOURS_INDICATORS):
                            hours_col_detected = True
                    break  # first match wins per standard column

    # Keep only the columns we could map; rename them.
    mapped_cols = {raw: std for raw, std in col_lookup.items()}
    found_standards = set(mapped_cols.values())
    required = {"Date", "Duration_Min", "Equipment", "Reason"}
    missing  = required - found_standards

    if missing:
        available = ", ".join(f'"{c}"' for c in data_df.columns[:15])
        return pd.DataFrame(), False, (
            f"Could not find columns for: {', '.join(sorted(missing))}. "
            f"Columns found in file: {available}."
        )

    # Rename and keep only the four standard columns.
    standard_df = data_df.rename(columns=mapped_cols)[list(required)].copy()
    return standard_df, hours_col_detected, None


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Coerce the Date column to datetime.  Rows that cannot be parsed are dropped.
    Handles: ISO dates, DD.MM.YYYY, "Sept'25", "Sep-25", plain month names, etc.
    """
    # pd.to_datetime with dayfirst=True covers most European/Indian plant formats.
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)

    # For remaining NaT values, try a second pass stripping apostrophes
    # (e.g. "Sept'25" → "Sept 25").
    mask = df["Date"].isna()
    if mask.any():
        repaired = df.loc[mask, "Date_raw"] if "Date_raw" in df.columns else df.loc[mask, "Date"].astype(str)
        repaired = repaired.str.replace("'", " ", regex=False)
        df.loc[mask, "Date"] = pd.to_datetime(repaired, errors="coerce", dayfirst=True)

    # Drop rows where date is still NaT after both attempts.
    before = len(df)
    df = df.dropna(subset=["Date"]).copy()
    dropped = before - len(df)
    if dropped:
        logger.info("_parse_dates: dropped %d rows with unparseable dates.", dropped)

    return df


def _parse_duration(df: pd.DataFrame, hours_col: bool) -> pd.DataFrame:
    """
    Convert Duration_Min to a numeric float in minutes.
    If the source column was hours-denominated, multiply by 60.
    Non-numeric values are coerced to NaN (not dropped — caller may want them).
    """
    df["Duration_Min"] = pd.to_numeric(df["Duration_Min"], errors="coerce")

    if hours_col:
        # Column was in hours — convert to minutes.
        df["Duration_Min"] = df["Duration_Min"] * 60
        logger.info("_parse_duration: converted hours → minutes (*60).")

    # Floor negative durations to 0 (data entry errors).
    df["Duration_Min"] = df["Duration_Min"].clip(lower=0)

    return df


def _final_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Final pass: drop rows with NaN Duration or Equipment; strip whitespace.
    """
    df = df.dropna(subset=["Duration_Min", "Equipment"])
    df["Equipment"] = df["Equipment"].astype(str).str.strip()
    df["Reason"]    = df["Reason"].fillna("Not specified").astype(str).str.strip()
    df = df[df["Duration_Min"] > 0]   # zero-duration rows carry no information
    df = df.reset_index(drop=True)
    return df


# ── MTBF / MTTR helpers for the QIP analysis tab ─────────────────────────────

def compute_mtbf_mttr_from_norm(df: pd.DataFrame, period_mask: pd.Series) -> dict:
    """
    Compute MTBF and MTTR from a normalised DataFrame for a given time window.

    Parameters
    ----------
    df          : normalised DataFrame (output of normalize_maintenance_data)
    period_mask : boolean Series indexing into df for the time window

    Returns
    -------
    dict with keys: failures, total_downtime_min, mttr_min, mtbf_h, period_hours
    """
    sub = df[period_mask].copy()

    if sub.empty:
        return {
            "failures": 0, "total_downtime_min": 0.0,
            "mttr_min": 0.0, "mtbf_h": 0.0, "period_hours": 0.0,
        }

    failures          = len(sub)
    total_downtime_min = sub["Duration_Min"].sum()
    mttr_min          = total_downtime_min / failures if failures else 0.0

    # Period span in hours.
    period_hours = (sub["Date"].max() - sub["Date"].min()).total_seconds() / 3600
    period_hours = max(period_hours, 1.0)   # avoid division by zero

    uptime_hours = period_hours - (total_downtime_min / 60)
    mtbf_h       = uptime_hours / failures if failures else uptime_hours

    return {
        "failures"          : failures,
        "total_downtime_min": round(total_downtime_min, 1),
        "mttr_min"          : round(mttr_min, 1),
        "mtbf_h"            : round(mtbf_h, 2),
        "period_hours"      : round(period_hours, 1),
    }
