import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import yaml from "js-yaml";
import type { LegacyPillar, Track } from "./taxonomy";
import { legacyPillarForTracks } from "./taxonomy";

export type Pillar = LegacyPillar;
export type SourceType =
  | "html_page"
  | "rss_feed"
  | "github_repo"
  | "ietf_draft"
  | "gemini_search"
  | "cf_browser_run";
export type SourceTier = "primary" | "measurement" | "specialist" | "commentary";
export type SourceRole =
  | "platform-docs"
  | "standards"
  | "regulator"
  | "legal-primary"
  | "publisher"
  | "infrastructure"
  | "measurement"
  | "reporting";

interface RawSource {
  slug: string;
  type: SourceType;
  display_name: string;
  default_tracks: Track[];
  tier: SourceTier;
  role: SourceRole;
  required_for_coverage?: boolean;
  url?: string;
  repo?: string;
  draft_name?: string;
  keyword_filter?: string[];
}

export interface Source extends RawSource {
  /** Transitional compatibility for old pages; removed with the new site shell. */
  pillar: Pillar;
}

let cached: Source[] | null = null;

export function loadSources(): Source[] {
  if (cached) return cached;
  const path = resolve(process.cwd(), "..", "sources.yaml");
  const raw = readFileSync(path, "utf-8");
  const parsed = yaml.load(raw) as RawSource[];
  cached = parsed.map((source) => ({
    ...source,
    pillar: legacyPillarForTracks(source.default_tracks),
  }));
  return cached;
}

export function findSource(slug: string): Source | undefined {
  return loadSources().find((s) => s.slug === slug);
}

export function crawlerSources(): Source[] {
  return loadSources().filter((s) => s.default_tracks.includes("crawler-controls"));
}

export function countsByPillar(): Record<Pillar, number> {
  const counts: Record<Pillar, number> = { crawler: 0, ecosystem: 0, agent: 0 };
  for (const s of loadSources()) counts[s.pillar]++;
  return counts;
}
