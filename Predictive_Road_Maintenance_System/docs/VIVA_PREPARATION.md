# VIVA VOCE DEFENSE & ORAL EXAMINATION NOTES
**Project Title:** AI-Based Intelligent Road Damage Detection, Severity Assessment, Repair Prioritization and Predictive Road Maintenance System  
**Component:** Component 4 — AI-Based Predictive Road Maintenance  
**Candidate:** Perera R.H.D. (IT23191174) — SLIIT  

---

## 1. Core Technical Defense Questions & Answers

### Q1: What is the exact research contribution of Component 4 compared to the other 3 components?
* **Answer:**  
  - *Component 1* detects present defects (YOLO-based bounding boxes on cracks and potholes).
  - *Component 2* assesses the present severity rating (e.g. low, medium, high severity index).
  - *Component 3* ranks immediate repair urgency based on static inventory.
  - **Component 4 (Our Component)** is the *forward-looking temporal intelligence layer*. It models the time-dimension: forecasting future pavement condition (PCI) over 3, 6, 12, and 24 months, calculating Remaining Road Life (RRL) before structural failure, and scheduling preventive interventions matched to the RDA Highway Schedule of Rates (HSR 2025).

### Q2: Why did Ridge Regression achieve a lower MAE (0.750) than XGBoost (1.070) for 12-month PCI prediction?
* **Answer:**  
  Pavement deterioration in short-to-medium intervals is predominantly continuous and quasi-linear with strong structural anchors (`current_pci` and `historical_decay_rate_annual`). Linear models with L2 regularization (Ridge) excel at preserving smooth continuous slopes without tree-based step-function quantization. However, for non-linear interactions under extreme axle loads and monsoon spikes, and for multi-class risk categorization, tree ensembles (Random Forest and XGBoost) demonstrated superior performance (Random Forest achieved **95.6% F1-score** and XGBoost achieved **94.1% F1-score**).

### Q3: What discrepancy did you identify in the initial proposal report (Figure 3 and Table 4)?
* **Answer:**  
  During our rigorous requirements audit, we identified that Table 4 and Figure 3 in the initial proposal contained residual template labels from a retail / smart shopping cart project (referencing "Purchase-history data preparation", "Shopping pattern analysis", and "Trolley tracking"). Rather than implementing these blindly, we performed a formal requirements clarification in `REQUIREMENTS.md`, audited the boundaries, and properly replaced them with authentic pavement engineering tasks: Pavement Condition Time-series, Traffic & Axle Load Harmonization, Deterioration Modeling, RRL Estimation, and Autonomous Work Order Dispatch.

### Q4: How is data leakage prevented during feature engineering and model training?
* **Answer:**  
  All preprocessing transformers (imputers, feature scaling, and interaction transformers) are fitted *strictly on the training split* (`X_train`) and only used to transform the test set and live API payloads. We also employed stratified section-aware grouping to ensure that spatial segments from the same road section did not appear across both train and test partitions.

### Q5: How is Remaining Road Life (RRL) calculated, and what are its engineering thresholds?
* **Answer:**  
  RRL is formulated using AASHTO / ASTM D6433 standard pavement condition thresholds:
  - *Rehabilitation Threshold:* PCI = 55. If condition drops below 55, preventive surface treatments are no longer viable and structural rehabilitation is required.
  - *Terminal Failure Threshold:* PCI = 40. Pavement experiences subgrade shear and structural failure requiring full reconstruction.
  The engine models non-linear monthly decay under local ESAL traffic and monsoon exposure to compute the exact number of months and days until these threshold intercepts occur.

### Q6: How are the maintenance cost savings calculated?
* **Answer:**  
  We utilize authentic unit costs from the RDA Highway Schedule of Rates (HSR 2025). Proactive intervention (e.g. polymer micro-surfacing at Rs. 591.20/sq.m or slurry seal at Rs. 640.15/sq.m) costs approximately **LKR 413,840** for a 100m carriageway section. If deferred until structural failure (PCI < 40), the section requires full-depth reconstruction with base stabilization (HSR Item 71 at Rs. 18,526.49/sq.m), costing **LKR 12,968,543**—over 31 times higher. The net preventive savings represents **LKR 12.55 Million per section**, yielding an average return on investment (ROI) of +34% to +180%.

---

## 2. Key Terminology Cheat Sheet
* **PCI (Pavement Condition Index):** Numerical rating from 0 (failed) to 100 (perfect), standardized by ASTM D6433.
* **ESAL (Equivalent Single Axle Load):** AASHTO standard conversion of mixed vehicular traffic into equivalent passes of an 18,000-pound (80 kN) single axle.
* **IRI (International Roughness Index):** Metric of longitudinal road roughness in meters per kilometer (m/km); higher values indicate rougher roads.
* **HSR (Highway Schedule of Rates):** Official annual engineering cost schedule published by the Ministry of Transport & Highways of Sri Lanka.
* **RRL (Remaining Road Life):** Time in months/years remaining before an asset requires major structural overhaul.
* **TreeSHAP / Feature Attribution:** Cooperative game theory method applied to decision trees to explain individual model prediction outputs.
