/**
 * api.ts
 * ------
 * Typed HTTP API client for Component 4 Research Backend.
 */

const API_BASE = '/api';

export interface DashboardSummary {
  status: string;
  engine_version: string;
  latency_ms: number;
  structural_health_index: number;
  total_monitored_km: number;
  monitored_corridors_count: number;
  total_sections_count: number;
  critical_decay_zones_count: number;
  warning_decay_zones_count: number;
  healthy_sections_count: number;
  preventive_savings_lkr: number;
  preventive_savings_usd: number;
  average_roi_percent: number;
  corridors: Array<{
    id: string;
    name: string;
    total_length_km: number;
    aadt: number;
    daily_esal: number;
    avg_pci: number;
    section_count: number;
    critical_sections: number;
  }>;
  anomaly_stream: Array<{
    badge: string;
    section_id: string;
    corridor_id: string;
    corridor_name: string;
    chainage_km: number;
    current_pci: number;
    days_to_collapse: number;
    distress_summary: string;
    recommended_action: string;
    action_type: string;
    estimated_cost_lkr: number;
  }>;
}

export interface RoadSectionItem {
  id: string;
  corridor_id: string;
  corridor_name: string;
  start_chainage_km: number;
  end_chainage_km: number;
  start_lat: number;
  start_lon: number;
  end_lat: number;
  end_lon: number;
  altitude_m: number;
  current_pci: number;
  historical_pci_1yr_ago: number;
  historical_decay_rate_annual: number;
  crack_density_pct: number;
  pothole_count: number;
  iri_roughness: number;
  rut_depth_mm: number;
  daily_esal: number;
  aadt: number;
  pavement_age_years: number;
  structural_number: number;
  monsoon_risk_factor: number;
  annual_precipitation_mm: number;
  heavy_vehicle_pct: number;
}

export interface DecayCurvePoint {
  month: number;
  month_label: string;
  status_quo_pci: number;
  mitigated_pci: number;
  ci_lower_pci: number;
  ci_upper_pci: number;
  critical_threshold: number;
  rehab_threshold: number;
}

export interface FullPrognosis {
  section_id: string;
  current_pci: number;
  predicted_condition_horizons: { [key: string]: number };
  predicted_risk_category_12m: string;
  remaining_road_life: {
    current_pci: number;
    condition_state: string;
    urgency_level: string;
    effective_monthly_decay_pci: number;
    rrl_rehabilitation_months: number;
    rrl_rehabilitation_days: number;
    rrl_failure_months: number;
    rrl_failure_days: number;
    assumptions: string[];
  };
  deterioration_curve_36m: DecayCurvePoint[];
  maintenance_recommendation: {
    priority: string;
    action: string;
    hsr_item_code: string;
    hsr_description: string;
    urgency_days: number;
    estimated_cost_lkr: number;
    emergency_rebuild_cost_lkr: number;
    preventive_savings_lkr: number;
    roi_percent: number;
    life_extension_years: number;
    rationale: string;
    standards_reference: string;
  };
  explainability: {
    section_id: string;
    primary_decay_driver: string;
    executive_summary: string;
    feature_attributions: Array<{
      factor: string;
      importance_pct: number;
      impact: string;
      note: string;
    }>;
  };
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const res = await fetch(`${API_BASE}/dashboard/summary`);
  if (!res.ok) throw new Error('Failed to load dashboard summary');
  return res.json();
}

export async function fetchRoads(corridorId?: string): Promise<{ sections: RoadSectionItem[] }> {
  const url = corridorId ? `${API_BASE}/roads?corridor_id=${corridorId}&limit=1000` : `${API_BASE}/roads?limit=1000`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to load road sections');
  return res.json();
}

export async function fetchRoadDetail(sectionId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/roads/${sectionId}`);
  if (!res.ok) throw new Error(`Failed to load section ${sectionId}`);
  return res.json();
}

export async function fetchDecayCurve(
  sectionId: string,
  interventionMonth = 11,
  trafficMult = 1.0,
  weatherMult = 1.0
): Promise<{ trajectory: DecayCurvePoint[]; section_id: string; current_pci: number }> {
  const res = await fetch(
    `${API_BASE}/roads/${sectionId}/decay-curve?intervention_month=${interventionMonth}&traffic_multiplier=${trafficMult}&weather_multiplier=${weatherMult}`
  );
  if (!res.ok) throw new Error('Failed to fetch decay curve');
  return res.json();
}

export async function runPrognosis(input: any): Promise<FullPrognosis> {
  const res = await fetch(`${API_BASE}/predict/prognosis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  });
  if (!res.ok) throw new Error('Prognosis inference failed');
  return res.json();
}

export async function fetchModelEvaluation(): Promise<any> {
  const res = await fetch(`${API_BASE}/models/evaluation`);
  if (!res.ok) throw new Error('Failed to fetch model evaluation');
  return res.json();
}

export async function fetchMaintenanceQueue(priority?: string): Promise<any> {
  const url = priority ? `${API_BASE}/maintenance/queue?priority=${priority}` : `${API_BASE}/maintenance/queue`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch maintenance queue');
  return res.json();
}

export async function dispatchWorkOrder(orderId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/maintenance/work-orders/${orderId}/dispatch`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to dispatch work order');
  return res.json();
}

export async function fetchMaintenanceGantt(): Promise<any> {
  const res = await fetch(`${API_BASE}/maintenance/gantt`);
  if (!res.ok) throw new Error('Failed to fetch maintenance Gantt');
  return res.json();
}

export async function fetchDatasets(): Promise<any> {
  const res = await fetch(`${API_BASE}/datasets`);
  if (!res.ok) throw new Error('Failed to fetch datasets list');
  return res.json();
}

export async function fetchDatasetPreview(key = 'features'): Promise<any> {
  const res = await fetch(`${API_BASE}/datasets/preview?file_key=${key}`);
  if (!res.ok) throw new Error('Failed to preview dataset');
  return res.json();
}

export async function fetchMockFixtures(): Promise<any> {
  const res = await fetch(`${API_BASE}/integration/mock-fixtures`);
  if (!res.ok) throw new Error('Failed to fetch mock fixtures');
  return res.json();
}

export async function submitIntegrationPayload(payload: any): Promise<any> {
  const res = await fetch(`${API_BASE}/integration/adapter/comp1-3`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Integration adapter submission failed');
  return res.json();
}
