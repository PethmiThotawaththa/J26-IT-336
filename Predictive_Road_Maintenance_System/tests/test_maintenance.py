import pytest
from backend.app.services.maintenance import recommend_maintenance_action, HSR_RATES

def test_hsr_rates_defined():
    assert "ROUTINE_CLEARANCE" in HSR_RATES
    assert "CRACK_SEALING" in HSR_RATES
    assert "SLURRY_SEAL" in HSR_RATES
    assert "MICRO_SURFACING" in HSR_RATES
    assert "MILL_AND_OVERLAY" in HSR_RATES
    assert "FULL_RECONSTRUCTION" in HSR_RATES

def test_recommendation_for_good_condition():
    rec = recommend_maintenance_action(pci=90.0)
    assert rec["priority"] == "P3"
    assert "Routine Maintenance" in rec["action"]
    assert rec["urgency_days"] >= 90

def test_recommendation_for_critical_condition():
    rec = recommend_maintenance_action(pci=35.0, crack_density_pct=35.0, pothole_count=5)
    assert rec["priority"] == "P1"
    assert "Full-Depth Base Stabilization" in rec["action"]
    assert rec["urgency_days"] <= 14

def test_capex_rescue_positive():
    rec = recommend_maintenance_action(pci=65.0, crack_density_pct=15.0)
    assert rec["preventive_savings_lkr"] > 0
    assert rec["roi_percent"] > 0
