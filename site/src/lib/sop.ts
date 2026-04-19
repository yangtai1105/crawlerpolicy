import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

export interface CrawlerUA {
  name: string;
  purpose: string;
  scope?: string;
  opt_out?: string;
}

export interface OptOutEntry {
  slug: string;
  display_name: string;
  supports_robots_txt: boolean | null;
  supports_user_agent_opt_out: boolean | null;
  policy_url: string;
  days_since_last_change: number;
  last_snapshot_date: string;
  user_agents?: CrawlerUA[];
}

export interface OptOutMatrix {
  generated_at: string;
  entries: OptOutEntry[];
}

export function findOptOutEntry(slug: string): OptOutEntry | undefined {
  return loadOptOutMatrix().entries.find((e) => e.slug === slug);
}

function tryLoad<T>(relPath: string, fallback: T): T {
  const p = resolve(process.cwd(), "..", "data", relPath);
  if (!existsSync(p)) return fallback;
  return JSON.parse(readFileSync(p, "utf-8"));
}

export function loadOptOutMatrix(): OptOutMatrix {
  return tryLoad("opt-out-matrix.json", { generated_at: "", entries: [] });
}

export function loadHealth(): { last_run_at: string; per_source_status: Record<string, string> } {
  return tryLoad("health.json", { last_run_at: "", per_source_status: {} });
}
