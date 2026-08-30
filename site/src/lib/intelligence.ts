import { existsSync, readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export interface WeeklyIntelligence {
  schema_version: number;
  week: string;
  generated_at: string;
  window_start: string;
  window_end: string;
  health_status: string;
  coverage: Record<string, number>;
  thesis: string;
  executive_shifts: Array<{
    headline: string;
    summary: string;
    evidence_event_ids: string[];
  }>;
  material_developments: Array<{
    track: string;
    material_change: boolean;
    event_ids: string[];
    summary: string;
  }>;
  intelligence_read: string;
  trend_deltas: Array<Record<string, unknown>>;
  actor_moves: Array<Record<string, unknown>>;
  watchlist: Array<{ question: string; tracks: string[] }>;
  source_ledger: Array<Record<string, unknown>>;
  model_generated: boolean;
}

function directory(): string {
  return resolve(process.cwd(), "..", "data", "intelligence");
}

export function loadIntelligenceArchive(): WeeklyIntelligence[] {
  const dir = directory();
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((name) => /^\d{4}-W\d{2}\.json$/.test(name))
    .sort()
    .reverse()
    .map((name) => JSON.parse(readFileSync(resolve(dir, name), "utf-8")));
}

export function loadLatestIntelligence(): WeeklyIntelligence | null {
  return loadIntelligenceArchive()[0] ?? null;
}

export function loadIntelligenceWeek(week: string): WeeklyIntelligence | null {
  const path = resolve(directory(), `${week}.json`);
  return existsSync(path) ? JSON.parse(readFileSync(path, "utf-8")) : null;
}
