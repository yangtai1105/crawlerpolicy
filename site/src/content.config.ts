import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { glob } from "astro/loaders";

const track = z.enum([
  "policy-regulation",
  "litigation-legal",
  "search-discovery",
  "crawler-controls",
  "agentic-web",
  "licensing-monetization",
  "standards-protocols",
  "asset-rights",
  "measurement-economics",
]);

const events = defineCollection({
  loader: glob({
    pattern: "**/*.md",
    base: "../content/events",
  }),
  schema: z.object({
    schema_version: z.literal(2),
    slug: z.string(),
    title: z.string(),
    source: z.string(),
    source_tier: z.enum(["primary", "measurement", "specialist", "commentary"]),
    primary_track: track,
    tracks: z.array(track).min(1),
    actors: z.array(z.string()).default([]),
    event_date: z.coerce.date(),
    published_at: z.coerce.date(),
    detected_at: z.coerce.date(),
    source_url: z.string().optional().default(""),
    change_kind: z.enum(["material", "cosmetic", "noise"]),
    importance: z.number().min(0).max(1),
    confidence: z.enum(["low", "medium", "high"]),
    evidence_ids: z.array(z.string()).min(1),
  }),
});

const feed = defineCollection({
  loader: glob({
    pattern: "**/*.md",
    base: "../content/feed",
  }),
  schema: z.object({
    schema_version: z.literal(1),
    slug: z.string(),
    title: z.string(),
    source: z.string(),
    source_tier: z.enum(["primary", "measurement", "specialist", "commentary"]),
    status: z.enum(["verified", "reported", "signal"]),
    primary_track: track,
    tracks: z.array(track).min(1),
    actors: z.array(z.string()).default([]),
    event_date: z.coerce.date(),
    published_at: z.coerce.date(),
    detected_at: z.coerce.date(),
    source_urls: z.array(z.string().url()).min(1),
    change_kind: z.enum(["material", "cosmetic", "noise"]),
    importance: z.number().min(0).max(1),
    confidence: z.enum(["low", "medium", "high"]),
    evidence_ids: z.array(z.string()).min(1),
    development_slug: z.string().optional(),
  }),
});

const legacyEvents = defineCollection({
  loader: glob({
    pattern: "**/*.md",
    base: "../content/legacy-events",
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

export const collections = { feed, events, legacyEvents };
