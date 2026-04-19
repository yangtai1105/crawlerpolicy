import { existsSync, readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export interface CriticalReadingItem {
  topic: string;
  tag: string;
  source_domain: string;
  url: string;
  title: string;
  frame: string;
  quote: string;
}

export interface CriticalReadingDigest {
  generated_at: string;
  iso_year: number;
  iso_week: number;
  topic_groups: string[];
  items: CriticalReadingItem[];
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

export function loadWeek(filename: string): CriticalReadingDigest | null {
  const p = resolve(dir(), filename);
  if (!existsSync(p)) return null;
  return JSON.parse(readFileSync(p, "utf-8"));
}

export function loadLatest(): CriticalReadingDigest | null {
  const weeks = listWeeks();
  if (weeks.length === 0) return null;
  return loadWeek(weeks[0].filename);
}

export function groupByTopic(
  items: CriticalReadingItem[],
  topics: string[],
): Map<string, CriticalReadingItem[]> {
  const m = new Map<string, CriticalReadingItem[]>();
  for (const t of topics) m.set(t, []);
  for (const it of items) {
    const bucket = m.get(it.topic);
    if (bucket) bucket.push(it);
    else {
      // Unknown topic — keep it, but at the end.
      if (!m.has(it.topic)) m.set(it.topic, []);
      m.get(it.topic)!.push(it);
    }
  }
  return m;
}
