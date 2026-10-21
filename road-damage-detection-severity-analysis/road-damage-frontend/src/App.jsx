
import { useEffect, useRef, useState } from "react";
import {
  Activity,
  BrainCircuit,
  Camera,
  CheckCircle2,
  FileText,
  Image as ImageIcon,
  Layers,
  LoaderCircle,
  Ruler,
  ScanLine,
  ShieldAlert,
  Upload,
} from "lucide-react";

import "./App.css";

function App() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [removeStrip, setRemoveStrip] = useState(false);
  const [scale, setScale] = useState(2);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  function handleFile(file) {
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setError("Please select a valid road image.");
      return;
    }

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setResults(null);
    setError("");
  }

  async function handleAnalyze() {
    if (!selectedFile) return;

    setLoading(true);
    setError("");
    setResults(null);

    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("remove_rda_strip", String(removeStrip));
    formData.append("assumed_mm_per_pixel", String(scale));

    try {
      // Python FastAPI backend will be connected next.
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("AI backend could not process the image.");
      }

      const data = await response.json();
      setResults(data);
    } catch {
      setError(
        "AI backend is not connected yet. We will connect the existing Python models in the next steps."
      );
    } finally {
      setLoading(false);
    }
  }

  const measurements = results?.measurements;
  const severity = results?.severity_predictions || [];

  function metric(value, digits = 4) {
    return typeof value === "number"
      ? value.toFixed(digits)
      : "—";
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <ScanLine size={25} />
          </div>
          <div>
            <h2>RoadVision AI</h2>
            <p>Research Intelligence</p>
          </div>
        </div>

        <div className="sidebar-section">WORKSPACE</div>

        <div className="nav-item active">
          <Activity size={19} />
          <span>Analysis Dashboard</span>
        </div>

        <div className="nav-item">
          <Layers size={19} />
          <span>Damage Detection</span>
        </div>

        <div className="nav-item">
          <BrainCircuit size={19} />
          <span>Severity Analysis</span>
        </div>

        <div className="nav-item">
          <FileText size={19} />
          <span>Research Results</span>
        </div>

        <div className="sidebar-bottom">
          <ShieldAlert size={19} />
          <div>
            <strong>Research Prototype</strong>
            <p>Experimental AI predictions</p>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            Research Workspace <span>/</span> Dashboard
          </div>
          <div className="system-badge">
            <span className="status-dot" />
            Local AI System
          </div>
        </header>

        <div className="dashboard-content">
          <div className="page-heading">
            <div>
              <p className="eyebrow">ROAD INFRASTRUCTURE INTELLIGENCE</p>
              <h1>Road Damage Analysis</h1>
              <p className="page-description">
                AI-powered crack segmentation, damage measurements and
                experimental severity classification.
              </p>
            </div>

            <div className="version-badge">
              <CheckCircle2 size={17} />
              Prototype V2
            </div>
          </div>

          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-heading">
                <span>Crack Length</span>
                <Ruler size={20} />
              </div>
              <div className="stat-value">
                {metric(measurements?.length_m)}
                <small>m*</small>
              </div>
              <p>Experimental length estimate</p>
            </div>

            <div className="stat-card">
              <div className="stat-heading">
                <span>Average Width</span>
                <ScanLine size={20} />
              </div>
              <div className="stat-value">
                {metric(measurements?.width_m)}
                <small>m*</small>
              </div>
              <p>Experimental width estimate</p>
            </div>

            <div className="stat-card">
              <div className="stat-heading">
                <span>Damage Area</span>
                <Layers size={20} />
              </div>
              <div className="stat-value">
                {metric(measurements?.area_m2, 6)}
                <small>m²*</small>
              </div>
              <p>Experimental surface estimate</p>
            </div>

            <div className="stat-card">
              <div className="stat-heading">
                <span>Detected Regions</span>
                <Activity size={20} />
              </div>
              <div className="stat-value">
                {results?.detected_regions ?? "—"}
              </div>
              <p>AI-detected crack regions</p>
            </div>
          </section>

          <div className="workspace-grid">
            <section className="panel upload-panel">
              <div className="panel-heading">
                <div>
                  <h3>
                    <Upload size={19} />
                    Road Image Input
                  </h3>
                  <p>Upload a road surface image for analysis.</p>
                </div>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                hidden
                onChange={(e) => handleFile(e.target.files[0])}
              />

              <div
                className="upload-zone"
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  handleFile(e.dataTransfer.files[0]);
                }}
              >
                {preview ? (
                  <img
                    src={preview}
                    alt="Selected road"
                    className="upload-preview"
                  />
                ) : (
                  <div className="upload-placeholder">
                    <div className="upload-icon">
                      <Camera size={30} />
                    </div>
                    <strong>Upload Road Image</strong>
                    <p>Drag and drop or click to browse</p>
                    <span>JPG, PNG or WEBP</span>
                  </div>
                )}
              </div>

              {selectedFile && (
                <p className="file-name">
                  <CheckCircle2 size={16} />
                  {selectedFile.name}
                </p>
              )}

              <div className="form-options">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={removeStrip}
                    onChange={(e) => setRemoveStrip(e.target.checked)}
                  />
                  Remove RDA bottom metadata strip
                </label>

                <label className="field-label">
                  Unverified demo scale (mm/pixel)
                  <input
                    className="scale-input"
                    type="number"
                    min="0"
                    step="0.1"
                    value={scale}
                    onChange={(e) => setScale(e.target.value)}
                  />
                </label>
              </div>

              <button
                className="analyze-button"
                onClick={handleAnalyze}
                disabled={!selectedFile || loading}
              >
                {loading ? (
                  <>
                    <LoaderCircle size={18} className="spin" />
                    Processing Image...
                  </>
                ) : (
                  <>
                    <BrainCircuit size={19} />
                    Run AI Analysis
                  </>
                )}
              </button>

              {error && <p className="error-message">{error}</p>}
            </section>

            <section className="panel results-panel">
              <div className="panel-heading">
                <div>
                  <h3>
                    <ScanLine size={19} />
                    AI Detection Results
                  </h3>
                  <p>Original image and model visualizations.</p>
                </div>
              </div>

              <div className="result-image-grid">
                <div className="result-image-card">
                  <h4>
                    <ImageIcon size={16} />
                    Original Image
                  </h4>
                  <div className="image-container">
                    {preview ? (
                      <img src={preview} alt="Original road" />
                    ) : (
                      <div className="empty-image">
                        <ImageIcon size={30} />
                        <span>No image uploaded</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="result-image-card">
                  <h4>
                    <ScanLine size={16} />
                    Crack Segmentation
                  </h4>
                  <div className="image-container">
                    {results?.crack_image ? (
                      <img
                        src={results.crack_image}
                        alt="AI crack segmentation"
                      />
                    ) : (
                      <div className="empty-image">
                        <ScanLine size={30} />
                        <span>Awaiting AI analysis</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="result-image-card">
                  <h4>
                    <BrainCircuit size={16} />
                    Severity Prediction
                  </h4>
                  <div className="image-container">
                    {results?.severity_image ? (
                      <img
                        src={results.severity_image}
                        alt="AI severity prediction"
                      />
                    ) : (
                      <div className="empty-image">
                        <BrainCircuit size={30} />
                        <span>Awaiting AI analysis</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </section>
          </div>

          <div className="bottom-grid">
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h3>
                    <BrainCircuit size={19} />
                    Severity Intelligence
                  </h3>
                  <p>Model V2 — experimental Low / High classification.</p>
                </div>
              </div>

              {severity.length > 0 ? (
                <div className="severity-list">
                  {severity.map((region, index) => (
                    <div className="severity-region" key={index}>
                      <div className="severity-region-heading">
                        <strong>Region {region.region_id}</strong>
                        <span className="severity-label">
                          {region.predicted_severity}
                        </span>
                      </div>

                      <p>
                        Low probability:{" "}
                        {(region.low_probability * 100).toFixed(2)}%
                      </p>
                      <p>
                        High probability:{" "}
                        {(region.high_probability * 100).toFixed(2)}%
                      </p>

                      {region.close_to_threshold && (
                        <p className="warning-text">
                          Near decision threshold
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <BrainCircuit size={26} />
                  <p>No severity results available yet.</p>
                </div>
              )}
            </section>

            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h3>
                    <FileText size={19} />
                    Analysis Report
                  </h3>
                  <p>AI-generated research prototype output.</p>
                </div>
              </div>


              
{/* STEP 662 - Download Analysis Report */}
{results?.report && (
  <button
    type="button"
    onClick={() => {
      const blob = new Blob([results.report], {
        type: "text/plain;charset=utf-8",
      });

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = "RoadVision_AI_Analysis_Report.txt";

      document.body.appendChild(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(url);
    }}
    style={{
      width: "100%",
      padding: "12px 16px",
      marginBottom: "15px",
      background: "#ea580c",
      color: "white",
      border: "none",
      borderRadius: "9px",
      fontWeight: "700",
      cursor: "pointer",
    }}
  >
    Download Analysis Report
  </button>
)}


              <div className="report-container">
                {results?.report ? (
                  <pre>{results.report}</pre>
                ) : (
                  <div className="empty-state">
                    <FileText size={26} />
                    <p>Analysis report will appear here.</p>
                  </div>
                )}
              </div>
            </section>
          </div>

          <div className="research-notice">
            <ShieldAlert size={22} />
            <p>
              <strong>Research Prototype — Important:</strong> Physical
              measurements are based on an unverified scale and are
              not calibrated. Severity predictions are not expert
              validated. Classification probabilities are not
              numerical road-damage severity scores.
            </p>
          </div>

          <footer className="dashboard-footer">
            <span>RoadVision AI | Research Prototype V2</span>
            <span>Deep Learning · Computer Vision · Road Analysis</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
