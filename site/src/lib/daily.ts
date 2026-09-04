import { existsSync, readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";

export interface DailyBriefItem {
  slug: string;
  status: "verified" | "reported" | "signal";
  importance: number;
  published_at: string;
}

export interface DailyBrief {
  schema_version: 1;
  edition_date: string;
  generated_at: string;
  status: "published" | "quiet";
  note: string;
  items: DailyBriefItem[];
}

export function loadLatestDailyBrief(): DailyBrief | null {
  const directory = resolve(process.cwd(), "..", "data", "daily");
  if (!existsSync(directory)) return null;

  const latest = readdirSync(directory)
    .filter((name) => /^\d{4}-\d{2}-\d{2}\.json$/.test(name))
    .sort()
    .at(-1);
  if (!latest) return null;

  return JSON.parse(readFileSync(resolve(directory, latest), "utf-8")) as DailyBrief;
}
