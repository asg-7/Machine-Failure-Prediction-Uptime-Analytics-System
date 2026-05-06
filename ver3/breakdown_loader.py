# utils/breakdown_loader.py

import pandas as pd
import re


# ── Column name cleaner ───────────────────────────────────────────────────────

def _clean_col(name: str) -> str:
    """
    Normalise a column name:
      - Remove non-breaking spaces (\xa0)
      - Collapse all whitespace runs (spaces, newlines, tabs) to a single space
      - Strip leading / trailing whitespace
    """
    name = str(name)
    name = name.replace('\xa0', ' ')      # non-breaking space → regular space
    name = re.sub(r'\s+', ' ', name)      # collapse all whitespace runs
    return name.strip()


# ── Main loader ───────────────────────────────────────────────────────────────

def load_breakdown_excel(uploaded_file):
    """
    Load a Breakdown Details Excel file and return structured data.

    Handles the real-world quirks confirmed in the WCTL breakdown files:
      - 'Monthly BD Sheet' : column names contain \\xa0 and embedded newlines
                             e.g. 'UNPLANNED B/D\\xa0 \\n(Min.)'
      - 'pivot'            : 2 blank rows before the actual header (row index 2)
                             columns also contain \\xa0 + \\n
      - 'PARETO'           : merged title row at index 0, real header at index 1
                             'EQUIPMENT' column has a trailing space

    Supports multiple files uploaded together (WCTL-1, WCTL-2, Slit).
    The AREA column drives all line-level filtering — nothing is hardcoded.

    Parameters
    ----------
    uploaded_file : file-like object
        Streamlit UploadedFile or any file-like accepted by pd.ExcelFile.

    Returns
    -------
    dict with keys:
        raw_df         : pd.DataFrame  – all breakdown events (cleaned)
        pivot_df       : pd.DataFrame  – equipment sum-hours & count
        pareto_df      : pd.DataFrame  – equipment sorted by hours descending
        line_list      : list[str]     – sorted unique AREA values
        equipment_list : list[str]     – sorted unique EQUIPMENT values
        _hr_col        : str           – resolved name of the hours column
                                         (used by app for dynamic recompute)
    """

    xl = pd.ExcelFile(uploaded_file)
    sheet_names = xl.sheet_names

    # ── 1. Raw breakdown data ─────────────────────────────────────────────────
    target_sheet = 'Monthly BD Sheet'
    raw_sheet = target_sheet if target_sheet in sheet_names else sheet_names[0]
    raw_df = pd.read_excel(uploaded_file, sheet_name=raw_sheet)

    # Deep-clean every column name (handles \xa0 + \n combos)
    raw_df.columns = [_clean_col(c) for c in raw_df.columns]

    # Drop completely empty rows (stray blank rows in real-world exports)
    raw_df.dropna(how='all', inplace=True)
    raw_df.reset_index(drop=True, inplace=True)

    # Resolve minutes and hours column names dynamically after cleaning
    # (avoids hard-coding the exact cleaned string)
    min_col = next(
        (c for c in raw_df.columns if 'MIN' in c.upper() and 'B/D' in c.upper()),
        None
    )
    hr_col = next(
        (c for c in raw_df.columns if 'HR' in c.upper() and 'B/D' in c.upper()),
        None
    )

    # Coerce to numeric
    if min_col:
        raw_df[min_col] = pd.to_numeric(raw_df[min_col], errors='coerce').fillna(0)
    if hr_col:
        raw_df[hr_col] = pd.to_numeric(raw_df[hr_col], errors='coerce').fillna(0)
    elif min_col:
        # Synthesise hours if the sheet only has the minutes column
        hr_col = 'UNPLANNED B/D (Hr)'
        raw_df[hr_col] = raw_df[min_col] / 60

    # Parse DATE
    if 'DATE' in raw_df.columns:
        raw_df['DATE'] = pd.to_datetime(raw_df['DATE'], errors='coerce')

    # Strip trailing spaces from key string columns
    # (real file has e.g. 'BELT CONVEYOR ', 'SCRAP TROLLEY ')
    for col in ['AREA', 'EQUIPMENT']:
        if col in raw_df.columns:
            raw_df[col] = raw_df[col].astype(str).str.strip()

    # Remove rows where EQUIPMENT is NaN / empty / 'nan' (footer/summary rows)
    raw_df = raw_df[
        raw_df['EQUIPMENT'].notna() &
        (raw_df['EQUIPMENT'].astype(str).str.lower() != 'nan') &
        (raw_df['EQUIPMENT'].astype(str).str.strip() != '')
    ].reset_index(drop=True)

    # Unique line and equipment lists (fully dynamic — no hardcoding)
    line_list = sorted(raw_df['AREA'].dropna().unique().tolist()) \
        if 'AREA' in raw_df.columns else []

    equipment_list = sorted(raw_df['EQUIPMENT'].dropna().unique().tolist()) \
        if 'EQUIPMENT' in raw_df.columns else []

    # ── 2. Pivot sheet ────────────────────────────────────────────────────────
    if 'pivot' in sheet_names:
        # Read without assuming a header row
        pivot_raw = pd.read_excel(uploaded_file, sheet_name='pivot', header=None)

        # Find the row containing 'Row Labels' (the actual header)
        header_row = None
        for i, row in pivot_raw.iterrows():
            if any('row labels' in str(v).lower() for v in row):
                header_row = i
                break

        if header_row is not None:
            pivot_df = pd.read_excel(
                uploaded_file, sheet_name='pivot', header=header_row
            )
            # Clean column names (they also contain \xa0 + \n)
            pivot_df.columns = [_clean_col(c) for c in pivot_df.columns]
            pivot_df.dropna(how='all', inplace=True)

            # Rename first column → EQUIPMENT
            pivot_df.rename(columns={pivot_df.columns[0]: 'EQUIPMENT'}, inplace=True)
            pivot_df['EQUIPMENT'] = pivot_df['EQUIPMENT'].astype(str).str.strip()

            # Drop Grand Total row if present
            pivot_df = pivot_df[
                pivot_df['EQUIPMENT'].str.lower() != 'grand total'
            ].reset_index(drop=True)

            # Standardise value column names regardless of exact wording
            sum_col   = next((c for c in pivot_df.columns if 'SUM'   in c.upper()), None)
            count_col = next((c for c in pivot_df.columns if 'COUNT' in c.upper()), None)

            rename_map = {}
            if sum_col:
                rename_map[sum_col]   = 'Sum of Unplanned B/D (Hr)'
            if count_col:
                rename_map[count_col] = 'Count of Unplanned B/D'
            pivot_df.rename(columns=rename_map, inplace=True)

            # Coerce value columns to numeric
            for col in ['Sum of Unplanned B/D (Hr)', 'Count of Unplanned B/D']:
                if col in pivot_df.columns:
                    pivot_df[col] = pd.to_numeric(pivot_df[col], errors='coerce').fillna(0)
        else:
            # Header row not found — compute from raw data
            pivot_df = _compute_pivot(raw_df, hr_col)
    else:
        pivot_df = _compute_pivot(raw_df, hr_col)

    # ── 3. Pareto sheet ───────────────────────────────────────────────────────
    if 'PARETO' in sheet_names:
        # Read without assuming a header row
        pareto_raw = pd.read_excel(uploaded_file, sheet_name='PARETO', header=None)

        # Find the row containing 'EQUIPMENT' (the actual header)
        # Row 0 = merged title 'MAJOR UNPLANNED BREAKDOWN'
        # Row 1 = real header: SL.NO | EQUIPMENT | BREAKDOWN(HRs) | BREAKDOWN(No.s)
        header_row = None
        for i, row in pareto_raw.iterrows():
            if any('equipment' in str(v).lower() for v in row):
                header_row = i
                break

        if header_row is not None:
            pareto_df = pd.read_excel(
                uploaded_file, sheet_name='PARETO', header=header_row
            )
            pareto_df.columns = [_clean_col(c) for c in pareto_df.columns]
            pareto_df.dropna(how='all', inplace=True)

            # Locate the three columns we need by fuzzy matching
            eq_col  = next((c for c in pareto_df.columns if 'EQUIP' in c.upper()), None)
            hrs_col = next((c for c in pareto_df.columns if 'HR'    in c.upper()), None)
            # 'No.s' column: must contain 'NO' and NOT be the SL.NO column
            nos_col = next(
                (c for c in pareto_df.columns
                 if 'NO' in c.upper() and c != eq_col and 'SL' not in c.upper()),
                None
            )

            if eq_col and hrs_col and nos_col:
                pareto_df = pareto_df[[eq_col, hrs_col, nos_col]].copy()
                pareto_df.columns = ['EQUIPMENT', 'BREAKDOWN(HRs)', 'BREAKDOWN(No.s)']
            else:
                # Columns not matched — fall back to computing from raw
                pareto_df = _compute_pareto(raw_df, hr_col)
        else:
            pareto_df = _compute_pareto(raw_df, hr_col)
    else:
        pareto_df = _compute_pareto(raw_df, hr_col)

    # ── Final cleanup on pareto ───────────────────────────────────────────────
    pareto_df['EQUIPMENT']       = pareto_df['EQUIPMENT'].astype(str).str.strip()
    pareto_df['BREAKDOWN(HRs)']  = pd.to_numeric(pareto_df['BREAKDOWN(HRs)'],  errors='coerce').fillna(0)
    pareto_df['BREAKDOWN(No.s)'] = pd.to_numeric(pareto_df['BREAKDOWN(No.s)'], errors='coerce').fillna(0)

    # Remove Grand Total row and empty rows
    pareto_df = pareto_df[
        (pareto_df['EQUIPMENT'].str.lower() != 'grand total') &
        (pareto_df['EQUIPMENT'].str.lower() != 'nan') &
        (pareto_df['EQUIPMENT'].str.strip() != '')
    ].sort_values('BREAKDOWN(HRs)', ascending=False).reset_index(drop=True)

    return {
        'raw_df':         raw_df,
        'pivot_df':       pivot_df,
        'pareto_df':      pareto_df,
        'line_list':      line_list,
        'equipment_list': equipment_list,
        '_hr_col':        hr_col,     # passed back so the app tab can recompute dynamically
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _compute_pivot(raw_df: pd.DataFrame, hr_col: str) -> pd.DataFrame:
    """Compute pivot summary from raw data when the pivot sheet is absent/unreadable."""
    grp = (
        raw_df.groupby('EQUIPMENT')[hr_col]
        .agg(['sum', 'count'])
        .reset_index()
    )
    grp.columns = ['EQUIPMENT', 'Sum of Unplanned B/D (Hr)', 'Count of Unplanned B/D']
    return grp.sort_values('Sum of Unplanned B/D (Hr)', ascending=False).reset_index(drop=True)


def _compute_pareto(raw_df: pd.DataFrame, hr_col: str) -> pd.DataFrame:
    """Compute Pareto table from raw data when the PARETO sheet is absent/unreadable."""
    grp = (
        raw_df.groupby('EQUIPMENT')[hr_col]
        .agg(['sum', 'count'])
        .reset_index()
    )
    grp.columns = ['EQUIPMENT', 'BREAKDOWN(HRs)', 'BREAKDOWN(No.s)']
    return grp.sort_values('BREAKDOWN(HRs)', ascending=False).reset_index(drop=True)
