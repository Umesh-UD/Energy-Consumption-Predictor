import pandas as pd
import numpy as np
import os
from pathlib import Path

# Config
RAW_DATA_PATH = Path("data/raw/household_energy_consumption.csv")
PROCESSED_DATA_PATH = Path("data/processed/zone_aggregated_data.csv")
NUM_ZONES = 5

def run_pipeline():
    print(f"Loading raw data from {RAW_DATA_PATH}...")
    df = pd.read_csv(RAW_DATA_PATH)
    
    # Clean data and drop incomplete date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Date'] <= '2025-04-07']
    df.dropna(subset=['Energy_Consumption_kWh'], inplace=True)
    
    # Map Has_AC to numeric
    df['Has_AC'] = df['Has_AC'].map({'Yes': 1, 'No': 0})
    
    # Group households into zones
    unique_meters = sorted(df['Household_ID'].unique())
    meters_per_zone = max(1, len(unique_meters) // NUM_ZONES)
    
    meter_to_zone = {}
    for i, meter in enumerate(unique_meters):
        zone_idx = min((i // meters_per_zone) + 1, NUM_ZONES)
        meter_to_zone[meter] = f"Zone_{zone_idx}"
        
    df['zone'] = df['Household_ID'].map(meter_to_zone)
    
    # Aggregate consumption per zone per day
    print("Aggregating consumption per zone per day...")
    zone_daily = df.groupby(['zone', 'Date']).agg({
        'Energy_Consumption_kWh': 'sum',
        'Avg_Temperature_C': 'mean',
        'Household_Size': 'mean',
        'Has_AC': 'mean',
        'Peak_Hours_Usage_kWh': 'sum'
    }).reset_index()
    
    # Rename columns to match existing pipeline
    zone_daily.rename(columns={
        'Date': 'date',
        'Energy_Consumption_kWh': 'consumption_kwh',
        'Avg_Temperature_C': 'temperature',
        'Household_Size': 'household_size',
        'Has_AC': 'has_ac_pct',
        'Peak_Hours_Usage_kWh': 'peak_hours_usage_kwh'
    }, inplace=True)
    
    # Add calendar features (no holidays for April 1-7, 2025 in Karnataka)
    print("Adding calendar features...")
    zone_daily['is_weekend'] = zone_daily['date'].dt.dayofweek.isin([5, 6]).astype(int)
    zone_daily['is_holiday'] = 0  # Hardcoded as per prompt
    zone_daily['day_of_week'] = zone_daily['date'].dt.dayofweek
    zone_daily['month'] = zone_daily['date'].dt.month
    
    # We no longer fetch from Open-Meteo as Temperature is included and Precipitation isn't available
    # We will just fill precipitation with 0 so the model features remain consistent if needed, 
    # but we will likely remove precipitation from features.
    zone_daily['precipitation'] = 0.0
    
    # Save the processed dataset
    print(f"Saving processed data to {PROCESSED_DATA_PATH}...")
    os.makedirs(PROCESSED_DATA_PATH.parent, exist_ok=True)
    zone_daily.to_csv(PROCESSED_DATA_PATH, index=False)
    
    print("Data pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()
