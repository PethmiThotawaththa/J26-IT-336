import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["models_loaded"] is True
    assert data["project_id"] == "J26-IT-336"

def test_dashboard_summary_endpoint():
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "structural_health_index" in data
    assert data["total_sections_count"] > 0
    assert len(data["corridors"]) >= 6

def test_roads_listing_and_detail():
    # List roads
    res = client.get("/api/roads?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert len(data["sections"]) == 5
    
    first_id = data["sections"][0]["id"]
    # Detail
    res_detail = client.get(f"/api/roads/{first_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["section"]["id"] == first_id

def test_prognosis_prediction():
    payload = {
        "current_pci": 68.0,
        "daily_esal": 2000.0,
        "annual_precipitation_mm": 2674.0,
        "historical_decay_rate_annual": 3.8,
        "crack_density_pct": 12.0,
        "pothole_count": 1,
        "rut_depth_mm": 8.0
    }
    res = client.post("/api/predict/prognosis", json=payload)
    assert res.status_code == 200
    prog = res.json()
    assert "predicted_condition_horizons" in prog
    assert "remaining_road_life" in prog
    assert "maintenance_recommendation" in prog
    assert "explainability" in prog

def test_maintenance_queue_and_gantt():
    res_q = client.get("/api/maintenance/queue?limit=10")
    assert res_q.status_code == 200
    assert len(res_q.json()["queue"]) > 0
    
    res_g = client.get("/api/maintenance/gantt")
    assert res_g.status_code == 200
    assert len(res_g.json()["schedule"]) == 14

def test_models_evaluation_endpoint():
    res = client.get("/api/models/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert "regression_benchmarks" in data
    assert "classification_benchmarks" in data
    assert "feature_importances" in data
