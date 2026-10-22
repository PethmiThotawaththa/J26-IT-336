import React from 'react';
import { 
  Activity, 
  TrendingDown, 
  MapPin, 
  BarChart3, 
  Database, 
  Share2, 
  Sliders,
  ShieldCheck,
  Cpu
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  systemStatus: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, systemStatus }) => {
  const menuItems = [
    { id: 'overview', label: 'Predictive Health', sublabel: 'PCI & Network Life', icon: Activity },
    { id: 'curves', label: 'Deterioration Curves', sublabel: 'AI Decay Simulation', icon: TrendingDown },
    { id: 'section', label: 'Section Telemetry', sublabel: 'Deep Stratigraphy & XAI', icon: Sliders },
    { id: 'gis', label: 'GIS & Road Stream', sublabel: 'GPS & Telemetry Feed', icon: MapPin },
    { id: 'models', label: 'Model Benchmarks', sublabel: 'Algorithm Evaluation', icon: BarChart3 },
    { id: 'datasets', label: 'Dataset Hub', sublabel: 'Data Quality & Hygiene', icon: Database },
    { id: 'integration', label: 'Integration Lab', sublabel: 'Components 1-3 Adapter', icon: Share2 },
  ];

  return (
    <aside className="w-64 bg-[#0D131F] border-r border-[#1E293B] flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand header */}
        <div className="p-4 border-b border-[#1E293B] flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded bg-cyan-600/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-bold font-mono">
              RP
            </div>
            <div>
              <div className="font-bold text-sm tracking-wide text-white flex items-center gap-1.5">
                RoadPredict AI
                <span className="text-[10px] px-1 py-0.2 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">v4.8</span>
              </div>
              <div className="text-[11px] text-slate-400 font-mono">COMPONENT 4 RESEARCH</div>
            </div>
          </div>
        </div>

        {/* Section title */}
        <div className="px-4 py-2.5 text-[10px] uppercase tracking-wider font-semibold text-slate-500 font-mono">
          System Modules
        </div>

        {/* Navigation list */}
        <nav className="space-y-1 px-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-md text-left transition-all ${
                  isActive
                    ? 'bg-cyan-950/60 text-cyan-400 border border-cyan-800/60 shadow-[0_0_12px_rgba(6,182,212,0.15)]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-[#131D2E]'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-medium leading-none truncate">{item.label}</div>
                  <div className="text-[10px] text-slate-500 leading-tight truncate mt-0.5 font-mono">{item.sublabel}</div>
                </div>
                {isActive && (
                  <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_6px_#22d3ee]" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* System state footer */}
      <div className="p-3 border-t border-[#1E293B] bg-[#0A0E17]/80 text-[11px] font-mono space-y-1.5">
        <div className="flex items-center justify-between text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            ENGINE STATUS:
          </span>
          <span className="text-emerald-400 font-semibold">{systemStatus}</span>
        </div>
        <div className="flex items-center justify-between text-slate-500 text-[10px]">
          <span>RESEARCH ID:</span>
          <span className="text-slate-400">SLIIT J26-IT-336</span>
        </div>
        <div className="flex items-center justify-between text-slate-500 text-[10px]">
          <span>TARGET REGION:</span>
          <span className="text-slate-400">RDA Sri Lanka (Colombo)</span>
        </div>
      </div>
    </aside>
  );
};
