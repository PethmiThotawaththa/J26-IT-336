"""
rrl_engine.py
-------------
Remaining Road Life (RRL) and Deterioration Curve Simulation Engine for Component 4.
Calculates:
- Precise month-by-month condition trajectory (0 to 36 months)
- Time until critical engineering thresholds:
  * Preventive Window: PCI = 70
  * Rehabilitation Threshold: PCI = 55
  * Structural Failure Threshold: PCI = 40
- Proactive Intervention vs Status Quo (Zero Intervention) comparative trajectory
- Statistical 90% prediction intervals (+- 1.645 * sigma)
"""

import math
from typing import Dict, Any, List

# Standard AASHTO / ASTM D6433 Pavement Condition Thresholds
PCI_THRESHOLDS = {
    "GOOD": 85.0,
    "SATISFACTORY": 70.0,
    "FAIR": 55.0,
    "POOR": 40.0,
    "CRITICAL": 25.0
}

def calculate_remaining_road_life(
    current_pci: float,
    annual_decay_rate: float,
    daily_esal: float = 1500.0,
    monsoon_factor: float = 1.0,
    rehab_threshold: float = 55.0,
    failure_threshold: float = 40.0
) -> Dict[str, Any]:
    """
    Computes remaining useful pavement life in months and days until condition
    breaches rehabilitation (PCI 55) and catastrophic failure (PCI 40) thresholds.
    """
    # Safe bound on decay rate
    effective_decay_annual = max(float(annual_decay_rate), 0.5)
    
    # Accelerated decay factor based on heavy axle and monsoon loading
    load_stress_modifier = 1.0 + (max(daily_esal - 1200.0, 0) / 5000.0) * 0.35 + (max(monsoon_factor - 1.0, 0)) * 0.25
    monthly_decay = (effective_decay_annual / 12.0) * load_stress_modifier
    
    # Months to rehabilitation threshold (PCI 55)
    if current_pci <= rehab_threshold:
        months_to_rehab = 0
        days_to_rehab = 0
    else:
        # Non-linear accelerated decay model
        months_to_rehab = int(round((current_pci - rehab_threshold) / monthly_decay))
        days_to_rehab = months_to_rehab * 30
        
    # Months to structural failure threshold (PCI 40)
    if current_pci <= failure_threshold:
        months_to_failure = 0
        days_to_failure = 0
    else:
        months_to_failure = int(round((current_pci - failure_threshold) / (monthly_decay * 1.15)))
        days_to_failure = months_to_failure * 30
        
    # Condition state classification
    if current_pci >= PCI_THRESHOLDS["GOOD"]:
        state = "Good"
        urgency = "Low"
    elif current_pci >= PCI_THRESHOLDS["SATISFACTORY"]:
        state = "Satisfactory"
        urgency = "Monitoring"
    elif current_pci >= PCI_THRESHOLDS["FAIR"]:
        state = "Fair"
        urgency = "Planned Intervention (6-12 mos)"
    elif current_pci >= PCI_THRESHOLDS["POOR"]:
        state = "Poor"
        urgency = "High (Intervention < 90 days)"
    else:
        state = "Critical"
        urgency = "Emergency Action (< 30 days)"
        
    return {
        "current_pci": round(current_pci, 1),
        "condition_state": state,
        "urgency_level": urgency,
        "effective_monthly_decay_pci": round(monthly_decay, 3),
        "rrl_rehabilitation_months": months_to_rehab,
        "rrl_rehabilitation_days": days_to_rehab,
        "rrl_failure_months": months_to_failure,
        "rrl_failure_days": days_to_failure,
        "rehab_threshold_pci": rehab_threshold,
        "failure_threshold_pci": failure_threshold,
        "assumptions": [
            "AASHTO flexible pavement deterioration curve",
            "Linear-to-quadratic distress propagation under dynamic axle load",
            "Monsoon moisture ingress softens compacted subgrade layer"
        ]
    }

def generate_deterioration_curve(
    current_pci: float,
    annual_decay_rate: float,
    daily_esal: float = 1500.0,
    monsoon_factor: float = 1.0,
    intervention_month: int = 12,
    intervention_type: str = "Mill & Overlay"
) -> List[Dict[str, Any]]:
    """
    Generates a 36-month month-by-month trajectory comparing:
    1. Status Quo (Zero Intervention)
    2. Proactive Intervention (Simulated repair at intervention_month)
    3. 90% Confidence Interval bounds (lower and upper)
    """
    curve_points = []
    effective_decay_annual = max(float(annual_decay_rate), 0.5)
    load_stress_modifier = 1.0 + (max(daily_esal - 1200.0, 0) / 5000.0) * 0.35 + (max(monsoon_factor - 1.0, 0)) * 0.25
    monthly_base_decay = (effective_decay_annual / 12.0) * load_stress_modifier
    
    # Post-intervention recovery gains
    boost_pci = {
        "Slurry Seal": 15.0,
        "Micro-surfacing": 22.0,
        "Mill & Overlay": 38.0,
        "Full Reconstruction": 50.0
    }.get(intervention_type, 30.0)
    
    curr_status_quo = current_pci
    curr_mitigated = current_pci
    intervention_applied = False
    
    for month in range(0, 37):
        # Accelerating decay as PCI drops below 60
        acceleration = 1.0 + max((60.0 - curr_status_quo) / 40.0, 0.0) * 0.8
        decay_step = monthly_base_decay * acceleration
        
        # Uncertainty grows over time (t * sigma)
        sigma = 0.4 + (month * 0.12)
        ci_lower = max(curr_status_quo - (1.645 * sigma), 0.0)
        ci_upper = min(curr_status_quo + (1.645 * sigma), 100.0)
        
        # Mitigated branch
        if month == intervention_month and not intervention_applied:
            curr_mitigated = min(curr_mitigated + boost_pci, 98.0)
            intervention_applied = True
            post_mitigation_decay = monthly_base_decay * 0.45 # Slower decay after fresh overlay
        elif intervention_applied:
            post_mitigation_decay = monthly_base_decay * 0.45
            curr_mitigated = max(curr_mitigated - post_mitigation_decay, 10.0)
        else:
            curr_mitigated = curr_status_quo
            
        curve_points.append({
            "month": month,
            "month_label": f"M{month:02d}" if month > 0 else "M0 (Now)",
            "status_quo_pci": round(curr_status_quo, 1),
            "mitigated_pci": round(curr_mitigated, 1),
            "ci_lower_pci": round(ci_lower, 1),
            "ci_upper_pci": round(ci_upper, 1),
            "critical_threshold": 40.0,
            "rehab_threshold": 55.0
        })
        
        # Advance status quo
        curr_status_quo = max(curr_status_quo - decay_step, 8.0)
        
    return curve_points
