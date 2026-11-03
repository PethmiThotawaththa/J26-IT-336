import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { 
  MapPin, 
  Layers, 
  Activity, 
  ChevronRight, 
  Sliders, 
  CheckCircle2, 
  AlertTriangle,
  Radio,
  Satellite
} from 'lucide-react';
import { RoadSectionItem } from '../services/api';

interface Props {
  sections: RoadSectionItem[];
  selectedSectionId: string;
  onSelectSection: (id: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const GisRoadOverview: React.FC<Props> = ({
  sections,
  selectedSectionId,
  onSelectSection,
  onNavigateTab
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const [activeCorridor, setActiveCorridor] = useState<string>('ALL');
  
  const selectedSection = sections.find((s) => s.id === selectedSectionId) || sections[0];

  const filteredSections = activeCorridor === 'ALL'
    ? sections
    : sections.filter((s) => s.corridor_id === activeCorridor);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Initialize Leaflet map centered on Colombo, Sri Lanka
    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [6.905, 79.945], // Colombo District RDA highway network
        zoom: 12,
        zoomControl: true
      });

      // Dark Matter CartoDB tiles for high-tech telemetry aesthetic
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://carto.com/">CARTO</a> | Road Development Authority Sri Lanka',
        maxZoom: 19
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    const map = mapInstanceRef.current;

    // Clear previous markers/polylines
    map.eachLayer((layer) => {
      if (layer instanceof L.Polyline || layer instanceof L.CircleMarker) {
        map.removeLayer(layer);
      }
    });

    // Render road section markers and connecting segments
    const validSections = filteredSections.filter(
      (s) => s.start_lat && s.start_lon && !isNaN(s.start_lat) && !isNaN(s.start_lon)
    );

    validSections.forEach((sec) => {
      const pci = sec.current_pci;
      const color = pci >= 70 ? '#10B981' : pci >= 55 ? '#F59E0B' : '#EF4444';
      const isSelected = sec.id === selectedSectionId;

      // Circle marker for station
      const marker = L.circleMarker([sec.start_lat, sec.start_lon], {
        radius: isSelected ? 8 : 4.5,
        fillColor: color,
        color: isSelected ? '#FFFFFF' : color,
        weight: isSelected ? 2.5 : 1,
        opacity: 0.9,
        fillOpacity: 0.8
      }).addTo(map);

      // Popup
      marker.bindPopup(`
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #0F172A;">
          <strong style="color: #0284C7;">${sec.id} (${sec.corridor_id})</strong><br/>
          <span>${sec.corridor_name}</span><br/>
          <span>Chainage: KM ${sec.start_chainage_km.toFixed(1)} - ${sec.end_chainage_km.toFixed(1)}</span><br/>
          <strong>PCI Score: ${pci.toFixed(1)}</strong><br/>
          <span>Cracks: ${sec.crack_density_pct.toFixed(1)}% | Rut: ${sec.rut_depth_mm.toFixed(1)}mm</span>
        </div>
      `);

      marker.on('click', () => {
        onSelectSection(sec.id);
      });

      // Polyline connecting to end coordinate
      if (sec.end_lat && sec.end_lon) {
        L.polyline(
          [
            [sec.start_lat, sec.start_lon],
            [sec.end_lat, sec.end_lon]
          ],
          {
            color: color,
            weight: isSelected ? 4 : 2.5,
            opacity: 0.75
          }
        ).addTo(map);
      }
    });

    // If section selected, pan map to it
    if (selectedSection && selectedSection.start_lat && selectedSection.start_lon) {
      map.panTo([selectedSection.start_lat, selectedSection.start_lon], { animate: true });
    }
  }, [filteredSections, selectedSectionId]);

  return (
    <div className="space-y-6">
      {/* Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1E293B] pb-4">
        <div>
          <div className="text-[11px] font-mono text-cyan-400 tracking-wider uppercase flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            GIS TELEMETRY ENGINE // WGS-84 PSEUDO-MERCATOR EPSG:3857
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight mt-0.5">
            Geospatial Road Corridor Telemetry & Sensor Feed
          </h1>
        </div>
        <div className="flex items-center space-x-2 font-mono text-xs">
          <label className="text-slate-400">FILTER CORRIDOR:</label>
          <select
            value={activeCorridor}
            onChange={(e) => setActiveCorridor(e.target.value)}
            className="bg-[#131D2E] border border-[#1E293B] text-cyan-400 rounded px-2.5 py-1 focus:outline-none focus:border-cyan-600 font-semibold"
          >
            <option value="ALL">All RDA Corridors ({sections.length} Segments)</option>
            <option value="B047">B047: Battaramulla - Pannipitiya</option>
            <option value="B174">B174: Kottawa - Malabe</option>
            <option value="B214">B214: Kirindiwela - Radawana</option>
            <option value="B240">B240: Meegoda - Athurugiriya</option>
            <option value="B263">B263: Madinnagoda - Rajagiriya</option>
            <option value="B435">B435: Sri Jayawardenepura - Kotte</option>
          </select>
        </div>
      </div>

      {/* MAP & TELEMETRY INSPECTOR GRID (Matches Page 36) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Interactive Leaflet Map (8 cols) */}
        <div className="lg:col-span-8 telemetry-card p-2 relative overflow-hidden flex flex-col h-[520px]">
          {/* Map Header Status overlay */}
          <div className="absolute top-4 left-4 z-10 bg-[#0D131F]/90 backdrop-blur border border-[#1E293B] px-3 py-1.5 rounded font-mono text-xs flex items-center space-x-3 shadow-lg">
            <div className="flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300">FLEET: 04 ACTIVE</span>
            </div>
            <span className="text-slate-600">|</span>
            <div className="text-slate-400">
              REFRESH: <span className="text-cyan-400">10 Hz</span>
            </div>
            <span className="text-slate-600">|</span>
            <div className="text-slate-400">
              LATENCY: <span className="text-emerald-400">18ms</span>
            </div>
          </div>

          {/* Map Legend Overlay */}
          <div className="absolute bottom-4 left-4 z-10 bg-[#0D131F]/90 backdrop-blur border border-[#1E293B] p-2.5 rounded font-mono text-[11px] space-y-1 shadow-lg">
            <div className="text-slate-400 text-[10px] uppercase font-bold tracking-wider mb-1">
              SURFACE CONDITION CLASSIFICATION
            </div>
            <div className="flex items-center space-x-2 text-rose-400">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
              <span>CRITICAL (PCI &lt; 55)</span>
            </div>
            <div className="flex items-center space-x-2 text-amber-400">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
              <span>MODERATE (PCI 55 - 70)</span>
            </div>
            <div className="flex items-center space-x-2 text-emerald-400">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <span>HEALTHY (PCI &ge; 70)</span>
            </div>
          </div>

          {/* Actual Map Container */}
          <div ref={mapContainerRef} className="w-full h-full rounded z-0" />
        </div>

        {/* Right: Selected Section Deep Inspector Panel (4 cols - Matches Page 36) */}
        <div className="lg:col-span-4 telemetry-card p-5 font-mono text-xs flex flex-col justify-between">
          <div>
            <div className="border-b border-[#1E293B] pb-3 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider block">[ DEEP TELEMETRY INSPECTOR ]</span>
                <h3 className="text-base font-bold text-white mt-0.5">{selectedSection?.id}</h3>
              </div>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  (selectedSection?.current_pci || 75) < 55
                    ? 'bg-rose-950 text-rose-300 border border-rose-800'
                    : (selectedSection?.current_pci || 75) < 70
                    ? 'bg-amber-950 text-amber-300 border border-amber-800'
                    : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                }`}
              >
                PCI: {selectedSection?.current_pci?.toFixed(1)} / 100
              </span>
            </div>

            {/* Road Corridor Specs */}
            <div className="mt-3 space-y-2 text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-500">CORRIDOR:</span>
                <span className="font-semibold text-white truncate max-w-[170px]">{selectedSection?.corridor_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">CHAINAGE:</span>
                <span className="text-slate-200">KM {selectedSection?.start_chainage_km?.toFixed(2)} - {selectedSection?.end_chainage_km?.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">LAT / LON:</span>
                <span className="text-cyan-400 text-[11px]">{selectedSection?.start_lat?.toFixed(5)}°N, {selectedSection?.start_lon?.toFixed(5)}°E</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">ELEVATION:</span>
                <span className="text-slate-200">+{selectedSection?.altitude_m?.toFixed(1)} m ASL</span>
              </div>
            </div>

            {/* Sensor Telemetry Readings (Matches Page 36) */}
            <div className="mt-4 pt-3 border-t border-[#1E293B]">
              <span className="text-[10px] text-slate-500 uppercase font-semibold tracking-wider block mb-2">
                SENSOR TELEMETRY READINGS
              </span>

              <div className="grid grid-cols-2 gap-2 text-center">
                <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
                  <div className="text-[10px] text-slate-500">CRACK DENSITY</div>
                  <div className="text-sm font-bold text-white mt-0.5">{selectedSection?.crack_density_pct?.toFixed(1)}%</div>
                </div>
                <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
                  <div className="text-[10px] text-slate-500">RUT DEPTH</div>
                  <div className="text-sm font-bold text-amber-400 mt-0.5">{selectedSection?.rut_depth_mm?.toFixed(1)} mm</div>
                </div>
                <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
                  <div className="text-[10px] text-slate-500">IRI ROUGHNESS</div>
                  <div className="text-sm font-bold text-white mt-0.5">{selectedSection?.iri_roughness?.toFixed(2)} m/km</div>
                </div>
                <div className="p-2 rounded bg-[#131D2E] border border-[#1E293B]">
                  <div className="text-[10px] text-slate-500">DAILY ESAL</div>
                  <div className="text-sm font-bold text-cyan-400 mt-0.5">{selectedSection?.daily_esal?.toFixed(0)}</div>
                </div>
              </div>
            </div>

            {/* Predictive Prognosis Snippet */}
            <div className="mt-4 p-3 rounded bg-cyan-950/30 border border-cyan-800/60">
              <div className="text-cyan-400 font-bold text-[11px] flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5" />
                PREDICTIVE AI PROGNOSIS
              </div>
              <p className="text-[11px] text-slate-300 mt-1 leading-relaxed">
                Projected annual condition loss: <strong>-{selectedSection?.historical_decay_rate_annual?.toFixed(1)} PCI/yr</strong> under current commercial axle traffic.
              </p>
            </div>
          </div>

          {/* Action Button */}
          <div className="mt-4 pt-3 border-t border-[#1E293B] space-y-2">
            <button
              onClick={() => onNavigateTab('section')}
              className="w-full py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold transition flex items-center justify-center gap-1.5"
            >
              <span>INSPECT STRATIGRAPHY & XAI</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onNavigateTab('curves')}
              className="w-full py-1.5 rounded bg-[#162032] hover:bg-[#1E2B42] text-slate-300 border border-[#233044] transition"
            >
              View 36-Month Decay Curve
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
