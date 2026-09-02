import type { APIRoute } from "astro";
import { findSource } from "../lib/sources";
import { feedSection, loadFeedItems } from "../lib/feed";

function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export const GET: APIRoute = async ({ site }) => {
  const siteUrl = site?.toString().replace(/\/$/, "") ?? "https://crawlerpolicy.com";
  const events = (await loadFeedItems()).slice(0, 100);

  const items = events
    .map((e) => {
      const source = findSource(e.data.source);
      const link = `${siteUrl}/events/${e.data.slug}`;
      const label = e.data.backfilled
        ? "Backfilled"
        : e.data.status[0].toUpperCase() + e.data.status.slice(1);
      return `
    <item>
      <title>${esc(`[${label}] ${e.data.title}`)}</title>
      <link>${link}</link>
      <guid isPermaLink="true">${link}</guid>
      <pubDate>${e.data.event_date.toUTCString()}</pubDate>
      <category>${esc(e.data.primary_track)}</category>
      ${e.data.tracks.map((track) => `<category>${esc(track)}</category>`).join("\n      ")}
      <category>${esc(source?.display_name ?? e.data.source)}</category>
      <description>${esc(`${feedSection(e.body, "Summary")}\n\nWhy it matters: ${feedSection(e.body, "Why it matters")}`)}</description>
    </item>`;
    })
    .join("");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Crawler Policy Ecosystem Feed</title>
    <link>${siteUrl}</link>
    <atom:link href="${siteUrl}/feed.xml" rel="self" type="application/rss+xml" />
    <description>Daily verified developments, reported intelligence, and early signals across the machine-readable web.</description>
    <language>en-US</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>${items}
  </channel>
</rss>`;

  return new Response(xml, {
    headers: { "content-type": "application/rss+xml; charset=utf-8" },
  });
};
