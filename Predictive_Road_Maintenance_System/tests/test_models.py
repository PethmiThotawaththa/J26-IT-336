import pytest
from backend.app.ml.models import model_service
from backend.app.ml.rrl_engine import calculate_remaining_road_life, generate_deterioration_curve

def test_model_service_loaded():
    assert model_service.is_loaded is True
    assert model_service.preprocessor is not None
    assert len(model_service.horizon_models) >= 4

def test_multi_horizon_prediction_monotonic_decay():
    input_data = {
        "current_pci": 75.0,
        "pavement_age_years": 4.0,
        "structural_number": 3.8,
        "aadt": 25000,
        "daily_esal": 1800.0,
        "heavy_vehicle_pct": 5.0,
        "annual_precipitation_mm": 2600.0,
        "mean_temp_c": 28.0,
        "mean_diurnal_range_c": 4.5,
        "monsoon_risk_factor": 1.7,
        "historical_decay_rate_annual": 3.5,
        "crack_density_pct": 8.0,
        "pothole_count": 0,
        "iri_roughness": 2.2,
        "rut_depth_mm": 4.0
    }
    
    preds = model_service.predict_multi_horizon(input_data)
    assert "3m" in preds
    assert "6m" in preds
    assert "12m" in preds
    assert "24m" in preds
    
    # Condition must degrade over time
    assert preds["3m"] >= preds["6m"] - 1.0 # Within minor statistical noise
    assert preds["6m"] >= preds["12m"] - 1.0
    assert preds["12m"] >= preds["24m"] - 1.0

def test_rrl_calculation_bounds():
    # Test healthy road
    rrl_healthy = calculate_remaining_road_life(current_pci=85.0, annual_decay_rate=3.0)
    assert rrl_healthy["rrl_rehabilitation_months"] > 60
    assert rrl_healthy["condition_state"] == "Good"
    
    # Test failed road
    rrl_failed = calculate_remaining_road_life(current_pci=35.0, annual_decay_rate=4.0)
    assert rrl_failed["rrl_rehabilitation_months"] == 0
    assert rrl_failed["rrl_failure_months"] == 0
    assert rrl_failed["condition_state"] == "Critical"

def test_deterioration_curve_generation():
    curve = generate_deterioration_curve(
        current_pci=70.0,
        annual_decay_rate=3.5,
        intervention_month=11
    )
    assert len(curve) == 37 # Months 0 to 36
    assert curve[0]["month"] == 0
    assert curve[0]["status_quo_pci"] == 70.0
    # Status quo at Month 36 must be significantly lower than Month 0
    assert curve[-1]["status_quo_pci"] < 70.0
    # Proactive intervention should elevate condition
    assert curve[12]["mitigated_pci"] > curve[10]["mitigated_pci"]
