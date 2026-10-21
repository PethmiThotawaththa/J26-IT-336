"""
maintenance.py
--------------
Preventive Maintenance Recommendation & Budgeting Engine for Component 4.
Translates predicted pavement condition, distress scores, and remaining life
into AASHTO-aligned engineering interventions, matched with RDA Highway Schedule
of Rates (HSR 2025) unit rates and Capex rescue calculations.
"""

from typing import Dict, Any, List

# RDA Sri Lanka HSR 2025 Standard Rates (in LKR)
# Based on RDA Engineering Division Schedule of Rates Summary
HSR_RATES = {
    "ROUTINE_CLEARANCE": {"code": "HSR-40", "desc": "Drainage and shoulder clearing", "unit": "sq.m", "rate_lkr": 8.60},
    "CRACK_SEALING": {"code": "HSR-43", "desc": "Bituminous crack sealing & mastic fill", "unit": "m", "rate_lkr": 109.55},
    "SLURRY_SEAL": {"code": "HSR-51", "desc": "Emulsified bitumen slurry seal 6mm", "unit": "sq.m", "rate_lkr": 640.15},
    "MICRO_SURFACING": {"code": "HSR-53", "desc": "Polymer-modified micro-surfacing 10mm", "unit": "sq.m", "rate_lkr": 591.20},
    "POTHOLE_PATCHING": {"code": "HSR-1", "desc": "Hot mix asphalt concrete premix patching", "unit": "m.ton", "rate_lkr": 23476.00},
    "MILL_AND_OVERLAY": {"code": "HSR-75", "desc": "Cold milling 50mm + Dense asphalt overlay", "unit": "sq.m", "rate_lkr": 3356.56},
    "FULL_RECONSTRUCTION": {"code": "HSR-71", "desc": "Full-depth base stabilization & reconstruction", "unit": "sq.m", "rate_lkr": 18526.49}
}

STANDARD_SECTION_AREA_SQM = 700.0 # 100m length x 7.0m standard 2-lane carriageway width

def recommend_maintenance_action(
    pci: float,
    crack_density_pct: float = 5.0,
    pothole_count: int = 0,
    rut_depth_mm: float = 0.0,
    daily_esal: float = 1500.0,
    section_area_sqm: float = STANDARD_SECTION_AREA_SQM
) -> Dict[str, Any]:
    """
    Evaluates condition metrics to determine the optimal engineering intervention,
    associated HSR cost, execution urgency, and economic deferral penalty.
    """
    # 1. Decision logic based on PCI & specific distress triggers
    if pci >= 85.0:
        priority = "P3"
        urgency_days = 180
        action = "Routine Maintenance & Drainage Clearance"
        hsr_item = HSR_RATES["ROUTINE_CLEARANCE"]
        cost_lkr = section_area_sqm * hsr_item["rate_lkr"]
        rationale = "Pavement in Good condition. Routine drainage clearing to prevent moisture accumulation."
        life_extension_years = 1.0
        
    elif pci >= 70.0:
        if crack_density_pct > 12.0:
            priority = "P2"
            urgency_days = 60
            action = "Crack Sealing & High-Modulus Mastic Seal"
            hsr_item = HSR_RATES["CRACK_SEALING"]
            cost_lkr = (section_area_sqm * (crack_density_pct / 100.0) * 1.5) * hsr_item["rate_lkr"]
            rationale = "Moderate fatigue cracking observed. Seal cracks to prevent sub-base water penetration."
            life_extension_years = 3.5
        else:
            priority = "P3"
            urgency_days = 90
            action = "Continuous Polymer Slurry Seal"
            hsr_item = HSR_RATES["SLURRY_SEAL"]
            cost_lkr = section_area_sqm * hsr_item["rate_lkr"]
            rationale = "Satisfactory condition with surface oxidation. Apply slurry seal to waterproof surface layer."
            life_extension_years = 4.0

    elif pci >= 55.0:
        if pothole_count > 2 or rut_depth_mm > 15.0:
            priority = "P1"
            urgency_days = 21
            action = "Cold Milling & Micro-surfacing Fiber Injection"
            hsr_item = HSR_RATES["MICRO_SURFACING"]
            # Add patching cost for potholes
            patching_cost = pothole_count * 0.45 * (HSR_RATES["POTHOLE_PATCHING"]["rate_lkr"] / 10.0)
            cost_lkr = (section_area_sqm * hsr_item["rate_lkr"]) + patching_cost
            rationale = "Fair condition with active pothole formation. Fiber micro-surfacing required to arrest structural decay."
            life_extension_years = 5.5
        else:
            priority = "P2"
            urgency_days = 45
            action = "Polymer-Modified Micro-Surfacing"
            hsr_item = HSR_RATES["MICRO_SURFACING"]
            cost_lkr = section_area_sqm * hsr_item["rate_lkr"]
            rationale = "Surface raveling and moderate friction decay. Micro-surfacing restores ride quality and skid resistance."
            life_extension_years = 5.0

    elif pci >= 40.0:
        priority = "P1"
        urgency_days = 14
        action = "Cold Milling (50mm) + Dense Asphalt Overlay"
        hsr_item = HSR_RATES["MILL_AND_OVERLAY"]
        cost_lkr = section_area_sqm * hsr_item["rate_lkr"]
        rationale = "Poor structural condition. Milling existing cracked wearing layer and placing new asphalt concrete overlay."
        life_extension_years = 8.0

    else: # PCI < 40
        priority = "P1"
        urgency_days = 7
        action = "Full-Depth Base Stabilization & Reconstruction"
        hsr_item = HSR_RATES["FULL_RECONSTRUCTION"]
        cost_lkr = section_area_sqm * hsr_item["rate_lkr"]
        rationale = "Critical failure! Sub-base shear and structural collapse imminent. Full-depth reconstruction required."
        life_extension_years = 15.0

    # 2. Economic Deferral Penalty Analysis
    # If proactive treatment is deferred, the road decays to full reconstruction
    emergency_rebuild_cost = section_area_sqm * HSR_RATES["FULL_RECONSTRUCTION"]["rate_lkr"]
    preventive_savings = max(emergency_rebuild_cost - cost_lkr, 0.0)
    roi_percent = round((preventive_savings / max(cost_lkr, 1.0)) * 100.0, 1)

    return {
        "priority": priority,
        "action": action,
        "hsr_item_code": hsr_item["code"],
        "hsr_description": hsr_item["desc"],
        "urgency_days": urgency_days,
        "estimated_cost_lkr": round(cost_lkr, 2),
        "emergency_rebuild_cost_lkr": round(emergency_rebuild_cost, 2),
        "preventive_savings_lkr": round(preventive_savings, 2),
        "roi_percent": roi_percent,
        "life_extension_years": life_extension_years,
        "rationale": rationale,
        "standards_reference": "AASHTO Maintenance Guidelines & RDA HSR 2025"
    }

def generate_priority_dispatch_queue(road_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks maintenance work orders into an operational priority dispatch queue.
    """
    queue = []
    for sec in road_sections:
        pci = sec.get("current_pci", 75.0)
        cracks = sec.get("crack_density_pct", 5.0)
        potholes = sec.get("pothole_count", 0)
        rut = sec.get("rut_depth_mm", 0.0)
        esal = sec.get("daily_esal", 1500.0)
        
        rec = recommend_maintenance_action(pci, cracks, potholes, rut, esal)
        
        # Engineering intervention window based on structural urgency
        intervention_window = f"Within {rec['urgency_days']} days"
        operational_status = "Critical Intervention Required" if rec["priority"] == "P1" else ("Scheduled Maintenance" if rec["priority"] == "P2" else "Routine Monitoring")
            
        queue.append({
            "section_id": sec.get("section_id", "SEC-UNKNOWN"),
            "corridor_id": sec.get("corridor_id", "B047"),
            "corridor_name": sec.get("corridor_name", ""),
            "chainage_km": sec.get("start_chainage_km", 0.0),
            "current_pci": pci,
            "priority": rec["priority"],
            "urgency_days": rec["urgency_days"],
            "action": rec["action"],
            "hsr_item_code": rec["hsr_item_code"],
            "estimated_cost_lkr": rec["estimated_cost_lkr"],
            "preventive_savings_lkr": rec["preventive_savings_lkr"],
            "roi_percent": rec["roi_percent"],
            "life_extension_years": rec["life_extension_years"],
            "intervention_window": intervention_window,
            "operational_status": operational_status,
            "rationale": rec["rationale"]
        })
        
    # Sort queue: P1 first, then lowest PCI
    queue.sort(key=lambda x: (0 if x["priority"] == "P1" else (1 if x["priority"] == "P2" else 2), x["current_pci"]))
    return queue
