const FOOTER_LINKS = [
  { id: "overview",   label: "Overview" },
  { id: "history",    label: "Historical Data" },
  { id: "allocation", label: "Allocation Planner" },
  { id: "results",    label: "Results & Reports" },
  { id: "map",        label: "Map View" },
];

/**
 * AppFooter — consistent page footer with nav, disclaimer, and dynamic year.
 *
 * @param {{ onNavigate: (page: string) => void }} props
 */
export function AppFooter({ onNavigate }) {
  const year = new Date().getFullYear();

  return (
    <footer
      className="mt-auto border-t"
      style={{ borderColor: "var(--color-border)", backgroundColor: "#fff" }}
    >
      <div className="mx-auto max-w-[1400px] px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">

          {/* Brand column */}
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl" aria-hidden="true">🛣️</span>
              <span
                className="text-sm font-bold"
                style={{ color: "var(--color-forest)" }}
              >
                Road Resource Planner
              </span>
            </div>
            <p className="mt-2 text-xs leading-5" style={{ color: "var(--color-secondary)" }}>
              AI-Driven Multi-Resource Allocation and Planning for Road Maintenance
            </p>
            <span
              className="mt-3 inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold"
              style={{ backgroundColor: "var(--color-amber-bg)", color: "#7A5300" }}
            >
              Research Prototype
            </span>
          </div>

          {/* Navigation column */}
          <div>
            <p
              className="mb-3 text-xs font-semibold uppercase tracking-wide"
              style={{ color: "var(--color-secondary)" }}
            >
              Navigation
            </p>
            <ul className="space-y-1.5">
              {FOOTER_LINKS.map((link) => (
                <li key={link.id}>
                  <button
                    id={`footer-nav-${link.id}`}
                    type="button"
                    onClick={() => onNavigate(link.id)}
                    className="text-sm transition-colors hover:underline"
                    style={{ color: "var(--color-secondary)" }}
                  >
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Disclaimer column */}
          <div>
            <p
              className="mb-2 text-xs font-semibold uppercase tracking-wide"
              style={{ color: "var(--color-secondary)" }}
            >
              Important Notice
            </p>
            <p className="text-xs leading-5" style={{ color: "var(--color-secondary)" }}>
              Decision-support prototype. Predictions and allocations require
              validation against approved engineering norms or actual resource
              records before operational use.
            </p>
            <p className="mt-2 text-xs leading-5" style={{ color: "var(--color-secondary)" }}>
              All demo data is labelled <strong>SIMULATED</strong> and does not
              represent real RDA records or government-approved findings.
            </p>
          </div>
        </div>

        {/* Bottom bar */}
        <div
          className="mt-8 border-t pt-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"
          style={{ borderColor: "var(--color-border)" }}
        >
          <p className="text-xs" style={{ color: "var(--color-secondary)" }}>
            © {year} Road Resource Planner · Research prototype · For academic evaluation only
          </p>
          <p className="text-xs" style={{ color: "var(--color-secondary)" }}>
            Final Year Research Project · SLIIT
          </p>
        </div>
      </div>
    </footer>
  );
}
