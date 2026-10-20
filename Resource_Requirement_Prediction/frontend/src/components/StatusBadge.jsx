/**
 * StatusBadge — shows data provenance labels as coloured pills.
 *
 * Supported statuses (case-insensitive):
 *   SIMULATED | PREDICTED | ACTUAL | ESTIMATED | OPTIMIZED | DEMO
 */

const CLASS_MAP = {
  simulated: "badge-simulated",
  predicted: "badge-predicted",
  actual:    "badge-actual",
  estimated: "badge-estimated",
  optimized: "badge-optimized",
  demo:      "badge-demo",
};

const LABEL_MAP = {
  simulated: "SIMULATED DATA",
  predicted: "PREDICTED",
  actual:    "ACTUAL",
  estimated: "ESTIMATED",
  optimized: "OPTIMIZED",
  demo:      "DEMO",
};

/**
 * @param {{ status: string, className?: string }} props
 */
export function StatusBadge({ status = "simulated", className = "" }) {
  const key = String(status).toLowerCase();
  const cls = CLASS_MAP[key] || "badge-simulated";
  const label = LABEL_MAP[key] || String(status).toUpperCase();

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5
        text-xs font-semibold tracking-wide uppercase ${cls} ${className}`}
    >
      {label}
    </span>
  );
}
