# SYSTEM ARCHITECTURE & TECHNICAL SPECIFICATION
**Project Title:** AI-Based Intelligent Road Damage Detection, Severity Assessment, Repair Prioritization and Predictive Road Maintenance System  
**Project ID:** J26-IT-336  
**Component:** Component 4 — AI-Based Predictive Road Maintenance  
**Author:** Perera R.H.D. (IT23191174)  

---

## 1. High-Level Architecture Overview

Component 4 is structured as a layered, modular service architecture decoupling data ingestion, feature engineering, machine learning inference, decision-support engines, backend REST services, and frontend visualization.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PRESENTATION LAYER                                     │
│  React 18 + TypeScript + Vite + Tailwind CSS + Lucide Icons + Recharts + Leaflet GIS   │
│  Pages: Overview Dashboard | Deterioration Curves | Road Telemetry | Maintenance Gantt │
│         GIS Map Explorer | Model Benchmark Lab | Dataset Quality Manager              │
└───────────────────────────────────────────▲────────────────────────────────────────────┘
                                            │ HTTP / JSON REST APIs
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                                BACKEND APPLICATION LAYER                              │
│  FastAPI (Python 3.14 / Uvicorn Async Server)                                          │
│  ├── Routers: /datasets, /models, /predict, /roads, /maintenance, /integration         │
│  ├── Service Layer: IngestionService, FeatureService, InferenceService, DispatchService │
│  └── Validation: Pydantic v2 Models & Schema Enforcers                                 │
└───────────────────────────────────────────▲────────────────────────────────────────────┘
                                            │
               ┌────────────────────────────┴───────────────────────────┐
               ▼                                                        ▼
┌──────────────────────────────┐                         ┌──────────────────────────────┐
│       AI / ML ENGINE         │                         │        DATABASE LAYER        │
│  Scikit-Learn | XGBoost      │                         │  SQLite (Dev) / PostgreSQL   │
│  LightGBM | TreeSHAP XAI     │                         │  SQLAlchemy 2.0 ORM Schema:  │
│  ├── Preprocessing Pipeline  │                         │  • RoadSections              │
│  ├── Multi-Horizon Models    │                         │  • Inspections & Defects     │
│  │   (3, 6, 12, 24 Months)   │                         │  • Traffic & Axle Loads      │
│  ├── RRL Survival Estimator  │                         │  • Weather & Climate         │
│  └── Maintenance Optimizer   │                         │  • Forecasts & Work Orders   │
└──────────────────────────────┘                         └──────────────────────────────┘
               ▲                                                        ▲
               └────────────────────────────┬───────────────────────────┘
                                            │
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                             DATA INGESTION & INTEGRATION LAYER                         │
│  • RDA Sri Lanka Survey Importers (B047, B174, B214, B240, B263, B435)                │
│  • Vehicle Traffic & Axle Load Classifier (16 Vehicle Classes -> ESAL)                │
│  • Colombo Meteorological Weather Harmonizer (Precipitation, Temperature)              │
│  • Highway Schedule of Rates (HSR 2025) Maintenance Item Matcher                      │
│  • Component 1, 2, 3 Integration Adapters & Mock Fixtures                              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component 4 Internal Modular Decomposition

### Module 1: Ingestion & Data Hygiene Engine (`backend/app/services/ingestion.py`)
* Ingests CSV, XLSX, and JSON files from RDA survey logs, weather series, and traffic sheets.
* Validates schema, null-thresholds, and physical bounds (e.g., $0 \le \text{PCI} \le 100$, latitude in Sri Lanka $[5.8, 9.9]$, longitude $[79.5, 82.0]$).
* Normalizes data into canonical domain entities.

### Module 2: Pavement Feature Engineering Pipeline (`backend/app/ml/features.py`)
* Derives domain-specific degradation indicators:
  - **$\text{ESAL}_{daily}$:** $\sum_{k=1}^{K} N_k \times \text{LEF}_k$ (where $N_k$ is count of vehicle class $k$ and $\text{LEF}_k$ is AASHTO Load Equivalency Factor).
  - **Heavy Vehicle Proportion:** $\frac{\sum \text{Trucks} + \text{Buses}}{\text{AADT}}$.
  - **Monsoon Water Ingress Factor:** 90-day moving cumulative precipitation $\times$ road surface permeability factor.
  - **Thermal Delta Exposure:** Diurnal range $|T_{max} - T_{min}|$ inducing asphalt expansion/contraction fatigue.
  - **Structural Pavement Age:** Current Year minus Year of Construction/Major Overlay.
  - **Pavement Distress Score:** Composite distress index combining crack density ($\%$) and pothole severity.

### Module 3: Multi-Model ML Architecture (`backend/app/ml/models.py`)
* Supports two distinct modeling paradigms:
  1. **Continuous Condition Regression:**
     - Target: Future PCI ($y_{t+h}$ for $h \in \{3, 6, 12, 24\}$ months).
     - Models: Ridge Regression, Decision Tree, Random Forest Regressor, XGBoost Regressor, LightGBM Regressor.
     - Loss: Mean Squared Error / Huber Loss (robust to survey outliers).
  2. **Maintenance Risk Categorization (Classification):**
     - Target: Risk Class ($0: \text{Good [85-100]}$, $1: \text{Satisfactory [70-84]}$, $2: \text{Fair [55-69]}$, $3: \text{Poor [40-54]}$, $4: \text{Critical [<40]}$).
     - Models: Logistic Regression, Random Forest Classifier, XGBoost Classifier.
* Strict validation design: TimeSeriesSplit and GroupKFold by road section to prevent spatial/temporal leakage.

### Module 4: Remaining Road Life (RRL) Calculation Engine (`backend/app/ml/rrl_engine.py`)
* Projects non-linear decay trajectories:
  $$\text{PCI}(t) = \text{PCI}_0 - \alpha \cdot t^\beta$$
  where $\alpha$ is calibrated from traffic/weather load and $\beta \ge 1.0$ represents accelerating distress propagation.
* Intercepts:
  - **Preventive Intervention Horizon:** $\text{PCI}(t) = 70$
  - **Rehabilitation Horizon:** $\text{PCI}(t) = 55$
  - **Terminal Structural Failure:** $\text{PCI}(t) = 40$
* Generates RRL in days/months with 90% confidence bands derived from model prediction error variance.

### Module 5: Maintenance Recommendation & Budgeting Engine (`backend/app/services/maintenance.py`)
* Maps forecasted PCI, distress profiles, and RRL into AASHTO/RDA maintenance rules:
  - $\text{PCI} \ge 85$: Routine Maintenance (Routine sweeping, drainage clearance — HSR Item 40).
  - $70 \le \text{PCI} < 85$: Preventive Crack Sealing / Fog Seal (HSR Item 43/51).
  - $55 \le \text{PCI} < 70$: Micro-surfacing / Slurry Seal / Pothole Patching (HSR Item 1/2/59).
  - $40 \le \text{PCI} < 55$: Asphalt Concrete Mill & Overlay (HSR Item 75).
  - $\text{PCI} < 40$: Full-Depth Reconstruction / Base Stabilization (HSR Item 71).
* Computes estimated intervention cost vs. Deferred Rebuild Penalty:
  $$\text{Savings} = \text{Cost}_{\text{Emergency Rebuild}} - \text{Cost}_{\text{Proactive Intervention}}$$

### Module 6: Explainable AI Service (`backend/app/ml/explainability.py`)
* Global feature importance across all candidate models.
* Localized contribution breakdowns for any queried road section, pinpointing whether deterioration is driven primarily by heavy axle loads, monsoon moisture, pavement age, or crack propagation.

---

## 3. Database Schema (SQLAlchemy / Relational Design)

The database schema is modeled for relational integrity and fast spatial/temporal querying:

```sql
-- 1. Road Corridors
CREATE TABLE road_corridors (
    id VARCHAR(32) PRIMARY KEY,       -- e.g. 'B047', 'B174'
    name VARCHAR(255) NOT NULL,       -- 'Battaramulla - Pannipitiya'
    total_length_km FLOAT NOT NULL,   -- 7.42
    district VARCHAR(64) DEFAULT 'Colombo',
    road_class VARCHAR(16) DEFAULT 'B'
);

-- 2. Road Sections (Segments)
CREATE TABLE road_sections (
    id VARCHAR(64) PRIMARY KEY,       -- e.g. 'B047-SEC-001'
    corridor_id VARCHAR(32) REFERENCES road_corridors(id),
    start_chainage_km FLOAT NOT NULL,
    end_chainage_km FLOAT NOT NULL,
    start_lat FLOAT NOT NULL,
    start_lon FLOAT NOT NULL,
    end_lat FLOAT NOT NULL,
    end_lon FLOAT NOT NULL,
    surface_type VARCHAR(64) DEFAULT 'Asphalt Concrete',
    lanes INT DEFAULT 2,
    construction_year INT,
    last_overlay_year INT
);

-- 3. Inspection Surveys (Mobile Camera / Visual / LiDAR)
CREATE TABLE inspection_surveys (
    id VARCHAR(64) PRIMARY KEY,
    section_id VARCHAR(64) REFERENCES road_sections(id),
    survey_date TIMESTAMP NOT NULL,
    pci_score FLOAT NOT NULL,         -- 0 - 100
    iri_roughness FLOAT,              -- m/km
    crack_density_pct FLOAT,          -- 0 - 100%
    pothole_count INT DEFAULT 0,
    rut_depth_mm FLOAT DEFAULT 0.0,
    operator VARCHAR(64),
    survey_vehicle VARCHAR(64),
    sample_image_path VARCHAR(255)
);

-- 4. Traffic Observations
CREATE TABLE traffic_observations (
    id VARCHAR(64) PRIMARY KEY,
    corridor_id VARCHAR(32) REFERENCES road_corridors(id),
    observation_date DATE NOT NULL,
    aadt INT NOT NULL,
    heavy_vehicle_pct FLOAT NOT NULL,
    daily_esal FLOAT NOT NULL,
    mcl_count INT,
    car_count INT,
    truck_count INT,
    bus_count INT
);

-- 5. Weather Telemetry
CREATE TABLE weather_telemetry (
    id VARCHAR(64) PRIMARY KEY,
    district VARCHAR(64) DEFAULT 'Colombo',
    record_date DATE NOT NULL,
    avg_temp_c FLOAT NOT NULL,
    min_temp_c FLOAT NOT NULL,
    max_temp_c FLOAT NOT NULL,
    precipitation_mm FLOAT NOT NULL,
    relative_humidity_pct FLOAT,
    wind_speed_kmh FLOAT
);

-- 6. Model Training Experiments
CREATE TABLE model_experiments (
    id VARCHAR(64) PRIMARY KEY,
    model_name VARCHAR(64) NOT NULL,   -- 'XGBoost', 'Random Forest', etc.
    task_type VARCHAR(32) NOT NULL,    -- 'regression' or 'classification'
    prediction_horizon_months INT,     -- 3, 6, 12, 24
    mae FLOAT,
    rmse FLOAT,
    r2_score FLOAT,
    accuracy FLOAT,
    f1_score FLOAT,
    hyperparameters JSON,
    feature_list JSON,
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    artifact_path VARCHAR(255)
);

-- 7. Condition Predictions
CREATE TABLE condition_predictions (
    id VARCHAR(64) PRIMARY KEY,
    section_id VARCHAR(64) REFERENCES road_sections(id),
    model_id VARCHAR(64) REFERENCES model_experiments(id),
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    horizon_months INT NOT NULL,
    predicted_pci FLOAT NOT NULL,
    predicted_pci_lower FLOAT,
    predicted_pci_upper FLOAT,
    risk_category VARCHAR(32) NOT NULL,
    estimated_rrl_months INT NOT NULL
);

-- 8. Maintenance Work Orders
CREATE TABLE maintenance_work_orders (
    id VARCHAR(64) PRIMARY KEY,
    section_id VARCHAR(64) REFERENCES road_sections(id),
    priority VARCHAR(8) NOT NULL,      -- 'P1', 'P2', 'P3'
    recommended_action VARCHAR(128) NOT NULL,
    urgency_days INT NOT NULL,
    hsr_item_code VARCHAR(32),
    estimated_cost_lkr FLOAT NOT NULL,
    preventive_savings_lkr FLOAT NOT NULL,
    status VARCHAR(32) DEFAULT 'QUEUED' -- 'QUEUED', 'APPROVED', 'DISPATCHED'
);
```

---

## 4. REST API Endpoint Specifications

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check, system uptime, and model loading status |
| `GET` | `/api/dashboard/summary` | KPI aggregates: average PCI, critical zones count, Capex rescue, monitored corridors |
| `GET` | `/api/roads` | List all monitored road corridors & summary statistics |
| `GET` | `/api/roads/{section_id}` | Detailed telemetry and condition record for specific road section |
| `GET` | `/api/roads/{section_id}/decay-curve` | 36-month condition trajectory, intervention vs status quo decay curves |
| `POST` | `/api/predict/condition` | Run multi-horizon condition prediction for custom road parameters |
| `POST` | `/api/predict/remaining-life` | Calculate remaining useful life (RRL) based on condition & deterioration rate |
| `POST` | `/api/predict/maintenance` | Generate maintenance recommendations, HSR cost, and dispatch urgency |
| `GET` | `/api/models/evaluation` | Full comparative benchmark matrix (MAE, RMSE, $R^2$, F1) across all algorithms |
| `POST` | `/api/models/train` | Trigger retraining & hyperparameter tuning on selected dataset |
| `GET` | `/api/datasets` | List uploaded datasets and validation metrics |
| `POST` | `/api/datasets/upload` | Ingest and validate external road condition CSV/XLSX |
| `POST` | `/api/integration/adapter/comp1-3` | Standardized payload adapter for receiving inputs from Components 1, 2, and 3 |

---

## 5. Frontend Architecture & Visual Telemetry Design

Built with **React 18**, **TypeScript**, and **Tailwind CSS**, adhering to the visual design specifications seen on Pages 33–36 of the research proposal:

1. **Design Tokens & Theme:**
   - Slate dark / high-contrast technical aesthetic.
   - Distinct status color accents:
     - Emerald Green (`#10B981`): Healthy / Stable / Low Risk ($\text{PCI} \ge 70$).
     - Amber Orange (`#F59E0B`): Warning / Moderate Risk ($55 \le \text{PCI} < 70$).
     - Crimson Red (`#EF4444`): Critical Collapse / High Risk ($\text{PCI} < 55$).
     - Cyan Blue (`#06B6D4`): Active Sensor / Model Telemetry.
   - Monospace numerical fonts for high-precision telemetry readings.
2. **Page Modules:**
   - **Page 1: Predictive Health (Overview):** Structural Health Index, critical decay zones, Capex rescue counter, anomaly stream with quick-dispatch action.
   - **Page 2: Deterioration Forecasting & Neural Curves:** Interactive 36-month decay charts, scenario modifier sliders (heavy traffic, monsoon deluge, aggregate type), proactive vs deferred cost delta.
   - **Page 3: Road Section Deep Inspector:** Stratigraphic geotechnical cross-section, localized feature importance attribution, crack and rut telemetry.
   - **Page 4: Priority Maintenance Dispatch:** Dynamic P1/P2/P3 queue, 14-day weather-locked maintenance Gantt (with precipitation lockout indicator), Bitumen/Crew readiness tracker.
   - **Page 5: GIS Geospatial Map:** Leaflet OpenStreetMap view rendering Sri Lanka RDA corridors (B047, B174, B214, B240, B263, B435) with clickable station markers, condition popups, and elevation profiles.
   - **Page 6: Model Evaluation Benchmark:** Tabular and graphical comparison of Linear Regression, Decision Tree, Random Forest, XGBoost, and LightGBM models.
   - **Page 7: Dataset & Ingestion Hub:** Data quality scorecard, schema validator, and CSV uploader.

---

## 6. Integration Contract (Components 1, 2, 3)

Component 4 specifies a clean, type-safe integration adapter:
```json
{
  "source_component": "Component_2_Severity_Assessment",
  "survey_metadata": {
    "survey_id": "SRV-2026-B047-01",
    "timestamp": "2026-10-17T12:00:00Z",
    "corridor_id": "B047",
    "chainage_km": 4.250,
    "gps": { "latitude": 6.87412, "longitude": 79.93215 }
  },
  "detected_distresses": [
    { "type": "Transverse Crack", "severity": "Medium", "area_sqm": 2.4, "confidence": 0.94 },
    { "type": "Pothole", "severity": "High", "depth_mm": 45, "area_sqm": 0.35, "confidence": 0.91 }
  ],
  "current_assessed_pci": 62.5,
  "component_3_priority_score": 7.8
}
```
Component 4 ingests this payload, matches the road corridor and chainage against historical traffic, environmental records, and maintenance logs, runs the predictive decay model, and returns:
- Predicted PCI at 3, 6, 12, and 24 months
- Estimated Remaining Road Life until PCI 55 and 40
- Recommended preventive treatment and HSR 2025 cost estimate
- Suggested intervention deadline before catastrophic cost escalation.
