import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export interface InsightThread {
  key: string;
  title: string;
  thesis: string;
  direction: "emerging" | "developing";
  confidence: "low" | "medium" | "high";
  first_observed_at: string;
  last_updated_at: string;
  related_feed_slugs: string[];
  verified_development_slugs: string[];
}

interface InsightThreadRegistry {
  schema_version: 1;
  threads: InsightThread[];
}

const directionRank = { developing: 1, emerging: 0 } as const;
const confidenceRank = { high: 2, medium: 1, low: 0 } as const;

export function loadInsightThreads(): InsightThread[] {
  const path = resolve(process.cwd(), "..", "data", "insight-threads.json");
  if (!existsSync(path)) return [];
  const registry = JSON.parse(readFileSync(path, "utf-8")) as InsightThreadRegistry;
  return registry.threads.sort(
    (left, right) =>
      directionRank[right.direction] - directionRank[left.direction]
      || confidenceRank[right.confidence] - confidenceRank[left.confidence]
      || Date.parse(right.last_updated_at) - Date.parse(left.last_updated_at)
      || right.related_feed_slugs.length - left.related_feed_slugs.length,
  );
}
