import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const events = defineCollection({
  loader: glob({
    pattern: "**/*.md",
    base: "../content/events",
  }),
  schema: z.object({
    slug: z.string(),
    title: z.string(),
    source: z.string(),
    pillar: z.enum(["crawler", "ecosystem", "agent"]),
    detected_at: z.coerce.date(),
    source_url: z.string().optional().default(""),
    change_kind: z.enum(["material", "cosmetic", "noise"]),
    importance: z.number().min(0).max(1),
  }),
});

export const collections = { events };
