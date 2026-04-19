---
slug: cloudflare-launches-redirects-for-ai-training-to-enforce-content-freshness-for-m
title: "Cloudflare launches Redirects for AI Training to enforce content freshness for model training bots"
source: cloudflare-blog
pillar: ecosystem
detected_at: 2026-04-17T21:00:00+00:00
source_url: "https://blog.cloudflare.com/ai-redirects/"
change_kind: material
importance: 0.72
---

## News

[Cloudflare has announced Redirects for AI Training](https://blog.cloudflare.com/ai-redirects/), a new capability that automatically redirects verified AI training crawlers (including GPTBot, ClaudeBot, and Bytespider) to canonical URLs instead of serving deprecated pages. The feature reads existing `<link rel="canonical">` tags in HTML and issues HTTP 301 redirects when AI Crawlers request non-canonical pages, without affecting human traffic or search indexing. Cloudflare observed that advisory signals like `noindex` tags failed to prevent deprecated content consumption—AI training crawlers visited legacy documentation at the same rate as current content during a 30-day measurement period. Additionally, [Radar's AI Insights page now includes response status code analysis](https://radar.cloudflare.com/ai-insights#response-status) showing how different crawler categories receive 2xx, 3xx, 4xx, and 5xx responses at scale across web traffic.

## Why it matters

This addresses a structural problem in the AI training supply chain: crawlers ingest stale content at model-training time, and unlike search engines (which respect noindex directives), training pipelines treat advisory metadata as optional. Cloudflare's internal experiment on developers.cloudflare.com documented concrete harm—legacy Wrangler CLI docs were crawled 46,000 times by OpenAI and 3,600 times by Anthropic in March 2026, resulting in at least one major LLM assistant returning out-of-date syntax. By leveraging HTTP status codes (which crawlers cannot ignore) rather than HTML directives, the feature makes content governance enforceable. The addition of public response-status-code telemetry in Radar provides publishers with ecosystem-wide visibility into whether compliance is occurring and which crawlers honor redirects. This approach is incremental—it does not retroactively fix training data already ingested, does not cover unverified crawlers, and does not prevent AI Agents or human users from accessing deprecated pages—but it raises the cost of shipping stale training data going forward.

