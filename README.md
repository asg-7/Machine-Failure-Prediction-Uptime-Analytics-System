# Machine-Failure-Prediction-Uptime-Analytics-System
A **Streamlit-based predictive maintenance dashboard** that analyzes machine logs to track uptime, detect failure patterns, and estimate **time-to-failure (TTF)** for proactive maintenance planning.

---

## 🚀 Features

### 📊 Uptime Analytics

* Machine-wise uptime vs downtime
* Daily uptime trends
* Best & worst performing machines

### 💥 Failure Detection

* Detects **UP → DOWN transitions** as failure events
* Runtime before failure analysis
* Failure frequency & patterns

### 🔮 Predictive Insights

* Time-to-Failure (TTF) estimation
* Remaining useful life calculation
* Machine risk classification:

  * 🔴 High
  * 🟡 Medium
  * 🟢 Low

### 🚨 Smart Alerts

* Flags high-risk machines
* Maintenance recommendations
* Sensor anomaly detection

### 🔬 Drilldown Analysis

* Machine-level deep dive
* Sensor trend visualization (temperature, load, vibration)
* Failure logs & raw data inspection

---

## 🏗️ Project Structure

```
├── app.py                      # Main Streamlit app
├── utils/
│   ├── data_loader.py         # Data loading & validation
│   ├── analytics.py           # Uptime & failure analysis
│   ├── predictor.py           # TTF prediction & risk scoring
│   ├── charts.py              # Plotly visualizations
│
├── components/
│   ├── ui_components.py       # UI elements (cards, alerts, etc.)
│
├── generate_sample_data.py    # Demo dataset generator
└── requirements.txt           # Dependencies
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/machine-failure-analytics.git
cd machine-failure-analytics
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

---

## 📂 Input Data Format

Upload a CSV or Excel file with the following structure:

| timestamp        | machine_id | status | temperature | load | vibration |
| ---------------- | ---------- | ------ | ----------- | ---- | --------- |
| 2024-01-01 00:00 | MCH-001    | UP     | 72.3        | 85   | 1.2       |
| 2024-01-01 00:30 | MCH-001    | DOWN   | 45.1        | 0    | 0.1       |

### Required Columns:

* `timestamp` (datetime)
* `machine_id`
* `status` (`UP` / `DOWN`)

### Optional:

* `temperature`
* `load`
* `vibration`

---

## 🧠 How It Works

### 1. Data Processing

* Cleans and validates input data
* Converts timestamps and sorts events

### 2. Failure Detection

* Identifies **UP → DOWN transitions**
* Calculates runtime before each failure

### 3. Analytics Engine

* Uptime/downtime computation
* Failure frequency & patterns
* Hourly and daily trends

### 4. Prediction Engine

* Estimates **Time-To-Failure (TTF)**:

  ```
  TTF ≈ Average Runtime Before Failure
  ```
* Computes:

  * Current runtime
  * Remaining TTF
  * Risk score

### 5. Risk Classification

Based on:

* Failure frequency
* Remaining TTF
* Sensor anomalies

---

## 📊 Dashboard Tabs

### 🏠 Overview

* KPIs & risk ranking
* Fleet-wide insights

### 📈 Uptime Analysis

* Machine availability trends
* Downtime analysis

### 💥 Failure Patterns

* Failure logs
* Runtime statistics

### 🔮 Predictions & Risk

* Risk cards
* Maintenance alerts

### 🔬 Machine Drilldown

* Sensor analysis
* Individual machine inspection

---

## ⚡ Tech Stack

* **Frontend/UI:** Streamlit
* **Data Processing:** Pandas, NumPy
* **Visualization:** Plotly
* **Modeling:** Statistical heuristics

---

## ⚠️ Limitations

* No advanced ML models (uses statistical estimation)
* Assumes consistent machine behavior over time
* No real-time data streaming
* Limited root cause analysis

---

## 🚀 Future Improvements

* ✅ Add ML models (Random Forest, XGBoost, LSTM)
* ✅ Real-time data ingestion (Kafka / MQTT)
* ✅ Database integration (PostgreSQL / InfluxDB)
* ✅ Alert system (Email / SMS)
* ✅ Root cause analysis using sensor correlation
* ✅ Multi-plant scalability
* ✅ API layer (FastAPI)

---

## 💡 Use Cases

* Manufacturing plants
* Steel & heavy industry
* Predictive maintenance systems
* Reliability engineering dashboards

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch
3. Make changes
4. Submit a pull request

---

## 📜 License

This project is licensed under the MIT License.

---

## 👤 Author

**Anubhav Sengupta**

---

## ⭐ If you found this useful

Give it a star on GitHub — it helps a lot!
