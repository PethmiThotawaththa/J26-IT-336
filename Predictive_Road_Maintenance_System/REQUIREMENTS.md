# SYSTEM REQUIREMENTS SPECIFICATION (SRS) & PROPOSAL ANALYSIS
**Project Title:** AI-Based Intelligent Road Damage Detection, Severity Assessment, Repair Prioritization and Predictive Road Maintenance System  
**Project ID:** J26-IT-336  
**Primary Focus:** Component 4 — AI-Based Predictive Road Maintenance  
**Academic Institution:** Sri Lanka Institute of Information Technology (SLIIT)  
**Researcher:** Perera R.H.D. (IT23191174)  
**Supervisors:** Ms. Akshi De Silva (Supervisor), Ms. Sasini Hathurusinghe (Co-Supervisor)  
**Date:** October 2026  

---

## 1. Executive Summary & Research Background

Road infrastructure represents one of the most critical public assets in Sri Lanka and worldwide. Conventional pavement maintenance methodologies are overwhelmingly **reactive**—interventions are initiated only after severe physical distresses (potholes, extensive fatigue cracking, base deformation) become visually prominent and hazardous. Reactive maintenance incurs substantially elevated lifecycle costs (often 400%–700% higher than timely preventive treatments), jeopardizes vehicular safety, and causes recurrent traffic disruptions.

Although modern computer vision and automated survey technologies (such as the road survey vehicles operated by the Road Development Authority (RDA) of Sri Lanka) can detect surface distresses, existing operational workflows treat damage identification as an endpoint rather than an input to forward-looking predictive planning. 

**Component 4 (Predictive Road Maintenance)** addresses this core gap. By synthesizing multi-source data—including longitudinal pavement condition indices (PCI), crack and pothole distress severity, vehicle classification traffic counts (ESALs), local micro-climatic environmental parameters (rainfall, temperature), structural road geometry, and historical maintenance interventions—Component 4 develops data-driven machine learning models to forecast future pavement deterioration, quantify Remaining Road Life (RRL), and generate actionable, cost-optimized preventive maintenance recommendations.

---

## 2. Comprehensive Proposal Analysis

### 2.1 Research Problem & Gap Analysis
* **Identified Research Gap:** While computer vision systems identify existing surface distress (Components 1 & 2), and prioritization algorithms rank immediate repairs (Component 3), infrastructure authorities lack an integrated intelligence layer that answers:
  1. *How rapidly will this specific road section deteriorate over the next 3, 6, 12, or 24 months?*
  2. *What is the estimated Remaining Road Life (RRL) before the section breaches critical structural thresholds?*
  3. *When is the optimal intervention window for cost-effective preventive maintenance before catastrophic failure occurs?*
  4. *What specific preventive engineering treatment (slurry seal, crack sealing, micro-surfacing, thin overlay vs. structural reconstruction) is technically indicated?*
* **Primary Scope:** Component 4 takes ownership of time-series deterioration modeling, machine learning condition forecasting, remaining life estimation, maintenance forecasting, and explainable decision support.

### 2.2 Main and Specific Objectives
* **Main Objective:** Develop an AI-based predictive road maintenance research prototype that leverages current and historical road condition data, traffic loading, environmental factors, and maintenance logs to forecast future road deterioration, estimate remaining useful life, and recommend preventive maintenance interventions.
* **Specific Objectives (Proposal Section 2.2):**
  1. Identify and analyze key deterioration factors: current condition, historical trends, traffic loading (axle loads/heavy vehicles), environmental exposure (precipitation, temperature), road structural characteristics, and prior maintenance.
  2. Implement a robust data management and preprocessing pipeline for cleaning, imputation, transformation, and feature engineering without data leakage.
  3. Build, train, optimize, and systematically compare multiple machine learning algorithms (Linear Regression, Decision Tree, Random Forest, XGBoost, LightGBM, CatBoost).
  4. Formulate quantitative Remaining Road Life (RRL) models based on condition decay curves and established engineering intervention thresholds (e.g., ASTM D6433 PCI standards).
  5. Develop an explainable maintenance forecasting and preventive recommendation engine linking predictions with Highway Schedule of Rates (HSR 2025) and RDA maintenance budgets.
  6. Design an interactive, enterprise-grade research dashboard inspired by the proposal's telemetry UI (Pages 33–36), coupled with an open REST API and database.

---

## 3. Requirements Clarification & Inconsistency Audit

In accordance with Section 1 of the Master Prompt, the proposal was audited for internal consistency and template artifacts:

| Item / Location in Proposal | Text in Proposal | Audit Finding & Classification | Engineering Decision & Resolution |
| :--- | :--- | :--- | :--- |
| **Figure 3 (Page 24)** | Table includes: "Purchase-history data preparation", "Shopping pattern analysis", "Monthly product prediction", "Product recognition", "Trolley tracking", "Cart product detection", "Billing synchronization" | **Template Artifact:** Residual text from an unrelated retail / smart shopping trolley project inadvertently left in the proposal draft. | **Exclusion & Replacement:** Strictly excluded. Replaced with actual Component 4 pavement engineering boundaries: Pavement Condition Time-series, Traffic & Axle Load Preparation, Deterioration Modeling, RRL Estimation, and Preventive Action Dispatch. |
| **Section 3.2.1 (Page 17)** | Subtitle: "Purchase History Data" | **Typographical / Template Error:** Intended to describe "Historical Road Condition & Maintenance Data". | **Corrected Definition:** Defined as longitudinal pavement distress, inspection surveys, and historical maintenance interventions. |
| **Section 3.2.2 (Page 17)** | Subtitle: "Questionnaire Data" | **Inconsistent Heading:** Body discusses traffic counts, rainfall, temperature, road age, and road type. | **Corrected Definition:** Defined as Environmental and Traffic Telemetry Data from RDA and meteorological stations. |
| **Section 7.3 (Page 28)** | Table 4 mentions "Preparing purchase-history data" | **Template Artifact:** Residual retail task label. | **Corrected Definition:** Replaced with "Road Condition and Maintenance History Data Curation". |
| **Confidence Percentages (UI vs Model)** | Proposal UI mockups (pp. 33-36) display "AI Confidence: 98.4%" | **Requirement Constraint:** Prompt explicitly forbids fabricated confidence percentages. | **Statistically Grounded Implementation:** Use authentic confidence intervals (e.g., prediction intervals from quantile regression or ensemble standard deviation) rather than static hardcoded metrics. |

---

## 4. System Boundaries & Component Interfacing

Component 4 operates as the predictive decision-support core of the four-component collaborative research architecture:

```
[ Component 1: Data Collection & Damage Detection ]
       │ (Camera Survey Frames, GPS Chainage, Detected Bounding Boxes)
       ▼
[ Component 2: Road Condition & Severity Assessment ]
       │ (Distress Types: Potholes, Cracks; Severity Levels; Local PCI Score)
       ▼
[ Component 3: Repair Prioritization & Asset Information ]
       │ (Asset Inventory, Immediate Repair Urgency, Budget Constraints)
       ▼
[ COMPONENT 4: PREDICTIVE ROAD MAINTENANCE (OUR SCOPE) ]
       │ ── Preprocessing & Feature Engineering
       │ ── Multi-Model ML Decay Curves (3, 6, 12, 24-Month Forecasts)
       │ ── Remaining Road Life (RRL) Estimation Engine
       │ ── Maintenance Forecasting & Preventive Intervention Engine
       │ ── Explainable AI (SHAP / Feature Attribution)
       ▼
[ System Outputs / Stakeholder Interface ]
  • Road Development Authority (RDA) Engineers
  • Provincial & Municipal Highway Planners
  • Autonomous Work Order Dispatch & HSR Budgeting
```

---

## 5. Functional Requirements (FR)

### Module A — Road Data Management
* **FR-A1:** Ingest structured road condition data via CSV, Excel, or JSON formats.
* **FR-A2:** Validate incoming datasets (schema validation, boundary checks: PCI $\in [0, 100]$, chainage $\ge 0$, coordinates within valid geographic bounds).
* **FR-A3:** Handle missing values through domain-appropriate imputation (median, forward-fill for time series, KNN).
* **FR-A4:** Deduplicate records and normalize inconsistent casing/naming conventions.
* **FR-A5:** Store and retrieve road section geometries, inspection surveys, traffic loading, weather exposure, and historical interventions.
* **FR-A6:** Generate interactive data quality and validation reports (missingness rate, distribution statistics, schema compliance).

### Module B — Dataset Preparation & Real-World Integration
* **FR-B1:** Ingest real RDA Sri Lanka datasets:
  - 6 Road Inspection Surveys (`B047`, `B174`, `B214`, `B240`, `B263`, `B435`) with exact GPS chainage, camera frames, and elevation.
  - Classified 16-category vehicle traffic counts (MCL, CAR, LGV, MG1, MG2, HG3, AG3–AG6) converted into Equivalent Single Axle Loads (ESAL).
  - Routine maintenance budget & Schedule of Rates (HSR 2025) with unit costs in LKR.
  - 365-day meteorological weather observations (precipitation, temperature, humidity).
* **FR-B2:** Incorporate standard Long-Term Pavement Performance (LTPP) longitudinal degradation parameters to capture multi-year deterioration curves.
* **FR-B3:** Provide a reproducible, parameterized synthetic data generator script for simulating extensive longitudinal histories with documented physical decay assumptions.

### Module C — Preprocessing & Feature Engineering Pipeline
* **FR-C1:** Fit all transformations (scalers, encoders, imputers) strictly on training splits to prevent data leakage.
* **FR-C2:** Apply time-aware and road-section-aware cross-validation (GroupKFold / TimeSeriesSplit).
* **FR-C3:** Derive domain-specific pavement engineering features:
  - Cumulative Heavy Vehicle ESAL exposure
  - Annual Precipitation Exposure Index (monsoon impact)
  - Thermal Fatigue Index (diurnal temperature swings)
  - Historical Deterioration Rate ($\Delta \text{PCI} / \Delta t$)
  - Pavement Age and Time Since Last Maintenance
  - Distress Density Scores (Crack Density %, Pothole Count per km)
* **FR-C4:** Serialize and persist versioned scikit-learn preprocessing pipelines (`pipeline.pkl`).

### Module D — Machine Learning Model Development
* **FR-D1:** Implement regression baselines: Linear Regression, Decision Tree Regressor.
* **FR-D2:** Implement advanced ensemble models: Random Forest, XGBoost Regressor, LightGBM Regressor.
* **FR-D3:** Implement classification baselines and ensembles for Condition Rating (Good, Fair, Poor, Critical).
* **FR-D4:** Execute hyperparameter tuning with GridSearchCV / RandomizedSearchCV under fixed random seeds (`random_state=42`).
* **FR-D5:** Persist trained model artifacts with metadata (hyperparameters, training timestamp, dataset hash, feature names).

### Module E — Future Condition Prediction
* **FR-E1:** Predict continuous pavement condition (PCI) across discrete horizons: 3, 6, 12, and 24 months.
* **FR-E2:** Classify predicted future risk states (Low, Moderate, High, Critical).
* **FR-E3:** Compute statistical prediction intervals (e.g., 90% confidence bounds based on residual quantile modeling).

### Module F — Remaining Road Life (RRL) Estimation
* **FR-F1:** Model continuous decay trajectories from $t_0$ forward until condition intercepts defined intervention thresholds (PCI = 55 for rehabilitation, PCI = 40 for critical failure).
* **FR-F2:** Calculate Remaining Useful Life in months/years.
* **FR-F3:** Document and present engineering decay assumptions and boundary conditions.

### Module G & H — Maintenance Forecasting & Preventive Recommendation
* **FR-G1:** Translate condition forecasts into required maintenance windows (Immediate < 30 days, Short-term 1–3 months, Planned 6–12 months, Monitor).
* **FR-H1:** Rule-based and model-informed recommendation engine recommending treatments:
  - Crack Sealing / Slurry Seal (Early stage fatigue, PCI 70–85)
  - Micro-surfacing / Thin Overlay (Moderate roughness, PCI 55–70)
  - Mill & Inlay / Resurfacing (Severe rutting/cracking, PCI 40–55)
  - Full-Depth Reclamation / Reconstruction (Base failure, PCI < 40)
* **FR-H2:** Estimate maintenance budgetary cost using RDA Sri Lanka HSR 2025 unit rates and calculate Capex rescue vs deferred reconstruction costs.

### Module I — Explainable AI (XAI)
* **FR-I1:** Generate global feature importance rankings across all trained tree models.
* **FR-I2:** Compute localized feature contributions for individual road section predictions (TreeSHAP or tree path attributions).

### Module J — Backend REST API
* **FR-J1:** FastAPI application providing endpoints:
  - `/api/health`
  - `/api/datasets/summary`, `/api/datasets/upload`
  - `/api/models/train`, `/api/models/evaluation`, `/api/models/compare`
  - `/api/predict/condition`, `/api/predict/remaining-life`, `/api/predict/maintenance`
  - `/api/roads`, `/api/roads/{road_id}`, `/api/roads/{road_id}/decay-curve`
  - `/api/integration/component-adapter` (mock ingest from Comp 1/2/3)
  - `/api/dashboard/summary`

### Module K — Frontend Dashboard
* **FR-K1:** Implement high-density, technical telemetry UI inspired by Pages 33–36:
  1. *Predictive Overview:* Real-time KPI matrix, deterioration radar, critical decay zones, Capex rescue.
  2. *Deterioration Curves:* Multi-horizon decay graph with confidence bands, scenario simulation (traffic & climate load modifiers).
  3. *Road Section Telemetry:* Deep inspector displaying chainage, surface distress, geotechnical stratigraphy, and localized XAI explanations.
  4. *Maintenance Planning:* Priority dispatch queue (P1/P2/P3), 14-day weather-linked scheduling Gantt, cost vs deferral penalty calculation.
  5. *GIS Map:* Interactive OpenStreetMap Leaflet visualization of Sri Lanka RDA road corridors with colored condition markers and telemetry callouts.
  6. *Model Evaluation Bench:* Side-by-side MAE, RMSE, $R^2$, and classification metrics with training curves.
  7. *Dataset Management:* Upload, schema audit, and data dictionary explorer.

### Module L — Component Integration
* **FR-L1:** Provide typed Pydantic integration contracts and adapter fixtures simulating incoming payloads from Component 1 (YOLO defect boxes), Component 2 (pavement condition rating), and Component 3 (asset priority).

---

## 6. Non-Functional Requirements (NFR)

* **NFR-1 (Performance & Latency):** Model inference latency $< 150\text{ ms}$ for single road segment; batch inference $< 1.5\text{ s}$ for 1,000 segments.
* **NFR-2 (Reproducibility):** All data splits, preprocessing steps, and model seeds locked to `seed=42`. All scripts runnable non-interactively.
* **NFR-3 (Reliability & Robustness):** Graceful handling of missing or out-of-range sensor readings without unhandled 500 errors.
* **NFR-4 (Extensibility):** Modular design allowing swapping of algorithms (e.g. Scikit-learn, XGBoost, LightGBM) via unified interface.
* **NFR-5 (Defensibility & Research Validity):** Clear separation between empirical data (RDA Sri Lanka, LTPP), synthetic validation datasets, and engineering rule-based logic. No hallucinated benchmarks.

---

## 7. Acceptance Criteria (Definition of Done)
1. Complete requirements, architecture, and implementation plans documented.
2. Ingestion pipeline operating on real RDA Sri Lanka road surveys, traffic, weather, and budget sheets.
3. Preprocessing and feature engineering pipeline functioning reproducibly without data leakage.
4. Multiple ML models trained, evaluated, and compared on identical test sets with documented MAE, RMSE, and $R^2$.
5. Future condition, RRL, and maintenance forecasting functioning with documented engineering thresholds.
6. FastAPI backend running with comprehensive endpoints, Pydantic validation, and SQLite persistence.
7. React TypeScript dashboard operational, matching proposal aesthetics with interactive charts and Leaflet GIS mapping.
8. Component 1, 2, 3 adapter interfaces and mock fixtures implemented.
9. Comprehensive automated test suite passing (unit, API, ML inference).
10. Final research documentation, viva defense notes, and run guides provided.
