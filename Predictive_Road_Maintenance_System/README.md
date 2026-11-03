# RoadPredict AI — Component 4: Predictive Road Maintenance Research System

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Tests](https://img.shields.io/badge/tests-20%20passed-brightgreen)]()
[![Backend](https://img.shields.io/badge/FastAPI-v0.115-009688)]()
[![Frontend](https://img.shields.io/badge/React%2019-Vite%20TypeScript-61DAFB)]()
[![ML Suite](https://img.shields.io/badge/ML-Scikit--Learn%20%7C%20XGBoost%20%7C%20LightGBM-orange)]()
[![Target](https://img.shields.io/badge/Target-RDA%20Sri%20Lanka%20(Colombo)-blue)]()

> **Project Title:** AI-Based Intelligent Road Damage Detection, Severity Assessment, Repair Prioritization and Predictive Road Maintenance System  
> **Project ID:** J26-IT-336  
> **Primary Research Scope:** Component 4 — AI-Based Predictive Road Maintenance  
> **Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
> **Researcher:** Perera R.H.D. (IT23191174)  

---

## 1. System Overview

RoadPredict AI is a complete, functioning research prototype for **Component 4: AI-Based Predictive Road Maintenance**. It translates raw pavement inspection surveys, classified vehicle axle traffic (ESAL), meteorological climate data, and historical maintenance interventions into:
1. **Multi-Horizon Condition Forecasting:** Predicts future Pavement Condition Index (PCI) across 3, 6, 12, and 24-month horizons using trained XGBoost and regularized ensemble models.
2. **Remaining Road Life (RRL) Estimation:** Quantifies remaining months/days until condition intercepts rehabilitation ($\text{PCI} = 55$) and catastrophic failure ($\text{PCI} = 40$) thresholds.
3. **Preventive Maintenance Optimization:** Recommends AASHTO-aligned engineering treatments matched with the **RDA Highway Schedule of Rates (HSR 2025)** unit costs in LKR.
4. **Explainable AI (XAI):** Deconstructs individual prediction drivers (axle loading, monsoon moisture, pavement age, cracking).
5. **Interactive Telemetry Dashboard:** Enterprise-grade engineering console inspired by the proposal's telemetry UI (Pages 33–36), featuring Leaflet GIS OpenStreetMap integration for Colombo RDA corridors (`B047`, `B174`, `B214`, `B240`, `B263`, `B435`).

---

## 2. Repository Architecture & Layout

```
hasini research/
├── backend/
│   ├── app/
│   │   ├── core/config.py              # Environment and path configurations
│   │   ├── ml/
│   │   │   ├── features.py             # Feature engineering & leak-free pipeline
│   │   │   ├── train.py                # ML training & benchmark experiment runner
│   │   │   ├── models.py               # Model inference & full prognosis service
│   │   │   ├── rrl_engine.py           # Remaining Road Life & 36-month curve generator
│   │   │   └── explainability.py       # Localized XAI & feature attribution
│   │   ├── models/
│   │   │   ├── database.py             # SQLite relational schema & data access layer
│   │   │   └── schemas.py              # Pydantic v2 validation schemas
│   │   ├── routers/
│   │   │   ├── dashboard.py            # /api/dashboard/summary
│   │   │   ├── roads.py                # /api/roads, /api/roads/:id/decay-curve
│   │   │   ├── predict.py              # /api/predict/condition, /remaining-life, /prognosis
│   │   │   ├── models.py               # /api/models/evaluation, /train
│   │   │   ├── maintenance.py          # /api/maintenance/queue, /gantt, /dispatch
│   │   │   ├── datasets.py             # /api/datasets, /preview
│   │   │   └── integration.py          # /api/integration/adapter/comp1-3
│   │   ├── services/
│   │   │   ├── database_seeder.py      # Database auto-seeder
│   │   │   └── maintenance.py          # HSR 2025 recommendation & budget engine
│   │   └── main.py                     # FastAPI application entrypoint
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx              # Telemetry status bar
│   │   │   └── Sidebar.tsx             # System module navigation
│   │   ├── pages/
│   │   │   ├── PredictiveOverview.tsx  # Page 1: Structural health & anomaly stream
│   │   │   ├── DeteriorationCurves.tsx # Page 2: 36-month neural decay curves
│   │   │   ├── RoadSectionAnalysis.tsx # Page 3: Pavement stratigraphy & XAI inspector
│   │   │   ├── MaintenancePlanning.tsx # Page 4: Autonomous dispatch queue & Gantt
│   │   │   ├── GisRoadOverview.tsx     # Page 5: Leaflet OpenStreetMap RDA view
│   │   │   ├── ModelEvaluation.tsx     # Page 6: Benchmark matrix & training lab
│   │   │   ├── DatasetManagement.tsx   # Page 7: Data quality & schema audit
│   │   │   └── IntegrationLab.tsx      # Page 8: Component 1-3 adapter testing lab
│   │   ├── services/api.ts             # Typed REST API client
│   │   ├── App.tsx                     # Top-level state & router
│   │   └── index.css                   # High-tech telemetry CSS styling
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── data/
│   ├── processed/                      # Curated datasets (675 sections, 3,375 surveys)
│   └── road_maintenance.db            # SQLite database
├── models/                             # Trained joblib model artifacts
├── experiments/                        # evaluation_results.json
├── scripts/
│   └── build_dataset.py               # Data harmonization pipeline
├── tests/                              # Automated Pytest suite (20 tests)
├── docs/
│   ├── RESEARCH_DOCUMENTATION.md       # Comprehensive 20-section academic research manual
│   └── VIVA_PREPARATION.md             # Oral examination questions and answers
├── REQUIREMENTS.md                     # Full requirements specification & audit
├── ARCHITECTURE.md                     # System architecture & database design
├── IMPLEMENTATION_PLAN.md              # Milestone roadmap
├── PROJECT_PROGRESS.md                 # Execution log
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 3. Quick Start & Execution Guide

### Prerequisites
* Python 3.10+ (Tested on Python 3.14.2)
* Node.js v18+ and npm (Tested on Node v24.14.0)

### Step 1: Clone & Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: (Optional) Build Datasets & Train Models
*(Pre-trained models and seeded databases are already committed and ready to run)*
```bash
# Harmonize RDA surveys, traffic, weather, and budget sheets
python scripts/build_dataset.py

# Run ML benchmarking experiment (Ridge, DT, RF, XGBoost, LightGBM)
python -m backend.app.ml.train

# Seed SQLite database
python -m backend.app.services.database_seeder
```

### Step 3: Launch Backend REST API Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* Health Check Endpoint: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Step 4: Launch Frontend Research Dashboard
In a second terminal window:
```bash
cd frontend
npm run dev
```
* Dashboard URL: [http://localhost:5173](http://localhost:5173)

---

## 4. Docker Deployment (Single Command)

To run both backend and frontend inside isolated Docker containers:
```bash
docker-compose up --build
```
Access the application at:
* Frontend Dashboard: [http://localhost:5173](http://localhost:5173)
* Backend API & Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Machine Learning Experimental Results

Evaluated on 675 road section samples across 6 RDA corridors under stratified out-of-sample testing:

### Continuous Condition Regression (12-Month PCI)
| Model | MAE | RMSE | $R^2$ Score | Selection Status |
| :--- | :--- | :--- | :--- | :--- |
| **Linear Regression (Ridge Baseline)** | **0.750** | **0.938** | **99.44%** | Selected Production Regressor |
| **XGBoost Regressor** | 1.070 | 1.673 | 98.22% | Multi-Horizon Engine (3m, 6m, 12m, 24m) |
| **Random Forest Regressor** | 1.190 | 1.773 | 98.00% | Ensemble XAI Engine |
| **Decision Tree Regressor** | 1.411 | 1.911 | 97.67% | Baseline |
| **LightGBM Regressor** | 1.359 | 2.400 | 96.33% | Evaluated |

### Risk Category Classification (Good, Satisfactory, Fair, Poor, Critical)
| Model | Accuracy | Precision | Recall | F1-Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Forest Classifier** | **95.56%** | **96.05%** | **95.56%** | **95.60%** | Selected Production Classifier |
| **XGBoost Classifier** | 94.07% | 94.60% | 94.07% | 94.13% | Evaluated |
| **LightGBM Classifier** | 94.07% | 94.34% | 94.07% | 94.12% | Evaluated |
| **Logistic Regression** | 92.59% | 92.68% | 92.59% | 92.63% | Baseline |

---

## 6. Running Automated Tests

Execute the automated test suite covering unit tests, ML inference, API endpoints, and component integration adapters:
```bash
python -m pytest tests -v
```
**Actual Result:** `20 passed in 6.04s`

---

## 7. Sample API Invocations

### Run Pavement Prognosis
```bash
curl -X POST "http://localhost:8000/api/predict/prognosis" \
     -H "Content-Type: application/json" \
     -d '{
       "current_pci": 68.4,
       "daily_esal": 1800,
       "pavement_age_years": 5,
       "structural_number": 3.8,
       "crack_density_pct": 14.2,
       "pothole_count": 1,
       "rut_depth_mm": 6.0,
       "annual_precipitation_mm": 2674,
       "monsoon_risk_factor": 1.78,
       "historical_decay_rate_annual": 4.1
     }'
```

### Ingest Payload from Component 1 or 2
```bash
curl -X POST "http://localhost:8000/api/integration/adapter/comp1-3" \
     -H "Content-Type: application/json" \
     -d '{
       "source_component": "Component_1_Damage_Detection",
       "corridor_id": "B047",
       "chainage_km": 3.8,
       "assessed_pci": 51.4,
       "distresses": [
         {"damage_type": "Pothole Breach", "severity": "High", "confidence": 0.92, "area_sqm": 0.45, "depth_mm": 48.0}
       ]
     }'
```

---

## 8. Academic & Viva Defense Resources
For oral defense preparation, architectural justifications, and detailed explanations of the proposal requirements audit (including the identification and exclusion of residual retail trolley artifacts), refer to:
* [RESEARCH_DOCUMENTATION.md](file:///c:/Users/kavee/Desktop/hasini%20research/docs/RESEARCH_DOCUMENTATION.md)
* [VIVA_PREPARATION.md](file:///c:/Users/kavee/Desktop/hasini%20research/docs/VIVA_PREPARATION.md)
* [REQUIREMENTS.md](file:///c:/Users/kavee/Desktop/hasini%20research/REQUIREMENTS.md)
* [ARCHITECTURE.md](file:///c:/Users/kavee/Desktop/hasini%20research/ARCHITECTURE.md)
