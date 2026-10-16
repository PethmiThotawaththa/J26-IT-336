# IMPLEMENTATION PLAN — COMPONENT 4 PREDICTIVE ROAD MAINTENANCE
**Project ID:** J26-IT-336  
**Scope:** Component 4 — AI-Based Predictive Road Maintenance Research System  
**Framework:** Autonomous Multi-Phase Execution  

---

## Phase Breakdown & Milestones

| Phase | Description | Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1: Research & Planning** | Comprehensive proposal review, requirements audit, architecture specification, workspace inventory. | `REQUIREMENTS.md`, `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `PROJECT_PROGRESS.md` | **In Progress** |
| **Phase 2: Dataset Preparation & Pipeline** | Ingestion of RDA Sri Lanka datasets (surveys, traffic counts, weather, maintenance budget), longitudinal synthesis, cleaning & feature pipeline. | `data/processed/`, `scripts/build_dataset.py`, `backend/app/ml/features.py` | Pending |
| **Phase 3: ML Modeling & Benchmarking** | Train baseline and ensemble models (LR, DT, RF, XGBoost, LightGBM), hyperparameter optimization, fair evaluation. | `backend/app/ml/train.py`, `models/`, `experiments/evaluation_results.json` | Pending |
| **Phase 4: Predictive Maintenance Engines** | Condition projection (3, 6, 12, 24 mo), Remaining Useful Life (RRL) calculator, HSR-aligned maintenance rules, XAI module. | `backend/app/ml/rrl_engine.py`, `backend/app/services/maintenance.py`, `backend/app/ml/explainability.py` | Pending |
| **Phase 5: Backend REST API Development** | FastAPI service, SQLAlchemy database models, seed scripts, Pydantic validation schemas, integration adapters for Components 1-3. | `backend/app/main.py`, `backend/app/routers/`, `backend/app/models/` | Pending |
| **Phase 6: Frontend Dashboard Development** | Modern React + TypeScript + Tailwind CSS dashboard matching proposal telemetry aesthetic (Pages 33-36), interactive decay curves, Leaflet GIS. | `frontend/src/pages/`, `frontend/src/components/` | Pending |
| **Phase 7: System Integration** | Connect frontend with backend API, verify live data flow, test component adapters. | End-to-end operational verification | Pending |
| **Phase 8: Validation & Automated Testing** | Unit tests for preprocessing, ML inference, API endpoints, integration adapters. | `tests/`, Pytest execution report | Pending |
| **Phase 9: Research Documentation & Handover** | Academic research documentation, data dictionary, viva preparation notes, run instructions. | `README.md`, `docs/VIVA_PREPARATION.md`, `docs/RESEARCH_DOCUMENTATION.md` | Pending |

---

## Detailed Technical Execution Steps

### Step 1: Data Curation & Preprocessing Engine
1. Parse RDA surveys for 6 corridors (`B047`, `B174`, `B214`, `B240`, `B263`, `B435`) extracting chainage, coordinates, and survey timestamps.
2. Ingest traffic count sheet, computing daily vehicle volume and AASHTO Equivalent Single Axle Loads (ESAL).
3. Ingest Colombo weather dataset (365 days) computing moving precipitation indices and thermal variation metrics.
4. Harmonize with Highway Schedule of Rates (HSR 2025) and RDA maintenance records.
5. Create longitudinal deterioration time series calibrated against AASHTO/LTPP deterioration mechanics.
6. Build scikit-learn compatible preprocessing pipeline with zero data leakage.

### Step 2: ML Model Training & Experiments
1. Implement regression models: Linear Regression, Decision Tree, Random Forest, XGBoost, LightGBM.
2. Implement classification models for condition risk categories.
3. Perform GroupKFold cross-validation by road section.
4. Record evaluation metrics: MAE, RMSE, $R^2$, Precision, Recall, F1.
5. Save model artifacts (`.pkl` / `.json`) and metadata.

### Step 3: Core Predictive Services
1. `PredictConditionService`: multi-horizon inference ($3, 6, 12, 24$ months).
2. `RemainingRoadLifeService`: continuous decay modeling to threshold intercept.
3. `MaintenanceForecastingService`: urgency, action selection, and HSR cost calculation.
4. `ExplainabilityService`: feature importance and localized SHAP / attribution factors.

### Step 4: Backend API Development
1. Setup FastAPI application structure with CORS and logging.
2. Setup SQLite database with SQLAlchemy 2.0 ORM and auto-seeding from processed RDA data.
3. Implement REST routers for roads, predictions, models, maintenance, datasets, and integration adapters.

### Step 5: Frontend Dashboard Development
1. Initialize Vite React TypeScript project with Tailwind CSS.
2. Build telemetry layout with sidebar navigation, header status bar, and monospace stat badges.
3. Implement 7 views:
   - Predictive Overview (KPI cards, deterioration radar, anomaly stream)
   - Deterioration Curves (Recharts multi-horizon curve, load modifiers)
   - Road Telemetry Inspector (geotechnical stratigraphy, localized XAI)
   - Maintenance Planning (P1/P2/P3 queue, 14-day weather-locked Gantt)
   - GIS Map Explorer (Leaflet OSM with Sri Lanka RDA roads)
   - Model Evaluation Bench (Side-by-side metric tables and charts)
   - Dataset Management (Dataset inspector & upload)

### Step 6: Automated Testing & Handover
1. Write Pytest test suite covering data pipeline, model inference, and API endpoints.
2. Run test suite and document test results.
3. Prepare academic research documentation and viva defense guide.
