
# Changelog

All notable changes to the TSDPL Kalinganagar Maintenance Dashboard will be documented in this file.

## [Unreleased] - 2026-04-24

### Added
- **QIP Analysis Module (Tab 11)**: Introduced a brand-new tab to perform "Before vs. After" comparison analysis on machine performance.
- **Real-World Data Ingestion**: Added a dedicated file uploader in the sidebar specifically built to ingest unstructured, raw maintenance logs directly from the plant floor.
- **Heuristic Data Loading**: Upgraded `utils/data_loader.py` with an "Anchor Search" to dynamically detect where tabular data begins, bypassing irrelevant header metadata.
- **Fuzzy Column Mapping**: Integrated a dictionary into the data loader to automatically standardize inconsistent column names (e.g., converting "B/D HOURS" to standard `duration_min`).
- **Smart Unit Detection**: Automatically identifies if duration values are in "hours" and converts them to standard "minutes" for internal processing.
- **Comparative Metrics Engine**: Added `compute_qip_comparison` in `utils/tsdpl_analytics.py` to calculate MTBF/MTTR and downtime deltas across distinct date ranges.
- **QIP Visualizations**: Added `chart_qip_comparison` in `utils/tsdpl_charts.py` to render side-by-side Plotly bar charts colored with the dashboard's `#38bdf8` (blue) and `#4ade80` (green) standard.
- **Narrative Generator**: Included logic in the QIP tab to automatically generate an English narrative explaining whether the maintenance intervention improved MTBF and MTTR.

### Changed
- **Consolidated Dashboard App**: Fully merged the experimental features from `app_version3.py` into the production-ready, security-hardened `app_version2.py`.
- **UI Enhancements**: Updated layout widths and metric card delta rendering to accommodate the new percentage-based improvements natively.

### Removed
- **Redundant Scripts**: Cleaned up the working directory by permanently removing the `app_version3.py` file, standardizing execution on a single entry point (`app_version2.py`).
