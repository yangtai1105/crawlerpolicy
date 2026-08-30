import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export type TrendStatus = "accelerating" | "stable" | "emerging" | "reversing" | "stalled";

export interface Trend {
  key: string;
  title: string;
  status: TrendStatus;
  previous_status?: TrendStatus | null;
  thesis: string;
  evidence_event_ids: string[];
  last_material_update?: string | null;
  delta_explanation: string;
}

export function loadTrends(): Trend[] {
  const path = resolve(process.cwd(), "..", "data", "trends.json");
  if (!existsSync(path)) return [];
  try {
    const raw = JSON.parse(readFileSync(path, "utf-8"));
    return Array.isArray(raw.trends) ? raw.trends : [];
  } catch {
    return [];
  }
}

export function sortTrendsByDelta(trends: Trend[]): Trend[] {
  return [...trends].sort((a, b) => {
    const aChanged = a.previous_status && a.previous_status !== a.status ? 1 : 0;
    const bChanged = b.previous_status && b.previous_status !== b.status ? 1 : 0;
    return bChanged - aChanged || a.title.localeCompare(b.title);
  });
}
