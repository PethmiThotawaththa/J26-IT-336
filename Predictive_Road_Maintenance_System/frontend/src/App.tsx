import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { PredictiveOverview } from './pages/PredictiveOverview';
import { DeteriorationCurves } from './pages/DeteriorationCurves';
import { RoadSectionAnalysis } from './pages/RoadSectionAnalysis';
import { GisRoadOverview } from './pages/GisRoadOverview';
import { ModelEvaluation } from './pages/ModelEvaluation';
import { DatasetManagement } from './pages/DatasetManagement';
import { IntegrationLab } from './pages/IntegrationLab';
import { 
  fetchDashboardSummary, 
  fetchRoads, 
  DashboardSummary, 
  RoadSectionItem 
} from './services/api';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [sections, setSections] = useState<RoadSectionItem[]>([]);
  const [selectedSectionId, setSelectedSectionId] = useState<string>('B047-SEC-001');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [prognosisNotice, setPrognosisNotice] = useState<string | null>(null);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    setIsRefreshing(true);
    try {
      const sum = await fetchDashboardSummary();
      setSummary(sum);
      const rList = await fetchRoads();
      setSections(rList.sections || []);
      if (rList.sections && rList.sections.length > 0) {
        setSelectedSectionId(rList.sections[0].id);
      }
    } catch (e) {
      console.error('Failed to load initial application state', e);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleRunPrognosis = () => {
    setPrognosisNotice('AI 36-Month Prognosis & Decay Simulation Synchronized for Network.');
    setActiveTab('curves');
    setTimeout(() => {
      setPrognosisNotice(null);
    }, 5000);
  };

  return (
    <div className="flex min-h-screen bg-[#0B0F17] text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemStatus={summary?.status || 'ONLINE'}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          onRunPrognosis={handleRunPrognosis}
          networkPci={summary?.structural_health_index || 71.6}
          totalKm={summary?.total_monitored_km || 67.2}
          onRefresh={loadAll}
          isRefreshing={isRefreshing}
        />

        {prognosisNotice && (
          <div className="mx-6 mt-4 p-3 rounded bg-cyan-950/80 border border-cyan-800 text-cyan-300 font-mono text-xs flex items-center justify-between shadow-lg">
            <span>⚡ {prognosisNotice}</span>
            <button onClick={() => setPrognosisNotice(null)} className="text-cyan-400 hover:text-white">✕</button>
          </div>
        )}

        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {activeTab === 'overview' && (
            <PredictiveOverview
              summary={summary}
              sections={sections}
              onSelectSection={setSelectedSectionId}
              onNavigateTab={setActiveTab}
              onInspectAnomaly={(secId) => {
                setSelectedSectionId(secId);
                setActiveTab('section');
              }}
            />
          )}

          {activeTab === 'curves' && (
            <DeteriorationCurves
              sections={sections}
              selectedSectionId={selectedSectionId}
              onSelectSection={setSelectedSectionId}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'section' && (
            <RoadSectionAnalysis
              sections={sections}
              selectedSectionId={selectedSectionId}
              onSelectSection={setSelectedSectionId}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'gis' && (
            <GisRoadOverview
              sections={sections}
              selectedSectionId={selectedSectionId}
              onSelectSection={setSelectedSectionId}
              onNavigateTab={setActiveTab}
            />
          )}

          {activeTab === 'models' && <ModelEvaluation />}

          {activeTab === 'datasets' && <DatasetManagement />}

          {activeTab === 'integration' && <IntegrationLab />}
        </main>
      </div>
    </div>
  );
}

export default App;
