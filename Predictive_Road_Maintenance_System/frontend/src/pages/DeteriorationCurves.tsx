import React, { useState, useEffect } from 'react';
import { 
  TrendingDown, 
  Sliders, 
  AlertTriangle, 
  CheckCircle2, 
  DollarSign, 
  Layers, 
  ArrowRight,
  ShieldAlert,
  Play
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  ReferenceLine,
  Area,
  ComposedChart
} from 'recharts';
import { RoadSectionItem, DecayCurvePoint, fetchDecayCurve } from '../services/api';

interface Props {
  sections: RoadSectionItem[];
  selectedSectionId: string;
  onSelectSection: (id: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const DeteriorationCurves: React.FC<Props> = ({
  sections,
  selectedSectionId,
  onSelectSection,
  onNavigateTab
}) => {
  const [horizon, setHorizon] = useState<'30D' | '90D' | '180D' | '1Y' | '3Y'>('90D');
  const [interventionMonth, setInterventionMonth] = useState<number>(11);
  const [trafficMult, setTrafficMult] = useState<number>(1.2);
  const [weatherMult, setWeatherMult] = useState<number>(1.3);
  const [curveData, setCurveData] = useState<DecayCurvePoint[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Active section data
  const currentSection = sections.find((s) => s.id === selectedSectionId) || sections[0];

  useEffect(() => {
    if (currentSection) {
      loadCurve(currentSection.id);
    }
  }, [currentSection?.id, interventionMonth, trafficMult, weatherMult]);

  const loadCurve = async (secId: string) => {
    setIsLoading(true);
    try {
      const data = await fetchDecayCurve(secId, interventionMonth, trafficMult, weatherMult);
      setCurveData(data.trajectory);
    } catch (e) {
      console.error('Failed to load decay curve', e);
    } finally {
      setIsLoading(false);
    }
  };

  const currentPci = currentSection?.current_pci || 68.4;
  // Estimate T+90D PCI from curve data
  const t90Pci = curveData.length > 3 ? curveData[3].status_quo_pci : currentPci - 4.5;
  const tMitigatedPci = curveData.length > 12 ? curveData[12].mitigated_pci : 88.0;

  // Dynamic Cost & Intervention calculation based on RDA HSR 2025 Standard Rates
  const cracks = currentSection?.crack_density_pct || 5.0;
  const potholes = currentSection?.pothole_count || 0;
  const rut = currentSection?.rut_depth_mm || 3.5;
  const area = 700.0; // standard 100m length x 7.0m 2-lane carriageway width

  let unitRate = 591.20; // HSR-53 Polymer-Modified Micro-Surfacing
  let actionWindowDays = 45;
  let failureProb = 58.4;
  let riskCode = 'BASE MOD-02';
  let indicatedIntervention = 'Polymer-Modified Micro-Surfacing';

  if (currentPci >= 85.0) {
    unitRate = 8.60; // HSR-40 Routine drainage clearing
    actionWindowDays = 180;
    failureProb = Math.min(Math.round(8.5 * trafficMult), 25);
    riskCode = 'NOMINAL-01';
    indicatedIntervention = 'Routine Drainage & Surface Clearance';
  } else if (currentPci >= 70.0) {
    if (cracks > 10.0) {
      unitRate = Math.max(109.55 * (cracks / 100.0) * 1.5 * 10, 85.0);
      actionWindowDays = 60;
      failureProb = Math.min(Math.round(28.0 * trafficMult), 45);
      riskCode = 'SURF WARN-02';
      indicatedIntervention = 'Bituminous Crack Sealing & Mastic Fill';
    } else {
      unitRate = 640.15; // HSR-51 Slurry Seal
      actionWindowDays = 90;
      failureProb = Math.min(Math.round(22.0 * trafficMult), 40);
      riskCode = 'SURF NOM-03';
      indicatedIntervention = 'Continuous Polymer Slurry Seal';
    }
  } else if (currentPci >= 55.0) {
    if (potholes > 2 || rut > 12.0) {
      unitRate = 591.20 + (potholes * 18.0);
      actionWindowDays = 21;
      failureProb = Math.min(Math.round(72.0 * trafficMult), 88);
      riskCode = 'BASE WARN-03';
      indicatedIntervention = 'Fiber Micro-Surfacing & Patching';
    } else {
      unitRate = 591.20;
      actionWindowDays = 45;
      failureProb = Math.min(Math.round(58.0 * trafficMult), 75);
      riskCode = 'BASE MOD-02';
      indicatedIntervention = 'Polymer-Modified Micro-Surfacing';
    }
  } else if (currentPci >= 40.0) {
    unitRate = 3356.56; // HSR-75 Cold Milling 50mm + Dense Asphalt Overlay
    actionWindowDays = 14;
    failureProb = Math.min(Math.round(88.4 * trafficMult), 96);
    riskCode = 'BASE CRIT-04';
    indicatedIntervention = 'Cold Milling 50mm + Dense Asphalt Overlay';
  } else {
    unitRate = 18526.49; // HSR-71 Full Reconstruction
    actionWindowDays = 7;
    failureProb = Math.min(Math.round(98.2 * trafficMult), 99);
    riskCode = 'COLLAPSE CRIT-01';
    indicatedIntervention = 'Full-Depth Base Stabilization & Reconstruction';
  }

  const potholePatchingCost = potholes * 4800;
  const proactiveCost = Math.round((area * unitRate) + potholePatchingCost);
  const rebuildCost = Math.round(area * 18526.49);
  const deferralLoss = Math.max(rebuildCost - proactiveCost, 0);
  const deferralPct = Math.round((deferralLoss / Math.max(proactiveCost, 1)) * 100);
  const ravelingDepthMm = Math.max(parseFloat((rut * 1.15 + cracks * 0.35).toFixed(1)), 3.5);

  return (
    <div className="space-y-6">
      {/* Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-4">
        <div>
          <div className="text-[11px] font-mono text-cyan-400 tracking-wider uppercase flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            SIMULATION ENGINE v3.4a // STOCHASTIC DECAY MODELER
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight mt-0.5">
            AI Deterioration Forecasting & Neural Decay Curves
          </h1>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs">
          <label className="text-slate-400">TARGET ASSET:</label>
          <select
            value={currentSection?.id}
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

      {/* HORIZON & SCENARIO CONTROL BAR (Matches Page 34) */}
      <div className="telemetry-card p-4 grid grid-cols-1 md:grid-cols-4 gap-4 font-mono text-xs">
        {/* Horizon Buttons */}
        <div>
          <label className="text-slate-400 uppercase tracking-wider block mb-1.5">FORECAST HORIZON</label>
          <div className="grid grid-cols-5 gap-1">
            {(['30D', '90D', '180D', '1Y', '3Y'] as const).map((h) => (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={`py-1 rounded text-center transition font-semibold ${
                  horizon === h ? 'bg-cyan-600 text-white shadow-[0_0_8px_rgba(6,182,212,0.4)]' : 'bg-[#162032] text-slate-400 hover:text-white'
                }`}
              >
                {h}
              </button>
            ))}
          </div>
        </div>

        {/* Precipitation Surge Slider */}
        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>PRECIPITATION SURGE</span>
            <span className="text-cyan-400">+{Math.round((weatherMult - 1.0) * 100)}%</span>
          </div>
          <input
            type="range"
            min="0.8"
            max="2.5"
            step="0.1"
            value={weatherMult}
            onChange={(e) => setWeatherMult(parseFloat(e.target.value))}
            className="w-full accent-cyan-400 bg-slate-800"
          />
          <div className="text-[10px] text-slate-500 mt-1">Monsoon Deluge Infiltration</div>
        </div>

        {/* Axle Stress Slider */}
        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>AXLE STRESS (ESAL)</span>
            <span className="text-amber-400">{((currentSection?.daily_esal || 1500) * trafficMult).toFixed(0)}/d</span>
          </div>
          <input
            type="range"
            min="0.7"
            max="2.5"
            step="0.1"
            value={trafficMult}
            onChange={(e) => setTrafficMult(parseFloat(e.target.value))}
            className="w-full accent-amber-400 bg-slate-800"
          />
          <div className="text-[10px] text-slate-500 mt-1">Commercial Freight Overload</div>
        </div>

        {/* Intervention Timing */}
        <div>
          <div className="flex justify-between text-slate-400 mb-1">
            <span>INTERVENTION TIMING</span>
            <span className="text-emerald-400 font-bold">Month {interventionMonth}</span>
          </div>
          <input
            type="range"
            min="1"
            max="24"
            step="1"
            value={interventionMonth}
            onChange={(e) => setInterventionMonth(parseInt(e.target.value))}
            className="w-full accent-emerald-400 bg-slate-800"
          />
          <div className="text-[10px] text-slate-500 mt-1">Recommended Overhaul Window</div>
        </div>
      </div>

      {/* COMPARISON CARDS: T-0 BASELINE VS T+90D AI PROJECTION (Matches Page 34) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono">
        {/* T-0 Baseline Observation */}
        <div className="telemetry-card p-4 border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1.5 text-slate-300 font-semibold">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              T-0 BASELINE OBSERVATION
            </span>
            <span className="px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800 text-amber-300 font-bold">
              PCI: {currentPci.toFixed(1)} / {currentPci >= 70 ? 'SATISFACTORY' : 'MODERATE'}
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2 mt-4 text-center">
            <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
              <div className="text-slate-500 text-[10px]">POTHOLES</div>
              <div className="text-base font-bold text-white mt-0.5">{currentSection?.pothole_count || 0}</div>
            </div>
            <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
              <div className="text-slate-500 text-[10px]">CRACK DENSITY</div>
              <div className="text-base font-bold text-white mt-0.5">{currentSection?.crack_density_pct.toFixed(1) || 5.0}%</div>
            </div>
            <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
              <div className="text-slate-500 text-[10px]">IRI ROUGHNESS</div>
              <div className="text-base font-bold text-white mt-0.5">{currentSection?.iri_roughness.toFixed(2) || 2.2} m/km</div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#1E293B] flex items-center justify-between text-xs">
            <div>
              <span className="text-slate-500 text-[10px] block">PROACTIVE MITIGATION COST</span>
              <span className="text-emerald-400 text-lg font-bold">LKR {proactiveCost.toLocaleString()}</span>
              <span className="text-slate-400 text-[11px] block">(~${Math.round(proactiveCost / 310)})</span>
            </div>
            <div className="text-right">
              <span className="text-slate-500 text-[10px] block">ACTION WINDOW</span>
              <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${
                actionWindowDays <= 14 
                  ? 'bg-rose-950 text-rose-400 border-rose-800' 
                  : actionWindowDays <= 45 
                  ? 'bg-amber-950 text-amber-400 border-amber-800' 
                  : 'bg-emerald-950 text-emerald-400 border-emerald-800'
              }`}>
                ≤ {actionWindowDays} DAYS REMAINING
              </span>
            </div>
          </div>
        </div>

        {/* T+90D AI Unmitigated Projection */}
        <div className="telemetry-card p-4 border-l-4 border-l-rose-500">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1.5 text-slate-300 font-semibold">
              <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
              T+90D AI UNMITIGATED PROJECTION
            </span>
            <span className="px-2 py-0.5 rounded bg-rose-950/60 border border-rose-800 text-rose-300 font-bold">
              PCI: {t90Pci.toFixed(1)} / {t90Pci < 55 ? 'CRITICAL RISK' : t90Pci < 70 ? 'MODERATE RISK' : 'STABLE'}
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2 mt-4 text-center">
            <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
              <div className="text-slate-500 text-[10px]">FAILURE PROBABILITY</div>
              <div className="text-base font-bold text-rose-400 mt-0.5">{failureProb.toFixed(1)}%</div>
            </div>
            <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
              <div className="text-slate-500 text-[10px]">RAVELING DEPTH</div>
              <div className="text-base font-bold text-rose-300 mt-0.5">{ravelingDepthMm} mm</div>
            </div>
            <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
              <div className="text-slate-500 text-[10px]">STRUCTURAL RISK</div>
              <div className="text-base font-bold text-rose-400 mt-0.5">{riskCode}</div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#1E293B] flex items-center justify-between text-xs">
            <div>
              <span className="text-slate-500 text-[10px] block">MANDATORY REBUILD COST</span>
              <span className="text-rose-400 text-lg font-bold">LKR {rebuildCost.toLocaleString()}</span>
              <span className="text-slate-400 text-[11px] block">(~${Math.round(rebuildCost / 310)})</span>
            </div>
            <div className="text-right">
              <span className="text-slate-500 text-[10px] block">NET DEFERRAL LOSS</span>
              <span className="text-rose-400 font-bold text-xs block">
                +LKR {deferralLoss.toLocaleString()} (+{deferralPct}%)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* FULL 36-MONTH INTERACTIVE RECHARTS CURVE */}
      <div className="telemetry-card p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-3 font-mono">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-cyan-400" />
              Continuous 36-Month Pavement Condition Trajectory (PCI vs Time)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Comparison of Status Quo Degradation vs Proactive Intervention at Month {interventionMonth} with 90% Confidence Interval
            </p>
          </div>
          <div className="flex items-center space-x-3 text-xs">
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-3 h-1 bg-emerald-400 inline-block"></span>
              Proactive Intervention
            </span>
            <span className="flex items-center gap-1.5 text-rose-400">
              <span className="w-3 h-1 bg-rose-500 inline-block"></span>
              Status Quo
            </span>
            <span className="flex items-center gap-1.5 text-slate-400">
              <span className="w-3 h-3 bg-cyan-900/30 border border-cyan-800 inline-block"></span>
              90% CI
            </span>
          </div>
        </div>

        {/* Chart */}
        <div className="h-80 w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={curveData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="month_label" stroke="#64748B" fontSize={11} fontFamily="JetBrains Mono" />
              <YAxis domain={[0, 100]} stroke="#64748B" fontSize={11} fontFamily="JetBrains Mono" label={{ value: 'PCI SCORE', angle: -90, position: 'insideLeft', fill: '#64748B', fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0D131F', borderColor: '#1E293B', borderRadius: '6px', fontSize: '12px', fontFamily: 'JetBrains Mono' }}
              />
              <ReferenceLine y={55} stroke="#F59E0B" strokeDasharray="3 3" label={{ value: 'REHABILITATION TRIGGER (PCI 55)', fill: '#F59E0B', fontSize: 10 }} />
              <ReferenceLine y={40} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'TERMINAL COLLAPSE (PCI 40)', fill: '#EF4444', fontSize: 10 }} />
              <ReferenceLine x={`M${interventionMonth.toString().padStart(2, '0')}`} stroke="#06B6D4" strokeDasharray="2 2" label={{ value: `INTERVENTION @ M${interventionMonth}`, fill: '#06B6D4', fontSize: 10 }} />
              
              {/* Confidence Interval band */}
              <Area type="monotone" dataKey="ci_upper_pci" stroke="none" fill="#06B6D4" fillOpacity={0.08} />
              <Area type="monotone" dataKey="ci_lower_pci" stroke="none" fill="#0B0F17" fillOpacity={1.0} />

              {/* Lines */}
              <Line type="monotone" dataKey="mitigated_pci" stroke="#10B981" strokeWidth={3} dot={{ r: 2, fill: '#10B981' }} name="With Recommended Intervention" />
              <Line type="monotone" dataKey="status_quo_pci" stroke="#EF4444" strokeWidth={2} strokeDasharray="4 4" dot={{ r: 2, fill: '#EF4444' }} name="Status Quo (No Action)" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
