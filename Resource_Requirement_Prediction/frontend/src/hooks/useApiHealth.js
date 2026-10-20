import { useState, useEffect, useCallback } from "react";

const HEALTH_ENDPOINT = "/api/health";
const POLL_INTERVAL_MS = 30_000; // 30 seconds — avoids excessive requests

/**
 * Polls the FastAPI /health endpoint and returns connection status.
 *
 * @returns {{
 *   status: "checking" | "connected" | "disconnected",
 *   modelAvailable: boolean | null,
 *   lastChecked: Date | null,
 *   error: string | null,
 * }}
 */
export function useApiHealth() {
  const [status, setStatus] = useState("checking");
  const [modelAvailable, setModelAvailable] = useState(null);
  const [lastChecked, setLastChecked] = useState(null);
  const [error, setError] = useState(null);

  const check = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(HEALTH_ENDPOINT, {
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      setStatus("connected");
      setModelAvailable(data.model_available ?? null);
      setLastChecked(new Date());
      setError(null);
    } catch (err) {
      if (err.name === "AbortError") {
        setError("Health check timed out.");
      } else {
        setError(err.message || "Could not reach the API.");
      }
      setStatus("disconnected");
      setModelAvailable(null);
    }
  }, []);

  useEffect(() => {
    check();
    const id = setInterval(check, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, [check]);

  return { status, modelAvailable, lastChecked, error };
}
