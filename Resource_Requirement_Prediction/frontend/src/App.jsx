import { useState } from "react";
import { AppHeader } from "./components/AppHeader.jsx";
import { AppFooter } from "./components/AppFooter.jsx";
import { OverviewPage } from "./pages/OverviewPage.jsx";
import { PredictionPage } from "./pages/PredictionPage.jsx";
import { PlaceholderPage } from "./pages/PlaceholderPage.jsx";

/* ── Page registry ────────────────────────────────────── */

const PAGES = {
  overview: () => null, // rendered below with props
  history: {
    title: "Historical Data",
    phase: "Phase 2",
    icon: "📂",
    description:
      "View, search, filter, and import road maintenance records across years " +
      "and planning periods. Supports CSV/Excel import with validation, " +
      "provenance labels (ACTUAL / ESTIMATED / SIMULATED), and duplicate detection.",
  },
  prediction: () => null, // rendered below
  inventory: {
    title: "Resource Inventory",
    phase: "Phase 3",
    icon: "📦",
    description:
      "Manage available labour teams, materials stock, and equipment capacity " +
      "for a planning period. Includes availability indicators, low-stock " +
      "warnings, and capacity summaries.",
  },
  allocation: {
    title: "Allocation Planner",
    phase: "Phase 5",
    icon: "⚙️",
    description:
      "Select maintenance tasks and a planning period, review inventory " +
      "capacity and predicted demand, then run NSGA-II multi-objective " +
      "optimisation and compare against the greedy priority baseline.",
  },
  results: {
    title: "Results & Reports",
    phase: "Phase 6",
    icon: "📊",
    description:
      "View allocation outcomes, resource utilisation charts, Pareto-front " +
      "visualisation, NSGA-II vs greedy comparison, and export reports " +
      "(CSV / PDF) with full provenance metadata.",
  },
  map: {
    title: "Map View",
    phase: "Phase 7",
    icon: "🗺️",
    description:
      "Visualise geographically referenced maintenance tasks using the Google " +
      "Maps JavaScript API when valid coordinates are available. Requires a " +
      "VITE_GOOGLE_MAPS_API_KEY to be configured.",
  },
};

/* ── App root ─────────────────────────────────────────── */

function App() {
  const [activePage, setActivePage] = useState("overview");

  function renderPage() {
    switch (activePage) {
      case "overview":
        return <OverviewPage onNavigate={setActivePage} />;
      case "prediction":
        return <PredictionPage />;
      default: {
        const cfg = PAGES[activePage];
        if (!cfg) return <OverviewPage onNavigate={setActivePage} />;
        return (
          <PlaceholderPage
            title={cfg.title}
            phase={cfg.phase}
            icon={cfg.icon}
            description={cfg.description}
          />
        );
      }
    }
  }

  return (
    <div
      className="flex min-h-screen flex-col"
      style={{ backgroundColor: "var(--color-bg)" }}
    >
      <AppHeader activePage={activePage} onNavigate={setActivePage} />

      <main id="main-content" className="flex-1" tabIndex={-1}>
        {renderPage()}
      </main>

      <AppFooter onNavigate={setActivePage} />
    </div>
  );
}

export default App;
