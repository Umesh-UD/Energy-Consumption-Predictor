import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)

MODELS_DIR = Path("app/models")
DATA_PATH = Path("data/processed/zone_aggregated_data.csv")

def get_zone_list():
    if not os.path.exists(DATA_PATH):
        return []
    df = pd.read_csv(DATA_PATH)
    return sorted(df['zone'].unique().tolist())

def get_zone_historical_averages(zone_id: str) -> dict:
    """
    Returns historical numerical column averages for the specified zone.
    Short-window proxy: the dataset covers only 7 days, so zone-level features
    (e.g., household_size, has_ac_pct / ac_penetration_pct, peak_hours_usage_kwh)
    default to that zone's historical average.
    """
    if not os.path.exists(DATA_PATH):
        return {}
    df = pd.read_csv(DATA_PATH)
    zone_df = df[df['zone'] == zone_id]
    if zone_df.empty:
        return {}
    
    means = zone_df.mean(numeric_only=True).to_dict()
    # Support aliases between has_ac_pct (0.0 to 1.0) and ac_penetration_pct (0.0 to 100.0)
    if 'has_ac_pct' in means and 'ac_penetration_pct' not in means:
        means['ac_penetration_pct'] = float(means['has_ac_pct']) * 100.0
    if 'ac_penetration_pct' in means and 'has_ac_pct' not in means:
        means['has_ac_pct'] = float(means['ac_penetration_pct']) / 100.0
    return means

def build_model_input_row(zone_id: str, features: list, dt: datetime = None, overrides: dict = None) -> dict:
    """
    Shared helper function to construct a complete input row containing ALL trained features.
    
    1. Date-driven features:
       - day_of_week, is_weekend, is_holiday, month, temperature (28.0 proxy avg), precipitation (0.0).
    2. Zone-level features:
       - Default to that zone's historical average (household_size, has_ac_pct, ac_penetration_pct, etc.).
       - Short-window proxy: the dataset covers only 7 days, so historical averages are used as proxies for future dates.
    3. User overrides:
       - Overrides from user inputs (e.g. What-If Simulator) are mapped to appropriate feature keys.
    4. Safety fallback:
       - Before returning, any feature expected by the model that is missing from input_row (or NaN)
         is populated with the zone's historical mean (or 0.0), and a warning is logged so KeyError is impossible.
    """
    if dt is None:
        dt = datetime.now()
        
    hist_means = get_zone_historical_averages(zone_id)
    
    # 1. Base date-driven features
    input_row = {
        'temperature': 28.0,  # Proxy average
        'precipitation': 0.0,
        'day_of_week': dt.weekday(),
        'is_weekend': 1 if dt.weekday() >= 5 else 0,
        'is_holiday': 0,
        'month': dt.month,
    }
    
    # 2. Zone-level features that cannot be known for future dates default to historical average
    # Short-window proxy: the dataset covers only 7 days, so zone-level features
    # default to that zone's historical average.
    for col, val in hist_means.items():
        if col not in input_row:
            input_row[col] = float(val) if pd.notna(val) else 0.0
            
    # Guarantee primary zone-level keys have values even if hist_means was empty
    if 'household_size' not in input_row:
        input_row['household_size'] = float(hist_means.get('household_size', 3.5))
    if 'has_ac_pct' not in input_row:
        input_row['has_ac_pct'] = float(hist_means.get('has_ac_pct', 0.5))
    if 'ac_penetration_pct' not in input_row:
        input_row['ac_penetration_pct'] = float(hist_means.get('ac_penetration_pct', 50.0))
        
    # 3. Apply user overrides if provided
    if overrides:
        for k, v in overrides.items():
            if v is not None:
                if k == 'is_holiday':
                    input_row[k] = 1 if v else 0
                elif k == 'ac_penetration_pct':
                    input_row['ac_penetration_pct'] = float(v)
                    input_row['has_ac_pct'] = float(v) / 100.0
                elif k == 'has_ac_pct':
                    input_row['has_ac_pct'] = float(v)
                    input_row['ac_penetration_pct'] = float(v) * 100.0
                else:
                    input_row[k] = v
                    
        # Compute derived is_weekend if day_of_week changed without explicit is_weekend
        if 'day_of_week' in overrides and overrides['day_of_week'] is not None:
            if 'is_weekend' not in overrides or overrides['is_weekend'] is None:
                input_row['is_weekend'] = 1 if int(input_row['day_of_week']) >= 5 else 0

    # 4. Safety fallback: fill any feature missing from input_row with the zone's historical mean
    # so a missing feature can never raise KeyError again.
    for f in features:
        if f not in input_row or input_row[f] is None or pd.isna(input_row[f]):
            fallback_val = float(hist_means.get(f, 0.0))
            logger.warning(
                f"[Safety Fallback] Feature '{f}' missing or NaN in input_row for zone '{zone_id}'. "
                f"Falling back to zone historical mean: {fallback_val}"
            )
            input_row[f] = fallback_val
            
    return input_row

def get_zone_history(zone_id):
    if not os.path.exists(DATA_PATH):
        return []
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    zone_df = df[df['zone'] == zone_id].copy()
    
    # Return last 30 days of history for the UI
    zone_df = zone_df.sort_values('date').tail(30)
    
    records = []
    for _, row in zone_df.iterrows():
        c_val = float(row['consumption_kwh']) if pd.notna(row['consumption_kwh']) else 0.0
        records.append({
            'date': row['date'].strftime('%Y-%m-%d'),
            'consumption': c_val
        })
    return records

def predict_future(zone_id, days=7):
    model_path = MODELS_DIR / f"{zone_id}_model.joblib"
    if not os.path.exists(model_path):
        return None, None, None
        
    model_data = joblib.load(model_path)
    model = model_data['model']
    features = model_data['features']
    historical_avg = float(model_data.get('historical_avg', 0.0))
    
    # Generate future dates
    today = datetime.now()
    future_dates = [today + timedelta(days=i) for i in range(1, days + 1)]
    
    future_records = []
    input_data = []
    for dt in future_dates:
        # Build complete feature row using shared helper with zone historical proxies and safety fallback
        input_row = build_model_input_row(zone_id, features, dt=dt)
        # Extract features in exact order expected by the model
        model_input = [input_row[f] for f in features]
        input_data.append(model_input)
        
    input_df = pd.DataFrame(input_data, columns=features)
    preds = model.predict(input_df)
    
    for i, dt in enumerate(future_dates):
        pred_val = float(preds[i])
        if pd.isna(pred_val) or np.isinf(pred_val):
            pred_val = historical_avg
        future_records.append({
            'date': dt.strftime('%Y-%m-%d'),
            'prediction': pred_val
        })
        
    clean_preds = [r['prediction'] for r in future_records]
    predicted_avg = float(sum(clean_preds) / len(clean_preds)) if clean_preds else historical_avg
    if pd.isna(predicted_avg) or np.isinf(predicted_avg):
        predicted_avg = historical_avg
        
    return future_records, predicted_avg, historical_avg

def get_zone_features(zone_id):
    model_path = MODELS_DIR / f"{zone_id}_model.joblib"
    if not os.path.exists(model_path):
        return None
    model_data = joblib.load(model_path)
    # Format for Recharts bar chart
    feats = []
    for k, v in model_data.get('feature_importance', {}).items():
        val = 0.0 if pd.isna(v) or np.isinf(v) else float(v)
        feats.append({"feature": k, "importance": val})
    return feats

def get_zone_metrics(zone_id):
    model_path = MODELS_DIR / f"{zone_id}_model.joblib"
    if not os.path.exists(model_path):
        return None
    model_data = joblib.load(model_path)
    raw_metrics = model_data.get('metrics', {})
    clean_metrics = {}
    for k, v in raw_metrics.items():
        if pd.isna(v) or np.isinf(v):
            clean_metrics[k] = 0.0
        else:
            clean_metrics[k] = float(v)
    return clean_metrics

def get_zone_anomalies(zone_id, threshold_pct=0.15):
    """
    Finds historical dates where the actual consumption deviated from the
    model's prediction by more than threshold_pct.
    """
    model_path = MODELS_DIR / f"{zone_id}_model.joblib"
    if not os.path.exists(model_path) or not os.path.exists(DATA_PATH):
        return []
        
    model_data = joblib.load(model_path)
    model = model_data['model']
    features = model_data['features']
    
    df = pd.read_csv(DATA_PATH)
    zone_df = df[df['zone'] == zone_id].copy()
    if zone_df.empty:
        return []
    
    # We only care about the last 30 days for anomalies in this view
    zone_df['date'] = pd.to_datetime(zone_df['date'])
    zone_df = zone_df.sort_values('date').tail(30)
    
    hist_means = get_zone_historical_averages(zone_id)
    # Safety fallback: ensure every expected feature is in zone_df and has no NaN
    for f in features:
        if f not in zone_df.columns:
            fallback_val = float(hist_means.get(f, 0.0))
            logger.warning(
                f"[Safety Fallback] Feature '{f}' missing from historical data for zone '{zone_id}'. "
                f"Filling with zone historical mean: {fallback_val}"
            )
            zone_df[f] = fallback_val
        else:
            if zone_df[f].isna().any():
                fallback_val = float(hist_means.get(f, 0.0))
                logger.warning(
                    f"[Safety Fallback] Feature '{f}' contains NaN in historical data for zone '{zone_id}'. "
                    f"Filling with zone historical mean: {fallback_val}"
                )
                zone_df[f] = zone_df[f].fillna(fallback_val)
                
    input_df = zone_df[features]
    preds = model.predict(input_df)
    
    anomalies = []
    for i, (_, row) in enumerate(zone_df.iterrows()):
        actual = float(row['consumption_kwh'])
        predicted = float(preds[i])
        
        if predicted > 0 and pd.notna(actual) and pd.notna(predicted) and not np.isinf(predicted):
            deviation = (actual - predicted) / predicted
            if not pd.isna(deviation) and not np.isinf(deviation) and abs(deviation) >= threshold_pct:
                anomalies.append({
                    "date": row['date'].strftime('%Y-%m-%d'),
                    "actual": actual,
                    "predicted": predicted,
                    "deviation_pct": float(deviation * 100)
                })
                
    # Sort anomalies with the most recent first
    return sorted(anomalies, key=lambda x: x['date'], reverse=True)

def simulate_prediction(zone_id, user_inputs):
    """
    Simulates a prediction based on user-provided inputs, falling back
    to sensible defaults and zone historical averages for any missing fields.
    """
    model_path = MODELS_DIR / f"{zone_id}_model.joblib"
    if not os.path.exists(model_path):
        return None
        
    model_data = joblib.load(model_path)
    model = model_data['model']
    features = model_data['features']
    historical_avg = float(model_data.get('historical_avg', 0.0))
    
    today = datetime.now()
    input_row = build_model_input_row(zone_id, features, dt=today, overrides=user_inputs)
    
    model_input = [input_row[f] for f in features]
    input_df = pd.DataFrame([model_input], columns=features)
    baseline_pred = float(model.predict(input_df)[0])
    if pd.isna(baseline_pred) or np.isinf(baseline_pred):
        baseline_pred = historical_avg
        
    result = {
        "simulated_prediction": baseline_pred,
        "baseline_prediction": baseline_pred
    }
    
    if 'ac_penetration_pct' in user_inputs and user_inputs['ac_penetration_pct'] is not None:
        new_ac_pct = float(user_inputs['ac_penetration_pct'])
        current_ac_insight = get_zone_ac_insight(zone_id)
        if current_ac_insight:
            current_ac_pct = current_ac_insight['ac_penetration_pct']
            # Approximate consumption delta based on training data: 
            # 100% AC adoption adds roughly 40% to base load. 
            # This is an approximation for simulation, not a re-trained ML model.
            AC_LOAD_IMPACT_FACTOR = 0.40  
            
            pct_change = (new_ac_pct - current_ac_pct) / 100.0
            adjusted_pred = baseline_pred * (1 + (pct_change * AC_LOAD_IMPACT_FACTOR))
            if pd.isna(adjusted_pred) or np.isinf(adjusted_pred):
                adjusted_pred = baseline_pred
            result["adjusted_prediction"] = float(adjusted_pred)
            
    return result

def get_zone_comparison():
    """
    Compares all zones based on their predicted vs historical average consumption.
    """
    zones = get_zone_list()
    comparison = []
    
    for zone in zones:
        model_path = MODELS_DIR / f"{zone}_model.joblib"
        if not os.path.exists(model_path):
            continue
            
        model_data = joblib.load(model_path)
        hist_avg = float(model_data.get('historical_avg', 0))
        
        # Get future predictions
        preds, pred_avg, _ = predict_future(zone, days=7)
        
        if pred_avg and hist_avg > 0:
            pct_change = ((pred_avg - hist_avg) / hist_avg) * 100
        else:
            pct_change = 0.0
            
        if pd.isna(pct_change) or np.isinf(pct_change):
            pct_change = 0.0
            
        comparison.append({
            "zone_id": zone,
            "zone_name": zone.replace('_', ' '),
            "historical_avg": hist_avg,
            "predicted_avg": pred_avg if pred_avg else 0.0,
            "percentage_change": float(pct_change)
        })
    return comparison

PEAK_RATIO_RISK_THRESHOLD = 0.45  # Simplified proxy for transformer/feeder stress, not real grid capacity data

def get_zone_peak_load(zone_id):
    hist_means = get_zone_historical_averages(zone_id)
    if not hist_means:
        return None
    
    # 7-day average (short window average based on dataset)
    total_consumption_kwh = float(hist_means.get('consumption_kwh', 0.0))
    peak_hours_usage_kwh = float(hist_means.get('peak_hours_usage_kwh', 0.0))
    
    peak_ratio = peak_hours_usage_kwh / total_consumption_kwh if total_consumption_kwh > 0 else 0.0
    if pd.isna(peak_ratio) or np.isinf(peak_ratio):
        peak_ratio = 0.0
    at_risk = bool(peak_ratio > PEAK_RATIO_RISK_THRESHOLD)
    
    return {
        "zone_id": zone_id,
        "total_consumption_kwh": total_consumption_kwh,
        "peak_hours_usage_kwh": peak_hours_usage_kwh,
        "peak_ratio": float(peak_ratio),
        "at_risk": at_risk,
        "threshold": PEAK_RATIO_RISK_THRESHOLD
    }

def get_zone_peak_load_summary():
    zones = get_zone_list()
    summary = []
    for zone in zones:
        data = get_zone_peak_load(zone)
        if data:
            summary.append(data)
    summary.sort(key=lambda x: x['peak_ratio'], reverse=True)
    return summary

def get_zone_ac_insight(zone_id):
    hist_means = get_zone_historical_averages(zone_id)
    if not hist_means:
        return None
    
    # 7-day average (short window average based on dataset)
    ac_penetration_pct = float(hist_means.get('ac_penetration_pct', hist_means.get('has_ac_pct', 0.0) * 100))
    avg_consumption_kwh = float(hist_means.get('consumption_kwh', 0.0))
    avg_temperature_c = float(hist_means.get('temperature', 0.0))
    
    if pd.isna(ac_penetration_pct) or np.isinf(ac_penetration_pct):
        ac_penetration_pct = 0.0
    if pd.isna(avg_consumption_kwh) or np.isinf(avg_consumption_kwh):
        avg_consumption_kwh = 0.0
    if pd.isna(avg_temperature_c) or np.isinf(avg_temperature_c):
        avg_temperature_c = 0.0
        
    return {
        "zone_id": zone_id,
        "ac_penetration_pct": ac_penetration_pct,
        "avg_consumption_kwh": avg_consumption_kwh,
        "avg_temperature_c": avg_temperature_c
    }

def get_zone_ac_insight_summary():
    zones = get_zone_list()
    summary = []
    for zone in zones:
        data = get_zone_ac_insight(zone)
        if data:
            summary.append(data)
    summary.sort(key=lambda x: x['ac_penetration_pct'], reverse=True)
    return summary
