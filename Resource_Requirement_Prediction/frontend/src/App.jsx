
import { useState } from "react";

const REPAIR_TYPES = {
  pothole_patch: {
    label: "Pothole Patching",
    unit: "sq_m",
    unitLabel: "Square metres",
  },
  drain_cleaning: {
    label: "Drain Cleaning",
    unit: "metres",
    unitLabel: "Metres",
  },
  resurfacing: {
    label: "Road Resurfacing",
    unit: "sq_m",
    unitLabel: "Square metres",
  },
};

const RESOURCE_INFO = [
  {
    key: "labour_person_days",
    label: "Labour Requirement",
    unit: "person-days",
    icon: "👷",
    description: "Estimated workforce effort",
  },
  {
    key: "asphalt_tonnes",
    label: "Asphalt",
    unit: "tonnes",
    icon: "🛣️",
    description: "Estimated asphalt quantity",
  },
  {
    key: "aggregate_tonnes",
    label: "Aggregate",
    unit: "tonnes",
    icon: "🪨",
    description: "Estimated aggregate quantity",
  },
  {
    key: "equipment_hours",
    label: "Equipment",
    unit: "hours",
    icon: "🚜",
    description: "Estimated equipment usage",
  },
];

function formatNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(2) : "—";
}

function App() {
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

    if (
      !Number.isInteger(priorityValue) ||
      priorityValue < 0 ||
      priorityValue > 10
    ) {
      setError("Priority must be a whole number from 0 to 10.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
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
    <div className="min-h-screen bg-slate-100 text-slate-800">
      <header className="bg-emerald-950 text-white shadow-md">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-5 py-5 sm:px-8">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-800 text-2xl">
            🛣️
          </div>

          <div>
            <h1 className="text-xl font-bold sm:text-2xl">
              Road Maintenance Resource Planner
            </h1>
            <p className="mt-1 text-sm text-emerald-200">
              AI-driven resource requirement prediction
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-8 sm:px-8">
        <section className="mb-8">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">
              RESEARCH PROTOTYPE
            </span>
            <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
              SIMULATED TRAINING DATA
            </span>
          </div>

          <h2 className="mt-4 text-2xl font-bold text-slate-900 sm:text-3xl">
            Resource Prediction Dashboard
          </h2>

          <p className="mt-2 max-w-3xl leading-7 text-slate-600">
            Enter road maintenance task details to estimate labour, asphalt,
            aggregate, and equipment requirements. Predictions are for research
            and demonstration only.
          </p>
        </section>

        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-5">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
            <div className="mb-6">
              <h3 className="text-lg font-bold text-slate-900">
                Maintenance Task Details
              </h3>
              <p className="mt-1 text-sm text-slate-500">
                Provide the details for the task to estimate.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label
                  htmlFor="repairType"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Repair Type
                </label>

                <select
                  id="repairType"
                  value={repairType}
                  onChange={(event) => {
                    setRepairType(event.target.value);
                    setResult(null);
                    setError("");
                  }}
                  className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"
                >
                  {Object.entries(REPAIR_TYPES).map(([value, repair]) => (
                    <option key={value} value={value}>
                      {repair.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  htmlFor="quantity"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Maintenance Quantity
                </label>

                <input
                  id="quantity"
                  type="number"
                  min="0.01"
                  step="any"
                  required
                  value={quantity}
                  onChange={(event) => setQuantity(event.target.value)}
                  placeholder="Enter quantity"
                  className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"
                />

                <p className="mt-2 text-sm text-slate-500">
                  Unit: {selectedRepair.unitLabel}
                </p>
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between gap-3">
                  <label
                    htmlFor="priority"
                    className="text-sm font-semibold text-slate-700"
                  >
                    Task Priority
                  </label>
                  <span className="rounded-lg bg-emerald-50 px-3 py-1 font-bold text-emerald-800">
                    {priority || "0"} / 10
                  </span>
                </div>

                <input
                  id="priority"
                  type="range"
                  min="0"
                  max="10"
                  step="1"
                  value={priority}
                  onChange={(event) => setPriority(event.target.value)}
                  className="w-full accent-emerald-700"
                />

                <div className="mt-1 flex justify-between text-xs text-slate-500">
                  <span>Low priority</span>
                  <span>High priority</span>
                </div>
              </div>

              {error && (
                <div
                  role="alert"
                  className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-800"
                >
                  <strong className="block">Unable to predict</strong>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-emerald-700 px-5 py-3.5 font-semibold text-white shadow-sm transition hover:bg-emerald-800 focus:outline-none focus:ring-4 focus:ring-emerald-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Predicting resources..." : "Predict Resource Requirements"}
              </button>

              <button
                type="button"
                onClick={resetForm}
                className="w-full rounded-lg border border-slate-300 px-5 py-3 font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                Reset Form
              </button>
            </form>

            <div className="mt-6 rounded-lg bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Request Summary
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700">
                {selectedRepair.label} · {quantity || "0"}{" "}
                {selectedRepair.unitLabel.toLowerCase()} · Priority {priority}
              </p>
            </div>
          </section>

          <section className="lg:col-span-3">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  Predicted Resource Requirements
                </h3>
                <p className="mt-1 text-sm text-slate-500">
                  Results returned by the Python prediction API
                </p>
              </div>

              {result && (
                <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800">
                  Prediction received
                </span>
              )}
            </div>

            {result ? (
              <>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {RESOURCE_INFO.map((resource) => (
                    <article
                      key={resource.key}
                      className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-medium text-slate-500">
                            {resource.label}
                          </p>
                          <p className="mt-3 break-words text-3xl font-bold text-emerald-900">
                            {formatNumber(
                              result.predicted_resources[resource.key],
                            )}
                          </p>
                          <p className="mt-1 text-sm text-slate-500">
                            {resource.unit}
                          </p>
                        </div>

                        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-xl">
                          {resource.icon}
                        </div>
                      </div>

                      <p className="mt-5 border-t border-slate-100 pt-3 text-sm text-slate-500">
                        {resource.description}
                      </p>
                    </article>
                  ))}
                </div>

                <div className="mt-5 rounded-xl border border-slate-200 bg-white p-5">
                  <h4 className="font-bold text-slate-900">
                    Prediction Summary
                  </h4>

                  <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <dt className="text-sm text-slate-500">Repair type</dt>
                      <dd className="mt-1 font-semibold text-slate-800">
                        {selectedRepair.label}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-slate-500">Quantity</dt>
                      <dd className="mt-1 font-semibold text-slate-800">
                        {result.input?.quantity ?? quantity}{" "}
                        {selectedRepair.unitLabel.toLowerCase()}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-slate-500">Priority</dt>
                      <dd className="mt-1 font-semibold text-slate-800">
                        {result.input?.priority ?? priority} / 10
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-slate-500">Data status</dt>
                      <dd className="mt-1 font-semibold text-amber-700">
                        {result.data_status || "Not specified by API"}
                      </dd>
                    </div>
                  </dl>
                </div>
              </>
            ) : (
              <div className="flex min-h-72 flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-300 bg-white px-6 py-12 text-center">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-50 text-3xl">
                  📊
                </div>

                <h4 className="mt-5 text-lg font-bold text-slate-900">
                  Your prediction will appear here
                </h4>

                <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
                  Enter the task details and select Predict Resource
                  Requirements to view the estimated resource quantities.
                </p>
              </div>
            )}

            <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-5">
              <h4 className="font-bold text-amber-900">
                Research Prototype Notice
              </h4>
              <p className="mt-2 text-sm leading-6 text-amber-900">
                This model was trained using simulated demonstration data.
                These estimates are not verified engineering requirements and
                must not be used for real roadworks without validation against
                approved engineering norms or actual resource records.
              </p>

              {result?.warning && (
                <p className="mt-3 border-t border-amber-200 pt-3 text-sm leading-6 text-amber-900">
                  API warning: {result.warning}
                </p>
              )}
            </div>
          </section>
        </div>

        <footer className="mt-10 border-t border-slate-200 py-6 text-center text-sm leading-6 text-slate-500">
          AI-Driven Multi-Resource Allocation and Planning for Road Maintenance
          <br />
          Research prototype · Resource requirement prediction
        </footer>
      </main>
    </div>
  );
}

export default App;
