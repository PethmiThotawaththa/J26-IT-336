# ACADEMIC RESEARCH DOCUMENTATION & TECHNICAL MANUAL
**Project Title:** AI-Based Intelligent Road Damage Detection, Severity Assessment, Repair Prioritization and Predictive Road Maintenance System  
**Project ID:** J26-IT-336  
**Primary Research Scope:** Component 4 — AI-Based Predictive Road Maintenance  
**Academic Degree:** B.Sc. (Hons) in Information Technology, Sri Lanka Institute of Information Technology (SLIIT)  
**Researcher:** Perera R.H.D. (IT23191174)  
**Supervisors:** Ms. Akshi De Silva (Supervisor), Ms. Sasini Hathurusinghe (Co-Supervisor)  
**Date of Completion:** October 2026  

---

## 1. Project Overview
Road transport infrastructure is an indispensable economic backbone for Sri Lanka. Prolonged trafficking, monsoon precipitation, thermal cycling, and delayed maintenance lead to progressive asphalt degradation. Conventional pavement management in Sri Lanka (managed by the Road Development Authority, RDA) has historically operated in a **reactive** paradigm: intervention occurs only after defects (potholes, extensive alligator fatigue cracking, rutting) become visible and hazardous.

**Component 4 (Predictive Road Maintenance)** addresses this fundamental limitation by establishing an artificial intelligence intelligence layer that models pavement decay before structural collapse occurs. It provides:
1. Continuous future Pavement Condition Index (PCI) forecasting across 3, 6, 12, and 24-month horizons.
2. Remaining Road Life (RRL) survival estimation to critical intervention thresholds.
3. Preventive maintenance recommendations matched with the RDA Highway Schedule of Rates (HSR 2025).
4. Explainable AI (XAI) feature attribution identifying whether degradation is driven primarily by heavy vehicle loading, monsoon moisture, pavement age, or distress propagation.

---

## 2. Research Problem, Gap & Objectives

### 2.1 Research Problem & Identified Gap
Existing literature and commercial pavement inspection systems focus primarily on **damage identification** (computer vision detection of cracks and potholes) or **immediate repair prioritization**. However, transportation agencies face a distinct predictive gap:
* *How will observed minor surface cracks deteriorate over the coming 12 to 24 months under prevailing traffic and weather?*
* *When is the precise cost-effective window for preventive sealing before structural subgrade failure forces full-depth reconstruction?*

Component 4 fills this gap by synthesizing current distresses, historical survey records, 16-class traffic axle loads, and meteorological precipitation data into an explainable predictive maintenance engine.

### 2.2 Objectives
* **Main Objective:** Develop, train, validate, and serve an AI-based predictive road maintenance research prototype that forecasts condition trajectories, calculates remaining useful life, and schedules cost-optimized preventive interventions.
* **Specific Objectives:**
  1. Ingest and harmonize heterogeneous RDA field datasets (surveys, traffic counts, weather, and budget rates).
  2. Implement leak-free preprocessing pipelines with domain-engineered pavement indices.
  3. Benchmark multiple baseline and advanced machine learning algorithms under fair, identical validation splits.
  4. Formulate non-linear Remaining Road Life (RRL) decay models with statistical confidence bounds.
  5. Build an interactive, telemetry-driven dashboard matching the proposal's engineering console design (Pages 33–36).
  6. Provide typed REST integration contracts for upstream research components (Components 1, 2, and 3).

---

## 3. Dataset Selection & Justification

### 3.1 Empirical Datasets Utilized
Rather than relying purely on theoretical simulations, the system was developed and validated on authentic Road Development Authority (RDA) of Sri Lanka datasets located in the Western Province / Colombo District:

1. **RDA Mobile Pavement Surveys (`RDA/Images/`):**
   - High-precision chainage, frame sequence, and GPS coordinates (Latitude, Longitude, Altitude) collected by the RDA mobile inspection vehicle across 6 primary highways:
     * `B047`: Battaramulla - Pannipitiya (7.42 km, 3,711 frames)
     * `B174`: Kottawa - Malabe (9.47 km, 9,471 frames)
     * `B214`: Kirindiwela - Radawana (9.10 km, 4,553 frames)
     * `B240`: Meegoda - Athurugiriya (28.00 km, 9,114 frames)
     * `B263`: Madinnagoda - Rajagiriya (5.55 km, 2,775 frames)
     * `B435`: Sri Jayawardenepura - Kotte / Orugodawatta (7.69 km, 3,844 frames)
2. **RDA Classified Vehicle Traffic Counts (`RDA/Traffic Data...xlsx`):**
   - 16 distinct vehicle categories: Motorcycles (MCL), Three-Wheelers (TWL), Passenger Cars (CAR), Light Goods (LGV), Medium Goods (MG1), Heavy Lorries (MG2, HG3), Articulated Trucks (AG3–AG6), and Buses (SBU, LBU).
   - Converted into AASHTO standard 18-kip Equivalent Single Axle Loads (ESAL).
3. **Colombo Meteorological Weather Telemetry (`RDA/Whether.csv`):**
   - 365 daily meteorological observations for 2025: Precipitation (2,674.9 mm annual rainfall), mean temperature (27.9°C), and diurnal temperature delta (4.5°C).
4. **Highway Schedule of Rates (HSR 2025) & Maintenance Budget (`RDA/Forecasted...xlsx`):**
   - Itemized unit rates in LKR for asphalt premix patching (Item 1: Rs. 23,476/ton), slurry seal (Item 51: Rs. 640.15/sq.m), crack sealing (Item 43: Rs. 109.55/m), micro-surfacing (Item 53: Rs. 591.20/sq.m), dense asphalt overlay (Item 75: Rs. 3,356.56/sq.m), and full reconstruction (Item 71: Rs. 18,526.49/sq.m).
5. **Synthetic Pipeline Benchmark (`data/processed/synthetic_pipeline_benchmark.csv`):**
   - 2,500 synthetic samples generated per Module B to validate pipeline scalability and extreme boundary conditions. Clearly distinguished from real experimental data.

---

## 4. Data Dictionary

| Attribute Name | Data Type | Physical Unit | Valid Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `section_id` | String | Categorical | `B047-SEC-001` | Unique 100m engineering section identifier |
| `corridor_id` | String | Categorical | `B047`–`B435` | Road route identifier |
| `start_chainage_km` | Float | Kilometers | $0.0 \dots 28.0$ | Start stationing along highway alignment |
| `start_lat`, `start_lon`| Float | Degrees | Sri Lanka bounds | Geographic coordinates from mobile survey GPS |
| `current_pci` | Float | Index (0–100) | $0.0 \dots 100.0$ | ASTM D6433 Pavement Condition Index |
| `pavement_age_years`| Float | Years | $0.5 \dots 15.0$ | Elapsed years since construction or last major overlay |
| `structural_number` | Float | Dimensionless | $2.5 \dots 6.5$ | AASHTO structural layer coefficient |
| `aadt` | Integer | Vehicles / day | $2,000 \dots 45,000$ | Annual Average Daily Traffic volume |
| `daily_esal` | Float | 18-kip ESAL / day| $300 \dots 5,000$ | Equivalent Single Axle Load stress factor |
| `heavy_vehicle_pct` | Float | Percentage | $2.0 \dots 15.0\%$ | Fraction of commercial freight vehicles and buses |
| `annual_precipitation_mm`| Float| Millimeters/yr | $1,500 \dots 3,500$ | Local annual rainfall causing subgrade saturation |
| `crack_density_pct` | Float | Percentage | $0.0 \dots 60.0\%$ | Surface area impacted by fatigue/alligator cracks |
| `pothole_count` | Integer | Count | $0 \dots 20$ | Active pothole frequency per 100m segment |
| `iri_roughness` | Float | m / km | $1.0 \dots 8.0$ | International Roughness Index |
| `rut_depth_mm` | Float | Millimeters | $0.0 \dots 40.0$ | Permanent deformation in wheel paths |
| `target_pci_12m` | Float | Index (0–100) | $0.0 \dots 100.0$ | Ground-truth condition at 12-month horizon |
| `remaining_road_life_months`| Integer | Months | $0 \dots 120$ | Months remaining until PCI crosses 55 threshold |

---

## 5. Preprocessing & Feature Engineering Methodology

### 5.1 Leakage Prevention
All feature transformations, medians for imputation, and standard scaling parameters are fitted strictly on the **training set** (`X_train`) and only transformed on test sets or incoming real-time payloads. Preprocessing pipelines are persisted in versioned joblib artifacts (`models/preprocessor.joblib`).

### 5.2 Domain-Engineered Pavement Features
Standard ML models benefit substantially from physics-informed interactions:
1. **Dynamic Water-Load Ingress (`traffic_precipitation_interaction`):**
   $$\text{Load} \times \text{Water} = \text{daily\_esal} \times \text{monsoon\_risk\_factor}$$
   Captures the well-known pavement engineering phenomenon where heavy axle loads over saturated subgrades accelerate hydraulic pumping and void collapse.
2. **Structural Load Intensity (`heavy_traffic_load_ratio`):**
   $$\frac{\text{daily\_esal}}{\text{structural\_number}}$$
   Normalizes the applied axle stress by the load-bearing capacity of the pavement cross-section.
3. **Composite Distress Index (`distress_composite_index`):**
   $$(0.4 \times \text{crack\_density}) + (3.5 \times \text{pothole\_count}) + (0.8 \times \text{rut\_depth})$$
   Aggregates discrete distress manifestations into a unified surface vulnerability metric.
4. **Thermal-Moisture Fatigue Index (`climate_fatigue_index`):**
   $$\frac{\text{annual\_precipitation} \times \text{diurnal\_delta}}{1000}$$
   Reflects the expansion/contraction cycling of asphalt binder in high-humidity tropical micro-climates.

---

## 6. Model Architecture & Experimental Evaluation

### 6.1 Experimental Setup
* **Splitting Strategy:** 80% Train (540 samples), 20% Test (135 samples) with Stratified Risk-Class partitioning and fixed random seed (`random_state=42`).
* **Hardware Environment:** 64-bit AMD64, Python 3.14.2.

### 6.2 Regression Benchmarks (Predicting 12-Month Future Condition)

| Model Name | Category | MAE (PCI) | RMSE (PCI) | $R^2$ Score | Train Time (s) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Linear Regression (Ridge Baseline)** | Baseline | **0.750** | **0.938** | **99.44%** | 0.02s |
| **XGBoost Regressor** | Advanced Ensemble | 1.070 | 1.673 | 98.22% | 0.40s |
| **Random Forest Regressor** | Advanced Ensemble | 1.190 | 1.773 | 98.00% | 0.34s |
| **Decision Tree Regressor** | Baseline | 1.411 | 1.911 | 97.67% | 0.01s |
| **LightGBM Regressor** | Advanced Ensemble | 1.359 | 2.400 | 96.33% | 0.14s |

### 6.3 Multi-Horizon Prediction Models (XGBoost Regressors)

| Horizon | Prediction Window | Test MAE | Test RMSE | Test $R^2$ Score |
| :--- | :--- | :--- | :--- | :--- |
| **3 Months** | Immediate quarterly planning | 0.564 | 1.458 | 98.31% |
| **6 Months** | Semi-annual budget allocation | 0.769 | 1.490 | 98.33% |
| **12 Months** | Annual routine maintenance | 1.070 | 1.673 | 98.22% |
| **24 Months** | Multi-year capital planning | 1.504 | 1.990 | 98.09% |

### 6.4 Classification Benchmarks (12-Month Risk Category)

| Model Name | Category | Accuracy | Precision (Weighted) | Recall (Weighted) | F1-Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Forest Classifier** | Advanced Ensemble | **95.56%** | **96.05%** | **95.56%** | **95.60%** |
| **XGBoost Classifier** | Advanced Ensemble | 94.07% | 94.60% | 94.07% | 94.13% |
| **LightGBM Classifier** | Advanced Ensemble | 94.07% | 94.34% | 94.07% | 94.12% |
| **Logistic Regression** | Baseline | 92.59% | 92.68% | 92.59% | 92.63% |
| **Decision Tree Classifier** | Baseline | 91.85% | 92.63% | 91.85% | 91.88% |

---

## 7. Remaining Road Life (RRL) Formulation
RRL is computed as the time remaining before the projected pavement condition crosses predefined intervention thresholds:
$$\text{RRL}_{\text{rehab}} = \frac{\text{PCI}_{\text{current}} - 55.0}{\text{Monthly Decay Rate} \times \phi(\text{ESAL}, \text{Monsoon})}$$

If $\text{PCI} \le 55.0$, $\text{RRL} = 0$, indicating that the window for preventive intervention has elapsed and structural rehabilitation is mandatory.

---

## 8. Preventive Maintenance Decision Logic & Economic Rescue
Component 4 maps forecasted condition and distress density into specific interventions aligned with the RDA Highway Schedule of Rates (HSR 2025):

1. **$\text{PCI} \ge 85$:** Routine clearance & drainage sweeping (HSR-40: Rs. 8.60/sq.m).
2. **$70 \le \text{PCI} < 85$:** Crack sealing with high-modulus mastic (HSR-43: Rs. 109.55/m) or slurry seal (HSR-51: Rs. 640.15/sq.m).
3. **$55 \le \text{PCI} < 70$:** Polymer-modified micro-surfacing (HSR-53: Rs. 591.20/sq.m) + hot mix patching.
4. **$40 \le \text{PCI} < 55$:** 50mm cold milling + dense asphalt concrete overlay (HSR-75: Rs. 3,356.56/sq.m).
5. **$\text{PCI} < 40$:** Full-depth reconstruction with base stabilization (HSR-71: Rs. 18,526.49/sq.m).

### Capex Rescue Calculation
$$\text{Preventive Savings} = \text{Cost}_{\text{Reconstruction}} - \text{Cost}_{\text{Proactive Treatment}}$$
Across the 675 monitored sections, proactive scheduling yields over **LKR 744,000,000 (USD $2.40 Million)** in capital rescue compared to deferred emergency reconstructions.

---

## 9. Explainable AI (XAI) Attribution
Global feature importance across ensemble models reveals:
1. `current_pci` (Primary anchor, 38.2% attribution)
2. `historical_decay_rate_annual` (Historical velocity, 21.4% attribution)
3. `traffic_precipitation_interaction` (Axle load under rain, 14.8% attribution)
4. `crack_density_pct` (Surface water breach, 11.2% attribution)
5. `pavement_age_years` (Binder oxidation, 7.6% attribution)

Localized explanations break down these factors for any individual road section, explaining *why* a particular section is decaying rapidly (e.g. "Fatigue Cracking accounts for 34.2% of projected condition loss due to water intrusion").

---

## 10. Research Limitations & Future Directions
1. **Survey Frequency:** Mobile survey vehicles currently survey corridors once per year. Real-time edge inference on public bus cameras could enable monthly updates.
2. **Subgrade GPR Telemetry:** While subgrade moisture is modeled via surface rainfall and soil classifications, ground-penetrating radar (GPR) sensors would directly measure sub-base void ratios.
3. **Multi-Asset Network Optimization:** Future research can formulate genetic algorithms or mixed-integer linear programming (MILP) to optimize county-wide crew routing under fixed annual capital budgets.
