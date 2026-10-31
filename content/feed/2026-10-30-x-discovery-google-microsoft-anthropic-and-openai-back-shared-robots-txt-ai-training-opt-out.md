---
schema_version: 1
slug: x-discovery-google-microsoft-anthropic-and-openai-back-shared-robots-txt-ai-training-opt-out
title: "Google, Microsoft, Anthropic, and OpenAI Back Shared Robots.txt AI Training Opt-Out Standard"
source: x-discovery
source_tier: commentary
status: signal
primary_track: standards-protocols
tracks:
  - standards-protocols
  - access-controls
  - platform-ecosystem
actors:
  - "Google"
  - "Microsoft"
  - "Anthropic"
  - "OpenAI"
  - "IETF"
subject: crawler
event_date: 2026-10-30T18:09:58+00:00
published_at: 2026-10-30T18:09:58+00:00
detected_at: 2026-10-31T14:19:26.797580+00:00
source_urls:
  - "https://x.com/vanessafox/status/2116231149873963129"
  - "https://www.vanessafox.com/complete-reference-blocking-llm-crawlers/#new-shared-standard-usage-ai-training-in-robots-txt"
change_kind: material
importance: 0.86
confidence: high
evidence_ids:
  - "x-discovery--8f9612399ddd6128"
trend_signals:
  - robots_txt_modernization
  - unified_ai_opt_outs
  - training_vs_search_decoupling
players:
  - "google"
  - "microsoft"
  - "anthropic"
  - "openai"
  - "ietf"
protocols:
  - "robots-txt"
position_claims:
  - player: "google"
    protocol: "robots-txt"
    status: stated
  - player: "microsoft"
    protocol: "robots-txt"
    status: stated
  - player: "anthropic"
    protocol: "robots-txt"
    status: stated
  - player: "openai"
    protocol: "robots-txt"
    status: stated
saved_copies:
  - "https://github.com/yangtai1105/crawlerpolicy-archive/blob/main/articles/2026-10-30/x-discovery--8f9612399ddd6128-1.md"
archived_copies:
  - "https://web.archive.org/web/20261031103150/https://www.vanessafox.com/complete-reference-blocking-llm-crawlers/"
backfilled: false
---

## Summary

Google, Microsoft, Anthropic, and OpenAI announced commitments to support a shared robots.txt user-agent standard targeting early 2027 to govern content use in AI training. Proposed by Anthropic's Kevin Kelley at the IETF, the standard establishes 'User-agent: __usage_ai-training' as a single directive for opting out across all four providers. Support will replace fragmented vendor-specific tokens while introducing distinct downstream grounding and search behaviors across platforms.

## Key facts

- Anthropic's Kevin Kelley proposed a new shared user-agent standard in robots.txt at the IETF to allow sites to block content use for AI training.
- Google, Microsoft, Anthropic, and OpenAI announced on October 30, 2026, that they will honor directives to 'User-agent: __usage_ai-training', targeting early 2027 for implementation.
- Google will treat '__usage_ai-training' directives identically to Google-Extended, opting content out of Gemini and Vertex AI grounding without affecting AI Overviews or AI Mode.
- Beginning February 1, 2027, Microsoft will recognize the shared '__usage_ai-training' robots.txt group alongside page-level 'ai-training:disallow' and 'ai-grounding:disallow' tags, replacing its previous reliance on the noarchive tag after March 1, 2027.
- Cloudflare data indicates that less than 1% of sites it serves block search bots, while 17% employ mechanisms to block AI training.

## Insight

AI developers and search incumbents are moving away from proprietary crawler tokens toward unified usage-based syntax in robots.txt, separating permission for AI model training from general web search indexing.

## Implication

Site operators will no longer need to maintain sprawling lists of vendor-specific AI crawlers in robots.txt, but they must monitor provider-specific edge cases, such as Google mapping the directive to Google-Extended grounding restrictions.

## Why it matters

Publisher opt-outs have suffered from crawler fragmentation and lack of consensus across major labs; an IETF-backed unified training token establishes the first cross-industry baseline for robots.txt since the advent of generative AI.

## Evidence

- [Primary source](https://x.com/vanessafox/status/2116231149873963129)
- [Supporting source 2](https://www.vanessafox.com/complete-reference-blocking-llm-crawlers/#new-shared-standard-usage-ai-training-in-robots-txt)
- Evidence ID: `x-discovery--8f9612399ddd6128`
