import { existsSync, readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export interface DispatchItem {
  topic: string;
  tag: string;
  source_domain: string;
  url: string;
  title: string;
  frame: string;
  quote: string;
  kind?: string;
}

export interface DispatchTopic {
  topic: string;
  tldr: string;
  items: DispatchItem[];
}

export interface WeeklyDispatch {
  generated_at: string;
  iso_year: number;
  iso_week: number;
  topics: DispatchTopic[];
}

function dir(): string {
  return resolve(process.cwd(), "..", "data", "critical-reading");
}

export function listWeeks(): { year: number; week: number; filename: string }[] {
  const d = dir();
  if (!existsSync(d)) return [];
  const out: { year: number; week: number; filename: string }[] = [];
  for (const name of readdirSync(d)) {
    const m = /^(\d{4})-W(\d{2})\.json$/.exec(name);
    if (!m) continue;
    out.push({ year: Number(m[1]), week: Number(m[2]), filename: name });
  }
  out.sort((a, b) => b.year * 100 + b.week - (a.year * 100 + a.week));
  return out;
}

export function loadWeek(filename: string): WeeklyDispatch | null {
  const p = resolve(dir(), filename);
  if (!existsSync(p)) return null;
  const raw = JSON.parse(readFileSync(p, "utf-8"));

  // Back-compat: older format had a flat items list at the root, not per-topic.
  if (raw.topics && Array.isArray(raw.topics)) return raw as WeeklyDispatch;
  if (Array.isArray(raw.items)) {
    const map = new Map<string, DispatchTopic>();
    const order: string[] = raw.topic_groups || [];
    for (const t of order) map.set(t, { topic: t, tldr: "", items: [] });
    for (const it of raw.items as DispatchItem[]) {
      if (!map.has(it.topic)) map.set(it.topic, { topic: it.topic, tldr: "", items: [] });
      map.get(it.topic)!.items.push(it);
    }
    return {
      generated_at: raw.generated_at,
      iso_year: raw.iso_year,
      iso_week: raw.iso_week,
      topics: Array.from(map.values()),
    };
  }
  return null;
}

export function loadLatest(): WeeklyDispatch | null {
  const weeks = listWeeks();
  if (weeks.length === 0) return null;
  return loadWeek(weeks[0].filename);
}
