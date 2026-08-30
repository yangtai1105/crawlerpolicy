---
slug: cloudflare-ai-crawl-control-adds-content-format-insights-and-renames-robots-txt-
title: "Cloudflare AI Crawl Control adds Content Format insights and renames Robots.txt tab to \"Directives\""
source: cf-changelog-ai-crawl-control
pillar: crawler
detected_at: 2026-04-17T08:00:00+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-04-17-tools-for-agentic-internet/"
change_kind: material
importance: 0.65
---

## What changed

Cloudflare's [AI Crawl Control changelog](https://developers.cloudflare.com/changelog/post/2026-04-17-tools-for-agentic-internet/) documents two new additions: (1) a **Content Format** chart in the Metrics tab showing what content types AI systems request vs. what the origin serves; (2) the **Robots.txt** tab has been renamed to **Directives** and now includes a link to the third-party [Agent Readiness score checker](https://isitagentready.com). Both changes are framed around readiness for an "agentic Internet" where AI agents are treated as first-class web citizens.

## Implication

Site operators using Cloudflare's AI Crawl Control now have a new signal (Content Format chart) to diagnose mismatches between what AI crawlers request and what their origin delivers, and a renamed UI surface ("Directives") that broadens scope beyond robots.txt alone — suggesting Cloudflare intends to expand agent-specific crawl controls further. The tie-in to [isitagentready.com](https://isitagentready.com) and the [accompanying blog post](https://blog.cloudflare.com/agent-readiness/) indicates Cloudflare is actively positioning itself as an infrastructure layer for the AI agent ecosystem.

