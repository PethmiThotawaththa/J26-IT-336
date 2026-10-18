"""
predict.py
----------
Inference REST Endpoints for Condition Forecasting, RRL, and Maintenance.
"""

from fastapi import APIRouter
from backend.app.models.schemas import (
    ConditionPredictionRequest,
    RemainingLifeResponse,
    MaintenanceRecommendationResponse,
    FullPrognosisResponse
)
from backend.app.ml.models import model_service
from backend.app.ml.rrl_engine import calculate_remaining_road_life
from backend.app.services.maintenance import recommend_maintenance_action

router = APIRouter(prefix="/predict", tags=["Predictions"])

@router.post("/condition")
def predict_road_condition(req: ConditionPredictionRequest):
    """Predicts future pavement condition across 3, 6, 12, and 24-month horizons."""
    data_dict = req.model_dump()
    predictions = model_service.predict_multi_horizon(data_dict)
    risk_category = model_service.predict_risk_category(data_dict)
    
    return {
        "section_id": req.section_id,
        "current_pci": req.current_pci,
        "predicted_horizons": predictions,
        "predicted_risk_category_12m": risk_category
    }

@router.post("/remaining-life")
def estimate_remaining_road_life(req: ConditionPredictionRequest):
    """Calculates Remaining Useful Road Life (RRL) in months and days to critical thresholds."""
    rrl = calculate_remaining_road_life(
        current_pci=req.current_pci,
        annual_decay_rate=req.historical_decay_rate_annual,
        daily_esal=req.daily_esal,
        monsoon_factor=req.monsoon_risk_factor
    )
    return rrl

@router.post("/maintenance")
def generate_maintenance_recommendation(req: ConditionPredictionRequest):
    """Generates preventive maintenance recommendation with RDA HSR 2025 unit costing."""
    rec = recommend_maintenance_action(
        pci=req.current_pci,
        crack_density_pct=req.crack_density_pct,
        pothole_count=req.pothole_count,
        rut_depth_mm=req.rut_depth_mm,
        daily_esal=req.daily_esal
    )
    return rec

@router.post("/prognosis")
def generate_full_prognosis(req: ConditionPredictionRequest):
    """
    Unified end-to-end endpoint: executes multi-horizon prediction, RRL estimation,
    maintenance recommendation, and localized Explainable AI attribution.
    """
    data_dict = req.model_dump()
    prognosis = model_service.generate_full_prognosis(data_dict)
    return prognosis
