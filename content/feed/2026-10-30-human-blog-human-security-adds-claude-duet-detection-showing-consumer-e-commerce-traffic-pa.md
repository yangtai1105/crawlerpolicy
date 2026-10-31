---
schema_version: 1
slug: human-blog-human-security-adds-claude-duet-detection-showing-consumer-e-commerce-traffic-pa
title: "HUMAN Security Adds Claude Duet Detection, Showing Consumer E-Commerce Traffic Patterns"
source: human-blog
source_tier: specialist
status: reported
primary_track: measurement-economics
tracks:
  - measurement-economics
  - access-controls
  - platform-ecosystem
actors:
  - "HUMAN Security"
  - "Anthropic"
  - "Meta"
  - "OpenAI"
  - "Google"
subject: agent
event_date: 2026-10-30T00:00:00+00:00
published_at: 2026-10-30T00:00:00+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_urls:
  - "https://www.humansecurity.com/learn/blog/human-sightline-detects-claude-duet/"
change_kind: material
importance: 0.72
confidence: high
evidence_ids:
  - "human-blog--0b41c1a9953f1b21"
trend_signals:
  - personal agent detection tooling
  - agentic browsing vs transaction separation
  - consumer retail browsing via personal agents
players:
  - "human-security"
  - "anthropic"
  - "meta"
  - "openai"
  - "google"
backfilled: false
---

## Summary

HUMAN Security updated its AgenticTrust detection to identify Anthropic's Claude Duet personal agent across its network starting October 28, 2026, following Duet's October 21 research preview launch. Network telemetry shows that 70.7% of early Duet traffic targeted retail and e-commerce sites and 21.2% targeted real estate, despite Anthropic positioning the tool for professional and small-business workflows. Fewer than 1% of Duet requests touched checkout or login endpoints, reflecting an architecture that seeks user authorization prior to completing transactions.

## Key facts

- Anthropic launched Claude Duet, powered by Claude Opus 5.5, in research preview on October 21, 2026, for Claude Pro and Claude Max tiers.
- HUMAN Security began detecting Claude Duet and providing customer visibility via AgenticTrust on October 28, 2026.
- On October 28, 2026, Meta's Muse generated approximately 3,350 times more traffic across HUMAN's network than Claude Duet.
- Retail and e-commerce properties accounted for 70.7% of early Claude Duet traffic, while real estate properties received 21.2%.
- Fewer than 1% of Claude Duet requests touched login or checkout routes, which authors Julian Norton and Lindsay Bender describe as 'consistent with an agent that asks before it pays.'
- Meta's Muse reached #1 on the App Store within 10 days of its September launch and generated 40% of all agentic traffic across HUMAN's network in September 2026.
- Anthropic publicly positions Claude Duet for 'professionals and small-business owners' and notes personal errands like booking tickets are 'not yet a strength.'

## Insight

Early telemetry on delegative personal agents reveals a gap between vendor positioning and real-world user deployment, with professional-oriented agents immediately gravitating toward consumer shopping discovery while avoiding sensitive transaction endpoints.

## Implication

E-commerce and real estate platforms face rising automated browsing that mimics consumer discovery without completing checkout, requiring bot mitigation teams to distinguish delegative agent browsing from malicious scraping without disrupting high-intent buyers.

## Why it matters

Personal agents are rapidly shifting machine access from background indexing to user-delegated discovery on retail and listing pages, forcing site operators to adopt agent-specific visibility before automated shopping volumes spike.

## Evidence

- [Primary source](https://www.humansecurity.com/learn/blog/human-sightline-detects-claude-duet/)
- Evidence ID: `human-blog--0b41c1a9953f1b21`
