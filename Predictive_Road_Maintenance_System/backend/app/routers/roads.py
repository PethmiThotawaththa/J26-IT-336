"""
roads.py
--------
Road Corridors and Sections REST API for Component 4.
Provides spatial coordinates, inspection telemetry, and decay simulations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.app.models.database import db_query_all, db_query_one
from backend.app.ml.rrl_engine import generate_deterioration_curve, calculate_remaining_road_life

router = APIRouter(prefix="/roads", tags=["Roads"])

@router.get("")
def list_roads(
    corridor_id: Optional[str] = Query(None, description="Filter by corridor ID, e.g. B047"),
    limit: int = Query(1000, ge=1, le=2000),
    offset: int = Query(0, ge=0)
):
    """Lists road sections with their current condition, GPS coordinates, and distress scores."""
    if corridor_id:
        sections = db_query_all("""
        SELECT * FROM road_sections 
        WHERE corridor_id = ? 
        ORDER BY start_chainage_km ASC 
        LIMIT ? OFFSET ?;
        """, (corridor_id, limit, offset))
    else:
        sections = db_query_all("""
        SELECT * FROM road_sections 
        ORDER BY corridor_id, start_chainage_km ASC 
        LIMIT ? OFFSET ?;
        """, (limit, offset))
        
    return {
        "count": len(sections),
        "limit": limit,
        "offset": offset,
        "sections": sections
    }

@router.get("/corridors")
def list_corridors():
    """Lists summary of all 6 RDA road corridors."""
    corridors = db_query_all("""
    SELECT 
        c.*,
        AVG(s.current_pci) as avg_pci,
        COUNT(s.id) as section_count
    FROM road_corridors c
    LEFT JOIN road_sections s ON c.id = s.corridor_id
    GROUP BY c.id;
    """)
    return {"corridors": corridors}

@router.get("/{section_id}")
def get_road_section_detail(section_id: str):
    """Retrieves deep telemetry inspection for a specific 100m road section."""
    sec = db_query_one("SELECT * FROM road_sections WHERE id = ?", (section_id,))
    if not sec:
        raise HTTPException(status_code=404, detail=f"Road section '{section_id}' not found.")
        
    # Get work order if exists
    wo = db_query_one("SELECT * FROM maintenance_work_orders WHERE section_id = ?", (section_id,))
    
    # Calculate RRL
    rrl = calculate_remaining_road_life(
        current_pci=sec["current_pci"],
        annual_decay_rate=sec["historical_decay_rate_annual"],
        daily_esal=sec["daily_esal"],
        monsoon_factor=sec["monsoon_risk_factor"]
    )
    
    return {
        "section": sec,
        "work_order": wo,
        "remaining_road_life": rrl
    }

@router.get("/{section_id}/decay-curve")
def get_road_decay_curve(
    section_id: str,
    intervention_month: int = Query(12, ge=1, le=36),
    traffic_multiplier: float = Query(1.0, ge=0.5, le=3.0),
    weather_multiplier: float = Query(1.0, ge=0.5, le=3.0)
):
    """
    Computes dynamic 36-month deterioration curve comparing Status Quo vs Proactive Intervention
    with configurable traffic load and monsoon weather scenario modifiers.
    """
    sec = db_query_one("SELECT * FROM road_sections WHERE id = ?", (section_id,))
    if not sec:
        raise HTTPException(status_code=404, detail=f"Road section '{section_id}' not found.")
        
    decay_curve = generate_deterioration_curve(
        current_pci=sec["current_pci"],
        annual_decay_rate=sec["historical_decay_rate_annual"] * weather_multiplier,
        daily_esal=sec["daily_esal"] * traffic_multiplier,
        monsoon_factor=sec["monsoon_risk_factor"] * weather_multiplier,
        intervention_month=intervention_month,
        intervention_type="Mill & Overlay"
    )
    
    return {
        "section_id": section_id,
        "current_pci": sec["current_pci"],
        "intervention_month": intervention_month,
        "traffic_multiplier": traffic_multiplier,
        "weather_multiplier": weather_multiplier,
        "trajectory": decay_curve
    }

@router.get("/{section_id}/history")
def get_road_inspection_history(section_id: str):
    """Retrieves longitudinal historical survey logs for this section."""
    surveys = db_query_all("""
    SELECT * FROM inspection_surveys 
    WHERE section_id = ? 
    ORDER BY survey_date ASC;
    """, (section_id,))
    
    return {
        "section_id": section_id,
        "history_count": len(surveys),
        "inspections": surveys
    }
