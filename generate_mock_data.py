import pandas as pd
import numpy as np
from datetime import timedelta

def generate_mock_data(output_file="backend/data/raw/bangalore_smart_meters_mock.csv"):
    # Generate 1 year of hourly data for 20 simulated meters (households)
    meters = [f"METER_{i:03d}" for i in range(1, 21)]
    start_date = pd.to_datetime("2024-01-01 00:00:00")
    end_date = pd.to_datetime("2024-12-31 23:00:00")
    date_range = pd.date_range(start=start_date, end=end_date, freq='h')

    data = []
    for meter in meters:
        # Base consumption varies by meter
        base_cons = np.random.uniform(0.5, 2.0)
        
        # Add random noise and diurnal/seasonal patterns
        for dt in date_range:
            # Diurnal pattern (peaks in morning and evening)
            hour = dt.hour
            hour_mult = 1.0
            if 7 <= hour <= 9 or 18 <= hour <= 21:
                hour_mult = 1.5
            
            # Seasonal pattern (higher in summer months: Mar, Apr, May)
            month = dt.month
            month_mult = 1.0
            if month in [3, 4, 5]:
                month_mult = 1.3
                
            noise = np.random.normal(0, 0.2)
            
            cons = max(0.1, base_cons * hour_mult * month_mult + noise)
            
            data.append({
                "meter_id": meter,
                "timestamp": dt,
                "consumption_kwh": round(cons, 3)
            })

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Generated mock data at {output_file} with {len(df)} rows.")

if __name__ == "__main__":
    generate_mock_data()
