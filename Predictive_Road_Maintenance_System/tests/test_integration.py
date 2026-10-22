import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_mock_fixtures_retrieval():
    res = client.get("/api/integration/mock-fixtures")
    assert res.status_code == 200
    fixtures = res.json()["fixtures"]
    assert len(fixtures) >= 3
    assert fixtures[0]["corridor_id"] == "B047"

def test_component_integration_adapter_payload():
    payload = {
        "source_component": "Component_1_Damage_Detection",
        "corridor_id": "B047",
        "chainage_km": 3.8,
        "assessed_pci": 51.4,
        "distresses": [
            {
                "damage_type": "Severe Longitudinal Fatigue Cracking",
                "severity": "High",
                "confidence": 0.94,
                "area_sqm": 4.5,
                "depth_mm": 0.0
            },
            {
                "damage_type": "Pothole Breach",
                "severity": "High",
                "confidence": 0.89,
                "area_sqm": 0.45,
                "depth_mm": 48.0
            }
        ],
        "component_3_priority_rank": 1
    }
    
    res = client.post("/api/integration/adapter/comp1-3", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "B047" in data["matched_section_id"]
    assert "prognosis" in data
    assert "predicted_condition_horizons" in data["prognosis"]
    assert "maintenance_recommendation" in data["prognosis"]

def test_invalid_corridor_fallback():
    # If corridor is unknown, it should return 404
    payload = {
        "source_component": "Component_2",
        "corridor_id": "UNKNOWN_ROAD_999",
        "chainage_km": 1.0,
        "assessed_pci": 70.0,
        "distresses": []
    }
    res = client.post("/api/integration/adapter/comp1-3", json=payload)
    assert res.status_code == 404
