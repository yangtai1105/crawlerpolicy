import { readdirSync, existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createPatch } from "diff";

export interface Snapshot {
  date: string;
  filename: string;
}

export function listSnapshots(slug: string): Snapshot[] {
  const dir = resolve(process.cwd(), "..", "content", "snapshots", slug);
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => /^\d{4}-\d{2}-\d{2}\./.test(f))
    .map((f) => ({ date: f.slice(0, 10), filename: f }))
    .sort((a, b) => b.date.localeCompare(a.date));
}

export function readSnapshot(slug: string, filename: string): string {
  const dir = resolve(process.cwd(), "..", "content", "snapshots", slug);
  return readFileSync(resolve(dir, filename), "utf-8");
}

export function daysSinceLatest(slug: string): number | null {
  const snaps = listSnapshots(slug);
  if (!snaps.length) return null;
  const latest = new Date(snaps[0].date);
  const now = new Date();
  return Math.floor((now.getTime() - latest.getTime()) / (1000 * 60 * 60 * 24));
}

export interface SnapshotTransition {
  prev: Snapshot;
  next: Snapshot;
  daysSpanned: number;
  unifiedDiff: string;
  added: number;
  removed: number;
}

/** Build pairwise (prev → next) transitions for a source's snapshot history,
 *  newest transition first. Suppresses transitions where the content is
 *  byte-identical after normalization. */
export function listTransitions(slug: string): SnapshotTransition[] {
  const snaps = listSnapshots(slug);
  if (snaps.length < 2) return [];
  const sortedAsc = [...snaps].reverse();
  const out: SnapshotTransition[] = [];
  for (let i = 1; i < sortedAsc.length; i++) {
    const prev = sortedAsc[i - 1];
    const next = sortedAsc[i];
    const prevText = readSnapshot(slug, prev.filename);
    const nextText = readSnapshot(slug, next.filename);
    if (prevText.trim() === nextText.trim()) continue;
    const unifiedDiff = createPatch(
      slug,
      prevText,
      nextText,
      prev.date,
      next.date,
      { context: 3 },
    );
    const added = (unifiedDiff.match(/^\+[^+]/gm) || []).length;
    const removed = (unifiedDiff.match(/^-[^-]/gm) || []).length;
    const daysSpanned = Math.round(
      (new Date(next.date).getTime() - new Date(prev.date).getTime()) /
        (1000 * 60 * 60 * 24),
    );
    out.push({ prev, next, daysSpanned, unifiedDiff, added, removed });
  }
  return out.reverse(); // newest transition first
}
