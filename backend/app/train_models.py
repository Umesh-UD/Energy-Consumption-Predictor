import pandas as pd
import numpy as np
import os
import joblib
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

DATA_PATH = Path("data/processed/zone_aggregated_data.csv")
MODELS_DIR = Path("app/models")

def train_and_evaluate():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])
    
    # Excluded precipitation as it's not in the new dataset. 
    # Added household_size and has_ac_pct. We omit peak_hours_usage_kwh from predictive features 
    # as it's part of the target, but keep it in the dataset for suggestions.
    features = ['temperature', 'is_weekend', 'is_holiday', 'day_of_week', 'month', 'household_size', 'has_ac_pct']
    target = 'consumption_kwh'
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    zones = df['zone'].unique()
    
    results = []
    
    for zone in zones:
        print(f"Training models for {zone}...")
        zone_df = df[df['zone'] == zone].copy()
        
        # We only have 7 days of data per zone. 
        # Known Limitation: Chronological split is not viable. Using random split (option A).
        X = zone_df[features]
        y = zone_df[target]
        
        # test_size=0.2 on 7 rows means ~2 test rows
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        models = {
            'LinearRegression': LinearRegression(),
            'DecisionTree': DecisionTreeRegressor(random_state=42, max_depth=5),
            'RandomForest': RandomForestRegressor(n_estimators=10, random_state=42, max_depth=5) # Reduced n_estimators for tiny dataset
        }
        
        best_r2 = -float('inf')
        best_model_name = ""
        best_model = None
        best_metrics = {}
        
        for name, model in models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            
            # Catch potential warnings on 2-row test set for r2
            if len(y_test) > 1:
                r2 = r2_score(y_test, preds)
            else:
                r2 = 0.0 # fallback if only 1 test row
                
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            mae = mean_absolute_error(y_test, preds)
            
            if r2 > best_r2 or (r2 == best_r2 and best_model is None):
                best_r2 = r2
                best_model_name = name
                best_model = model
                best_metrics = {'R2': round(r2, 3), 'RMSE': round(rmse, 3), 'MAE': round(mae, 3)}
                
        print(f"  Best model: {best_model_name} (R2: {best_metrics['R2']})")
        
        # Extract feature importance
        feature_importance = {}
        if hasattr(best_model, 'feature_importances_'):
            importances = best_model.feature_importances_
            feature_importance = {f: float(imp) for f, imp in zip(features, importances)}
        elif hasattr(best_model, 'coef_'):
            importances = np.abs(best_model.coef_)
            feature_importance = {f: float(imp) for f, imp in zip(features, importances)}
            
        # Save model and metadata
        model_data = {
            'model': best_model,
            'model_name': best_model_name,
            'features': features,
            'metrics': best_metrics,
            'feature_importance': feature_importance,
            'historical_avg': float(y_train.mean())
        }
        
        model_path = MODELS_DIR / f"{zone}_model.joblib"
        joblib.dump(model_data, model_path)
        print(f"  Saved {zone} model to {model_path}")
        
        results.append({
            'zone': zone,
            'best_model': best_model_name,
            **best_metrics
        })
        
    print("\n--- Training Summary ---")
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))

if __name__ == "__main__":
    train_and_evaluate()
