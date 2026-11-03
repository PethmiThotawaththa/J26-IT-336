"""
integration.py
--------------
Inter-Component Integration Adapter & Mock Fixtures for Component 4.
Provides standardized contract interfaces for receiving detection & condition inputs
from Component 1 (Damage Detection), Component 2 (Severity Assessment), and Component 3 (Repair Prioritization).
"""

from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import (
    ComponentIntegrationPayload,
    ComponentIntegrationResponse
)
from backend.app.models.database import db_query_one
from backend.app.ml.models import model_service

router = APIRouter(prefix="/integration", tags=["Integration"])

# Mock integration test fixtures simulating upstream component payloads
MOCK_INTEGRATION_FIXTURES = [
    {
        "source_component": "Component_1_Damage_Detection",
        "corridor_id": "B047",
        "chainage_km": 3.8,
        "assessed_pci": 51.4,
        "distresses": [
            {"damage_type": "Severe Longitudinal Fatigue Cracking", "severity": "High", "confidence": 0.94, "area_sqm": 4.5, "depth_mm": 0.0},
            {"damage_type": "Pothole Breach", "severity": "High", "confidence": 0.89, "area_sqm": 0.45, "depth_mm": 48.0}
        ],
        "component_3_priority_rank": 1,
        "description": "Simulation: Component 1 drone/camera detected alligator cracks and deep pothole on B047."
    },
    {
        "source_component": "Component_2_Severity_Assessment",
        "corridor_id": "B435",
        "chainage_km": 1.2,
        "assessed_pci": 62.0,
        "distresses": [
            {"damage_type": "Moderate Rutting & Surface Polish", "severity": "Medium", "confidence": 0.91, "area_sqm": 12.0, "depth_mm": 16.5}
        ],
        "component_3_priority_rank": 3,
        "description": "Simulation: Component 2 severity rating classified section as Fair (PCI 62) with wheel rutting."
    },
    {
        "source_component": "Component_3_Repair_Prioritization",
        "corridor_id": "B174",
        "chainage_km": 5.4,
        "assessed_pci": 76.5,
        "distresses": [
            {"damage_type": "Hairline Thermal Cracking", "severity": "Low", "confidence": 0.87, "area_sqm": 2.1, "depth_mm": 0.0}
        ],
        "component_3_priority_rank": 7,
        "description": "Simulation: Component 3 scheduled routine priority on B174."
    }
]

@router.get("/mock-fixtures")
def get_mock_fixtures():
    """Returns sample payloads representing data formats received from other research components."""
    return {"fixtures": MOCK_INTEGRATION_FIXTURES}

@router.post("/adapter/comp1-3", response_model=ComponentIntegrationResponse)
def ingest_component_payload(payload: ComponentIntegrationPayload):
    """
    Adapter endpoint accepting payloads from Component 1, 2, or 3.
    Matches road corridor and chainage against the RDA spatial ledger,
    retrieves environmental and traffic loading factors,
    and runs the AI predictive maintenance engine.
    """
    # 1. Match section in database
    sec = db_query_one("""
    SELECT * FROM road_sections 
    WHERE corridor_id = ? AND ? >= start_chainage_km AND ? <= end_chainage_km
    LIMIT 1;
    """, (payload.corridor_id, payload.chainage_km, payload.chainage_km))
    
    if not sec:
        # Fallback to closest section in that corridor
        sec = db_query_one("""
        SELECT * FROM road_sections 
        WHERE corridor_id = ? 
        ORDER BY ABS(start_chainage_km - ?) ASC 
        LIMIT 1;
        """, (payload.corridor_id, payload.chainage_km))
        
    if not sec:
        raise HTTPException(status_code=404, detail=f"Corridor '{payload.corridor_id}' not found in spatial network.")
        
    # 2. Extract distresses from payload
    pothole_count = sum(1 for d in payload.distresses if "pothole" in d.damage_type.lower())
    crack_pct = sum(d.area_sqm or 1.0 for d in payload.distresses if "crack" in d.damage_type.lower()) / 7.0 # Normalize by 700sqm
    crack_pct = min(max(crack_pct, 2.0), 45.0)
    
    # 3. Construct input feature vector
    input_features = {
        "section_id": sec["id"],
        "current_pci": payload.assessed_pci,
        "pavement_age_years": sec["pavement_age_years"],
        "structural_number": sec["structural_number"],
        "aadt": sec["aadt"],
        "daily_esal": sec["daily_esal"],
        "heavy_vehicle_pct": sec["heavy_vehicle_pct"],
        "annual_precipitation_mm": sec["annual_precipitation_mm"],
        "mean_temp_c": 28.0,
        "mean_diurnal_range_c": 4.5,
        "monsoon_risk_factor": sec["monsoon_risk_factor"],
        "historical_decay_rate_annual": sec["historical_decay_rate_annual"],
        "crack_density_pct": round(crack_pct, 2),
        "pothole_count": pothole_count,
        "iri_roughness": sec["iri_roughness"],
        "rut_depth_mm": sec["rut_depth_mm"]
    }
    
    # 4. Run prognosis
    prognosis = model_service.generate_full_prognosis(input_features)
    
    notes = (
        f"Successfully ingested telemetry from {payload.source_component}. "
        f"Matched to RDA section {sec['id']} (Ch {sec['start_chainage_km']} - {sec['end_chainage_km']} km). "
        f"Applied local traffic load ({sec['daily_esal']:.0f} ESAL/day) and monsoon factor ({sec['monsoon_risk_factor']})."
    )
    
    return {
        "status": "SUCCESS",
        "matched_section_id": sec["id"],
        "corridor_name": sec["corridor_name"],
        "prognosis": prognosis,
        "integration_notes": notes
    }
