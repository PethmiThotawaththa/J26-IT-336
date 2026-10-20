
import { useState } from 'react'
import {
  Activity,
  AlertCircle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  ClipboardList,
  Gauge,
  Layers3,
  LoaderCircle,
  Menu,
  RotateCcw,
  Route,
  Settings2,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Wrench,
  X,
} from 'lucide-react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

// --------------------------------------------------
// Prediction modules
// --------------------------------------------------

const modules = [
  {
    id: 'cost',
    title: 'Repair Cost Prediction',
    shortTitle: 'Cost Prediction',
    description:
      'Estimate road repair cost using the existing trained Extra Trees regression model.',
    icon: CircleDollarSign,
    number: '01',
    iconStyle: 'bg-blue-100 text-blue-600',
    gradient: 'from-blue-500 to-blue-800',
  },
  {
    id: 'method',
    title: 'Repair Method Prediction',
    shortTitle: 'Repair Method',
    description:
      'Identify a possible pavement repair method using the trained classification model.',
    icon: Wrench,
    number: '02',
    iconStyle: 'bg-cyan-100 text-cyan-600',
    gradient: 'from-cyan-400 to-blue-600',
  },
  {
    id: 'priority',
    title: 'Repair Priority Prediction',
    shortTitle: 'Repair Priority',
    description:
      'Predict provisional maintenance inspection priority for a road section.',
    icon: Gauge,
    number: '03',
    iconStyle: 'bg-indigo-100 text-indigo-600',
    gradient: 'from-indigo-500 to-blue-700',
  },
]

// --------------------------------------------------
// Prediction fields
// --------------------------------------------------

const priorityFields = [
  {
    name: 'section_length_m',
    label: 'Section Length',
    unit: 'meters',
    group: 'Road Information',
    placeholder: 'e.g. 500',
    positive: true,
  },
  {
    name: 'traffic_mean_vehicles_per_hour',
    label: 'Average Traffic Volume',
    unit: 'vehicles/hour',
    group: 'Road Information',
    placeholder: 'e.g. 750',
  },
  {
    name: 'nearby_hospital_count_500m',
    label: 'Nearby Hospitals',
    unit: 'within 500m',
    group: 'Nearby Facilities',
    placeholder: 'e.g. 1',
    integer: true,
  },
  {
    name: 'nearby_school_count_500m',
    label: 'Nearby Schools',
    unit: 'within 500m',
    group: 'Nearby Facilities',
    placeholder: 'e.g. 2',
    integer: true,
  },
  {
    name: 'nearby_police_count_500m',
    label: 'Nearby Police Stations',
    unit: 'within 500m',
    group: 'Nearby Facilities',
    placeholder: 'e.g. 0',
    integer: true,
  },
  {
    name: 'section_forecast_budget_lkr',
    label: 'Forecast Budget',
    unit: 'LKR',
    group: 'Maintenance Planning',
    placeholder: 'e.g. 250000',
  },
  {
    name: 'planned_item_1_count',
    label: 'Planned Item 1 Count',
    unit: 'count',
    group: 'Maintenance Planning',
    placeholder: 'e.g. 3',
    integer: true,
  },
  {
    name: 'planned_item_2_count',
    label: 'Planned Item 2 Count',
    unit: 'count',
    group: 'Maintenance Planning',
    placeholder: 'e.g. 1',
    integer: true,
  },
  {
    name: 'planned_item_75_count',
    label: 'Planned Item 75 Count',
    unit: 'count',
    group: 'Maintenance Planning',
    placeholder: 'e.g. 0',
    integer: true,
  },
]

const methodFields = [
  {
    name: 'length_m',
    label: 'Length',
    unit: 'm',
    group: 'Repair Measurements',
    placeholder: 'e.g. 10',
  },
  {
    name: 'width_m',
    label: 'Width',
    unit: 'm',
    group: 'Repair Measurements',
    placeholder: 'e.g. 2',
  },
  {
    name: 'depth_m',
    label: 'Depth',
    unit: 'm',
    group: 'Repair Measurements',
    placeholder: 'e.g. 0.05',
  },
  {
    name: 'area_sqm',
    label: 'Area',
    unit: 'sq.m',
    group: 'Repair Measurements',
    placeholder: 'e.g. 20',
  },
  {
    name: 'count',
    label: 'Count',
    unit: 'count',
    group: 'Repair Measurements',
    placeholder: 'e.g. 1',
  },
]

const itemCodes = [
  '1', '2', '40', '42', '43', '44', '45', '46',
  '50', '51', '52', '53', '54', '59', '60',
  '61', '62', '63', '64', '66', '67', '69',
  '70', '71', '75',
]

const costFields = [
  {
    name: 'length_m',
    label: 'Length',
    unit: 'm',
    group: 'Repair Measurements',
    placeholder: 'e.g. 10',
  },
  {
    name: 'width_m',
    label: 'Width',
    unit: 'm',
    group: 'Repair Measurements',
    placeholder: 'e.g. 2',
  },
  {
    name: 'depth_m',
    label: 'Depth',
    unit: 'm',
    group: 'Repair Measurements',
    placeholder: 'e.g. 0.05',
  },
  {
    name: 'area_sqm',
    label: 'Area',
    unit: 'sq.m',
    group: 'Repair Measurements',
    placeholder: 'e.g. 20',
  },
  {
    name: 'calculated_work_area_sqm',
    label: 'Calculated Work Area',
    unit: 'sq.m',
    group: 'Repair Measurements',
    placeholder: 'e.g. 20',
  },
  {
    name: 'count',
    label: 'Count',
    unit: 'count',
    group: 'Work Details',
    placeholder: 'e.g. 1',
  },
  {
    name: 'times_per_year_frequency',
    label: 'Times per Year (Frequency)',
    unit: 'times/year',
    group: 'Work Details',
    placeholder: 'e.g. 1',
  },
  {
    name: 'density_kg_m3',
    label: 'Density',
    unit: 'kg/m³',
    group: 'Work Details',
    placeholder: 'e.g. 0',
  },
  {
    name: 'item_code',
    label: 'Item Code',
    group: 'Work Details',
    options: itemCodes,
  },
  {
    name: 'units',
    label: 'Units',
    group: 'Work Details',
    options: ['m', 'm.ton', 'no', 'sq.m'],
  },
]

const fieldsByModule = {
  cost: costFields,
  method: methodFields,
  priority: priorityFields,
}

const groupsByModule = {
  cost: ['Repair Measurements', 'Work Details'],
  method: ['Repair Measurements'],
  priority: [
    'Road Information',
    'Nearby Facilities',
    'Maintenance Planning',
  ],
}

function emptyForm(moduleId) {
  return Object.fromEntries(
    fieldsByModule[moduleId].map((field) => [field.name, ''])
  )
}

function isValidValue(field, value) {
  if (value === '') return false

  if (field.options) {
    return field.options.includes(value)
  }

  const number = Number(value)

  return (
    Number.isFinite(number) &&
    number >= 0 &&
    (!field.integer || Number.isInteger(number)) &&
    (!field.positive || number > 0)
  )
}

// --------------------------------------------------
// Verified evaluation report data
// These are historical report results, NOT live API
// scores or per-prediction confidence values.
// --------------------------------------------------

const methodConfusion = [
  [5, 2, 0],
  [2, 3, 0],
  [0, 0, 4],
]

const priorityConfusion = [
  [0, 2, 0],
  [2, 1, 0],
  [0, 1, 3],
]

const costComparison = [
  { name: 'Extra Trees', mae: 165197.29, relative: '30.20%' },
  { name: 'Gradient Boosting (Work Area)', mae: 191906.54, relative: '35.08%' },
  { name: 'Gradient Boosting (GB_A)', mae: 201407.02, relative: '36.81%' },
  { name: 'Random Forest', mae: 214010.64, relative: '39.12%' },
  { name: 'Ridge', mae: 312580.50, relative: '57.14%' },
]

function formatLkr(value) {
  return new Intl.NumberFormat('en-LK', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

// --------------------------------------------------
// Reusable performance components
// --------------------------------------------------

function MetricCard({ label, value, detail, icon: Icon }) {
  return (
    <div className="rounded-2xl border border-blue-100 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
            {label}
          </p>
          <h3 className="mt-3 wrap-break-word text-2xl font-black text-blue-800 sm:text-3xl">
            {value}
          </h3>
          <p className="mt-2 text-xs leading-5 text-slate-500">
            {detail}
          </p>
        </div>

        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
          <Icon size={24} />
        </div>
      </div>
    </div>
  )
}

function ConfusionMatrix({ title, labels, values }) {
  return (
    <div className="rounded-3xl border border-blue-100 bg-white p-5 shadow-sm sm:p-7">
      <h4 className="text-lg font-extrabold text-slate-900">
        {title}
      </h4>

      <p className="mt-2 text-xs leading-5 text-slate-500">
        Rows represent actual labels. Columns represent predicted labels.
        Diagonal cells are correct predictions.
      </p>

      <div className="mt-5 overflow-x-auto">
        <table className="w-full min-w-100 border-separate border-spacing-2 text-center text-xs sm:text-sm">
          <thead>
            <tr>
              <th className="p-2 text-left text-slate-500">
                Actual / Predicted
              </th>
              {labels.map((label) => (
                <th key={label} className="p-2 text-slate-600">
                  {label}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {values.map((row, rowIndex) => (
              <tr key={labels[rowIndex]}>
                <th className="p-2 text-left text-slate-600">
                  {labels[rowIndex]}
                </th>

                {row.map((value, columnIndex) => (
                  <td
                    key={`${rowIndex}-${columnIndex}`}
                    className={`rounded-xl p-4 font-black ${
                      rowIndex === columnIndex
                        ? 'bg-emerald-100 text-emerald-800'
                        : value > 0
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-slate-50 text-slate-400'
                    }`}
                  >
                    {value}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function PerformanceDashboard() {
  return (
    <div className="space-y-8">
      {/* Performance hero */}

      <section className="relative overflow-hidden rounded-3xl bg-linear-to-r from-blue-800 via-blue-600 to-cyan-500 p-7 text-white shadow-lg shadow-blue-200 sm:p-9">
        <div className="relative flex items-start gap-5">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-white/20">
            <BarChart3 size={32} />
          </div>

          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-cyan-100">
              Research Evaluation
            </p>

            <h2 className="mt-2 text-2xl font-black sm:text-3xl">
              Model Performance
            </h2>

            <p className="mt-3 max-w-2xl text-sm leading-6 text-blue-50">
              Evaluation evidence from existing RoadWise AI research
              reports. Classification accuracy, F1-scores,
              regression errors, and validation limitations.
            </p>
          </div>
        </div>
      </section>

      <div className="rounded-2xl border border-blue-200 bg-blue-50 p-5">
        <div className="flex items-start gap-3">
          <ShieldCheck
            size={21}
            className="mt-0.5 shrink-0 text-blue-700"
          />

          <div>
            <p className="font-extrabold text-blue-900">
              Evaluation evidence, not live accuracy
            </p>

            <p className="mt-2 text-sm leading-6 text-blue-800">
              These metrics come from saved research reports.
              They do not change when a user submits a new prediction,
              and they do not represent the confidence of an
              individual prediction.
            </p>
          </div>
        </div>
      </div>

      {/* Main evaluation metrics */}

      <section>
        <div className="mb-5">
          <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
            Validated Results
          </p>

          <h3 className="mt-2 text-2xl font-extrabold">
            Performance Overview
          </h3>
        </div>

        <div className="grid gap-5 lg:grid-cols-3">
          <MetricCard
            label="Repair Method Accuracy"
            value="75.00%"
            detail="12 of 16 correct • Leave-One-Road-Out validation"
            icon={Wrench}
          />

          <MetricCard
            label="Repair Priority Accuracy"
            value="44.44%"
            detail="4 of 9 correct • Experimental road-group validation"
            icon={Gauge}
          />

          <MetricCard
            label="Extra Trees Cost MAE"
            value="Rs. 165,197.29"
            detail="Reported overall model comparison • 123 records"
            icon={CircleDollarSign}
          />
        </div>
      </section>

      {/* Repair Method */}

      <section className="space-y-5">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-100 text-cyan-700">
            <Wrench size={23} />
          </div>

          <div>
            <h3 className="text-xl font-extrabold">
              Repair Method Classification
            </h3>
            <p className="text-sm text-slate-500">
              Experimental pavement repair model
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <MetricCard
            label="Accuracy"
            value="75.00%"
            detail="12 correct predictions out of 16"
            icon={CheckCircle2}
          />

          <MetricCard
            label="Macro F1"
            value="0.7714"
            detail="Average class-level F1-score"
            icon={BarChart3}
          />

          <MetricCard
            label="Validation Records"
            value="16"
            detail="6 independent road groups"
            icon={Route}
          />
        </div>

        <ConfusionMatrix
          title="Repair Method — Confusion Matrix"
          labels={[
            'Pothole Patching',
            'Crack Sealing',
            'Section Overlay',
          ]}
          values={methodConfusion}
        />

        <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm">
          <h4 className="font-extrabold">
            Validation Methodology
          </h4>

          <p className="mt-3 text-sm leading-7 text-slate-600">
            Leave-One-Road-Out validation was used across six
            roads. The report recorded 75% accuracy and a Macro
            F1-score of 0.7714. The model was evaluated using
            16 records.
          </p>

          <p className="mt-4 rounded-xl bg-amber-50 p-4 text-xs leading-6 text-amber-900">
            Limitation: The dataset is small. Pothole Patching
            and Crack Sealing records include identical
            all-zero measurement patterns with different labels.
            Model suggestions require engineering verification.
          </p>

          <p className="mt-4 text-xs text-slate-400">
            Evidence: pavement_repair_training_report.txt
          </p>
        </div>
      </section>

      {/* Repair Priority */}

      <section className="space-y-5">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-100 text-indigo-700">
            <Gauge size={23} />
          </div>

          <div>
            <h3 className="text-xl font-extrabold">
              Repair Priority Classification
            </h3>
            <p className="text-sm text-slate-500">
              Experimental maintenance inspection priority model
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <MetricCard
            label="Accuracy"
            value="44.44%"
            detail="4 correct predictions out of 9"
            icon={CheckCircle2}
          />

          <MetricCard
            label="Macro F1"
            value="0.3810"
            detail="Experimental pooled held-out evaluation"
            icon={BarChart3}
          />

          <MetricCard
            label="Balanced Accuracy"
            value="36.11%"
            detail="9 labelled sections across 6 roads"
            icon={Route}
          />
        </div>

        <ConfusionMatrix
          title="Repair Priority — Decision Tree Confusion Matrix"
          labels={['Low', 'Medium', 'High']}
          values={priorityConfusion}
        />

        <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm">
          <h4 className="font-extrabold">
            Validation Methodology
          </h4>

          <p className="mt-3 text-sm leading-7 text-slate-600">
            Road-group-aware Leave-One-Road-Out
            cross-validation was performed on nine manually
            labelled sections from six roads. The reported
            Decision Tree accuracy was 44.44%.
          </p>

          <p className="mt-4 rounded-xl bg-amber-50 p-4 text-xs leading-6 text-amber-900">
            Limitation: These scores are exploratory feasibility
            results, not reliable generalization estimates.
            The labels represent provisional maintenance or
            inspection priority, not verified road damage
            severity or repair urgency.
          </p>

          <p className="mt-4 text-xs text-slate-400">
            Evidence: priority_classification_comparison_report.txt
            and priority_model_training_report.txt
          </p>
        </div>
      </section>

      {/* Cost Regression */}

      <section className="space-y-5">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
            <CircleDollarSign size={23} />
          </div>

          <div>
            <h3 className="text-xl font-extrabold">
              Repair Cost Regression
            </h3>
            <p className="text-sm text-slate-500">
              Final deployed model: Extra Trees Regressor
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <MetricCard
            label="Reported MAE"
            value="Rs. 165,197.29"
            detail="Extra Trees • Overall model comparison"
            icon={CircleDollarSign}
          />

          <MetricCard
            label="Reported Relative MAE"
            value="30.20%"
            detail="Relative error metric, NOT classification accuracy"
            icon={TrendingUp}
          />

          <MetricCard
            label="Comparison Records"
            value="123"
            detail="Records in the overall comparison group"
            icon={ClipboardList}
          />
        </div>

        <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm sm:p-8">
          <h4 className="text-lg font-extrabold">
            Cost Model Algorithm Comparison
          </h4>

          <p className="mt-2 text-sm leading-6 text-slate-500">
            Mean Absolute Error (MAE). Lower values indicate
            lower average absolute prediction error in this
            reported comparison.
          </p>

          <div className="mt-6 space-y-5">
            {costComparison.map((model) => {
              const maxMae = 312580.5
              const width = (model.mae / maxMae) * 100
              const isFinal = model.name === 'Extra Trees'

              return (
                <div key={model.name}>
                  <div className="mb-2 flex flex-wrap items-center justify-between gap-2 text-sm">
                    <span className={`font-semibold ${
                      isFinal
                        ? 'text-blue-700'
                        : 'text-slate-700'
                    }`}>
                      {model.name}
                      {isFinal && (
                        <span className="ml-2 rounded-full bg-blue-100 px-2 py-1 text-[10px] font-bold text-blue-700">
                          DEPLOYED
                        </span>
                      )}
                    </span>

                    <span className="font-bold text-slate-700">
                      Rs. {formatLkr(model.mae)}
                    </span>
                  </div>

                  <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className={`h-full rounded-full ${
                        isFinal
                          ? 'bg-linear-to-r from-blue-600 to-cyan-400'
                          : 'bg-slate-300'
                      }`}
                      style={{ width: `${width}%` }}
                    />
                  </div>

                  <p className="mt-1 text-right text-xs text-slate-500">
                    Relative MAE: {model.relative}
                  </p>
                </div>
              )
            })}
          </div>
        </div>

        <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm">
          <h4 className="font-extrabold">
            Cost Evaluation Interpretation
          </h4>

          <p className="mt-3 text-sm leading-7 text-slate-600">
            The existing comparison report shows Extra Trees
            achieving the lowest overall MAE among the listed
            regression algorithms. The deployed cost prediction
            endpoint uses the saved Extra Trees model.
          </p>

          <p className="mt-4 rounded-xl bg-amber-50 p-4 text-xs leading-6 text-amber-900">
            Important: The reported Extra Trees MAE is a
            comparison result. The available report does not
            establish a separately verified final-model RMSE
            or R². Random Forest road-validation metrics must
            not be presented as Extra Trees metrics.
          </p>

          <p className="mt-4 text-xs text-slate-400">
            Evidence: final_model_verification_report.txt
          </p>
        </div>
      </section>

      {/* Research limitations */}

      <section className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex items-center gap-3">
          <AlertCircle size={23} className="text-amber-600" />
          <h3 className="text-xl font-extrabold">
            Research Limitations
          </h3>
        </div>

        <div className="mt-5 space-y-4 text-sm leading-7 text-slate-600">
          <p>
            <strong>Limited training data:</strong> The repair
            method and priority classification datasets are
            small, which limits confidence in performance on
            unseen roads.
          </p>

          <p>
            <strong>Validation scope:</strong> The classification
            results use road-aware validation. The cost
            comparison result must not be interpreted as a
            guaranteed real-world error rate.
          </p>

          <p>
            <strong>Prediction interpretation:</strong> Road
            priority predictions support maintenance inspection
            decisions. They do not establish actual road damage
            severity.
          </p>

          <p>
            <strong>Human verification:</strong> Engineering
            assessment and additional independent data are
            necessary before operational deployment.
          </p>
        </div>
      </section>
    </div>
  )
}

// --------------------------------------------------
// Main application
// --------------------------------------------------

function App() {
  const [activeModule, setActiveModule] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const [forms, setForms] = useState({
    cost: emptyForm('cost'),
    method: emptyForm('method'),
    priority: emptyForm('priority'),
  })

  const [results, setResults] = useState({
    cost: null,
    method: null,
    priority: null,
  })

  const [errors, setErrors] = useState({
    cost: '',
    method: '',
    priority: '',
  })

  const [loading, setLoading] = useState({
    cost: false,
    method: false,
    priority: false,
  })

  const selectedModule = modules.find(
    (module) => module.id === activeModule
  )

  const SelectedIcon = selectedModule?.icon
  const fields = fieldsByModule[activeModule] || []
  const currentForm = forms[activeModule] || {}

  const filledCount = fields.filter(
    (field) => currentForm[field.name] !== ''
  ).length

  const validCount = fields.filter((field) =>
    isValidValue(field, currentForm[field.name])
  ).length

  const canPredict =
    fields.length > 0 &&
    validCount === fields.length &&
    !loading[activeModule]

  // Navigation

  function navigate(moduleId) {
    setActiveModule(moduleId)
    setSidebarOpen(false)
  }

  // Input changes

  function updateField(name, value) {
    setForms((previous) => ({
      ...previous,
      [activeModule]: {
        ...previous[activeModule],
        [name]: value,
      },
    }))

    setResults((previous) => ({
      ...previous,
      [activeModule]: null,
    }))

    setErrors((previous) => ({
      ...previous,
      [activeModule]: '',
    }))
  }

  function resetForm() {
    setForms((previous) => ({
      ...previous,
      [activeModule]: emptyForm(activeModule),
    }))

    setResults((previous) => ({
      ...previous,
      [activeModule]: null,
    }))

    setErrors((previous) => ({
      ...previous,
      [activeModule]: '',
    }))
  }

  // FastAPI prediction request

  async function predict(event) {
    event.preventDefault()

    const moduleId = activeModule
    const moduleFields = fieldsByModule[moduleId]
    const values = forms[moduleId]

    const valid = moduleFields.every((field) =>
      isValidValue(field, values[field.name])
    )

    if (!valid) return

    const payload = Object.fromEntries(
      moduleFields.map((field) => [
        field.name,
        field.options
          ? values[field.name]
          : Number(values[field.name]),
      ])
    )

    setLoading((previous) => ({
      ...previous,
      [moduleId]: true,
    }))

    setResults((previous) => ({
      ...previous,
      [moduleId]: null,
    }))

    setErrors((previous) => ({
      ...previous,
      [moduleId]: '',
    }))

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/predict/${moduleId}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        const detail =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(
                data.detail || 'Prediction request failed'
              )

        throw new Error(detail)
      }

      setResults((previous) => ({
        ...previous,
        [moduleId]: data,
      }))
    } catch (error) {
      const message =
        error instanceof TypeError
          ? 'Cannot connect to the backend. Check that FastAPI is running on port 8000.'
          : error.message

      setErrors((previous) => ({
        ...previous,
        [moduleId]: message,
      }))
    } finally {
      setLoading((previous) => ({
        ...previous,
        [moduleId]: false,
      }))
    }
  }

  // Input field renderer

  function renderField(field) {
    const value = currentForm[field.name]

    return (
      <label key={field.name} className="block">
        <span className="mb-2 block text-sm font-semibold text-slate-700">
          {field.label}
        </span>

        <div className="relative">
          {field.options ? (
            <select
              value={value}
              onChange={(event) =>
                updateField(field.name, event.target.value)
              }
              disabled={loading[activeModule]}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
            >
              <option value="">
                Select {field.label}
              </option>

              {field.options.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          ) : (
            <input
              type="number"
              min={field.positive ? '0.000001' : '0'}
              step={field.integer ? '1' : 'any'}
              value={value}
              onChange={(event) =>
                updateField(field.name, event.target.value)
              }
              disabled={loading[activeModule]}
              placeholder={field.placeholder}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 pr-28 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
            />
          )}

          {field.unit && (
            <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs text-slate-400">
              {field.unit}
            </span>
          )}
        </div>
      </label>
    )
  }

  // Prediction result renderer

  function renderResult() {
    const result = results[activeModule]
    const error = errors[activeModule]
    const isLoading = loading[activeModule]

    let value = ''
    let caption = ''
    let note = ''

    if (result && activeModule === 'cost') {
      value = new Intl.NumberFormat('en-LK', {
        style: 'currency',
        currency: 'LKR',
        minimumFractionDigits: 2,
      }).format(result.predicted_cost_lkr)

      caption = 'Estimated Repair Cost'
      note =
        'Model estimate only; not a verified engineering quotation.'
    } else if (result && activeModule === 'method') {
      value = result.repair_method
      caption = `Repair Method Code: ${result.repair_method_code}`
      note =
        'Experimental model suggestion; confirm with a qualified road engineer.'
    } else if (result && activeModule === 'priority') {
      value = result.prediction
      caption = 'Provisional Maintenance Inspection Priority'
      note =
        'This is inspection priority, not a verified measure of road damage or repair urgency.'
    }

    return (
      <div className="space-y-5">
        <div className="overflow-hidden rounded-3xl border border-blue-100 bg-white shadow-sm">
          <div className="bg-linear-to-r from-blue-700 to-indigo-700 p-6 text-white">
            <div className="flex items-center gap-3">
              <BarChart3 size={22} />

              <h3 className="text-lg font-extrabold">
                Prediction Result
              </h3>
            </div>

            <p className="mt-2 text-xs text-blue-100">
              Live FastAPI machine learning output
            </p>
          </div>

          <div className="px-6 py-9 text-center">
            {isLoading ? (
              <>
                <LoaderCircle
                  size={45}
                  className="mx-auto animate-spin text-blue-600"
                />

                <h4 className="mt-5 text-lg font-extrabold">
                  Running Prediction...
                </h4>

                <p className="mt-2 text-sm text-slate-500">
                  Waiting for the trained model.
                </p>
              </>
            ) : error ? (
              <>
                <AlertCircle
                  size={44}
                  className="mx-auto text-rose-500"
                />

                <h4 className="mt-4 text-lg font-extrabold text-rose-700">
                  Prediction Failed
                </h4>

                <p
                  role="alert"
                  className="mt-3 wrap-break-word text-sm leading-6 text-rose-600"
                >
                  {error}
                </p>
              </>
            ) : result ? (
              <>
                <CheckCircle2
                  size={44}
                  className="mx-auto text-emerald-600"
                />

                <p className="mt-4 text-xs font-bold uppercase tracking-wide text-slate-500">
                  {caption}
                </p>

                <h4 className="mt-3 wrap-break-word text-2xl font-black text-blue-800">
                  {value}
                </h4>

                <p className="mt-4 text-xs leading-5 text-slate-500">
                  {note}
                </p>

                <div className="mt-5 wrap-break-word rounded-xl bg-blue-50 p-3 text-xs text-blue-700">
                  Model: {result.model}
                </div>
              </>
            ) : (
              <>
                <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-blue-50 text-blue-500">
                  {SelectedIcon && (
                    <SelectedIcon size={37} />
                  )}
                </div>

                <h4 className="mt-5 text-lg font-extrabold">
                  Awaiting Prediction
                </h4>

                <p className="mt-3 text-sm leading-6 text-slate-500">
                  Complete the input form and click Predict
                  to see the model result.
                </p>

                <div className="mt-6 rounded-xl border border-dashed border-blue-200 bg-blue-50 p-4 text-xs font-semibold text-blue-700">
                  Result: Not generated yet
                </div>
              </>
            )}
          </div>
        </div>

        <div className="rounded-3xl border border-cyan-100 bg-linear-to-br from-cyan-50 to-blue-50 p-6">
          <div className="flex items-center gap-3">
            <CheckCircle2
              size={21}
              className="text-blue-600"
            />

            <h4 className="font-extrabold">
              Input Summary
            </h4>
          </div>

          <p className="mt-3 text-sm text-slate-600">
            {filledCount} of {fields.length} fields completed.
          </p>

          <p className="mt-2 text-sm font-semibold text-blue-700">
            {validCount} valid inputs
          </p>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            All numeric fields must be non-negative.
            Item Code and Units must use model-supported values.
          </p>
        </div>
      </div>
    )
  }

  // --------------------------------------------------
  // Dashboard UI
  // --------------------------------------------------

  return (
    <div className="min-h-screen bg-[#f3f7ff] text-slate-900">
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-slate-950/50 lg:hidden"
        />
      )}

      {/* SIDEBAR */}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col bg-[#0b1f45] text-white shadow-2xl transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen
            ? 'translate-x-0'
            : '-translate-x-full'
        }`}
      >
        <div className="border-b border-white/10 px-6 py-7">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-linear-to-br from-cyan-400 to-blue-600 shadow-lg">
                <Route size={25} />
              </div>

              <div>
                <h1 className="text-lg font-extrabold tracking-tight">
                  RoadWise AI
                </h1>

                <p className="text-[10px] font-semibold tracking-widest text-blue-200">
                  DECISION SUPPORT SYSTEM
                </p>
              </div>
            </div>

            <button
              type="button"
              aria-label="Close menu"
              onClick={() => setSidebarOpen(false)}
              className="text-blue-200 lg:hidden"
            >
              <X size={22} />
            </button>
          </div>
        </div>

        <nav className="flex-1 space-y-2 overflow-y-auto px-4 py-7">
          <p className="mb-4 px-3 text-[11px] font-bold uppercase tracking-[0.2em] text-blue-300/70">
            Main Menu
          </p>

          <button
            type="button"
            onClick={() => navigate('overview')}
            className={`flex w-full items-center gap-3 rounded-xl px-4 py-3.5 text-left text-sm font-semibold transition ${
              activeModule === 'overview'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-blue-100 hover:bg-white/10'
            }`}
          >
            <BarChart3 size={19} />
            Dashboard Overview
            <ChevronRight
              size={16}
              className="ml-auto opacity-60"
            />
          </button>

          <p className="mb-3 mt-9 px-3 text-[11px] font-bold uppercase tracking-[0.2em] text-blue-300/70">
            AI Prediction Modules
          </p>

          {modules.map((module) => {
            const Icon = module.icon

            return (
              <button
                type="button"
                key={module.id}
                onClick={() => navigate(module.id)}
                className={`flex w-full items-center gap-3 rounded-xl px-4 py-3.5 text-left text-sm font-medium transition ${
                  activeModule === module.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-blue-100 hover:bg-white/10'
                }`}
              >
                <Icon size={19} />
                {module.shortTitle}
                <ChevronRight
                  size={16}
                  className="ml-auto opacity-60"
                />
              </button>
            )
          })}

          {/* NEW MODEL PERFORMANCE NAVIGATION */}

          <p className="mb-3 mt-9 px-3 text-[11px] font-bold uppercase tracking-[0.2em] text-blue-300/70">
            Research Evaluation
          </p>

          <button
            type="button"
            onClick={() => navigate('performance')}
            className={`flex w-full items-center gap-3 rounded-xl px-4 py-3.5 text-left text-sm font-medium transition ${
              activeModule === 'performance'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-blue-100 hover:bg-white/10'
            }`}
          >
            <TrendingUp size={19} />
            Model Performance
            <ChevronRight
              size={16}
              className="ml-auto opacity-60"
            />
          </button>
        </nav>

        <div className="p-4">
          <div className="rounded-2xl border border-blue-400/20 bg-linear-to-br from-blue-700/60 to-cyan-700/30 p-4">
            <ShieldCheck
              size={23}
              className="mb-3 text-cyan-200"
            />

            <p className="text-sm font-bold">
              Research Project
            </p>

            <p className="mt-1 text-xs leading-5 text-blue-100">
              Machine learning powered road maintenance
              decision support.
            </p>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}

      <div className="min-h-screen lg:ml-72">
        <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-blue-100 bg-white/95 px-5 backdrop-blur-xl sm:px-8">
          <div className="flex items-center gap-4">
            <button
              type="button"
              aria-label="Open menu"
              onClick={() => setSidebarOpen(true)}
              className="rounded-xl p-2 text-slate-600 hover:bg-blue-50 lg:hidden"
            >
              <Menu size={23} />
            </button>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-blue-500">
                Road Infrastructure Intelligence
              </p>

              <h2 className="mt-1 text-lg font-extrabold sm:text-xl">
                {activeModule === 'performance'
                  ? 'Model Performance'
                  : selectedModule?.title ||
                    'Dashboard Overview'}
              </h2>
            </div>
          </div>

          <div className="hidden items-center gap-3 sm:flex">
            <div className="flex items-center gap-2 rounded-full border border-emerald-100 bg-emerald-50 px-4 py-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />

              <span className="text-xs font-bold text-emerald-700">
                API Integration Ready
              </span>
            </div>

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-linear-to-br from-blue-500 to-indigo-600 text-sm font-bold text-white">
              AI
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl space-y-8 p-5 sm:p-8">
          {activeModule === 'overview' ? (
            <>
              {/* HERO SECTION */}

              <section className="relative overflow-hidden rounded-[28px] bg-linear-to-r from-[#103b91] via-[#155be0] to-[#0895c9] p-7 text-white shadow-xl shadow-blue-200/60 sm:p-10">
                <div className="pointer-events-none absolute -right-20 -top-28 h-80 w-80 rounded-full border-45 border-white/10" />

                <div className="relative max-w-2xl">
                  <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/15 px-4 py-2 text-xs font-bold">
                    <Sparkles
                      size={15}
                      className="text-cyan-200"
                    />
                    INTELLIGENT ROAD MAINTENANCE
                  </div>

                  <h2 className="text-3xl font-black leading-tight tracking-tight sm:text-4xl">
                    Smarter Roads.
                    <br />
                    Better Decisions.
                  </h2>

                  <p className="mt-4 max-w-xl text-sm leading-7 text-blue-50 sm:text-base">
                    An integrated machine learning dashboard
                    for road repair cost estimation, repair
                    method selection, and maintenance
                    inspection priority prediction.
                  </p>

                  <button
                    type="button"
                    onClick={() => navigate('priority')}
                    className="mt-7 inline-flex items-center gap-3 rounded-xl bg-white px-5 py-3 font-bold text-blue-700 shadow-lg transition hover:-translate-y-0.5 hover:bg-blue-50"
                  >
                    Explore Priority Module
                    <ArrowRight size={18} />
                  </button>
                </div>
              </section>

              {/* SUMMARY CARDS */}

              <section className="grid gap-4 md:grid-cols-3">
                {[
                  {
                    title: 'Prediction Modules',
                    value: '03',
                    detail: 'Machine learning components',
                    icon: Layers3,
                    gradient: 'from-blue-500 to-blue-700',
                  },
                  {
                    title: 'Frontend Technology',
                    value: 'React',
                    detail: 'Responsive web interface',
                    icon: Activity,
                    gradient: 'from-cyan-500 to-blue-600',
                  },
                  {
                    title: 'Model Integration',
                    value: 'Ready',
                    detail: 'FastAPI prediction endpoints',
                    icon: CheckCircle2,
                    gradient: 'from-indigo-500 to-violet-600',
                  },
                ].map((item) => {
                  const Icon = item.icon

                  return (
                    <div
                      key={item.title}
                      className="rounded-2xl border border-blue-100 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-sm font-medium text-slate-500">
                            {item.title}
                          </p>

                          <p className="mt-3 text-3xl font-black">
                            {item.value}
                          </p>

                          <p className="mt-2 text-xs text-slate-500">
                            {item.detail}
                          </p>
                        </div>

                        <div
                          className={`flex h-12 w-12 items-center justify-center rounded-2xl bg-linear-to-br ${item.gradient} text-white shadow-md`}
                        >
                          <Icon size={23} />
                        </div>
                      </div>
                    </div>
                  )
                })}
              </section>

              {/* MODULE CARDS */}

              <section>
                <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
                      Intelligent Analysis
                    </p>

                    <h3 className="mt-2 text-2xl font-extrabold">
                      Prediction Modules
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                      Select a module to begin your analysis.
                    </p>
                  </div>

                  <span className="rounded-full bg-blue-100 px-4 py-2 text-xs font-bold text-blue-700">
                    3 Prediction Modules
                  </span>
                </div>

                <div className="grid gap-5 md:grid-cols-3">
                  {modules.map((module) => {
                    const Icon = module.icon

                    return (
                      <button
                        type="button"
                        key={module.id}
                        onClick={() => navigate(module.id)}
                        className="group overflow-hidden rounded-3xl border border-blue-100 bg-white text-left shadow-sm transition duration-300 hover:-translate-y-1 hover:border-blue-300 hover:shadow-xl"
                      >
                        <div
                          className={`h-2 bg-linear-to-r ${module.gradient}`}
                        />

                        <div className="p-6">
                          <div className="flex items-start justify-between">
                            <div
                              className={`flex h-14 w-14 items-center justify-center rounded-2xl ${module.iconStyle}`}
                            >
                              <Icon size={27} />
                            </div>

                            <span className="text-3xl font-black text-slate-100">
                              {module.number}
                            </span>
                          </div>

                          <h4 className="mt-6 text-lg font-extrabold">
                            {module.title}
                          </h4>

                          <p className="mt-3 min-h-20 text-sm leading-6 text-slate-500">
                            {module.description}
                          </p>

                          <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-5">
                            <span className="text-sm font-bold text-blue-600">
                              Open Module
                            </span>

                            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-50 text-blue-600 transition group-hover:bg-blue-600 group-hover:text-white">
                              <ArrowRight size={18} />
                            </div>
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </section>

              {/* NEW PERFORMANCE PREVIEW */}

              <section className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm sm:p-8">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
                      Research Evidence
                    </p>

                    <h3 className="mt-2 text-xl font-extrabold">
                      Model Evaluation Results
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-slate-500">
                      Review accuracy, regression errors,
                      confusion matrices, and research limitations.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => navigate('performance')}
                    className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
                  >
                    View Performance
                    <ArrowRight size={17} />
                  </button>
                </div>

                <div className="mt-6 grid gap-4 sm:grid-cols-3">
                  <div className="rounded-2xl bg-blue-50 p-5">
                    <p className="text-xs font-semibold text-blue-700">
                      Repair Method Accuracy
                    </p>

                    <p className="mt-2 text-2xl font-black text-blue-900">
                      75.00%
                    </p>
                  </div>

                  <div className="rounded-2xl bg-indigo-50 p-5">
                    <p className="text-xs font-semibold text-indigo-700">
                      Repair Priority Accuracy
                    </p>

                    <p className="mt-2 text-2xl font-black text-indigo-900">
                      44.44%
                    </p>
                  </div>

                  <div className="rounded-2xl bg-cyan-50 p-5">
                    <p className="text-xs font-semibold text-cyan-700">
                      Extra Trees Cost MAE
                    </p>

                    <p className="mt-2 text-xl font-black text-cyan-900">
                      Rs. 165,197.29
                    </p>
                  </div>
                </div>

                <p className="mt-4 text-xs text-slate-500">
                  Reported research evaluation results;
                  not per-prediction confidence scores.
                </p>
              </section>

              {/* WORKFLOW */}

              <section className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm sm:p-8">
                <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
                  How It Works
                </p>

                <h3 className="mt-2 text-xl font-extrabold">
                  Intelligent Decision Workflow
                </h3>

                <div className="mt-6 grid gap-4 md:grid-cols-3">
                  {[
                    {
                      number: '01',
                      title: 'Enter Road Data',
                      detail:
                        'Provide required road and maintenance information.',
                      icon: ClipboardList,
                    },
                    {
                      number: '02',
                      title: 'Run ML Prediction',
                      detail:
                        'Send validated inputs to the trained prediction model.',
                      icon: Settings2,
                    },
                    {
                      number: '03',
                      title: 'Review Results',
                      detail:
                        'View outputs in a decision-support interface.',
                      icon: TrendingUp,
                    },
                  ].map((step) => {
                    const Icon = step.icon

                    return (
                      <div
                        key={step.number}
                        className="rounded-2xl border border-blue-100 bg-linear-to-b from-blue-50 to-white p-5"
                      >
                        <div className="mb-4 flex items-center justify-between">
                          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-white">
                            <Icon size={21} />
                          </div>

                          <span className="text-xl font-black text-blue-200">
                            {step.number}
                          </span>
                        </div>

                        <h4 className="font-bold">
                          {step.title}
                        </h4>

                        <p className="mt-2 text-sm leading-6 text-slate-500">
                          {step.detail}
                        </p>
                      </div>
                    )
                  })}
                </div>
              </section>
            </>
          ) : activeModule === 'performance' ? (
            <PerformanceDashboard />
          ) : (
            <>
              {/* MODULE HEADER */}

              <section className="relative overflow-hidden rounded-3xl bg-linear-to-r from-blue-800 via-blue-600 to-cyan-500 p-7 text-white shadow-lg shadow-blue-200 sm:p-9">
                <div className="pointer-events-none absolute -right-12 -top-16 h-56 w-56 rounded-full border-30 border-white/10" />

                <div className="relative flex items-start gap-5">
                  <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-white/20">
                    {SelectedIcon && (
                      <SelectedIcon size={31} />
                    )}
                  </div>

                  <div>
                    <p className="mb-2 text-xs font-bold uppercase tracking-widest text-cyan-100">
                      AI Prediction Module {selectedModule.number}
                    </p>

                    <h2 className="text-2xl font-black sm:text-3xl">
                      {selectedModule.title}
                    </h2>

                    <p className="mt-3 max-w-2xl text-sm leading-6 text-blue-50">
                      {selectedModule.description}
                    </p>
                  </div>
                </div>
              </section>

              {/* PREDICTION FORM AND RESULT */}

              <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_330px]">
                <form
                  onSubmit={predict}
                  className="overflow-hidden rounded-3xl border border-blue-100 bg-white shadow-sm"
                >
                  <div className="border-b border-blue-100 bg-linear-to-r from-blue-50 to-cyan-50 px-6 py-6 sm:px-8">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <h3 className="text-xl font-extrabold">
                          {activeModule === 'priority'
                            ? 'Road Section Information'
                            : activeModule === 'cost'
                              ? 'Repair Cost Information'
                              : 'Pavement Repair Information'}
                        </h3>

                        <p className="mt-1 text-sm text-slate-500">
                          Enter the required model input values.
                        </p>
                      </div>

                      <span className="rounded-full bg-white px-4 py-2 text-xs font-bold text-blue-700 shadow-sm">
                        {filledCount} / {fields.length} Fields
                      </span>
                    </div>

                    <div className="mt-5 h-2 overflow-hidden rounded-full bg-blue-100">
                      <div
                        className="h-full rounded-full bg-linear-to-r from-blue-600 to-cyan-400 transition-all"
                        style={{
                          width: `${
                            (filledCount / fields.length) * 100
                          }%`,
                        }}
                      />
                    </div>
                  </div>

                  <div className="space-y-9 p-6 sm:p-8">
                    {groupsByModule[activeModule].map(
                      (group, index) => (
                        <section key={group}>
                          <div className="mb-5 flex items-center gap-3">
                            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-100 text-sm font-black text-blue-700">
                              {index + 1}
                            </span>

                            <h4 className="text-base font-extrabold">
                              {group}
                            </h4>
                          </div>

                          <div className="grid gap-5 md:grid-cols-2">
                            {fields
                              .filter(
                                (field) =>
                                  field.group === group
                              )
                              .map(renderField)}
                          </div>
                        </section>
                      )
                    )}

                    {activeModule === 'cost' && (
                      <p className="rounded-xl bg-amber-50 p-4 text-xs leading-5 text-amber-800">
                        Item Code and Units are individually
                        supported categories. Not every
                        combination is necessarily present
                        in the training data. Enter
                        measurements consistent with the
                        selected repair item.
                      </p>
                    )}

                    {/* ACTION BUTTONS */}

                    <div className="flex flex-wrap gap-3 border-t border-slate-100 pt-6">
                      <button
                        type="submit"
                        disabled={!canPredict}
                        className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-linear-to-r from-blue-600 to-cyan-500 px-5 py-3.5 text-sm font-bold text-white transition hover:from-blue-700 hover:to-cyan-600 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {loading[activeModule] ? (
                          <LoaderCircle
                            size={18}
                            className="animate-spin"
                          />
                        ) : (
                          <Sparkles size={18} />
                        )}

                        {loading[activeModule]
                          ? 'Predicting...'
                          : activeModule === 'priority'
                            ? 'Predict Priority'
                            : activeModule === 'cost'
                              ? 'Predict Cost'
                              : 'Predict Method'}

                        {!loading[activeModule] && (
                          <ArrowRight size={17} />
                        )}
                      </button>

                      <button
                        type="button"
                        onClick={resetForm}
                        disabled={loading[activeModule]}
                        className="flex items-center justify-center gap-2 rounded-xl border border-blue-200 bg-white px-5 py-3.5 text-sm font-bold text-blue-700 transition hover:bg-blue-50 disabled:opacity-50"
                      >
                        <RotateCcw size={17} />
                        Reset
                      </button>
                    </div>

                    <p className="text-xs text-slate-400">
                      Predictions are generated by the
                      existing saved ML models through FastAPI.
                    </p>
                  </div>
                </form>

                {/* LIVE PREDICTION RESULT */}

                {renderResult()}
              </div>
            </>
          )}

          {/* FOOTER */}

          <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-blue-100 py-5 text-xs text-slate-400">
            <span>
              © 2026 RoadWise AI — Road Repair Priority
              Decision Support System
            </span>

            <span className="flex items-center gap-2">
              <ShieldCheck size={14} />
              Research Project Dashboard
            </span>
          </footer>
        </main>
      </div>
    </div>
  )
}

export default App
