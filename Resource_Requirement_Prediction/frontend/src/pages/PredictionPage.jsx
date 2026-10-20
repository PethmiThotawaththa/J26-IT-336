import { useState } from "react";
import { StatusBadge } from "../components/StatusBadge.jsx";

/* ── Constants ─────────────────────────────────────────── */

const REPAIR_TYPES = {
  pothole_patch: {
    label: "Pothole Patching",
    unit: "sq_m",
    unitLabel: "Square metres (sq m)",
    description: "Surface patching of potholes and surface defects",
  },
  drain_cleaning: {
    label: "Drain Cleaning",
    unit: "metres",
    unitLabel: "Metres (m)",
    description: "Clearing and desilting of roadside drainage channels",
  },
  resurfacing: {
    label: "Road Resurfacing",
    unit: "sq_m",
    unitLabel: "Square metres (sq m)",
    description: "Full pavement resurfacing with asphalt overlay",
  },
};

const RESOURCE_INFO = [
  {
    key: "labour_person_days",
    label: "Labour",
    unit: "person-days",
    icon: "👷",
    description: "Workforce effort required",
    color: "#16845B",
  },
  {
    key: "asphalt_tonnes",
    label: "Asphalt",
    unit: "tonnes",
    icon: "🛣️",
    description: "Asphalt material required",
    color: "#386CB0",
  },
  {
    key: "aggregate_tonnes",
    label: "Aggregate",
    unit: "tonnes",
    icon: "🪨",
    description: "Aggregate material required",
    color: "#68736C",
  },
  {
    key: "equipment_hours",
    label: "Equipment",
    unit: "hours",
    icon: "🚜",
    description: "Equipment operating time required",
    color: "#D99A22",
  },
];

function formatNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(2) : "—";
}

function priorityLabel(p) {
  const n = Number(p);
  if (n >= 8) return "High";
  if (n >= 4) return "Medium";
  return "Low";
}

function priorityColor(p) {
  const n = Number(p);
  if (n >= 8) return "#C94040";
  if (n >= 4) return "#D99A22";
  return "#16845B";
}

/* ── Page ──────────────────────────────────────────────── */

export function PredictionPage() {
  const [repairType, setRepairType] = useState("drain_cleaning");
  const [quantity, setQuantity] = useState("120");
  const [priority, setPriority] = useState("5");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const selectedRepair = REPAIR_TYPES[repairType];

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    const quantityValue = Number(quantity);
    const priorityValue = Number(priority);

    if (!Number.isFinite(quantityValue) || quantityValue <= 0) {
      setError("Please enter a quantity greater than zero.");
      return;
    }
    if (!Number.isFinite(priorityValue) || priorityValue < 0 || priorityValue > 10) {
      setError("Priority must be a whole number from 0 to 10.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repair_type: repairType,
          quantity: quantityValue,
          quantity_unit: selectedRepair.unit,
          priority: priorityValue,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join("; ")
          : data.detail;
        throw new Error(
          typeof detail === "string"
            ? detail
            : "Prediction failed. Check the input and API.",
        );
      }

      if (!data.predicted_resources) {
        throw new Error("The API response did not contain predicted resources.");
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message ||
        "Could not connect to the prediction API. Check that the Python backend is running on port 8000.",
      );
    } finally {
      setLoading(false);
    }
  }

  function resetForm() {
    setRepairType("drain_cleaning");
    setQuantity("120");
    setPriority("5");
    setResult(null);
    setError("");
  }

  return (
    <div className="mx-auto max-w-[1400px] px-4 py-8 sm:px-6 lg:px-8">
      {/* ── Page header ─────────────────────────────────── */}
      <div className="mb-8">
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <StatusBadge status="simulated" />
          <span
            className="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5
              text-xs font-semibold tracking-wide uppercase"
            style={{ backgroundColor: "var(--color-light)", color: "#0E5C3C" }}
          >
            Random Forest · 4 features
          </span>
        </div>

        <h1
          className="text-2xl font-bold sm:text-3xl"
          style={{ color: "var(--color-text)" }}
        >
          Resource Prediction Dashboard
        </h1>
        <p
          className="mt-2 max-w-3xl text-sm leading-7"
          style={{ color: "var(--color-secondary)" }}
        >
          Enter road maintenance task details to estimate labour, asphalt,
          aggregate, and equipment requirements using the Random Forest
          regression model. All predictions use <strong>simulated training
          data</strong> and are for research demonstration only.
        </p>
      </div>

      <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-5">

        {/* ── Form panel ──────────────────────────────── */}
        <section
          className="rounded-2xl border p-6 lg:col-span-2"
          style={{
            backgroundColor: "#fff",
            borderColor: "var(--color-border)",
          }}
        >
          <div className="mb-6">
            <h2 className="text-base font-bold" style={{ color: "var(--color-text)" }}>
              Maintenance Task Details
            </h2>
            <p className="mt-1 text-sm" style={{ color: "var(--color-secondary)" }}>
              Provide the task details to estimate resource requirements.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Repair Type */}
            <div>
              <label
                htmlFor="repairType"
                className="mb-2 block text-sm font-semibold"
                style={{ color: "var(--color-text)" }}
              >
                Repair Type
              </label>
              <select
                id="repairType"
                value={repairType}
                onChange={(e) => {
                  setRepairType(e.target.value);
                  setResult(null);
                  setError("");
                }}
                className="w-full rounded-lg border px-4 py-3 text-sm
                  outline-none transition focus:ring-2"
                style={{
                  borderColor: "var(--color-border)",
                  color: "var(--color-text)",
                  "--tw-ring-color": "var(--color-light)",
                }}
              >
                {Object.entries(REPAIR_TYPES).map(([value, repair]) => (
                  <option key={value} value={value}>
                    {repair.label}
                  </option>
                ))}
              </select>
              <p className="mt-1.5 text-xs" style={{ color: "var(--color-secondary)" }}>
                {selectedRepair.description}
              </p>
            </div>

            {/* Quantity */}
            <div>
              <label
                htmlFor="quantity"
                className="mb-2 block text-sm font-semibold"
                style={{ color: "var(--color-text)" }}
              >
                Maintenance Quantity
              </label>
              <div className="relative">
                <input
                  id="quantity"
                  type="number"
                  min="0.01"
                  step="any"
                  required
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  placeholder="Enter quantity"
                  className="w-full rounded-lg border px-4 py-3 pr-20 text-sm
                    outline-none transition focus:ring-2"
                  style={{ borderColor: "var(--color-border)", color: "var(--color-text)" }}
                />
                <span
                  className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2
                    text-xs font-medium"
                  style={{ color: "var(--color-secondary)" }}
                >
                  {selectedRepair.unit}
                </span>
              </div>
              <p className="mt-1.5 text-xs" style={{ color: "var(--color-secondary)" }}>
                Unit: {selectedRepair.unitLabel}
              </p>
            </div>

            {/* Priority */}
            <div>
              <div className="mb-2 flex items-center justify-between gap-3">
                <label
                  htmlFor="priority"
                  className="text-sm font-semibold"
                  style={{ color: "var(--color-text)" }}
                >
                  Task Priority
                </label>
                <span
                  className="rounded-lg px-3 py-1 text-sm font-bold"
                  style={{
                    backgroundColor: "var(--color-light)",
                    color: priorityColor(priority),
                  }}
                >
                  {priority || "0"} / 10 · {priorityLabel(priority)}
                </span>
              </div>
              <input
                id="priority"
                type="range"
                min="0"
                max="10"
                step="1"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full"
                style={{ accentColor: "var(--color-brand)" }}
              />
              <div
                className="mt-1 flex justify-between text-xs"
                style={{ color: "var(--color-secondary)" }}
              >
                <span>Low priority (0)</span>
                <span>High priority (10)</span>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div
                role="alert"
                className="rounded-lg border p-4 text-sm leading-6"
                style={{
                  borderColor: "#FBBFBF",
                  backgroundColor: "var(--color-red-bg)",
                  color: "var(--color-red)",
                }}
              >
                <strong className="block mb-1">Unable to predict</strong>
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              id="btn-predict"
              type="submit"
              disabled={loading}
              className="w-full rounded-lg px-5 py-3.5 text-sm font-semibold
                text-white shadow-sm transition-colors focus:outline-none focus:ring-4"
              style={{
                backgroundColor: loading ? "var(--color-secondary)" : "var(--color-brand)",
                "--tw-ring-color": "var(--color-light)",
              }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Predicting resources…
                </span>
              ) : (
                "Predict Resource Requirements"
              )}
            </button>

            <button
              id="btn-reset"
              type="button"
              onClick={resetForm}
              className="w-full rounded-lg border px-5 py-3 text-sm font-semibold transition-colors"
              style={{
                borderColor: "var(--color-border)",
                color: "var(--color-secondary)",
              }}
            >
              Reset Form
            </button>
          </form>

          {/* Request summary */}
          <div
            className="mt-6 rounded-lg p-4"
            style={{ backgroundColor: "var(--color-bg)" }}
          >
            <p
              className="text-xs font-semibold uppercase tracking-wide"
              style={{ color: "var(--color-secondary)" }}
            >
              Request Summary
            </p>
            <p className="mt-2 text-sm leading-6" style={{ color: "var(--color-text)" }}>
              {selectedRepair.label} · {quantity || "0"} {selectedRepair.unit} · Priority {priority}
            </p>
          </div>
        </section>

        {/* ── Results panel ───────────────────────────── */}
        <section className="lg:col-span-3 space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold" style={{ color: "var(--color-text)" }}>
                Predicted Resource Requirements
              </h2>
              <p className="mt-0.5 text-sm" style={{ color: "var(--color-secondary)" }}>
                Results from the Python prediction API
              </p>
            </div>
            {result && <StatusBadge status="predicted" />}
          </div>

          {result ? (
            <>
              {/* Resource cards */}
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {RESOURCE_INFO.map((resource) => (
                  <article
                    key={resource.key}
                    className="rounded-2xl border p-5"
                    style={{
                      backgroundColor: "#fff",
                      borderColor: "var(--color-border)",
                    }}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-xs font-medium uppercase tracking-wide"
                          style={{ color: "var(--color-secondary)" }}>
                          {resource.label}
                        </p>
                        <p className="mt-2 break-words text-3xl font-bold"
                          style={{ color: resource.color }}>
                          {formatNumber(result.predicted_resources[resource.key])}
                        </p>
                        <p className="mt-0.5 text-xs" style={{ color: "var(--color-secondary)" }}>
                          {resource.unit}
                        </p>
                      </div>
                      <div
                        className="flex h-11 w-11 shrink-0 items-center justify-center
                          rounded-xl text-xl"
                        style={{ backgroundColor: "var(--color-light)" }}
                        aria-hidden="true"
                      >
                        {resource.icon}
                      </div>
                    </div>
                    <p
                      className="mt-4 border-t pt-3 text-xs"
                      style={{ borderColor: "var(--color-border)", color: "var(--color-secondary)" }}
                    >
                      {resource.description}
                    </p>
                  </article>
                ))}
              </div>

              {/* Summary table */}
              <div
                className="rounded-xl border p-5"
                style={{ backgroundColor: "#fff", borderColor: "var(--color-border)" }}
              >
                <h3 className="mb-4 text-sm font-bold" style={{ color: "var(--color-text)" }}>
                  Prediction Summary
                </h3>
                <dl className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                  {[
                    { label: "Repair type", value: selectedRepair.label },
                    { label: "Quantity", value: `${result.input?.quantity ?? quantity} ${selectedRepair.unit}` },
                    { label: "Priority", value: `${result.input?.priority ?? priority} / 10` },
                    { label: "Data status", value: result.data_status || "Not specified" },
                  ].map(({ label, value }) => (
                    <div key={label}>
                      <dt className="text-xs" style={{ color: "var(--color-secondary)" }}>{label}</dt>
                      <dd className="mt-1 text-sm font-semibold" style={{ color: "var(--color-text)" }}>
                        {value}
                      </dd>
                    </div>
                  ))}
                </dl>

                {/* Resource table */}
                <div className="mt-5 overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr
                        className="border-b text-left"
                        style={{ borderColor: "var(--color-border)" }}
                      >
                        <th className="pb-2 pr-4 text-xs font-semibold"
                          style={{ color: "var(--color-secondary)" }}>Resource</th>
                        <th className="pb-2 pr-4 text-xs font-semibold text-right"
                          style={{ color: "var(--color-secondary)" }}>Predicted</th>
                        <th className="pb-2 text-xs font-semibold"
                          style={{ color: "var(--color-secondary)" }}>Unit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {RESOURCE_INFO.map((resource, idx) => (
                        <tr
                          key={resource.key}
                          className={idx < RESOURCE_INFO.length - 1 ? "border-b" : ""}
                          style={{ borderColor: "var(--color-border)" }}
                        >
                          <td className="py-2 pr-4 font-medium" style={{ color: "var(--color-text)" }}>
                            {resource.icon} {resource.label}
                          </td>
                          <td className="py-2 pr-4 text-right font-mono font-semibold"
                            style={{ color: resource.color }}>
                            {formatNumber(result.predicted_resources[resource.key])}
                          </td>
                          <td className="py-2 text-xs" style={{ color: "var(--color-secondary)" }}>
                            {resource.unit}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            /* Empty state */
            <div
              className="flex min-h-72 flex-col items-center justify-center rounded-2xl
                border-2 border-dashed px-6 py-12 text-center"
              style={{ borderColor: "var(--color-border)", backgroundColor: "#fff" }}
            >
              <div
                className="flex h-16 w-16 items-center justify-center rounded-2xl text-3xl"
                style={{ backgroundColor: "var(--color-light)" }}
                aria-hidden="true"
              >
                📊
              </div>
              <h3 className="mt-5 text-base font-bold" style={{ color: "var(--color-text)" }}>
                Your prediction will appear here
              </h3>
              <p className="mt-2 max-w-sm text-sm leading-6" style={{ color: "var(--color-secondary)" }}>
                Enter the task details and select{" "}
                <strong>Predict Resource Requirements</strong> to view the
                estimated resource quantities from the API.
              </p>
            </div>
          )}

          {/* Model info / warning panel */}
          <div
            className="rounded-xl border p-5"
            style={{
              borderColor: "#F5D580",
              backgroundColor: "var(--color-amber-bg)",
            }}
          >
            <div className="flex items-start gap-3">
              <span className="mt-0.5 text-base" aria-hidden="true">⚠️</span>
              <div>
                <h3 className="text-sm font-bold" style={{ color: "#7A5300" }}>
                  Research Prototype — Simulated Training Data
                </h3>
                <p className="mt-1.5 text-xs leading-5" style={{ color: "#7A5300" }}>
                  This model (RandomForestRegressor) was trained on{" "}
                  <strong>24 synthetic/simulated records</strong>. The metrics
                  below do <strong>not</strong> demonstrate real-world accuracy.
                  Estimates must not be used for actual roadworks without
                  validation against approved engineering norms.
                </p>
                <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
                  {[
                    { label: "Labour MAE", value: "1.19 pd" },
                    { label: "Asphalt MAE", value: "2.81 t" },
                    { label: "Aggregate MAE", value: "0.97 t" },
                    { label: "Equipment MAE", value: "0.59 hr" },
                  ].map(({ label, value }) => (
                    <div key={label} className="rounded-lg p-2.5"
                      style={{ backgroundColor: "rgba(0,0,0,0.06)" }}>
                      <p className="text-xs" style={{ color: "#7A5300" }}>{label}</p>
                      <p className="text-sm font-bold" style={{ color: "#7A5300" }}>{value}</p>
                    </div>
                  ))}
                </div>
                {result?.warning && (
                  <p className="mt-3 border-t pt-3 text-xs leading-5"
                    style={{ borderColor: "#F5D580", color: "#7A5300" }}>
                    API: {result.warning}
                  </p>
                )}
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
