import { StatusBadge } from "../components/StatusBadge.jsx";

/**
 * PlaceholderPage — shown for pages not yet implemented.
 * Displays the page name, phase info, and a "coming soon" notice.
 *
 * @param {{ title: string, phase: string, description: string, icon: string }} props
 */
export function PlaceholderPage({ title, phase, description, icon }) {
  return (
    <div className="mx-auto max-w-[1400px] px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <StatusBadge status="simulated" />
        <span
          className="inline-flex items-center rounded-full px-2.5 py-0.5
            text-xs font-semibold uppercase tracking-wide"
          style={{
            backgroundColor: "var(--color-blue-bg)",
            color: "var(--color-blue)",
          }}
        >
          {phase}
        </span>
      </div>

      <h1
        className="text-2xl font-bold sm:text-3xl mb-2"
        style={{ color: "var(--color-text)" }}
      >
        {icon} {title}
      </h1>
      <p
        className="text-sm leading-7 max-w-2xl"
        style={{ color: "var(--color-secondary)" }}
      >
        {description}
      </p>

      <div
        className="mt-10 flex flex-col items-center justify-center rounded-2xl
          border-2 border-dashed py-20 text-center"
        style={{
          borderColor: "var(--color-border)",
          backgroundColor: "#fff",
        }}
      >
        <div
          className="flex h-20 w-20 items-center justify-center rounded-2xl text-4xl mb-4"
          style={{ backgroundColor: "var(--color-light)" }}
          aria-hidden="true"
        >
          {icon}
        </div>
        <h2
          className="text-base font-bold"
          style={{ color: "var(--color-text)" }}
        >
          {title}
        </h2>
        <p
          className="mt-2 max-w-sm text-sm leading-6"
          style={{ color: "var(--color-secondary)" }}
        >
          This module will be implemented in a future phase. The Resource
          Prediction page is fully functional — use the navigation to access it.
        </p>
        <span
          className="mt-4 inline-block rounded-full px-3 py-1 text-xs font-semibold"
          style={{
            backgroundColor: "var(--color-amber-bg)",
            color: "#7A5300",
          }}
        >
          Planned · {phase}
        </span>
      </div>
    </div>
  );
}
