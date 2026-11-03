"""
models.py
---------
Model Inference and Lifecycle Service for Component 4.
Loads versioned model artifacts and executes prediction pipelines for:
- Discrete prediction horizons (3, 6, 12, 24 months)
- Risk classification (Good, Satisfactory, Fair, Poor, Critical)
- Comprehensive Pavement Prognosis (Condition + RRL + Maintenance + XAI)
"""

import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

from backend.app.core.config import settings
from backend.app.ml.features import (
    RAW_FEATURE_COLUMNS,
    load_pipeline
)
from backend.app.ml.rrl_engine import (
    calculate_remaining_road_life,
    generate_deterioration_curve
)
from backend.app.services.maintenance import recommend_maintenance_action
from backend.app.ml.explainability import explain_road_prediction

class ModelService:
    def __init__(self):
        self.preprocessor = None
        self.production_regressor = None
        self.production_classifier = None
        self.horizon_models = {}
        self.is_loaded = False
        self.load_models()
        
    def load_models(self):
        try:
            preprocessor_path = os.path.join(settings.MODELS_DIR, "preprocessor.joblib")
            if os.path.exists(preprocessor_path):
                self.preprocessor = load_pipeline(preprocessor_path)
                
            reg_path = os.path.join(settings.MODELS_DIR, "production_regressor.joblib")
            if os.path.exists(reg_path):
                self.production_regressor = joblib.load(reg_path)
                
            clf_path = os.path.join(settings.MODELS_DIR, "production_classifier.joblib")
            if os.path.exists(clf_path):
                self.production_classifier = joblib.load(clf_path)
                
            # Multi-horizon regressors
            for h in ["3m", "6m", "12m", "24m"]:
                h_path = os.path.join(settings.MODELS_DIR, f"xgb_regressor_{h}.joblib")
                if os.path.exists(h_path):
                    self.horizon_models[h] = joblib.load(h_path)
                    
            self.is_loaded = (self.preprocessor is not None and len(self.horizon_models) > 0)
            print(f"[ModelService] Models successfully loaded. Ready: {self.is_loaded}")
        except Exception as e:
            print(f"[ModelService] Warning: Failed to load some model artifacts: {e}")
            self.is_loaded = False
            
    def _prepare_input_df(self, raw_input: Dict[str, Any]) -> pd.DataFrame:
        """Constructs DataFrame aligned with RAW_FEATURE_COLUMNS."""
        row = {}
        for col in RAW_FEATURE_COLUMNS:
            row[col] = [raw_input.get(col, 0.0)]
        return pd.DataFrame(row)

    def predict_multi_horizon(self, raw_input: Dict[str, Any]) -> Dict[str, float]:
        """Predicts condition PCI across 3, 6, 12, and 24-month horizons."""
        df_in = self._prepare_input_df(raw_input)
        X_proc = self.preprocessor.transform(df_in)
        
        predictions = {}
        for h in ["3m", "6m", "12m", "24m"]:
            if h in self.horizon_models:
                pred_val = float(self.horizon_models[h].predict(X_proc)[0])
                predictions[h] = round(float(np.clip(pred_val, 0.0, 100.0)), 1)
            else:
                # Fallback to calibrated annual deterioration rate if model artifact is missing
                cur = float(raw_input.get("current_pci", 75.0))
                rate = float(raw_input.get("historical_decay_rate_annual", 3.0))
                factor = {"3m": 0.25, "6m": 0.5, "12m": 1.0, "24m": 2.0}.get(h, 1.0)
                predictions[h] = round(max(cur - (rate * factor), 5.0), 1)
                
        return predictions

    def predict_risk_category(self, raw_input: Dict[str, Any]) -> str:
        """Predicts risk category classification."""
        risk_classes = ["Critical", "Poor", "Fair", "Satisfactory", "Good"]
        if self.production_classifier is not None:
            df_in = self._prepare_input_df(raw_input)
            X_proc = self.preprocessor.transform(df_in)
            idx = int(self.production_classifier.predict(X_proc)[0])
            return risk_classes[idx] if 0 <= idx < len(risk_classes) else "Fair"
        else:
            # Rule-based fallback based on predicted 12m PCI
            pci = float(raw_input.get("current_pci", 75.0))
            if pci >= 85: return "Good"
            if pci >= 70: return "Satisfactory"
            if pci >= 55: return "Fair"
            if pci >= 40: return "Poor"
            return "Critical"

    def generate_full_prognosis(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes complete predictive maintenance analysis:
        1. Multi-horizon condition prediction (3m, 6m, 12m, 24m)
        2. Risk classification
        3. Remaining Road Life (RRL) calculation
        4. Deterioration decay curves (36 calendar months)
        5. Preventive maintenance recommendation & HSR cost
        6. Explainable AI feature attribution
        """
        cur_pci = float(raw_input.get("current_pci", 75.0))
        decay_rate = float(raw_input.get("historical_decay_rate_annual", 3.2))
        esal = float(raw_input.get("daily_esal", 1500.0))
        monsoon = float(raw_input.get("monsoon_risk_factor", 1.2))
        cracks = float(raw_input.get("crack_density_pct", 5.0))
        potholes = int(raw_input.get("pothole_count", 0))
        rut = float(raw_input.get("rut_depth_mm", 4.0))
        
        # 1. Condition predictions
        horizon_preds = self.predict_multi_horizon(raw_input)
        risk_cat = self.predict_risk_category(raw_input)
        
        # 2. Remaining Road Life
        rrl_data = calculate_remaining_road_life(
            current_pci=cur_pci,
            annual_decay_rate=decay_rate,
            daily_esal=esal,
            monsoon_factor=monsoon
        )
        
        # 3. Deterioration curve
        decay_curve = generate_deterioration_curve(
            current_pci=cur_pci,
            annual_decay_rate=decay_rate,
            daily_esal=esal,
            monsoon_factor=monsoon,
            intervention_month=11
        )
        
        # 4. Maintenance Recommendation & Budget
        maint_data = recommend_maintenance_action(
            pci=cur_pci,
            crack_density_pct=cracks,
            pothole_count=potholes,
            rut_depth_mm=rut,
            daily_esal=esal
        )
        
        # 5. Explainable AI
        xai_data = explain_road_prediction(raw_input)
        
        return {
            "section_id": raw_input.get("section_id", "CUSTOM-SECTION"),
            "current_pci": cur_pci,
            "predicted_condition_horizons": horizon_preds,
            "predicted_risk_category_12m": risk_cat,
            "remaining_road_life": rrl_data,
            "deterioration_curve_36m": decay_curve,
            "maintenance_recommendation": maint_data,
            "explainability": xai_data
        }

# Global singleton model service
model_service = ModelService()
