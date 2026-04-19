import { readdirSync, existsSync } from "node:fs";
import { resolve } from "node:path";

export function listSnapshots(slug: string): { date: string; filename: string }[] {
  const dir = resolve(process.cwd(), "..", "content", "snapshots", slug);
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => /^\d{4}-\d{2}-\d{2}\./.test(f))
    .map((f) => ({ date: f.slice(0, 10), filename: f }))
    .sort((a, b) => b.date.localeCompare(a.date));
}

export function daysSinceLatest(slug: string): number | null {
  const snaps = listSnapshots(slug);
  if (!snaps.length) return null;
  const latest = new Date(snaps[0].date);
  const now = new Date();
  return Math.floor((now.getTime() - latest.getTime()) / (1000 * 60 * 60 * 24));
}
