# Zone-Wise Energy Consumption Prediction Dashboard

This project is a full-stack web application designed for electricity distribution companies (DISCOMs). It simulates city zones, analyzes historical electricity consumption, predicts future consumption using machine learning, identifies key driving factors, and generates plain-language suggestions for load planning.

## Features

- **Zone Simulation**: Groups household smart meters into distinct regional zones.
- **Data Integration**: Merges consumption data with historical weather patterns (from Open-Meteo) and holiday schedules.
- **Machine Learning**: Trains and evaluates multiple regression models (Linear Regression, Decision Tree, Random Forest) to predict 7-day future consumption, choosing the best performing model per zone.
- **Dashboard UI**: A sleek, modern React dashboard utilizing Recharts for visual analytics.
- **Rule-based Suggestions**: Analyzes model predictions to offer human-readable operational advice (e.g. warning about peak load).

## Project Structure

- `backend/`: FastAPI backend and data/ML pipeline in Python.
- `frontend/`: React + Vite frontend application.
- `generate_mock_data.py`: Script to generate a simulated dataset for testing purposes.

## Setup Instructions

### 1. Data Generation

Before running the backend, generate the mock dataset and process it:

```bash
cd energy-consumption-prediction
python generate_mock_data.py
cd backend
python app/data_pipeline.py
python app/train_models.py
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The FastAPI server will start at `http://localhost:8000`. You can view the API documentation at `http://localhost:8000/docs`.

### 3. Frontend Setup

In a new terminal window:

```bash
cd frontend
npm install
npm run dev
```

The React dashboard will start at `http://localhost:5173`. Open this URL in your browser to interact with the application.

## Acknowledgements

Dataset inspiration: "Smart Energy Meters in Bangalore India" from Kaggle.
Weather Data: Open-Meteo API.
