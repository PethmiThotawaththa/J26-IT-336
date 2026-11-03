"""
models.py
---------
Model Benchmarks, Evaluation Metrics, and Training Management REST API.
"""

import os
import json
import math
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.app.core.config import settings
from backend.app.ml.train import train_and_evaluate_all
from backend.app.ml.explainability import get_global_feature_importance

router = APIRouter(prefix="/models", tags=["Models"])

def sanitize_json(obj):
    """Recursively replaces float('nan') or float('inf') with None/0.0 for strict JSON compliance."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    return obj

@router.get("/evaluation")
def get_model_evaluation():
    """
    Returns authentic academic benchmark matrix comparing:
    - Regression: Ridge Baseline, Decision Tree, Random Forest, XGBoost, LightGBM (MAE, RMSE, R2)
    - Classification: Logistic Regression, Decision Tree, Random Forest, XGBoost, LightGBM (Accuracy, Precision, Recall, F1)
    - Multi-Horizon Metrics (3m, 6m, 12m, 24m)
    """
    results_path = os.path.join(settings.EXPERIMENTS_DIR, "evaluation_results.json")
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Model evaluation results not found. Trigger training first.")
        
    with open(results_path, "r") as f:
        data = json.load(f)
        
    return sanitize_json(data)

@router.get("/feature-importance")
def get_features_importance():
    """Returns global feature importance rankings across ensemble models."""
    return {"feature_importances": get_global_feature_importance()}

@router.post("/train")
def trigger_training(background_tasks: BackgroundTasks):
    """Triggers background model retraining and benchmarking on latest dataset."""
    background_tasks.add_task(train_and_evaluate_all)
    return {
        "status": "ACCEPTED",
        "message": "ML model training and evaluation experiment launched in background."
    }
