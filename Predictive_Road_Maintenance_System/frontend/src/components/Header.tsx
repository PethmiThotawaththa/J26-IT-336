import React from 'react';
import { Search, Zap, Radio, Satellite, RefreshCw } from 'lucide-react';

interface HeaderProps {
  onQuickDispatch?: () => void;
  networkPci?: number;
  totalKm?: number;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onQuickDispatch,
  networkPci = 78.4,
  totalKm = 67.2,
  onRefresh,
  isRefreshing = false
}) => {
  return (
    <header className="h-14 bg-[#0D131F]/90 backdrop-blur border-b border-[#1E293B] px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Left status telemetry */}
      <div className="flex items-center space-x-5 text-xs font-mono">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-slate-400 uppercase tracking-wider text-[11px]">MODEL ENGINE:</span>
          <span className="text-emerald-400 font-semibold">ONLINE</span>
        </div>
        <div className="hidden md:flex items-center space-x-1.5 text-slate-400">
          <span>LATENCY:</span>
          <span className="text-cyan-400">18ms</span>
        </div>
        <div className="hidden lg:flex items-center space-x-1.5 text-slate-400">
          <Satellite className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-300">RDA GPS & LiDAR SYNCED</span>
        </div>
        <div className="hidden xl:flex items-center space-x-1.5 text-slate-400">
          <Radio className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-slate-300">EPHEMERIS SYNC: 100%</span>
        </div>
      </div>

      {/* Right actions */}
      <div className="flex items-center space-x-3">
        {/* Network health badge */}
        <div className="hidden sm:flex items-center bg-[#131D2E] border border-[#1E293B] px-2.5 py-1 rounded text-xs font-mono">
          <span className="text-slate-400 mr-2">NETWORK HEALTH:</span>
          <span className={`font-bold ${networkPci >= 70 ? 'text-emerald-400' : networkPci >= 55 ? 'text-amber-400' : 'text-rose-400'}`}>
            {networkPci.toFixed(1)} PCI
          </span>
          <span className="mx-1.5 text-slate-600">|</span>
          <span className="text-slate-400">{totalKm} KM</span>
        </div>

        {/* Refresh button */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-1.5 rounded bg-[#131D2E] border border-[#1E293B] text-slate-400 hover:text-cyan-400 hover:border-cyan-800 transition"
            title="Refresh Telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        )}

        {/* Quick Dispatch CTA button */}
        <button
          onClick={onQuickDispatch}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs font-mono shadow-[0_0_12px_rgba(6,182,212,0.35)] transition"
        >
          <Zap className="w-3.5 h-3.5" />
          <span>QUICK DISPATCH</span>
        </button>
      </div>
    </header>
  );
};
