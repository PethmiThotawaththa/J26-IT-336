
import { useState } from 'react'
import {
  Activity,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  ClipboardList,
  Construction,
  Database,
  Gauge,
  Layers3,
  MapPin,
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

const modules = [
  {
    id: 'cost',
    title: 'Repair Cost Prediction',
    shortTitle: 'Cost Prediction',
    description:
      'Estimate expected road repair costs using the trained machine learning regression model.',
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
      'Identify a suitable pavement repair method using machine learning classification.',
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
      'Predict provisional maintenance inspection priority for road sections.',
    icon: Gauge,
    number: '03',
    iconStyle: 'bg-indigo-100 text-indigo-600',
    gradient: 'from-indigo-500 to-blue-700',
  },
]

const priorityFields = [
  {
    name: 'section_length_m',
    label: 'Section Length',
    unit: 'meters',
    placeholder: 'e.g. 500',
    group: 'Road Information',
    icon: Route,
    integer: false,
  },
  {
    name: 'traffic_mean_vehicles_per_hour',
    label: 'Average Traffic Volume',
    unit: 'vehicles/hour',
    placeholder: 'e.g. 750',
    group: 'Road Information',
    icon: Activity,
    integer: false,
  },
  {
    name: 'nearby_hospital_count_500m',
    label: 'Nearby Hospitals',
    unit: 'within 500m',
    placeholder: 'e.g. 1',
    group: 'Nearby Facilities',
    icon: MapPin,
    integer: true,
  },
  {
    name: 'nearby_school_count_500m',
    label: 'Nearby Schools',
    unit: 'within 500m',
    placeholder: 'e.g. 2',
    group: 'Nearby Facilities',
    icon: MapPin,
    integer: true,
  },
  {
    name: 'nearby_police_count_500m',
    label: 'Nearby Police Stations',
    unit: 'within 500m',
    placeholder: 'e.g. 0',
    group: 'Nearby Facilities',
    icon: MapPin,
    integer: true,
  },
  {
    name: 'section_forecast_budget_lkr',
    label: 'Forecast Budget',
    unit: 'LKR',
    placeholder: 'e.g. 250000',
    group: 'Maintenance Planning',
    icon: CircleDollarSign,
    integer: false,
  },
  {
    name: 'planned_item_1_count',
    label: 'Planned Item 1 Count',
    unit: 'count',
    placeholder: 'e.g. 3',
    group: 'Maintenance Planning',
    icon: ClipboardList,
    integer: true,
  },
  {
    name: 'planned_item_2_count',
    label: 'Planned Item 2 Count',
    unit: 'count',
    placeholder: 'e.g. 1',
    group: 'Maintenance Planning',
    icon: ClipboardList,
    integer: true,
  },
  {
    name: 'planned_item_75_count',
    label: 'Planned Item 75 Count',
    unit: 'count',
    placeholder: 'e.g. 0',
    group: 'Maintenance Planning',
    icon: ClipboardList,
    integer: true,
  },
]

const createEmptyForm = () =>
  Object.fromEntries(priorityFields.map((field) => [field.name, '']))

function App() {
  const [activeModule, setActiveModule] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [priorityForm, setPriorityForm] = useState(createEmptyForm)

  const selectedModule = modules.find(
    (module) => module.id === activeModule
  )

  const SelectedIcon = selectedModule?.icon

  const filledFields = Object.values(priorityForm).filter(
    (value) => value !== ''
  ).length

  const validFields = priorityFields.filter((field) => {
    const value = priorityForm[field.name]

    if (value === '') return false

    const number = Number(value)

    return (
      Number.isFinite(number) &&
      number >= 0 &&
      (!field.integer || Number.isInteger(number)) &&
      (field.name !== 'section_length_m' || number > 0)
    )
  }).length

  function navigate(moduleId) {
    setActiveModule(moduleId)
    setSidebarOpen(false)
  }

  function updatePriorityField(name, value) {
    setPriorityForm((previous) => ({
      ...previous,
      [name]: value,
    }))
  }

  function resetPriorityForm() {
    setPriorityForm(createEmptyForm())
  }

  function renderPriorityFields(group) {
    return priorityFields
      .filter((field) => field.group === group)
      .map((field) => {
        const Icon = field.icon

        return (
          <label key={field.name} className="block">
            <span className="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
              <Icon size={15} className="text-blue-500" />
              {field.label}
            </span>

            <div className="relative">
              <input
                type="number"
                min={field.name === 'section_length_m' ? '0.01' : '0'}
                step={field.integer ? '1' : 'any'}
                value={priorityForm[field.name]}
                onChange={(event) =>
                  updatePriorityField(field.name, event.target.value)
                }
                placeholder={field.placeholder}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 pr-32 text-sm text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
              />

              <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-xs text-slate-400">
                {field.unit}
              </span>
            </div>
          </label>
        )
      })
  }

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
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="border-b border-white/10 px-6 py-7">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-linear-to-br from-cyan-400 to-blue-600 shadow-lg shadow-blue-900/30">
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
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-950/30'
                : 'text-blue-100 hover:bg-white/10'
            }`}
          >
            <BarChart3 size={19} />
            Dashboard Overview
            <ChevronRight size={16} className="ml-auto opacity-60" />
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
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-950/30'
                    : 'text-blue-100 hover:bg-white/10'
                }`}
              >
                <Icon size={19} />
                {module.shortTitle}
                <ChevronRight size={16} className="ml-auto opacity-60" />
              </button>
            )
          })}
        </nav>

        <div className="p-4">
          <div className="rounded-2xl border border-blue-400/20 bg-linear-to-br from-blue-700/60 to-cyan-700/30 p-4">
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-white/15">
              <ShieldCheck size={21} className="text-cyan-200" />
            </div>

            <p className="text-sm font-bold">Research Project</p>
            <p className="mt-1 text-xs leading-5 text-blue-100">
              Machine learning powered road maintenance decision support.
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
              <h2 className="mt-1 text-lg font-extrabold text-slate-900 sm:text-xl">
                {selectedModule?.title || 'Dashboard Overview'}
              </h2>
            </div>
          </div>

          <div className="hidden items-center gap-3 sm:flex">
            <div className="flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-4 py-2">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              <span className="text-xs font-bold text-blue-700">
                Frontend Preview
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
                <div className="pointer-events-none absolute -bottom-40 right-24 h-80 w-80 rounded-full bg-cyan-300/10 blur-3xl" />

                <div className="relative max-w-2xl">
                  <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/15 px-4 py-2 text-xs font-bold">
                    <Sparkles size={15} className="text-cyan-200" />
                    INTELLIGENT ROAD MAINTENANCE
                  </div>

                  <h2 className="text-3xl font-black leading-tight tracking-tight sm:text-4xl">
                    Smarter Roads.
                    <br />
                    Better Decisions.
                  </h2>

                  <p className="mt-4 max-w-xl text-sm leading-7 text-blue-50 sm:text-base">
                    An integrated machine learning dashboard for road repair
                    cost estimation, repair method selection, and maintenance
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
                    value: 'Next',
                    detail: 'Backend connection pending',
                    icon: Database,
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
                          <p className="mt-3 text-3xl font-black text-slate-900">
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

              {/* PREDICTION MODULE CARDS */}
              <section>
                <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
                      Intelligent Analysis
                    </p>
                    <h3 className="mt-2 text-2xl font-extrabold text-slate-900">
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

                          <h4 className="mt-6 text-lg font-extrabold text-slate-900">
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

              {/* WORKFLOW */}
              <section className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm sm:p-8">
                <div className="mb-6">
                  <p className="text-xs font-bold uppercase tracking-widest text-blue-600">
                    How It Works
                  </p>
                  <h3 className="mt-2 text-xl font-extrabold">
                    Intelligent Decision Workflow
                  </h3>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  {[
                    {
                      number: '01',
                      title: 'Enter Road Data',
                      detail:
                        'Provide the required road and maintenance information.',
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
                        'View model outputs in a clear decision-support interface.',
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

                        <h4 className="font-bold text-slate-900">
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
          ) : (
            <>
              {/* MODULE HEADER */}
              <section className="relative overflow-hidden rounded-3xl bg-linear-to-r from-blue-800 via-blue-600 to-cyan-500 p-7 text-white shadow-lg shadow-blue-200 sm:p-9">
                <div className="pointer-events-none absolute -right-12 -top-16 h-56 w-56 rounded-full border-30 border-white/10" />

                <div className="relative flex items-start gap-5">
                  <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-white/20">
                    {SelectedIcon && <SelectedIcon size={31} />}
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

              {activeModule === 'priority' ? (
                <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_330px]">
                  {/* PRIORITY INPUT FORM */}
                  <div className="overflow-hidden rounded-3xl border border-blue-100 bg-white shadow-sm">
                    <div className="border-b border-blue-100 bg-linear-to-r from-blue-50 to-cyan-50 px-6 py-6 sm:px-8">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <h3 className="text-xl font-extrabold text-slate-900">
                            Road Section Information
                          </h3>

                          <p className="mt-1 text-sm text-slate-500">
                            Enter the required values for priority classification.
                          </p>
                        </div>

                        <span className="rounded-full bg-white px-4 py-2 text-xs font-bold text-blue-700 shadow-sm">
                          {filledFields} / 9 Fields
                        </span>
                      </div>

                      <div className="mt-5 h-2 overflow-hidden rounded-full bg-blue-100">
                        <div
                          className="h-full rounded-full bg-linear-to-r from-blue-600 to-cyan-400 transition-all"
                          style={{
                            width: `${(filledFields / 9) * 100}%`,
                          }}
                        />
                      </div>
                    </div>

                    <div className="space-y-9 p-6 sm:p-8">
                      {[
                        'Road Information',
                        'Nearby Facilities',
                        'Maintenance Planning',
                      ].map((group, index) => (
                        <section key={group}>
                          <div className="mb-5 flex items-center gap-3">
                            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-100 text-sm font-black text-blue-700">
                              {index + 1}
                            </span>

                            <h4 className="text-base font-extrabold text-slate-900">
                              {group}
                            </h4>
                          </div>

                          <div className="grid gap-5 md:grid-cols-2">
                            {renderPriorityFields(group)}
                          </div>
                        </section>
                      ))}

                      <div className="flex flex-wrap gap-3 border-t border-slate-100 pt-6">
                        <button
                          type="button"
                          disabled
                          title="Prediction will be enabled after backend integration"
                          className="flex flex-1 cursor-not-allowed items-center justify-center gap-2 rounded-xl bg-linear-to-r from-blue-600 to-cyan-500 px-5 py-3.5 text-sm font-bold text-white opacity-60"
                        >
                          <Sparkles size={18} />
                          Predict Priority
                          <ArrowRight size={17} />
                        </button>

                        <button
                          type="button"
                          onClick={resetPriorityForm}
                          className="flex items-center justify-center gap-2 rounded-xl border border-blue-200 bg-white px-5 py-3.5 text-sm font-bold text-blue-700 transition hover:bg-blue-50"
                        >
                          <RotateCcw size={17} />
                          Reset
                        </button>
                      </div>

                      <p className="text-xs text-slate-400">
                        Prediction will be enabled after the Python API is connected.
                      </p>
                    </div>
                  </div>

                  {/* PRIORITY RESULT PANEL */}
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
                          Machine learning classification output
                        </p>
                      </div>

                      <div className="flex flex-col items-center px-6 py-10 text-center">
                        <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-blue-50 text-blue-500">
                          <Gauge size={37} />
                        </div>

                        <h4 className="mt-5 text-lg font-extrabold text-slate-900">
                          Awaiting Prediction
                        </h4>

                        <p className="mt-3 text-sm leading-6 text-slate-500">
                          The predicted priority will appear here after
                          connecting the backend and running the model.
                        </p>

                        <div className="mt-6 w-full rounded-xl border border-dashed border-blue-200 bg-blue-50 p-4 text-xs font-semibold text-blue-700">
                          Result: Not generated yet
                        </div>
                      </div>
                    </div>

                    <div className="rounded-3xl border border-cyan-100 bg-linear-to-br from-cyan-50 to-blue-50 p-6">
                      <div className="flex items-center gap-3">
                        <CheckCircle2
                          size={21}
                          className="text-blue-600"
                        />
                        <h4 className="font-extrabold text-slate-900">
                          Input Summary
                        </h4>
                      </div>

                      <p className="mt-3 text-sm text-slate-600">
                        {filledFields} of 9 fields completed.
                      </p>

                      <p className="mt-2 text-sm font-semibold text-blue-700">
                        {validFields} valid inputs
                      </p>

                      <p className="mt-2 text-xs leading-5 text-slate-500">
                        All fields require valid non-negative numbers.
                        Section length must be greater than zero.
                        Count fields require whole numbers.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                /* COST / METHOD PLACEHOLDERS */
                <section className="rounded-3xl border border-blue-100 bg-white p-8 shadow-sm sm:p-12">
                  <div className="mx-auto max-w-xl text-center">
                    <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-linear-to-br from-blue-100 to-cyan-100 text-blue-600">
                      {activeModule === 'cost' ? (
                        <CircleDollarSign size={37} />
                      ) : (
                        <Construction size={37} />
                      )}
                    </div>

                    <h3 className="mt-6 text-2xl font-extrabold text-slate-900">
                      {selectedModule.title}
                    </h3>

                    <p className="mt-4 text-sm leading-7 text-slate-500">
                      This module's input form will be added after checking
                      the exact input features of the existing trained
                      machine learning model.
                    </p>

                    <div className="mt-7 rounded-2xl border border-blue-100 bg-blue-50 px-5 py-4 text-sm font-medium text-blue-700">
                      Dashboard UI ready — model integration is the next phase.
                    </div>

                    <button
                      type="button"
                      onClick={() => navigate('overview')}
                      className="mt-7 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-700"
                    >
                      Back to Dashboard
                      <ArrowRight size={17} />
                    </button>
                  </div>
                </section>
              )}
            </>
          )}

          {/* FOOTER */}
          <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-blue-100 py-5 text-xs text-slate-400">
            <span>
              © 2026 RoadWise AI — Road Repair Priority Decision Support System
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
