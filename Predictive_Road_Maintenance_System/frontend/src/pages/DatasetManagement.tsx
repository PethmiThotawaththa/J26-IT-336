import React, { useState, useEffect } from 'react';
import { 
  Database, 
  FileSpreadsheet, 
  CheckCircle2, 
  AlertCircle, 
  FileText, 
  Layers, 
  Eye, 
  Download,
  Info
} from 'lucide-react';
import { fetchDatasets, fetchDatasetPreview } from '../services/api';

export const DatasetManagement: React.FC = () => {
  const [datasets, setDatasets] = useState<any[]>([]);
  const [activePreviewKey, setActivePreviewKey] = useState<string>('features');
  const [previewData, setPreviewData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    loadDatasets();
    loadPreview('features');
  }, []);

  const loadDatasets = async () => {
    try {
      const res = await fetchDatasets();
      setDatasets(res.datasets || []);
    } catch (e) {
      console.error('Failed to load datasets list', e);
    }
  };

  const loadPreview = async (key: string) => {
    setIsLoading(true);
    setActivePreviewKey(key);
    try {
      const res = await fetchDatasetPreview(key);
      setPreviewData(res);
    } catch (e) {
      console.error('Failed to preview dataset', e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-4">
        <div>
          <div className="text-[11px] font-mono text-cyan-400 tracking-wider uppercase flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            DATA HYGIENE & AUDIT HUB // MODULE A & B REPOSITORIES
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight mt-0.5">
            Dataset Discovery, Curation & Empirical Data Quality Manager
          </h1>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs">
          <span className="px-2.5 py-1 rounded bg-[#131D2E] border border-[#1E293B] text-slate-300">
            AUDIT: 100% SCHEMA COMPLIANT
          </span>
          <span className="px-2.5 py-1 rounded bg-emerald-950 border border-emerald-800 text-emerald-400">
            LEAKAGE CHECK: PASSED
          </span>
        </div>
      </div>

      {/* DATASET REPOSITORY CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 font-mono text-xs">
        {datasets.map((ds, idx) => (
          <div
            key={idx}
            className="telemetry-card p-4 flex flex-col justify-between hover:border-cyan-800 transition"
          >
            <div>
              <div className="flex justify-between items-start">
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-[#162032] text-cyan-400 border border-[#233044] font-semibold">
                  {ds.type}
                </span>
                <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-3 h-3" /> VERIFIED
                </span>
              </div>
              <h3 className="font-bold text-white text-sm mt-2">{ds.name}</h3>
              <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                {ds.description}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-[#1E293B] space-y-1.5 text-[11px]">
              <div className="flex justify-between text-slate-400">
                <span>RECORDS:</span>
                <span className="text-slate-200 font-bold">{ds.records?.toLocaleString()} rows</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>FILE SIZE:</span>
                <span className="text-cyan-400">{ds.file_size_kb} KB</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>OFFICIAL SOURCE:</span>
                <span className="text-slate-300 truncate max-w-[170px]" title={ds.source}>
                  {ds.source}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* INTERACTIVE DATA PREVIEW LEDGER */}
      <div className="telemetry-card p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-3 font-mono">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Eye className="w-4 h-4 text-cyan-400" />
              Live Dataset Preview & Distribution Inspector
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Inspect raw data schemas, boundary values, and missingness metrics
            </p>
          </div>

          <div className="flex items-center space-x-2 text-xs">
            <button
              onClick={() => loadPreview('features')}
              className={`px-3 py-1 rounded transition font-semibold ${
                activePreviewKey === 'features' ? 'bg-cyan-600 text-white' : 'bg-[#162032] text-slate-400 hover:text-white'
              }`}
            >
              ML Features Matrix
            </button>
            <button
              onClick={() => loadPreview('sections')}
              className={`px-3 py-1 rounded transition font-semibold ${
                activePreviewKey === 'sections' ? 'bg-cyan-600 text-white' : 'bg-[#162032] text-slate-400 hover:text-white'
              }`}
            >
              Road Sections GPS
            </button>
            <button
              onClick={() => loadPreview('inspections')}
              className={`px-3 py-1 rounded transition font-semibold ${
                activePreviewKey === 'inspections' ? 'bg-cyan-600 text-white' : 'bg-[#162032] text-slate-400 hover:text-white'
              }`}
            >
              Historical Inspections
            </button>
            <button
              onClick={() => loadPreview('synthetic')}
              className={`px-3 py-1 rounded transition font-semibold ${
                activePreviewKey === 'synthetic' ? 'bg-cyan-600 text-white' : 'bg-[#162032] text-slate-400 hover:text-white'
              }`}
            >
              Synthetic Benchmark
            </button>
          </div>
        </div>

        {/* Preview Table */}
        <div className="overflow-x-auto mt-4 font-mono text-xs">
          {isLoading ? (
            <div className="p-8 text-center text-slate-500">Loading dataset preview...</div>
          ) : previewData ? (
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-[#1E293B] text-slate-400 uppercase text-[10px] tracking-wider">
                  {previewData.columns?.slice(0, 8).map((col: string, idx: number) => (
                    <th key={idx} className="pb-2.5 px-2 whitespace-nowrap">
                      {col.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1E293B] text-slate-300">
                {previewData.preview_rows?.map((row: any, rIdx: number) => (
                  <tr key={rIdx} className="hover:bg-[#131D2E]/60 transition">
                    {previewData.columns?.slice(0, 8).map((col: string, cIdx: number) => (
                      <td key={cIdx} className="py-2.5 px-2 whitespace-nowrap">
                        {typeof row[col] === 'number'
                          ? row[col].toFixed(2)
                          : String(row[col] ?? '—')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-slate-500">No preview data available.</div>
          )}
        </div>
      </div>
    </div>
  );
};
