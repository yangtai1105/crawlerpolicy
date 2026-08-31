import { existsSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import { getCollection, type CollectionEntry } from "astro:content";

const REQUIRED_SECTIONS = ["Summary", "Insight", "Implication", "Why it matters", "Evidence"];

export function feedSection(body: string | undefined, heading: string): string {
  const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = body?.match(new RegExp(`^## ${escaped}\\s*$\\n+([\\s\\S]*?)(?=^## |$)`, "m"));
  return match?.[1].trim() ?? "";
}

export function validateFeedBody(item: CollectionEntry<"feed">): void {
  const missing = REQUIRED_SECTIONS.filter((heading) => !feedSection(item.body, heading));
  if (missing.length) {
    throw new Error(`${item.data.slug} is missing feed sections: ${missing.join(", ")}`);
  }
}

export async function loadFeedItems(): Promise<CollectionEntry<"feed">[]> {
  const directory = resolve(process.cwd(), "..", "content", "feed");
  if (!existsSync(directory) || !readdirSync(directory).some((name) => name.endsWith(".md"))) {
    return [];
  }
  const items = await getCollection("feed");
  items.forEach(validateFeedBody);
  return items.sort(
    (left, right) => right.data.published_at.getTime() - left.data.published_at.getTime(),
  );
}
