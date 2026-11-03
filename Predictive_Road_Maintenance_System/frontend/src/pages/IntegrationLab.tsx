import React, { useState, useEffect } from 'react';
import { 
  Share2, 
  Send, 
  CheckCircle2, 
  ArrowRight, 
  Layers, 
  AlertTriangle,
  Code,
  Sparkles,
  Zap
} from 'lucide-react';
import { fetchMockFixtures, submitIntegrationPayload } from '../services/api';

export const IntegrationLab: React.FC = () => {
  const [fixtures, setFixtures] = useState<any[]>([]);
  const [selectedFixtureIdx, setSelectedFixtureIdx] = useState<number>(0);
  const [payloadText, setPayloadText] = useState<string>('');
  const [response, setResponse] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    loadFixtures();
  }, []);

  const loadFixtures = async () => {
    try {
      const res = await fetchMockFixtures();
      const fixList = res.fixtures || [];
      setFixtures(fixList);
      if (fixList.length > 0) {
        setPayloadText(JSON.stringify(fixList[0], null, 2));
      }
    } catch (e) {
      console.error('Failed to load mock fixtures', e);
    }
  };

  const handleSelectFixture = (idx: number) => {
    setSelectedFixtureIdx(idx);
    setPayloadText(JSON.stringify(fixtures[idx], null, 2));
    setResponse(null);
    setErrorMsg(null);
  };

  const handleTestSubmit = async () => {
    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      const parsed = JSON.parse(payloadText);
      const res = await submitIntegrationPayload(parsed);
      setResponse(res);
    } catch (e: any) {
      setErrorMsg(e.message || 'Submission failed. Please check JSON schema.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-4">
        <div>
          <div className="text-[11px] font-mono text-cyan-400 tracking-wider uppercase flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            SYSTEM INTEGRATION ADAPTER // MODULE L CONTRACT VERIFIER
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight mt-0.5">
            Inter-Component Integration & Telemetry Ingestion Lab
          </h1>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded bg-[#131D2E] border border-[#1E293B] text-slate-300">
            COMPONENTS 1, 2, 3 ADAPTER: READY
          </span>
          <span className="px-2.5 py-1 rounded bg-emerald-950 border border-emerald-800 text-emerald-400">
            PYDANTIC CONTRACT VALIDATED
          </span>
        </div>
      </div>

      {/* COMPONENT INTERACTION ARCHITECTURE CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono text-xs">
        <div className="telemetry-card p-4 border-t-2 border-t-cyan-500">
          <div className="text-cyan-400 font-bold uppercase">Component 1</div>
          <div className="font-semibold text-white mt-1">Road Damage Detection & Severity</div>
          <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
            YOLO computer vision crack segmentation, pothole detection bounding boxes & GPS telemetry.
          </p>
        </div>

        <div className="telemetry-card p-4 border-t-2 border-t-blue-500">
          <div className="text-blue-400 font-bold uppercase">Component 2</div>
          <div className="font-semibold text-white mt-1">Repair Priority & Decision Support</div>
          <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
            P1/P2/P3 repair priority ranking, multi-criteria decision index, and urgent repair recommendations.
          </p>
        </div>

        <div className="telemetry-card p-4 border-t-2 border-t-purple-500">
          <div className="text-purple-400 font-bold uppercase">Component 3</div>
          <div className="font-semibold text-white mt-1">Multi-Resource Allocation & Planning</div>
          <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
            Contractor crew assignment, paving fleet allocation, bitumen reserves, and dispatch planning.
          </p>
        </div>

        <div className="telemetry-card p-4 border-t-2 border-t-emerald-500 bg-emerald-950/20 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
          <div className="text-emerald-400 font-bold uppercase">Component 4 (My Exclusive Scope)</div>
          <div className="font-semibold text-white mt-1">Predictive Road Management System</div>
          <p className="text-[11px] text-slate-200 mt-1 leading-relaxed">
            Multi-horizon PCI forecasting, 36-month non-linear decay curves, RRL survival estimation, stratigraphy & life-cycle cost optimization.
          </p>
        </div>
      </div>

      {/* TEST PAYLOAD EDITOR & REAL-TIME PROGNOSIS RESPONSE */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Fixture Selector & Payload Editor (6 cols) */}
        <div className="lg:col-span-6 telemetry-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1E293B] pb-3 font-mono">
              <div className="flex items-center space-x-2">
                <Code className="w-4 h-4 text-cyan-400" />
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Upstream Telemetry Payload
                </h2>
              </div>
              <span className="text-xs text-slate-400">Select Mock Simulation Fixture:</span>
            </div>

            {/* Fixture Selector Buttons */}
            <div className="grid grid-cols-3 gap-2 my-3 font-mono text-xs">
              {fixtures.map((f, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectFixture(idx)}
                  className={`p-2 rounded border text-left transition ${
                    selectedFixtureIdx === idx
                      ? 'bg-cyan-950/60 border-cyan-500 text-white font-semibold'
                      : 'bg-[#131D2E] border-[#1E293B] text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <div className="text-[10px] text-cyan-400">{f.source_component.split('_')[1] || 'Comp'}</div>
                  <div className="font-bold truncate mt-0.5">{f.corridor_id} Ch {f.chainage_km}km</div>
                </button>
              ))}
            </div>

            {/* JSON Editor */}
            <div className="mt-2 font-mono text-xs">
              <label className="text-slate-500 text-[10px] uppercase tracking-wider block mb-1">
                JSON PAYLOAD BODY (POST /api/integration/adapter/comp1-3)
              </label>
              <textarea
                value={payloadText}
                onChange={(e) => setPayloadText(e.target.value)}
                rows={12}
                className="w-full bg-[#0D131F] border border-[#1E293B] text-slate-200 rounded p-3 font-mono text-xs leading-relaxed focus:outline-none focus:border-cyan-500 resize-none"
              />
            </div>

            {errorMsg && (
              <div className="mt-2 p-2.5 rounded bg-rose-950/60 border border-rose-800 text-rose-300 font-mono text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                {errorMsg}
              </div>
            )}
          </div>

          <button
            onClick={handleTestSubmit}
            disabled={isSubmitting}
            className="w-full mt-4 py-2.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-bold transition flex items-center justify-center gap-2 shadow-[0_0_12px_rgba(6,182,212,0.3)]"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{isSubmitting ? 'INGESTING & RUNNING PROGNOSIS...' : 'INGEST PAYLOAD & GENERATE PROGNOSIS'}</span>
          </button>
        </div>

        {/* Right: Ingestion Response & Predictive Output (6 cols) */}
        <div className="lg:col-span-6 telemetry-card p-5 font-mono text-xs flex flex-col justify-between">
          <div>
            <div className="border-b border-[#1E293B] pb-3 flex items-center justify-between">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                Component 4 Predictive Response
              </h2>
              {response && (
                <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-bold">
                  HTTP 200 OK
                </span>
              )}
            </div>

            {response ? (
              <div className="mt-4 space-y-4">
                {/* Section Match Banner */}
                <div className="p-3 rounded bg-[#131D2E] border border-cyan-800/60">
                  <div className="flex justify-between items-center text-slate-400">
                    <span>MATCHED RDA ASSET:</span>
                    <span className="font-bold text-cyan-400 text-sm">{response.matched_section_id}</span>
                  </div>
                  <div className="text-[11px] text-slate-300 mt-1">
                    {response.integration_notes}
                  </div>
                </div>

                {/* Multi-Horizon Results */}
                <div className="p-3 rounded bg-[#131D2E] border border-[#1E293B]">
                  <div className="text-slate-400 text-[10px] uppercase font-bold tracking-wider mb-2">
                    PROJECTED DETERIORATION HORIZONS
                  </div>
                  <div className="grid grid-cols-4 gap-2 text-center">
                    <div className="p-2 rounded bg-[#0D131F]">
                      <div className="text-[10px] text-slate-500">3 MOS</div>
                      <div className="text-base font-bold text-white mt-0.5">
                        {response.prognosis?.predicted_condition_horizons?.['3m']}
                      </div>
                    </div>
                    <div className="p-2 rounded bg-[#0D131F]">
                      <div className="text-[10px] text-slate-500">6 MOS</div>
                      <div className="text-base font-bold text-white mt-0.5">
                        {response.prognosis?.predicted_condition_horizons?.['6m']}
                      </div>
                    </div>
                    <div className="p-2 rounded bg-[#0D131F]">
                      <div className="text-[10px] text-slate-500">12 MOS</div>
                      <div className="text-base font-bold text-cyan-400 mt-0.5">
                        {response.prognosis?.predicted_condition_horizons?.['12m']}
                      </div>
                    </div>
                    <div className="p-2 rounded bg-[#0D131F]">
                      <div className="text-[10px] text-slate-500">24 MOS</div>
                      <div className="text-base font-bold text-amber-400 mt-0.5">
                        {response.prognosis?.predicted_condition_horizons?.['24m']}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Remaining Useful Life & Indicated Action */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded bg-[#131D2E] border border-[#1E293B]">
                    <div className="text-slate-500 text-[10px]">REMAINING ROAD LIFE</div>
                    <div className="text-xl font-extrabold text-cyan-400 mt-1">
                      {response.prognosis?.remaining_road_life?.rrl_rehabilitation_months} Months
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">Until PCI reaches 55</div>
                  </div>

                  <div className="p-3 rounded bg-[#131D2E] border border-[#1E293B]">
                    <div className="text-slate-500 text-[10px]">HSR PREVENTIVE SAVINGS</div>
                    <div className="text-xl font-extrabold text-emerald-400 mt-1">
                      +{response.prognosis?.maintenance_recommendation?.roi_percent}% ROI
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">Vs Deferred Rebuild</div>
                  </div>
                </div>

                {/* Recommended Engineering Action */}
                <div className="p-3 rounded bg-emerald-950/20 border border-emerald-900/60">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] text-emerald-400 font-bold uppercase">
                      INDICATED RDA PREVENTIVE ACTION
                    </span>
                    <span className="px-2 py-0.2 rounded bg-emerald-900 text-emerald-200 text-[10px] font-bold">
                      {response.prognosis?.maintenance_recommendation?.priority}
                    </span>
                  </div>
                  <div className="font-bold text-white text-sm mt-1">
                    {response.prognosis?.maintenance_recommendation?.action}
                  </div>
                  <div className="text-[11px] text-slate-300 mt-1">
                    Cost: LKR {response.prognosis?.maintenance_recommendation?.estimated_cost_lkr?.toLocaleString()} ({response.prognosis?.maintenance_recommendation?.hsr_item_code})
                  </div>
                </div>
              </div>
            ) : (
              <div className="my-auto py-16 text-center text-slate-500">
                <Share2 className="w-8 h-8 text-slate-600 mx-auto mb-2 opacity-50" />
                Select a fixture or enter a telemetry payload and click "INGEST PAYLOAD".
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-[#1E293B] text-[11px] text-slate-500">
            Adapter complies with Component 4 Specification (IT23191174 Proposal Section 4.3).
          </div>
        </div>
      </div>
    </div>
  );
};
