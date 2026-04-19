import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export interface PillarDigest {
  headline: string;
  body: string;
  themes: string[];
  event_count: number;
  window_days: number;
}

export interface PillarDigests {
  generated_at: string;
  crawler: PillarDigest;
  ecosystem: PillarDigest;
  agent: PillarDigest;
}

export function loadPillarDigests(): PillarDigests | null {
  const p = resolve(process.cwd(), "..", "data", "pillar-digests.json");
  if (!existsSync(p)) return null;
  return JSON.parse(readFileSync(p, "utf-8"));
}
