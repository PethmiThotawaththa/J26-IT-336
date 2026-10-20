import { useState, useEffect } from "react";

const TZ = "Asia/Colombo";

function formatColomboParts() {
  const now = new Date();
  const datePart = new Intl.DateTimeFormat("en-LK", {
    timeZone: TZ,
    year: "numeric",
    month: "short",
    day: "2-digit",
  }).format(now);

  const timePart = new Intl.DateTimeFormat("en-LK", {
    timeZone: TZ,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(now);

  return { date: datePart, time: timePart };
}

/**
 * Returns live Sri Lanka time (Asia/Colombo), updated every second.
 * @returns {{ date: string, time: string }}
 */
export function useSriLankaTime() {
  const [value, setValue] = useState(formatColomboParts);

  useEffect(() => {
    const id = setInterval(() => setValue(formatColomboParts()), 1000);
    return () => clearInterval(id);
  }, []);

  return value;
}
