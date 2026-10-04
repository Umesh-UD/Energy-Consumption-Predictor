from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

class SimulatorInput(BaseModel):
    temperature: Optional[float] = None
    precipitation: Optional[float] = None
    is_weekend: Optional[int] = None
    is_holiday: Optional[int] = None
    day_of_week: Optional[int] = None
    month: Optional[int] = None
    ac_penetration_pct: Optional[float] = None

# Use absolute imports or run from the backend directory using uvicorn app.main:app
try:
    from app.inference import get_zone_list, get_zone_history, predict_future, get_zone_features, get_zone_metrics, get_zone_anomalies, simulate_prediction, get_zone_comparison, get_zone_peak_load, get_zone_peak_load_summary, get_zone_ac_insight, get_zone_ac_insight_summary
    from app.suggestions import generate_suggestion
except ImportError:
    from inference import get_zone_list, get_zone_history, predict_future, get_zone_features, get_zone_metrics, get_zone_anomalies, simulate_prediction, get_zone_comparison, get_zone_peak_load, get_zone_peak_load_summary, get_zone_ac_insight, get_zone_ac_insight_summary
    from suggestions import generate_suggestion

app = FastAPI(title="Zone-Wise Energy Consumption Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/zones")
def get_zones():
    zones = get_zone_list()
    return [{"id": z, "name": z.replace('_', ' ')} for z in zones]

@app.get("/zones/comparison")
def compare_zones(sort_by: str = "change"):
    comp = get_zone_comparison()
    if sort_by == "change":
        comp.sort(key=lambda x: x["percentage_change"], reverse=True)
    elif sort_by == "predicted":
        comp.sort(key=lambda x: x["predicted_avg"], reverse=True)
    elif sort_by == "zone_name":
        comp.sort(key=lambda x: x["zone_name"])
    return comp

@app.get("/zones/{zone_id}/history")
def get_history(zone_id: str):
    history = get_zone_history(zone_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Zone history not found")
    return {"zone_id": zone_id, "history": history}

@app.get("/zones/{zone_id}/predict")
def predict(zone_id: str, days: int = 7):
    preds, _, _ = predict_future(zone_id, days)
    if preds is None:
        raise HTTPException(status_code=404, detail="Model not found for zone")
    return {"zone_id": zone_id, "predictions": preds}

@app.get("/zones/{zone_id}/features")
def features(zone_id: str):
    feats = get_zone_features(zone_id)
    if feats is None:
        raise HTTPException(status_code=404, detail="Model not found for zone")
    return {"zone_id": zone_id, "features": feats}

@app.get("/zones/{zone_id}/suggestion")
def suggestion(zone_id: str):
    preds, pred_avg, hist_avg = predict_future(zone_id, 7)
    if preds is None:
        raise HTTPException(status_code=404, detail="Model not found for zone")
        
    sugg = generate_suggestion(zone_id, pred_avg, hist_avg)
    return {"zone_id": zone_id, "suggestion": sugg}

@app.get("/zones/{zone_id}/metrics")
def metrics(zone_id: str):
    mets = get_zone_metrics(zone_id)
    if mets is None:
        raise HTTPException(status_code=404, detail="Model not found for zone")
    return {"zone_id": zone_id, "metrics": mets}

@app.get("/zones/{zone_id}/anomalies")
def anomalies(zone_id: str):
    anoms = get_zone_anomalies(zone_id)
    return {"zone_id": zone_id, "anomalies": anoms}

@app.post("/zones/{zone_id}/simulate")
def simulate(zone_id: str, inputs: SimulatorInput):
    pred_data = simulate_prediction(zone_id, inputs.dict())
    if pred_data is None:
        raise HTTPException(status_code=404, detail="Model not found for zone")
    return {"zone_id": zone_id, **pred_data}

@app.get("/zones/peak-load/summary")
def peak_load_summary():
    summary = get_zone_peak_load_summary()
    if not summary:
        raise HTTPException(status_code=404, detail="No data available")
    return summary

@app.get("/zones/{zone_id}/peak-load")
def peak_load(zone_id: str):
    data = get_zone_peak_load(zone_id)
    if not data:
        raise HTTPException(status_code=404, detail="Zone data not found")
    return data

@app.get("/zones/ac-insight/summary")
def ac_insight_summary():
    summary = get_zone_ac_insight_summary()
    if not summary:
        raise HTTPException(status_code=404, detail="No data available")
    return summary

@app.get("/zones/{zone_id}/ac-insight")
def ac_insight(zone_id: str):
    data = get_zone_ac_insight(zone_id)
    if not data:
        raise HTTPException(status_code=404, detail="Zone data not found")
    return data

