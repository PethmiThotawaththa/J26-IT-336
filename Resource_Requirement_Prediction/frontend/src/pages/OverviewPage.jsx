import { useApiHealth } from "../hooks/useApiHealth.js";
import { StatusBadge } from "../components/StatusBadge.jsx";

const DEMO_KPI = [
  {
    id: "total-tasks",
    label: "Total Maintenance Tasks",
    value: "3",
    unit: "tasks",
    icon: "📋",
    color: "var(--color-brand)",
    note: "DEMO data — 3 simulated tasks",
  },
  {
    id: "labour-predicted",
    label: "Predicted Labour",
    value: "—",
    unit: "person-days",
    icon: "👷",
    color: "#386CB0",
    note: "Run a prediction to populate",
  },
  {
    id: "material-predicted",
    label: "Predicted Asphalt",
    value: "—",
    unit: "tonnes",
    icon: "🛣️",
    color: "#68736C",
    note: "Run a prediction to populate",
  },
  {
    id: "tasks-shortage",
    label: "Tasks with Shortage",
    value: "2",
    unit: "tasks",
    icon: "⚠️",
    color: "#D99A22",
    note: "Based on DEMO allocation run",
  },
  {
    id: "resources-available",
    label: "Resource Categories",
    value: "6",
    unit: "resources",
    icon: "📦",
    color: "#16845B",
    note: "Labour, materials, equipment",
  },
  {
    id: "planning-period",
    label: "Active Planning Period",
    value: "DEMO",
    unit: "period",
    icon: "📅",
    color: "#123B2A",
    note: "Demo period — no real period loaded",
  },
];

const PHASE_CARDS = [
  {
    id: "nav-history",
    icon: "📂",
    title: "Historical Data",
    desc: "View, search, filter, and import road maintenance records across years and planning periods.",
    page: "history",
    badge: "Phase 2",
  },
  {
    id: "nav-prediction",
    icon: "🤖",
    title: "Resource Prediction",
    desc: "Use the Random Forest model to predict labour, asphalt, aggregate, and equipment requirements.",
    page: "prediction",
    badge: "Active",
    active: true,
  },
  {
    id: "nav-inventory",
    icon: "📦",
    title: "Resource Inventory",
    desc: "Manage available labour teams, materials stock, and equipment capacity for a planning period.",
    page: "inventory",
    badge: "Phase 3",
  },
  {
    id: "nav-allocation",
    icon: "⚙️",
    title: "Allocation Planner",
    desc: "Run NSGA-II multi-objective optimisation and compare against the greedy priority baseline.",
    page: "allocation",
    badge: "Phase 5",
  },
  {
    id: "nav-results",
    icon: "📊",
    title: "Results & Reports",
    desc: "View allocation outcomes, resource utilisation, Pareto fronts, and export reports.",
    page: "results",
    badge: "Phase 6",
  },
  {
    id: "nav-map",
    icon: "🗺️",
    title: "Map View",
    desc: "Visualise geographically referenced maintenance tasks using Google Maps when coordinates are available.",
    page: "map",
    badge: "Phase 7",
  },
];

/**
 * OverviewPage — application home dashboard.
 * @param {{ onNavigate: (page: string) => void }} props
 */
export function OverviewPage({ onNavigate }) {
  const { status, modelAvailable } = useApiHealth();

  return (
    <div className="mx-auto max-w-[1400px] px-4 py-8 sm:px-6 lg:px-8">

      {/* ── Page header ─────────────────────────────── */}
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <StatusBadge status="demo" />
            <StatusBadge status="simulated" />
          </div>
          <h1
            className="text-2xl font-bold sm:text-3xl"
            style={{ color: "var(--color-text)" }}
          >
            Overview Dashboard
          </h1>
          <p
            className="mt-1 max-w-2xl text-sm leading-6"
            style={{ color: "var(--color-secondary)" }}
          >
            System overview for the AI-driven road maintenance resource planning
            prototype. KPI values below are based on the{" "}
            <strong>DEMO simulation dataset</strong> and will update as real
            data is loaded in later phases.
          </p>
        </div>

        {/* API / model status card */}
        <div
          className="shrink-0 rounded-xl border p-4 min-w-[200px]"
          style={{
            backgroundColor: "#fff",
            borderColor: "var(--color-border)",
          }}
        >
          <p className="text-xs font-semibold uppercase tracking-wide"
            style={{ color: "var(--color-secondary)" }}>
            System Status
          </p>
          <div className="mt-2 space-y-1.5">
            <div className="flex items-center justify-between gap-3">
              <span className="text-xs" style={{ color: "var(--color-secondary)" }}>API</span>
              <span
                className={`text-xs font-semibold ${
                  status === "connected" ? "text-green-700" :
                  status === "disconnected" ? "text-red-600" : "text-amber-600"
                }`}
              >
                {status === "connected" ? "✓ Connected" :
                 status === "disconnected" ? "✗ Disconnected" : "… Checking"}
              </span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <span className="text-xs" style={{ color: "var(--color-secondary)" }}>ML Model</span>
              <span
                className={`text-xs font-semibold ${
                  modelAvailable === true ? "text-green-700" :
                  modelAvailable === false ? "text-red-600" : "text-amber-600"
                }`}
              >
                {modelAvailable === true ? "✓ Loaded" :
                 modelAvailable === false ? "✗ Missing" : "…"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ── KPI Cards ───────────────────────────────── */}
      <section aria-labelledby="kpi-heading" className="mb-10">
        <h2
          id="kpi-heading"
          className="mb-4 text-sm font-semibold uppercase tracking-wide"
          style={{ color: "var(--color-secondary)" }}
        >
          Key Metrics (Demo Data)
        </h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {DEMO_KPI.map((kpi) => (
            <article
              key={kpi.id}
              id={kpi.id}
              className="rounded-xl border p-4"
              style={{
                backgroundColor: "#fff",
                borderColor: "var(--color-border)",
              }}
            >
              <div
                className="flex h-9 w-9 items-center justify-center rounded-lg text-lg mb-3"
                style={{ backgroundColor: "var(--color-light)" }}
                aria-hidden="true"
              >
                {kpi.icon}
              </div>
              <p className="text-2xl font-bold tabular-nums"
                style={{ color: kpi.color }}>
                {kpi.value}
              </p>
              <p className="text-xs mt-0.5" style={{ color: "var(--color-secondary)" }}>
                {kpi.unit}
              </p>
              <p className="mt-2 text-xs leading-4 font-medium"
                style={{ color: "var(--color-text)" }}>
                {kpi.label}
              </p>
              <p className="mt-1 text-[11px]" style={{ color: "var(--color-secondary)" }}>
                {kpi.note}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* ── Workflow pipeline visual ─────────────────── */}
      <section aria-labelledby="workflow-heading" className="mb-10">
        <h2
          id="workflow-heading"
          className="mb-4 text-sm font-semibold uppercase tracking-wide"
          style={{ color: "var(--color-secondary)" }}
        >
          Research Workflow
        </h2>
        <div className="overflow-x-auto pb-2">
          <div className="flex items-center gap-0 min-w-max">
            {[
              "Historical Data",
              "ML Prediction",
              "Resource Inventory",
              "NSGA-II Allocation",
              "Greedy Baseline",
              "Results & Reports",
              "Map View",
            ].map((step, i, arr) => (
              <div key={step} className="flex items-center">
                <div
                  className="flex flex-col items-center"
                  style={{ minWidth: "90px" }}
                >
                  <div
                    className="h-8 w-8 rounded-full flex items-center justify-center
                      text-sm font-bold text-white"
                    style={{ backgroundColor: "var(--color-brand)" }}
                    aria-hidden="true"
                  >
                    {i + 1}
                  </div>
                  <p className="mt-1.5 text-center text-[11px] font-medium leading-3"
                    style={{ color: "var(--color-text)", maxWidth: "80px" }}>
                    {step}
                  </p>
                </div>
                {i < arr.length - 1 && (
                  <div
                    className="mx-1 h-0.5 w-6 shrink-0"
                    style={{ backgroundColor: "var(--color-border)" }}
                    aria-hidden="true"
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Module cards ────────────────────────────── */}
      <section aria-labelledby="modules-heading">
        <h2
          id="modules-heading"
          className="mb-4 text-sm font-semibold uppercase tracking-wide"
          style={{ color: "var(--color-secondary)" }}
        >
          System Modules
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {PHASE_CARDS.map((card) => (
            <button
              key={card.id}
              id={card.id}
              type="button"
              onClick={() => onNavigate(card.page)}
              className="group rounded-xl border p-5 text-left transition-all
                hover:shadow-md"
              style={{
                backgroundColor: "#fff",
                borderColor: card.active
                  ? "var(--color-brand)"
                  : "var(--color-border)",
              }}
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <div
                  className="flex h-10 w-10 items-center justify-center rounded-xl text-xl"
                  style={{ backgroundColor: "var(--color-light)" }}
                  aria-hidden="true"
                >
                  {card.icon}
                </div>
                <span
                  className="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  style={
                    card.active
                      ? { backgroundColor: "var(--color-light)", color: "var(--color-brand)" }
                      : { backgroundColor: "var(--color-bg)", color: "var(--color-secondary)" }
                  }
                >
                  {card.badge}
                </span>
              </div>
              <h3
                className="text-sm font-bold group-hover:underline"
                style={{ color: "var(--color-text)" }}
              >
                {card.title}
              </h3>
              <p
                className="mt-1.5 text-xs leading-5"
                style={{ color: "var(--color-secondary)" }}
              >
                {card.desc}
              </p>
            </button>
          ))}
        </div>
      </section>

      {/* ── Important disclaimers ────────────────────── */}
      <div
        className="mt-10 rounded-xl border p-5"
        style={{
          borderColor: "#F5D580",
          backgroundColor: "var(--color-amber-bg)",
        }}
      >
        <h3 className="text-sm font-bold mb-2" style={{ color: "#7A5300" }}>
          ⚠️ Research Prototype Limitations
        </h3>
        <ul className="space-y-1">
          {[
            "All demo training data is SIMULATED and does not represent actual RDA resource-consumption records.",
            "The Random Forest model was trained on 24 synthetic examples. Metrics do not establish real-world accuracy.",
            "NSGA-II and greedy allocations use invented demo values. They are not operational RDA allocation plans.",
            "Geographical coordinates in the demo data are illustrative only — not verified field measurements.",
            "This prototype requires validation against real engineering norms before any operational use.",
          ].map((item) => (
            <li key={item} className="flex items-start gap-2 text-xs leading-5"
              style={{ color: "#7A5300" }}>
              <span aria-hidden="true">·</span>
              {item}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
