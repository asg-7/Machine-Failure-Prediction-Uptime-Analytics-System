# ⚙️ Machine Failure Prediction & Uptime Analytics System

A lightweight Streamlit app for plant engineers, maintenance teams, and operations managers to:

- Track uptime/downtime per machine
- Detect failure patterns and time-of-day trends
- Predict Time-to-Failure (TTF) using moving averages + linear regression
- Rank machines by risk: 🔴 High / 🟡 Medium / 🟢 Low

---

## 📁 File Structure

```
machine_failure_app/
├── app.py                      # Main Streamlit entry point
├── requirements.txt            # Python dependencies
├── generate_sample_data.py     # Demo data generator
├── sample_data.csv             # Pre-generated sample (5 machines, 60 days)
├── utils/
│   ├── __init__.py
│   ├── data_loader.py          # File upload, validation, preprocessing
│   ├── analytics.py            # Uptime engine + failure pattern detection
│   ├── predictor.py            # TTF prediction + risk scoring
│   └── charts.py               # All Plotly visualizations
└── components/
    ├── __init__.py
    └── ui_components.py        # Reusable Streamlit UI blocks
```

---

## 🚀 Setup & Run

### 1. Install Python (3.10+)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 📊 Input Data Format

Upload a CSV or Excel file with these columns:

| Column | Required | Description |
|--------|----------|-------------|
| `timestamp` | ✅ | Any standard datetime string |
| `machine_id` | ✅ | Unique identifier per machine |
| `status` | ✅ | `UP` or `DOWN` |
| `temperature` | Optional | Sensor reading |
| `load` | Optional | Sensor reading |
| `vibration` | Optional | Sensor reading |

### Example row:
```
2024-01-15 08:30:00, MCH-001, UP, 72.3, 85.0, 1.2
```

---

## 🧠 Prediction Model

The TTF prediction uses a two-stage approach:
1. **Moving Average** of recent failure intervals (last 5 events)
2. **Linear Regression** on failure intervals to detect trend

Both are combined via a weighted average where the regression weight increases with R² score.

**Risk Score (0–100):**
- Based on ratio of current runtime to predicted TTF cycle
- Penalized by coefficient of variation in historical runtimes
- **High ≥ 70 | Medium ≥ 40 | Low < 40**

---

## 🎲 Demo Data

Run without uploading by clicking **Load Demo Data** in the sidebar, or generate manually:

```bash
python generate_sample_data.py
```
Creates `sample_data.csv` with 5 machines, 60 days of data, varied failure patterns.

---

## ✅ Tested with
- Python 3.10 / 3.11
- Streamlit 1.32+
- Pandas 2.0+
- scikit-learn 1.3+
