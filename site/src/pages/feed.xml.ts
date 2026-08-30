import type { APIRoute } from "astro";
import { findSource } from "../lib/sources";
import { loadCurrentEvents } from "../lib/events";

function esc(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export const GET: APIRoute = async ({ site }) => {
  const siteUrl = site?.toString().replace(/\/$/, "") ?? "https://tracker.example.com";
  const events = (await loadCurrentEvents())
    .filter((e) => e.data.change_kind === "material")
    .sort((a, b) => b.data.detected_at.getTime() - a.data.detected_at.getTime())
    .slice(0, 100);

  const items = events
    .map((e) => {
      const source = findSource(e.data.source);
      const link = `${siteUrl}/events/${e.data.slug}`;
      return `
    <item>
      <title>${esc(e.data.title)}</title>
      <link>${link}</link>
      <guid isPermaLink="true">${link}</guid>
      <pubDate>${e.data.event_date.toUTCString()}</pubDate>
      <category>${esc(e.data.primary_track)}</category>
      ${e.data.tracks.map((track) => `<category>${esc(track)}</category>`).join("\n      ")}
      <category>${esc(source?.display_name ?? e.data.source)}</category>
      <description>${esc(e.body?.slice(0, 4000) ?? "")}</description>
    </item>`;
    })
    .join("");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Crawler Policy Developments</title>
    <link>${siteUrl}</link>
    <atom:link href="${siteUrl}/feed.xml" rel="self" type="application/rss+xml" />
    <description>Evidence-backed developments in machine access, content rights, agent identity, and web economics.</description>
    <language>en-US</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>${items}
  </channel>
</rss>`;

  return new Response(xml, {
    headers: { "content-type": "application/rss+xml; charset=utf-8" },
  });
};
