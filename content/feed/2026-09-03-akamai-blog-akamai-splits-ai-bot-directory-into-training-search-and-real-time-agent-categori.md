---
schema_version: 1
slug: akamai-blog-akamai-splits-ai-bot-directory-into-training-search-and-real-time-agent-categori
title: "Akamai Splits AI Bot Directory Into Training, Search, and Real-Time Agent Categories"
source: akamai-blog
source_tier: specialist
status: reported
primary_track: access-controls
tracks:
  - access-controls
  - platform-ecosystem
  - identity-authorization
actors:
  - "Akamai"
  - "OpenAI"
  - "Anthropic"
  - "Meta"
  - "Perplexity"
  - "Google"
subject: both
event_date: 2026-09-03T06:00:00+00:00
published_at: 2026-09-03T06:00:00+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_urls:
  - "https://www.akamai.com/blog/security/2026/sep/introducing-more-granular-controls-ai-bot-traffic"
change_kind: material
importance: 0.78
confidence: high
evidence_ids:
  - "akamai-blog--6a6bbb03a50581df"
trend_signals:
  - granular edge access control for AI
  - decoupling AI training from search indexing
  - preparation for agentic commerce
players:
  - "akamai"
  - "openai"
  - "anthropic"
  - "meta"
  - "perplexity"
  - "google"
backfilled: false
---

## Summary

Akamai has updated its Bot Directory to split its single 'AI Bots' category into three distinct classifications: AI training crawlers, AI search crawlers, and AI fetchers and agents. The structural update enables site operators using Akamai Bot & Agent Control to differentiate policy enforcement between bulk model training, AI search indexing, and real-time user-driven agent tasks. The classification categorizes named entities including GPTBot, ClaudeBot, OAI-SearchBot, PerplexityBot, ChatGPT-User, and GoogleAgent-Mariner.

## Key facts

- Akamai updated the Akamai Bot Directory by dividing 1 legacy 'AI Bots' category into 3 distinct categories: AI training crawlers, AI search crawlers, and AI fetchers and agents.
- AI training crawlers harvest bulk data for model training and fine-tuning, with Akamai citing GPTBot (OpenAI), ClaudeBot (Anthropic), and Meta-ExternalAgent (Meta) as examples.
- AI search crawlers index content for generative search discovery and citations, exemplified by OAI-SearchBot (OpenAI), Claude-SearchBot (Anthropic), and PerplexityBot (Perplexity).
- AI fetchers and agents execute real-time user-driven prompts or automated multi-step workflows, including ChatGPT-User, Claude-User, Perplexity-User, ChatGPT Agent, and GoogleAgent-Mariner.
- Akamai author Emily Lyons stated that the split enables websites to resolve contradictory goals: 'You do not want an AI company crawling that content to train its models. But you do want an AI search engine to index it so your brand will appear when someone searches for information via an AI platform.'
- Granular policy enforcement is managed via Akamai Bot & Agent Control alongside search optimization visibility tracking through Akamai AI Brand Presence.

## Insight

Edge security providers are formalizing the separation between unreciprocated content harvesting for model training and real-time proxy traffic acting on behalf of interactive users, shifting access control from binary IP-or-user-agent blocking to operational intent classification.

## Implication

Web publishers can selectively block bulk training scraping while preserving discoverability in generative search engines and enabling agentic commerce transactions, forcing AI vendors to maintain strict separation across operational user-agent identities.

## Why it matters

Edge network vendors like Akamai determine default access policies for a major portion of enterprise web traffic; unbundling AI bots into functional classes allows websites to protect training rights without suffering complete disappearance from generative search platforms.

## Evidence

- [Primary source](https://www.akamai.com/blog/security/2026/sep/introducing-more-granular-controls-ai-bot-traffic)
- Evidence ID: `akamai-blog--6a6bbb03a50581df`
