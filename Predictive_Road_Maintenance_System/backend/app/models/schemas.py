"""
schemas.py
----------
Pydantic v2 Data Transfer Objects (DTOs) and Validation Schemas for Component 4.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# -------------------------------------------------------------
# Road Corridor & Section Schemas
# -------------------------------------------------------------
class RoadCorridorBase(BaseModel):
    id: str
    name: str
    road_class: str
    total_length_km: float
    district: str
    lanes: int
    aadt: int
    daily_esal: float
    heavy_vehicle_pct: float

class RoadSectionItem(BaseModel):
    id: str
    corridor_id: str
    corridor_name: Optional[str] = None
    start_chainage_km: float
    end_chainage_km: float
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    altitude_m: float
    current_pci: float
    historical_decay_rate_annual: float
    crack_density_pct: float
    pothole_count: int
    iri_roughness: float
    rut_depth_mm: float
    daily_esal: float
    pavement_age_years: float

class RoadSectionDetail(RoadSectionItem):
    surface_type: str
    structural_number: float
    aadt: int
    heavy_vehicle_pct: float
    annual_precipitation_mm: float
    monsoon_risk_factor: float
    historical_pci_1yr_ago: float

# -------------------------------------------------------------
# Prediction Request & Response Schemas
# -------------------------------------------------------------
class ConditionPredictionRequest(BaseModel):
    section_id: Optional[str] = "CUSTOM"
    current_pci: float = Field(..., ge=0.0, le=100.0, description="Current Pavement Condition Index")
    pavement_age_years: float = Field(4.0, ge=0.0, le=30.0)
    structural_number: float = Field(3.8, ge=1.5, le=8.0)
    aadt: int = Field(20000, ge=100)
    daily_esal: float = Field(1500.0, ge=10.0)
    heavy_vehicle_pct: float = Field(5.0, ge=0.0, le=60.0)
    annual_precipitation_mm: float = Field(2674.0, ge=200.0)
    mean_temp_c: float = Field(28.0, ge=5.0, le=50.0)
    mean_diurnal_range_c: float = Field(4.5, ge=1.0, le=25.0)
    monsoon_risk_factor: float = Field(1.78, ge=0.2, le=3.0)
    historical_decay_rate_annual: float = Field(3.2, ge=0.1, le=20.0)
    crack_density_pct: float = Field(5.0, ge=0.0, le=100.0)
    pothole_count: int = Field(0, ge=0, le=50)
    iri_roughness: float = Field(2.2, ge=0.5, le=15.0)
    rut_depth_mm: float = Field(3.5, ge=0.0, le=50.0)

class RemainingLifeResponse(BaseModel):
    current_pci: float
    condition_state: str
    urgency_level: str
    effective_monthly_decay_pci: float
    rrl_rehabilitation_months: int
    rrl_rehabilitation_days: int
    rrl_failure_months: int
    rrl_failure_days: int
    rehab_threshold_pci: float
    failure_threshold_pci: float
    assumptions: List[str]

class MaintenanceRecommendationResponse(BaseModel):
    priority: str
    action: str
    hsr_item_code: str
    hsr_description: str
    urgency_days: int
    estimated_cost_lkr: float
    emergency_rebuild_cost_lkr: float
    preventive_savings_lkr: float
    roi_percent: float
    life_extension_years: float
    rationale: str
    standards_reference: str

class FullPrognosisResponse(BaseModel):
    section_id: str
    current_pci: float
    predicted_condition_horizons: Dict[str, float]
    predicted_risk_category_12m: str
    remaining_road_life: RemainingLifeResponse
    deterioration_curve_36m: List[Dict[str, Any]]
    maintenance_recommendation: MaintenanceRecommendationResponse
    explainability: Dict[str, Any]

# -------------------------------------------------------------
# Component 1-3 Integration Adapter Schemas
# -------------------------------------------------------------
class DetectedDamageItem(BaseModel):
    damage_type: str = Field(..., example="Alligator Cracking")
    severity: str = Field(..., example="Medium")
    confidence: float = Field(..., ge=0.0, le=1.0, example=0.92)
    area_sqm: Optional[float] = 1.5
    depth_mm: Optional[float] = 0.0

class ComponentIntegrationPayload(BaseModel):
    source_component: str = Field("Component_2_Severity_Assessment", example="Component_2_Severity_Assessment")
    corridor_id: str = Field(..., example="B047")
    chainage_km: float = Field(..., example=3.5)
    assessed_pci: float = Field(..., ge=0.0, le=100.0, example=64.2)
    distresses: List[DetectedDamageItem] = []
    component_3_priority_rank: Optional[int] = None

class ComponentIntegrationResponse(BaseModel):
    status: str
    matched_section_id: str
    corridor_name: str
    prognosis: FullPrognosisResponse
    integration_notes: str
