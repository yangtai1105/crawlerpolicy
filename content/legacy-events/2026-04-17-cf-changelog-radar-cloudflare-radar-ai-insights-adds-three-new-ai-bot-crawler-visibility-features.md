---
slug: cloudflare-radar-ai-insights-adds-three-new-ai-bot-crawler-visibility-features
title: "Cloudflare Radar AI Insights adds three new AI bot/crawler visibility features"
source: cf-changelog-radar
pillar: crawler
detected_at: 2026-04-17T08:00:00+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-04-17-radar-ai-insights-updates/"
change_kind: material
importance: 0.65
---

## What changed

Cloudflare Radar's [AI Insights page](https://radar.cloudflare.com/ai-insights) gained three new features (announced 2026-04-17): (1) an [Adoption of AI Agent Standards widget](https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards) tracking website adoption of agent-facing standards (filterable by domain category, updated weekly), backed by a new [Agent Readiness API](https://developers.cloudflare.com/api/resources/radar/subresources/agent_readiness/methods/summary/); (2) a [Markdown for Agents savings gauge](https://radar.cloudflare.com/ai-insights#markdown-for-agents-savings) showing median response-size reduction when serving Markdown vs. HTML to AI bots, with a corresponding [Markdown for Agents API](https://developers.cloudflare.com/api/resources/radar/subresources/ai/subresources/markdown_for_agents/methods/summary); and (3) a [Response Status widget](https://radar.cloudflare.com/ai-insights#response-status) showing HTTP status code distribution (200/403/404 or 2xx–5xx groupings) for AI bot/crawler traffic, also surfaced on individual verified bot detail pages. The [URL Scanner](https://radar.cloudflare.com/scan) also gained an **Agent Readiness** tab evaluating scanned URLs against the [isitagentready.com](https://isitagentready.com/) scoring criteria.

## Implication

Operators and researchers can now use Cloudflare Radar to audit how broadly AI agent standards (e.g., llms.txt, robots.txt AI directives) are being adopted across the web, quantify bandwidth/token savings from Markdown serving, and inspect how sites are responding (blocking vs. allowing) to specific AI crawlers — all via both the dashboard UI and new API endpoints.

