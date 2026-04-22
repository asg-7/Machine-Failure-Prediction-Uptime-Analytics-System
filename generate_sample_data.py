"""
generate_sample_data.py
Run this once to create a sample CSV for testing:
    python generate_sample_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(n_machines=5, days=60, output_path="sample_data.csv"):
    random.seed(42)
    np.random.seed(42)

    machines = [f"MCH-{str(i).zfill(3)}" for i in range(1, n_machines + 1)]
    # Different reliability profiles per machine
    failure_probs = {m: random.uniform(0.01, 0.06) for m in machines}

    rows = []
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    total_minutes = days * 24 * 60
    step_minutes = 30  # one record every 30 min

    for machine in machines:
        current_time = start_time
        status = "UP"
        downtime_remaining = 0
        temp_base = random.uniform(60, 80)
        load_base = random.uniform(50, 85)
        vibration_base = random.uniform(0.5, 2.0)

        for _ in range(0, total_minutes, step_minutes):
            if downtime_remaining > 0:
                status = "DOWN"
                downtime_remaining -= step_minutes
                temp = temp_base * random.uniform(0.5, 0.7)
                load = 0
                vibration = random.uniform(0.0, 0.3)
            else:
                status = "UP"
                # Gradually increase stress near failure
                stress = random.uniform(0.9, 1.1)
                temp = temp_base * stress + random.uniform(-3, 3)
                load = load_base * stress + random.uniform(-5, 5)
                vibration = vibration_base * stress + random.uniform(-0.1, 0.1)

                # Random failure event
                if random.random() < failure_probs[machine] * (step_minutes / 60):
                    status = "DOWN"
                    downtime_remaining = random.randint(60, 480)  # 1-8 hrs downtime

            rows.append({
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "machine_id": machine,
                "status": status,
                "temperature": round(max(0, temp), 2),
                "load": round(max(0, min(100, load)), 2),
                "vibration": round(max(0, vibration), 3),
            })
            current_time += timedelta(minutes=step_minutes)

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"Sample data saved to {output_path} ({len(df)} rows, {n_machines} machines)")
    return df

if __name__ == "__main__":
    generate_sample_data()
