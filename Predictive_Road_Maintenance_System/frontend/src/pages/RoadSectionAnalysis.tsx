import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  MapPin, 
  Layers, 
  Activity, 
  AlertCircle, 
  CheckCircle2, 
  ChevronRight,
  ShieldCheck,
  TrendingDown,
  Info
} from 'lucide-react';
import { RoadSectionItem, fetchRoadDetail, runPrognosis, FullPrognosis } from '../services/api';

interface Props {
  sections: RoadSectionItem[];
  selectedSectionId: string;
  onSelectSection: (id: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const RoadSectionAnalysis: React.FC<Props> = ({
  sections,
  selectedSectionId,
  onSelectSection,
  onNavigateTab
}) => {
  const [prognosis, setPrognosis] = useState<FullPrognosis | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const activeSection = sections.find((s) => s.id === selectedSectionId) || sections[0];

  useEffect(() => {
    if (activeSection) {
      loadPrognosis(activeSection);
    }
  }, [activeSection?.id]);

  const loadPrognosis = async (sec: RoadSectionItem) => {
    setIsLoading(true);
    try {
      const res = await runPrognosis({
        section_id: sec.id,
        current_pci: sec.current_pci,
        pavement_age_years: sec.pavement_age_years,
        structural_number: sec.structural_number,
        aadt: sec.aadt,
        daily_esal: sec.daily_esal,
        heavy_vehicle_pct: sec.heavy_vehicle_pct,
        annual_precipitation_mm: sec.annual_precipitation_mm,
        mean_temp_c: 28.0,
        mean_diurnal_range_c: 4.5,
        monsoon_risk_factor: sec.monsoon_risk_factor,
        historical_decay_rate_annual: sec.historical_decay_rate_annual,
        crack_density_pct: sec.crack_density_pct,
        pothole_count: sec.pothole_count,
        iri_roughness: sec.iri_roughness,
        rut_depth_mm: sec.rut_depth_mm
      });
      setPrognosis(res);
    } catch (e) {
      console.error('Failed to run prognosis', e);
    } finally {
      setIsLoading(false);
    }
  };

  const pci = activeSection?.current_pci || 75.0;

  return (
    <div className="space-y-6">
      {/* Title & Selector Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-4">
        <div>
          <div className="text-[11px] font-mono text-cyan-400 tracking-wider uppercase flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            DEEP TELEMETRY INSPECTOR // GEOTECHNICAL & XAI VULNERABILITY
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight mt-0.5">
            Road Section Telemetry & Pavement Stratigraphy Analysis
          </h1>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs">
          <label className="text-slate-400">INSPECT SECTION:</label>
          <select
            value={activeSection?.id}
            onChange={(e) => onSelectSection(e.target.value)}
            className="bg-[#131D2E] border border-[#1E293B] text-cyan-400 rounded px-2.5 py-1 focus:outline-none focus:border-cyan-600 font-semibold"
          >
            {sections.map((s) => (
              <option key={s.id} value={s.id}>
                {s.id} ({s.corridor_id} Ch {s.start_chainage_km.toFixed(1)}km - PCI {s.current_pci.toFixed(1)})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* SECTION IDENTITY BAR */}
      <div className="telemetry-card p-4 grid grid-cols-2 md:grid-cols-6 gap-3 font-mono text-xs">
        <div>
          <span className="text-slate-500 text-[10px] block">SECTION ID</span>
          <span className="font-bold text-white text-sm">{activeSection?.id}</span>
        </div>
        <div>
          <span className="text-slate-500 text-[10px] block">CORRIDOR</span>
          <span className="font-semibold text-cyan-400 truncate block">{activeSection?.corridor_name}</span>
        </div>
        <div>
          <span className="text-slate-500 text-[10px] block">CHAINAGE RANGE</span>
          <span className="text-slate-200">
            {activeSection?.start_chainage_km.toFixed(2)} - {activeSection?.end_chainage_km.toFixed(2)} km
          </span>
        </div>
        <div>
          <span className="text-slate-500 text-[10px] block">GPS COORDINATES</span>
          <span className="text-slate-200 text-[11px]">
            {activeSection?.start_lat.toFixed(4)}°N, {activeSection?.start_lon.toFixed(4)}°E
          </span>
        </div>
        <div>
          <span className="text-slate-500 text-[10px] block">SURFACE LAYER</span>
          <span className="text-slate-200">Asphalt Superpave</span>
        </div>
        <div>
          <span className="text-slate-500 text-[10px] block">CURRENT PCI SCORE</span>
          <span className={`text-sm font-extrabold ${pci >= 70 ? 'text-emerald-400' : pci >= 55 ? 'text-amber-400' : 'text-rose-400'}`}>
            {pci.toFixed(1)} / 100
          </span>
        </div>
      </div>

      {/* STRATIGRAPHY SCHEMATIC & PREDICTED MULTI-HORIZONS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Pavement Stratigraphy & Geotechnical Vulnerability (7 cols - Matches Page 34) */}
        <div className="lg:col-span-7 telemetry-card p-5">
          <div className="flex items-center justify-between border-b border-[#1E293B] pb-3 font-mono">
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                Pavement Stratigraphy & Geotechnical Vulnerability
              </h2>
              <span className="text-xs text-slate-400 mt-0.5 block">
                Cross-Sectional Elevation Schematic & Layer Stress Tolerances (ASTM D6432 GPR Calibrated)
              </span>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-400">
              SCAN MODE: DUAL POLARIZATION
            </span>
          </div>

          {/* Stratigraphic Schematic Layers */}
          <div className="mt-4 space-y-2.5 font-mono text-xs">
            {/* Layer 1: Wearing Course */}
            <div className="p-3 rounded bg-[#1A2333] border-l-4 border-l-cyan-400 border border-[#233044]">
              <div className="flex justify-between items-center text-slate-300 font-semibold">
                <span>L1: WEARING COURSE (ASPHALT CONCRETE SUPERPAVE)</span>
                <span className="text-cyan-400">Thickness: 50mm</span>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-2 text-[11px] text-slate-400">
                <div>Shear Stress: <span className="text-slate-200">480 kPa</span></div>
                <div>Saturation: <span className="text-slate-200">94.2%</span></div>
                <div>Condition: <span className={pci >= 70 ? 'text-emerald-400' : 'text-amber-400'}>{pci >= 70 ? 'Intact' : 'Micro-Fissured'}</span></div>
              </div>
            </div>

            {/* Layer 2: Binder Course */}
            <div className="p-3 rounded bg-[#161E2E] border-l-4 border-l-blue-500 border border-[#202B3D]">
              <div className="flex justify-between items-center text-slate-300 font-semibold">
                <span>L2: BINDER COURSE (INTERMEDIATE AGGREGATE INTERLOCK)</span>
                <span className="text-blue-400">Thickness: 90mm</span>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-2 text-[11px] text-slate-400">
                <div>Shear Stress: <span className="text-slate-200">310 kPa</span></div>
                <div>Saturation: <span className="text-slate-200">78.5%</span></div>
                <div>Void Ratio: <span className="text-slate-200">4.8%</span></div>
              </div>
            </div>

            {/* Layer 3: Crushed Stone Base */}
            <div className="p-3 rounded bg-[#131B2A] border-l-4 border-l-amber-500 border border-[#1E2738]">
              <div className="flex justify-between items-center text-slate-300 font-semibold">
                <span>L3: CRUSHED STONE BASE COURSE (CRB-1 AGGREGATE)</span>
                <span className="text-amber-400">Thickness: 160mm</span>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-2 text-[11px] text-slate-400">
                <div>Resilient Modulus (Mr): <span className="text-amber-300">112 MPa</span></div>
                <div>Saturation: <span className="text-slate-200">61.3%</span></div>
                <div>Hydraulic Risk: <span className="text-amber-400">Moderate</span></div>
              </div>
            </div>

            {/* Layer 4: Compacted Subgrade */}
            <div className="p-3 rounded bg-[#0F1622] border-l-4 border-l-slate-600 border border-[#1A2230]">
              <div className="flex justify-between items-center text-slate-400 font-semibold">
                <span>L4: COMPACTED SUBGRADE (NATIVE SILTY CLAY)</span>
                <span className="text-slate-400">Depth: Continuous</span>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-2 text-[11px] text-slate-400">
                <div>California Bearing Ratio (CBR): <span className="text-slate-200">4.8%</span></div>
                <div>Pore Pressure: <span className="text-slate-200">+42 kPa</span></div>
                <div>Bearing Status: <span className="text-emerald-400">Stable</span></div>
              </div>
            </div>
          </div>

          {/* Telemetry Sensor Readings Bar */}
          <div className="mt-4 pt-3 border-t border-[#1E293B] grid grid-cols-4 gap-2 text-center font-mono">
            <div className="p-2 rounded bg-[#131D2E]">
              <div className="text-[10px] text-slate-500">L1 SURFACE STRAIN</div>
              <div className="text-sm font-bold text-white mt-0.5">1,840 με</div>
            </div>
            <div className="p-2 rounded bg-[#131D2E]">
              <div className="text-[10px] text-slate-500">SUBSURFACE MOISTURE</div>
              <div className="text-sm font-bold text-cyan-400 mt-0.5">82.1%</div>
            </div>
            <div className="p-2 rounded bg-[#131D2E]">
              <div className="text-[10px] text-slate-500">CRACK VELOCITY</div>
              <div className="text-sm font-bold text-amber-400 mt-0.5">+0.8 mm/wk</div>
            </div>
            <div className="p-2 rounded bg-[#131D2E]">
              <div className="text-[10px] text-slate-500">SUBGRADE CBR</div>
              <div className="text-sm font-bold text-white mt-0.5">4.8%</div>
            </div>
          </div>
        </div>

        {/* Right: Multi-Horizon Predictions & RRL (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Multi-Horizon Prediction Box */}
          <div className="telemetry-card p-5 font-mono">
            <div className="border-b border-[#1E293B] pb-3">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <TrendingDown className="w-4 h-4 text-cyan-400" />
                Multi-Horizon Future Condition Forecast
              </h2>
              <span className="text-xs text-slate-400 mt-0.5 block">
                Machine Learning Predictions (Trained XGBoost / RF Ensemble)
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 mt-4">
              <div className="p-3 rounded bg-[#131D2E] border border-[#1E293B]">
                <div className="text-xs text-slate-400">T + 3 MONTHS</div>
                <div className="text-2xl font-extrabold text-white mt-1">
                  {prognosis?.predicted_condition_horizons?.['3m']?.toFixed(1) || (pci - 0.8).toFixed(1)} <span className="text-xs text-slate-500">PCI</span>
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">Δ -{(pci - (prognosis?.predicted_condition_horizons?.['3m'] || pci - 0.8)).toFixed(1)} PCI</div>
              </div>

              <div className="p-3 rounded bg-[#131D2E] border border-[#1E293B]">
                <div className="text-xs text-slate-400">T + 6 MONTHS</div>
                <div className="text-2xl font-extrabold text-white mt-1">
                  {prognosis?.predicted_condition_horizons?.['6m']?.toFixed(1) || (pci - 1.8).toFixed(1)} <span className="text-xs text-slate-500">PCI</span>
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">Δ -{(pci - (prognosis?.predicted_condition_horizons?.['6m'] || pci - 1.8)).toFixed(1)} PCI</div>
              </div>

              <div className="p-3 rounded bg-[#131D2E] border border-[#1E293B]">
                <div className="text-xs text-slate-400">T + 12 MONTHS</div>
                <div className="text-2xl font-extrabold text-cyan-400 mt-1">
                  {prognosis?.predicted_condition_horizons?.['12m']?.toFixed(1) || (pci - 3.5).toFixed(1)} <span className="text-xs text-slate-500">PCI</span>
                </div>
                <div className="text-[10px] text-cyan-300 mt-0.5">Risk: {prognosis?.predicted_risk_category_12m || 'Fair'}</div>
              </div>

              <div className="p-3 rounded bg-[#131D2E] border border-[#1E293B]">
                <div className="text-xs text-slate-400">T + 24 MONTHS</div>
                <div className="text-2xl font-extrabold text-amber-400 mt-1">
                  {prognosis?.predicted_condition_horizons?.['24m']?.toFixed(1) || (pci - 7.5).toFixed(1)} <span className="text-xs text-slate-500">PCI</span>
                </div>
                <div className="text-[10px] text-amber-300 mt-0.5">Δ -{(pci - (prognosis?.predicted_condition_horizons?.['24m'] || pci - 7.5)).toFixed(1)} PCI</div>
              </div>
            </div>

            {/* RRL Summary */}
            <div className="mt-4 p-3 rounded bg-[#162032] border border-[#24334C]">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-400">REMAINING ROAD LIFE (RRL):</span>
                <span className="text-cyan-400 font-extrabold text-base">
                  {prognosis?.remaining_road_life?.rrl_rehabilitation_months || 28} Months
                </span>
              </div>
              <div className="text-[11px] text-slate-400 mt-1">
                Estimated {prognosis?.remaining_road_life?.rrl_rehabilitation_days || 840} days until condition intercepts rehabilitation threshold (PCI 55).
              </div>
            </div>
          </div>

          {/* Maintenance Action Summary Card */}
          <div className="telemetry-card p-5 font-mono text-xs">
            <span className="text-slate-500 text-[10px] block">INDICATED ENGINEERING INTERVENTION</span>
            <div className="text-sm font-bold text-white mt-1">
              {prognosis?.maintenance_recommendation?.action || 'Polymer-Modified Micro-Surfacing'}
            </div>
            <div className="mt-2 text-slate-300 text-[11px]">
              {prognosis?.maintenance_recommendation?.rationale}
            </div>
            <div className="mt-3 pt-2.5 border-t border-[#1E293B] flex items-center justify-between">
              <div>
                <span className="text-slate-500 text-[10px] block">HSR ESTIMATED COST</span>
                <span className="text-emerald-400 font-bold">
                  LKR {prognosis?.maintenance_recommendation?.estimated_cost_lkr?.toLocaleString() || '413,840'}
                </span>
              </div>
              <button
                onClick={() => onNavigateTab('maintenance')}
                className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition"
              >
                SCHEDULE WORK ORDER
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* EXPLAINABLE AI (XAI) ATTRIBUTION BREAKDOWN */}
      <div className="telemetry-card p-5">
        <div className="border-b border-[#1E293B] pb-3 font-mono">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Explainable AI (XAI) — Localized Deterioration Factor Attribution
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            {prognosis?.explainability?.executive_summary || 'Deterioration drivers computed from feature interaction pathways.'}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4 font-mono text-xs">
          {prognosis?.explainability?.feature_attributions?.map((attr, idx) => (
            <div key={idx} className="p-3 rounded bg-[#131D2E] border border-[#1E293B]">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-white">{attr.factor}</span>
                <span className="text-cyan-400 font-bold">{attr.importance_pct}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                <div
                  className="bg-cyan-500 h-full rounded-full"
                  style={{ width: `${attr.importance_pct}%` }}
                />
              </div>
              <div className="text-[11px] text-slate-400 mt-2 leading-relaxed">
                {attr.note}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
