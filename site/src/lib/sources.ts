import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import yaml from "js-yaml";
import type { Track } from "./taxonomy";

export type SourceType =
  | "html_page"
  | "rss_feed"
  | "github_repo"
  | "ietf_draft"
  | "gemini_search"
  | "cf_browser_run"
  | "xai_search";
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

export interface Source {
  slug: string;
  type: SourceType;
  display_name: string;
  default_tracks: Track[];
  tier: SourceTier;
  role: SourceRole;
  enabled?: boolean;
  required_for_coverage?: boolean;
  url?: string;
  repo?: string;
  draft_name?: string;
  keyword_filter?: string[];
  query?: string;
  x_handles?: string[];
  lookback_hours?: number;
  shadow?: boolean;
}

let cached: Source[] | null = null;

export function loadSources(): Source[] {
  if (cached) return cached;
  const path = resolve(process.cwd(), "..", "sources.yaml");
  const raw = readFileSync(path, "utf-8");
  cached = yaml.load(raw) as Source[];
  return cached;
}

export function findSource(slug: string): Source | undefined {
  return loadSources().find((s) => s.slug === slug);
}

export function crawlerSources(): Source[] {
  return loadSources().filter((s) => s.default_tracks.includes("crawler-controls"));
}
