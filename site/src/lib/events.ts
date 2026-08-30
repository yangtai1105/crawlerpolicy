import { existsSync, readdirSync } from "node:fs";
import { resolve } from "node:path";
import { getCollection, type CollectionEntry } from "astro:content";

export async function loadCurrentEvents(): Promise<CollectionEntry<"events">[]> {
  const directory = resolve(process.cwd(), "..", "content", "events");
  if (!existsSync(directory) || !readdirSync(directory).some((name) => name.endsWith(".md"))) {
    return [];
  }
  return getCollection("events");
}
