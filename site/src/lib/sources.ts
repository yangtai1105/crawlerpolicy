import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import yaml from "js-yaml";

export type Pillar = "crawler" | "ecosystem" | "agent";
export type SourceType = "html_page" | "rss_feed" | "github_repo" | "ietf_draft";

export interface Source {
  slug: string;
  pillar: Pillar;
  type: SourceType;
  display_name: string;
  url?: string;
  repo?: string;
  draft_name?: string;
  keyword_filter?: string[];
}

let cached: Source[] | null = null;

export function loadSources(): Source[] {
  if (cached) return cached;
  const path = resolve(process.cwd(), "..", "sources.yaml");
  const raw = readFileSync(path, "utf-8");
  const parsed = yaml.load(raw) as Source[];
  cached = parsed;
  return parsed;
}

export function findSource(slug: string): Source | undefined {
  return loadSources().find((s) => s.slug === slug);
}

export function crawlerSources(): Source[] {
  return loadSources().filter((s) => s.pillar === "crawler");
}

export function countsByPillar(): Record<Pillar, number> {
  const counts: Record<Pillar, number> = { crawler: 0, ecosystem: 0, agent: 0 };
  for (const s of loadSources()) counts[s.pillar]++;
  return counts;
}
