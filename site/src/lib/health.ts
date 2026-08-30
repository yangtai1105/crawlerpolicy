import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

export type HealthStatus = "healthy" | "degraded" | "critical" | "unknown";
export type StageStatus = "ok" | "failed" | "pending";

export interface SourceStageHealth {
  fetch: StageStatus;
  evidence: StageStatus;
  analysis: StageStatus;
  publish: StageStatus;
  error?: string | null;
}

export interface PipelineHealth {
  status: HealthStatus;
  last_attempted_at: string | null;
  last_fully_successful_at: string | null;
  coverage: {
    configured: number;
    completed: number;
    fetched: number;
    analyzed: number;
    published: number;
    failed: number;
    required_failed: number;
  };
  per_source: Record<string, SourceStageHealth>;
}

const EMPTY: PipelineHealth = {
  status: "unknown",
  last_attempted_at: null,
  last_fully_successful_at: null,
  coverage: {
    configured: 0,
    completed: 0,
    fetched: 0,
    analyzed: 0,
    published: 0,
    failed: 0,
    required_failed: 0,
  },
  per_source: {},
};

export function loadHealth(): PipelineHealth {
  const path = resolve(process.cwd(), "..", "data", "health.json");
  if (!existsSync(path)) return EMPTY;
  try {
    const raw = JSON.parse(readFileSync(path, "utf-8"));
    if (!["healthy", "degraded", "critical"].includes(raw.status)) return EMPTY;
    return {
      ...EMPTY,
      ...raw,
      coverage: { ...EMPTY.coverage, ...(raw.coverage ?? {}) },
      per_source: raw.per_source ?? {},
    } as PipelineHealth;
  } catch {
    return EMPTY;
  }
}
