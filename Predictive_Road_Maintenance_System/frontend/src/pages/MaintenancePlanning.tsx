import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  Calendar, 
  DollarSign, 
  Clock, 
  CheckCircle2, 
  Truck, 
  CloudRain, 
  Sun, 
  AlertTriangle,
  Zap,
  Filter
} from 'lucide-react';
import { 
  fetchMaintenanceQueue, 
  fetchMaintenanceGantt, 
  dispatchWorkOrder 
} from '../services/api';

interface Props {
  onSelectSection: (id: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const MaintenancePlanning: React.FC<Props> = ({
  onSelectSection,
  onNavigateTab
}) => {
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [queue, setQueue] = useState<any[]>([]);
  const [ganttData, setGanttData] = useState<any>(null);
  const [dispatchedIds, setDispatchedIds] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    loadData();
  }, [priorityFilter]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const qRes = await fetchMaintenanceQueue(priorityFilter === 'ALL' ? undefined : priorityFilter);
      setQueue(qRes.queue || []);
      const gRes = await fetchMaintenanceGantt();
      setGanttData(gRes);
    } catch (e) {
      console.error('Failed to load maintenance data', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDispatch = async (orderId: string) => {
    try {
      await dispatchWorkOrder(orderId);
      setDispatchedIds((prev) => new Set(prev).add(orderId));
    } catch (e) {
      console.error('Failed to dispatch order', e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-4">
        <div>
          <div className="text-[11px] font-mono text-cyan-400 tracking-wider uppercase flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            DISPATCH ENGINE // MATRIX SCHEDULING (PROPOSAL PAGE 35)
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight mt-0.5">
            Autonomous Maintenance Dispatch & Weather-Locked Gantt Scheduling
          </h1>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded bg-[#131D2E] border border-[#1E293B] text-slate-300">
            OPTIMIZATION: MIN_CO2 // MIN_DELAY
          </span>
          <span className="px-2.5 py-1 rounded bg-emerald-950 border border-emerald-800 text-emerald-400 font-bold">
            CONFIDENCE: 99.1%
          </span>
        </div>
      </div>

      {/* 4 TOP STATUS METRICS (Matches Page 35) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
        {/* Metric 1: Algorithmic Cost Savings */}
        <div className="telemetry-card p-4">
          <div className="flex justify-between text-slate-400">
            <span>ALGORITHMIC COST SAVINGS</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-white mt-2">
            $412,000
          </div>
          <div className="text-[11px] text-emerald-400 mt-1">
            +18.4% <span className="text-slate-400">vs ad-hoc single-site repair</span>
          </div>
        </div>

        {/* Metric 2: Work Orders Queued */}
        <div className="telemetry-card p-4">
          <div className="flex justify-between text-slate-400">
            <span>WORK ORDERS QUEUED</span>
            <Wrench className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-extrabold text-white mt-2">
            {queue.length} <span className="text-xs text-slate-400 font-normal">Scheduled</span>
          </div>
          <div className="text-[11px] text-cyan-400 mt-1">
            Ranked by crack velocity & decay
          </div>
        </div>

        {/* Metric 3: Bitumen Reserve */}
        <div className="telemetry-card p-4">
          <div className="flex justify-between text-slate-400">
            <span>BITUMEN RESERVE</span>
            <span className="text-amber-400">ACTIVE</span>
          </div>
          <div className="text-2xl font-extrabold text-amber-400 mt-2">
            84.0%
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            34,200 gal terminal silo supply
          </div>
        </div>

        {/* Metric 4: Fleet Readiness */}
        <div className="telemetry-card p-4">
          <div className="flex justify-between text-slate-400">
            <span>FLEET READINESS</span>
            <Truck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-white mt-2">
            6 Pavers / 4 Slurry
          </div>
          <div className="text-[11px] text-emerald-400 mt-1">
            100% telemetry link active
          </div>
        </div>
      </div>

      {/* DYNAMIC AI PRIORITY DISPATCH QUEUE (Matches Page 35) */}
      <div className="telemetry-card p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-3 font-mono">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4 text-cyan-400" />
              Dynamic AI Priority Dispatch Queue
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Automated work order staging prioritized by structural collapse urgency, PCI, and economic return
            </p>
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-1.5 text-xs">
            <span className="text-slate-500 flex items-center gap-1 mr-1">
              <Filter className="w-3 h-3" /> FILTER:
            </span>
            {(['ALL', 'P1', 'P2', 'P3'] as const).map((lvl) => (
              <button
                key={lvl}
                onClick={() => setPriorityFilter(lvl)}
                className={`px-2.5 py-1 rounded transition font-semibold ${
                  priorityFilter === lvl
                    ? 'bg-cyan-600 text-white'
                    : 'bg-[#162032] text-slate-400 hover:text-white'
                }`}
              >
                {lvl === 'ALL' ? 'All Orders' : `Priority ${lvl}`}
              </button>
            ))}
          </div>
        </div>

        {/* Queue Table */}
        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#1E293B] text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-2.5">Rank</th>
                <th className="pb-2.5">Asset & Segment ID</th>
                <th className="pb-2.5">Current PCI</th>
                <th className="pb-2.5">Intervention Technique</th>
                <th className="pb-2.5">Cost / Savings</th>
                <th className="pb-2.5">Assigned Crew & ETA</th>
                <th className="pb-2.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E293B] text-slate-300">
              {queue.map((item) => {
                const isDispatched = dispatchedIds.has(item.id) || item.status === 'DISPATCHED';
                const rankColor =
                  item.priority === 'P1'
                    ? 'bg-rose-950 text-rose-300 border-rose-800'
                    : item.priority === 'P2'
                    ? 'bg-amber-950 text-amber-300 border-amber-800'
                    : 'bg-cyan-950 text-cyan-300 border-cyan-800';

                return (
                  <tr key={item.id} className="hover:bg-[#131D2E]/60 transition">
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${rankColor}`}>
                        {item.priority}
                      </span>
                    </td>
                    <td className="py-3">
                      <div className="font-bold text-white">{item.section_id}</div>
                      <div className="text-[11px] text-slate-400">{item.corridor_name} (Ch {item.start_chainage_km?.toFixed(1)} km)</div>
                    </td>
                    <td className="py-3">
                      <span className="font-bold text-white">{item.current_pci?.toFixed(1)}</span>
                      <div className="text-[10px] text-slate-500">{item.crack_density_pct?.toFixed(1)}% cracks</div>
                    </td>
                    <td className="py-3">
                      <div className="text-slate-100 font-semibold">{item.action}</div>
                      <div className="text-[10px] text-cyan-400">{item.hsr_item_code}</div>
                    </td>
                    <td className="py-3">
                      <div className="text-emerald-400 font-bold">
                        LKR {item.estimated_cost_lkr?.toLocaleString()}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        Rescue: +LKR {item.preventive_savings_lkr?.toLocaleString()}
                      </div>
                    </td>
                    <td className="py-3">
                      <div className="text-slate-200">{item.assigned_crew}</div>
                      <div className="text-[10px] text-slate-400 font-semibold">{item.urgency_days}d Urgency Deadline</div>
                    </td>
                    <td className="py-3 text-right">
                      {isDispatched ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[11px] font-semibold">
                          <CheckCircle2 className="w-3 h-3" /> DISPATCHED
                        </span>
                      ) : (
                        <button
                          onClick={() => handleDispatch(item.id)}
                          className="px-3 py-1 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-[11px] transition shadow-[0_0_8px_rgba(6,182,212,0.3)]"
                        >
                          DISPATCH
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 14-DAY WEATHER-LOCKED MAINTENANCE GANTT (Matches Page 35) */}
      <div className="telemetry-card p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-3 font-mono">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Calendar className="w-4 h-4 text-cyan-400" />
              14-Day Rolling Maintenance Gantt (Weather Telemetry Synced)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Automatic rainfall lockout detection prevents premature bitumen surfacing failures
            </p>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-400">
            COLOMBO METEOROLOGICAL LINK ACTIVE
          </span>
        </div>

        {/* Gantt Timeline Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-7 gap-2 mt-4 font-mono text-xs">
          {ganttData?.schedule?.map((item: any, idx: number) => {
            const isLockout = item.lockout;
            return (
              <div
                key={idx}
                className={`p-3 rounded border flex flex-col justify-between ${
                  isLockout
                    ? 'bg-rose-950/30 border-rose-900/60 text-rose-200'
                    : 'bg-[#131D2E] border-[#1E293B] text-slate-200 hover:border-cyan-800'
                } transition`}
              >
                <div>
                  <div className="flex justify-between items-center text-[11px]">
                    <span className="font-bold text-white">{item.day}</span>
                    <span
                      className={`flex items-center gap-1 text-[10px] font-semibold ${
                        isLockout ? 'text-rose-400' : 'text-emerald-400'
                      }`}
                    >
                      {isLockout ? <CloudRain className="w-3 h-3" /> : <Sun className="w-3 h-3" />}
                      {item.weather}
                    </span>
                  </div>
                  <div className="mt-2 text-[11px] font-semibold line-clamp-2">
                    {item.task}
                  </div>
                </div>

                <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-400">
                  {item.corridor}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
