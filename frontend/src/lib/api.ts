import { useEffect, useState } from "react";

const BASE = import.meta.env.VITE_API_BASE ?? "";

export async function get<T>(path: string, params: Record<string, string | undefined> = {}): Promise<T> {
  const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v) as [string, string][]).toString();
  const r = await fetch(`${BASE}/api${path}${qs ? `?${qs}` : ""}`);
  if (!r.ok) throw new Error(r.status === 404 ? "Not found" : `Request failed (${r.status})`);
  return r.json();
}

export function useApi<T>(path: string, params: Record<string, string | undefined> = {}) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const key = path + JSON.stringify(params);
  const [tick, setTick] = useState(0);
  useEffect(() => {
    let live = true;
    setError(null);
    get<T>(path, params).then((d) => live && setData(d)).catch((e) => live && setError(e.message));
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, tick]);
  // Serverless hosts cannot hold a stream open, so poll once a minute while the tab is visible.
  useEffect(() => {
    const id = setInterval(() => { if (document.visibilityState === "visible") setTick((t) => t + 1); }, 60_000);
    return () => clearInterval(id);
  }, []);
  return { data, error, loading: !data && !error };
}
