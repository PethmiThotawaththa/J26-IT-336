import React, { useState } from 'react';
import { 
  AlertTriangle, 
  TrendingDown, 
  DollarSign, 
  ShieldAlert, 
  ArrowUpRight, 
  CheckCircle2, 
  ChevronRight,
  Activity,
  Layers,
  Zap
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  ReferenceLine 
} from 'recharts';
import { DashboardSummary, RoadSectionItem } from '../services/api';

interface Props {
  summary: DashboardSummary | null;
  sections: RoadSectionItem[];
  onSelectSection: (sectionId: string) => void;
  onNavigateTab: (tabId: string) => void;
  onInspectAnomaly?: (sectionId: string) => void;
}

export const PredictiveOverview: React.FC<Props> = ({
  summary,
  sections,
  onSelectSection,
  onNavigateTab,
  onInspectAnomaly
}) => {
  const [selectedScenario, setSelectedScenario] = useState<'heavy' | 'moderate'>('heavy');

  // Mini preview decay curve data
  const previewCurveData = [
    { month: 'M0', statusQuo: summary?.structural_health_index || 71.6, mitigated: summary?.structural_health_index || 71.6 },
    { month: 'M06', statusQuo: (summary?.structural_health_index || 71.6) - 2.8, mitigated: (summary?.structural_health_index || 71.6) - 1.2 },
    { month: 'M11 (Intervene)', statusQuo: (summary?.structural_health_index || 71.6) - 5.4, mitigated: 88.5 },
    { month: 'M18', statusQuo: (summary?.structural_health_index || 71.6) - 10.2, mitigated: 86.8 },
    { month: 'M24', statusQuo: (summary?.structural_health_index || 71.6) - 16.5, mitigated: 85.0 },
    { month: 'M30', statusQuo: (summary?.structural_health_index || 71.6) - 24.1, mitigated: 83.2 },
    { month: 'M36', statusQuo: 28.4, mitigated: 81.5 },
  ];

  return (
    <div className="space-y-6">
      {/* Page Title & Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-4">
        <div>
          <div className="text-[11px] font-mono text-cyan-400 tracking-wider uppercase flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            STATE ARTERY MATRIX: ACTIVE // COMPONENT 4 PREDICTIVE RADAR
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight mt-0.5">
            Predictive Health & Structural Deterioration Overview
          </h1>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="px-2.5 py-1 rounded bg-[#131D2E] border border-[#1E293B] text-slate-300">
            NETWORK: RDA COLOMBO
          </span>
          <span className="px-2.5 py-1 rounded bg-cyan-950/60 border border-cyan-800 text-cyan-400">
            AUTONOMOUS PROGNOSIS ACTIVE
          </span>
        </div>
      </div>

      {/* 4 TOP TELEMETRY KPI CARDS (Matches Proposal Page 33) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono">
        {/* Card 1: Structural Health PQI */}
        <div className="telemetry-card p-4 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="uppercase tracking-wider">Structural Health PQI</span>
            <span className="text-cyan-400">INDEX</span>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <div>
              <div className="text-3xl font-extrabold text-white tracking-tight">
                {summary?.structural_health_index.toFixed(1) || '71.6'}
              </div>
              <div className="text-xs text-emerald-400 font-medium mt-0.5">
                Stable <span className="text-slate-400">±0.8% variance</span>
              </div>
            </div>
            <div className="w-12 h-12 rounded-full border-4 border-emerald-500/30 border-t-emerald-400 flex items-center justify-center font-bold text-xs text-emerald-400">
              {Math.round(summary?.structural_health_index || 72)}%
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-[#1E293B] flex justify-between text-[11px] text-slate-400">
            <span>SURFACE DEFORMATION:</span>
            <span className="text-slate-200">&lt; 1.2 mm</span>
          </div>
        </div>

        {/* Card 2: Critical Decay Zones */}
        <div className="telemetry-card p-4 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="uppercase tracking-wider">Critical Decay Zones</span>
            <span className="text-rose-400 font-semibold">&lt; 55 PCI</span>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <div>
              <div className="text-3xl font-extrabold text-rose-400 tracking-tight">
                {summary?.critical_decay_zones_count || 14}
              </div>
              <div className="text-xs text-rose-300 font-medium mt-0.5">
                Sectors at criticality
              </div>
            </div>
            <AlertTriangle className="w-8 h-8 text-rose-500/40" />
          </div>
          <div className="mt-3 pt-2.5 border-t border-[#1E293B] flex justify-between text-[11px] text-slate-400">
            <span>FAILURE TIMELINE:</span>
            <span className="text-rose-400 font-semibold">&lt; 60 Days</span>
          </div>
        </div>

        {/* Card 3: Preventive Savings */}
        <div className="telemetry-card p-4 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="uppercase tracking-wider">Preventive Savings</span>
            <span className="text-emerald-400 font-semibold">+{summary?.average_roi_percent || 34}% ROI</span>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <div>
              <div className="text-3xl font-extrabold text-emerald-400 tracking-tight">
                ${((summary?.preventive_savings_usd || 2400000) / 1000000).toFixed(2)}M
              </div>
              <div className="text-xs text-slate-400 font-medium mt-0.5">
                LKR {(summary?.preventive_savings_lkr || 744000000).toLocaleString('en-US', { maximumFractionDigits: 0 })}
              </div>
            </div>
            <DollarSign className="w-8 h-8 text-emerald-500/40" />
          </div>
          <div className="mt-3 pt-2.5 border-t border-[#1E293B] flex justify-between text-[11px] text-slate-400">
            <span>DEFERRED REBUILD RESCUE:</span>
            <span className="text-emerald-400">AVOIDED</span>
          </div>
        </div>

        {/* Card 4: Monitored Corridors */}
        <div className="telemetry-card p-4 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="uppercase tracking-wider">Monitored Corridors</span>
            <span className="text-cyan-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
              LiDAR Synced
            </span>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <div>
              <div className="text-3xl font-extrabold text-white tracking-tight">
                {summary?.total_monitored_km || 67.2} <span className="text-base text-slate-400 font-normal">km</span>
              </div>
              <div className="text-xs text-cyan-300 font-medium mt-0.5">
                {summary?.total_sections_count || 675} Section Segments
              </div>
            </div>
            <Layers className="w-8 h-8 text-cyan-500/40" />
          </div>
          <div className="mt-3 pt-2.5 border-t border-[#1E293B] flex justify-between text-[11px] text-slate-400">
            <span>GEOSPATIAL ACCURACY:</span>
            <span className="text-slate-200">± 0.05 m Resolution</span>
          </div>
        </div>
      </div>

      {/* MIDDLE SECTION: AI DETERIORATION FORECASTING & REAL-TIME ANOMALY STREAM */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: AI Deterioration Curve Preview (7 cols) */}
        <div className="lg:col-span-7 telemetry-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1E293B] pb-3">
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                    AI Deterioration Forecasting & Decay Curve
                  </h2>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-400 border border-cyan-800">
                    MODEL v9.3-PRO
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Pavement Quality Index (PCI) degradation trajectory over 36 calendar months with dynamic load modeling
                </p>
              </div>

              {/* Scenario Toggles */}
              <div className="flex items-center space-x-1.5 font-mono text-[11px]">
                <button
                  onClick={() => setSelectedScenario('heavy')}
                  className={`px-2.5 py-1 rounded transition ${
                    selectedScenario === 'heavy'
                      ? 'bg-cyan-600 text-white font-semibold'
                      : 'bg-[#162032] text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Heavy (4.2M ESAL)
                </button>
                <button
                  onClick={() => setSelectedScenario('moderate')}
                  className={`px-2.5 py-1 rounded transition ${
                    selectedScenario === 'moderate'
                      ? 'bg-cyan-600 text-white font-semibold'
                      : 'bg-[#162032] text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Moderate
                </button>
              </div>
            </div>

            {/* Legend */}
            <div className="flex flex-wrap items-center gap-4 text-xs font-mono my-3">
              <span className="flex items-center gap-1.5 text-slate-300">
                <span className="w-3 h-0.5 bg-emerald-400 inline-block"></span>
                Recommended Intervention (Mill & Overlay @ M11)
              </span>
              <span className="flex items-center gap-1.5 text-rose-400">
                <span className="w-3 h-0.5 bg-rose-500 inline-block stroke-dasharray"></span>
                Status Quo / Zero Intervention
              </span>
            </div>

            {/* Recharts Curve */}
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={previewCurveData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                  <XAxis dataKey="month" stroke="#64748B" fontSize={11} fontFamily="JetBrains Mono" />
                  <YAxis domain={[0, 100]} stroke="#64748B" fontSize={11} fontFamily="JetBrains Mono" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0D131F', borderColor: '#1E293B', borderRadius: '6px', fontSize: '12px', fontFamily: 'JetBrains Mono' }}
                  />
                  <ReferenceLine y={40} stroke="#EF4444" strokeDasharray="3 3" label={{ value: 'FAIL: PCI 40', fill: '#EF4444', fontSize: 10 }} />
                  <ReferenceLine y={55} stroke="#F59E0B" strokeDasharray="3 3" label={{ value: 'REHAB: PCI 55', fill: '#F59E0B', fontSize: 10 }} />
                  <Line type="monotone" dataKey="mitigated" stroke="#10B981" strokeWidth={2.5} dot={{ r: 3, fill: '#10B981' }} name="Mitigated Trajectory" />
                  <Line type="monotone" dataKey="statusQuo" stroke="#EF4444" strokeWidth={2} strokeDasharray="4 4" dot={{ r: 3, fill: '#EF4444' }} name="Status Quo (No Action)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-3 pt-3 border-t border-[#1E293B] flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">
              CLUSTER: <span className="text-slate-200">COLOMBO-RDA-NET-01</span>
            </span>
            <button
              onClick={() => onNavigateTab('curves')}
              className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold"
            >
              Open Full 36-Month Decay Simulator <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Right: Real-Time Anomaly Stream (5 cols - Matches Page 33) */}
        <div className="lg:col-span-5 telemetry-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-[#1E293B] pb-3">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
                <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                  Real-Time Anomaly Stream
                </h2>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#162032] text-slate-300 border border-[#1E293B]">
                AUTONOMOUS FEED
              </span>
            </div>

            {/* Anomaly list */}
            <div className="space-y-3 mt-3">
              {summary?.anomaly_stream && summary.anomaly_stream.length > 0 ? (
                summary.anomaly_stream.slice(0, 3).map((item, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-lg border transition ${
                      item.badge.startsWith('CRIT')
                        ? 'bg-rose-950/20 border-rose-900/50 hover:border-rose-700'
                        : item.badge.startsWith('WARN')
                        ? 'bg-amber-950/20 border-amber-900/50 hover:border-amber-700'
                        : 'bg-cyan-950/20 border-cyan-900/50 hover:border-cyan-700'
                    }`}
                  >
                    <div className="flex items-center justify-between font-mono text-xs">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            item.badge.startsWith('CRIT')
                              ? 'bg-rose-900 text-rose-200'
                              : item.badge.startsWith('WARN')
                              ? 'bg-amber-900 text-amber-200'
                              : 'bg-cyan-900 text-cyan-200'
                          }`}
                        >
                          {item.badge}
                        </span>
                        <span className="font-semibold text-white truncate max-w-[170px]">
                          {item.section_id} ({item.corridor_id})
                        </span>
                      </div>
                      <span className="text-rose-400 font-semibold text-[11px]">
                        {item.days_to_collapse}d to Failure
                      </span>
                    </div>

                    <div className="mt-2 text-xs text-slate-300 line-clamp-2">
                      <span className="text-slate-500 font-mono">Distress:</span> {item.distress_summary}
                    </div>

                    <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between font-mono text-[11px]">
                      <span className="text-slate-400">
                        PCI: <strong className="text-white">{item.current_pci.toFixed(1)}</strong>
                      </span>
                      <button
                        onClick={() => {
                          if (onInspectAnomaly) onInspectAnomaly(item.section_id);
                          onSelectSection(item.section_id);
                          onNavigateTab('section');
                        }}
                        className="px-2 py-0.5 rounded bg-cyan-900 hover:bg-cyan-800 text-cyan-200 border border-cyan-700 text-[10px] font-semibold transition"
                      >
                        {item.action_type || 'INSPECT PROGNOSIS'}
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-6 text-center text-slate-500 text-xs font-mono">
                  No active anomalies detected in current survey cycle.
                </div>
              )}
            </div>
          </div>

          <button
            onClick={() => onNavigateTab('curves')}
            className="w-full mt-3 py-2 rounded bg-gradient-to-r from-cyan-950 to-blue-900 hover:from-cyan-900 hover:to-blue-800 border border-cyan-800/60 text-slate-100 font-mono text-xs font-semibold flex items-center justify-center gap-2 transition"
          >
            <TrendingDown className="w-3.5 h-3.5 text-cyan-400" />
            SIMULATE 36-MONTH DECAY TRAJECTORIES ({summary?.critical_decay_zones_count || 14} CRITICAL ASSETS)
          </button>
        </div>
      </div>

      {/* BOTTOM SECTION: TARGET SECTOR STRUCTURAL DIAGNOSTICS & TELEMETRY LEDGER */}
      <div className="telemetry-card p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-3">
          <div>
            <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Target Sector Structural Diagnostics & Telemetry Ledger
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Live telemetry monitoring across {sections.length} road corridor segments (RDA Western Province Network)
            </p>
          </div>
          <button
            onClick={() => onNavigateTab('gis')}
            className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold"
          >
            Inspect on GIS Map <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Ledger Table */}
        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#1E293B] text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-2.5">Asset ID</th>
                <th className="pb-2.5">Corridor Name</th>
                <th className="pb-2.5">Chainage</th>
                <th className="pb-2.5">PCI Current</th>
                <th className="pb-2.5">IRI Roughness</th>
                <th className="pb-2.5">Crack Density</th>
                <th className="pb-2.5">Predicted Decay</th>
                <th className="pb-2.5">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E293B] text-slate-300">
              {sections.slice(0, 7).map((sec) => {
                const pci = sec.current_pci;
                const statusBadge =
                  pci < 55
                    ? { label: 'CRIT', color: 'text-rose-400 bg-rose-950/60 border-rose-800' }
                    : pci < 70
                    ? { label: 'WARN', color: 'text-amber-400 bg-amber-950/60 border-amber-800' }
                    : { label: 'NOM', color: 'text-emerald-400 bg-emerald-950/60 border-emerald-800' };

                return (
                  <tr key={sec.id} className="hover:bg-[#131D2E]/60 transition">
                    <td className="py-2.5 font-semibold text-white">{sec.id}</td>
                    <td className="py-2.5 text-slate-300 truncate max-w-[200px]">{sec.corridor_name}</td>
                    <td className="py-2.5 text-slate-400">
                      KM {sec.start_chainage_km.toFixed(1)} - {sec.end_chainage_km.toFixed(1)}
                    </td>
                    <td className="py-2.5">
                      <span className="font-bold text-white mr-1.5">{pci.toFixed(1)}</span>
                      <span className={`text-[10px] px-1 py-0.2 rounded border font-semibold ${statusBadge.color}`}>
                        [{statusBadge.label}]
                      </span>
                    </td>
                    <td className="py-2.5 text-slate-400">{sec.iri_roughness.toFixed(2)} m/km</td>
                    <td className="py-2.5 text-slate-400">{sec.crack_density_pct.toFixed(1)}%</td>
                    <td className="py-2.5 text-rose-400 font-semibold">
                      -{sec.historical_decay_rate_annual.toFixed(1)} PCI/yr
                    </td>
                    <td className="py-2.5">
                      <button
                        onClick={() => {
                          onSelectSection(sec.id);
                          onNavigateTab('section');
                        }}
                        className="px-2.5 py-1 rounded bg-[#162032] hover:bg-cyan-900 text-cyan-400 hover:text-white border border-[#233044] hover:border-cyan-700 text-[11px] font-semibold transition"
                      >
                        INSPECT
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
