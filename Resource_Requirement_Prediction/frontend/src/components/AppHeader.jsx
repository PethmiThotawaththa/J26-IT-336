import { useState } from "react";
import { useSriLankaTime } from "../hooks/useSriLankaTime.js";
import { useApiHealth } from "../hooks/useApiHealth.js";

const NAV_LINKS = [
  { id: "overview",    label: "Overview" },
  { id: "history",     label: "Historical Data" },
  { id: "prediction",  label: "Resource Prediction" },
  { id: "inventory",   label: "Resource Inventory" },
  { id: "allocation",  label: "Allocation Planner" },
  { id: "results",     label: "Results & Reports" },
  { id: "map",         label: "Map View" },
];

function ApiStatusPill({ status, modelAvailable, lastChecked }) {
  const dot =
    status === "connected"
      ? "bg-green-400"
      : status === "disconnected"
        ? "bg-red-400"
        : "bg-amber-400 animate-pulse";

  const label =
    status === "connected"
      ? "Connected"
      : status === "disconnected"
        ? "Disconnected"
        : "Checking…";

  const color =
    status === "connected"
      ? "text-green-300"
      : status === "disconnected"
        ? "text-red-300"
        : "text-amber-300";

  return (
    <div className="flex items-center gap-1.5" title={lastChecked ? `Last checked: ${lastChecked.toLocaleTimeString("en-LK")}` : undefined}>
      <span className={`h-2 w-2 rounded-full shrink-0 ${dot}`} aria-hidden="true" />
      <span className={`text-xs font-medium ${color}`}>
        API: {label}
      </span>
      {status === "connected" && modelAvailable === false && (
        <span className="text-xs text-amber-300" title="ML model file not found on server">
          · Model missing
        </span>
      )}
    </div>
  );
}

/**
 * AppHeader — consistent application header with nav, live clock, and API status.
 *
 * @param {{ activePage: string, onNavigate: (page: string) => void }} props
 */
export function AppHeader({ activePage, onNavigate }) {
  const { date, time } = useSriLankaTime();
  const { status, modelAvailable, lastChecked } = useApiHealth();
  const [mobileOpen, setMobileOpen] = useState(false);

  function handleNav(id) {
    onNavigate(id);
    setMobileOpen(false);
  }

  return (
    <header
      className="sticky top-0 z-50 shadow-md"
      style={{ backgroundColor: "var(--color-forest)" }}
    >
      {/* ── Top bar ─────────────────────────────────────────── */}
      <div className="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between gap-4 py-3">

          {/* Brand */}
          <div className="flex items-center gap-3 shrink-0">
            <div
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-xl"
              style={{ backgroundColor: "var(--color-brand)" }}
              aria-hidden="true"
            >
              🛣️
            </div>
            <div>
              <p className="text-sm font-bold leading-tight text-white sm:text-base">
                Road Resource Planner
              </p>
              <p className="hidden text-[11px] leading-tight text-green-300 sm:block">
                AI-Driven Road Maintenance Decision Support
              </p>
            </div>
          </div>

          {/* Right-side status bar */}
          <div className="hidden items-center gap-4 lg:flex">
            <ApiStatusPill
              status={status}
              modelAvailable={modelAvailable}
              lastChecked={lastChecked}
            />
            <div
              className="h-4 w-px"
              style={{ backgroundColor: "rgba(255,255,255,0.2)" }}
              aria-hidden="true"
            />
            <div className="text-right">
              <p className="text-xs font-semibold text-white tabular-nums">{time}</p>
              <p className="text-[11px] text-green-300">{date} · Sri Lanka (IST)</p>
            </div>
          </div>

          {/* Mobile hamburger */}
          <button
            id="mobile-menu-toggle"
            type="button"
            aria-label={mobileOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((prev) => !prev)}
            className="flex items-center justify-center rounded-lg p-2 text-white transition hover:bg-white/10 lg:hidden"
          >
            {mobileOpen ? (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {/* ── Desktop nav ───────────────────────────────────── */}
        <nav
          aria-label="Main navigation"
          className="hidden border-t border-white/10 pb-0 lg:block"
        >
          <ul className="flex items-center gap-0">
            {NAV_LINKS.map((link) => {
              const isActive = activePage === link.id;
              return (
                <li key={link.id}>
                  <button
                    id={`nav-${link.id}`}
                    type="button"
                    aria-current={isActive ? "page" : undefined}
                    onClick={() => handleNav(link.id)}
                    className={`
                      relative px-3 py-2.5 text-sm font-medium transition-colors duration-150
                      focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60
                      ${isActive
                        ? "text-white"
                        : "text-green-200 hover:text-white"
                      }
                    `}
                  >
                    {link.label}
                    {isActive && (
                      <span
                        className="absolute bottom-0 left-0 right-0 h-0.5 rounded-t"
                        style={{ backgroundColor: "var(--color-brand)" }}
                        aria-hidden="true"
                      />
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>

      {/* ── Mobile nav drawer ─────────────────────────────── */}
      {mobileOpen && (
        <div
          className="border-t border-white/10 lg:hidden"
          style={{ backgroundColor: "var(--color-forest)" }}
        >
          {/* Status bar (mobile) */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
            <ApiStatusPill
              status={status}
              modelAvailable={modelAvailable}
              lastChecked={lastChecked}
            />
            <div className="text-right">
              <p className="text-xs font-semibold text-white tabular-nums">{time}</p>
              <p className="text-[11px] text-green-300">{date} · IST</p>
            </div>
          </div>

          <nav aria-label="Mobile navigation">
            <ul className="py-2">
              {NAV_LINKS.map((link) => {
                const isActive = activePage === link.id;
                return (
                  <li key={link.id}>
                    <button
                      id={`mobile-nav-${link.id}`}
                      type="button"
                      aria-current={isActive ? "page" : undefined}
                      onClick={() => handleNav(link.id)}
                      className={`
                        flex w-full items-center px-6 py-3 text-sm font-medium transition-colors
                        ${isActive
                          ? "text-white"
                          : "text-green-200 hover:text-white hover:bg-white/5"
                        }
                      `}
                    >
                      {isActive && (
                        <span
                          className="mr-3 h-4 w-0.5 rounded"
                          style={{ backgroundColor: "var(--color-brand)" }}
                          aria-hidden="true"
                        />
                      )}
                      {link.label}
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>
      )}
    </header>
  );
}
