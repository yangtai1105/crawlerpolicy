---
schema_version: 1
slug: cloudflare-blog-cloudflare-releases-open-source-clef-decision-models-for-fast-agentic-routing-an
title: "Cloudflare releases open-source Clef decision models for fast agentic routing and bot classification"
source: cloudflare-blog
source_tier: specialist
status: reported
primary_track: agentic-web
tracks:
  - agentic-web
  - crawler-controls
  - measurement-economics
actors:
  - "Cloudflare"
  - "Typesafe AI"
event_date: 2026-10-01T15:34:02+00:00
published_at: 2026-10-01T15:34:02+00:00
detected_at: 2026-10-02T14:29:07.997977+00:00
source_urls:
  - "https://blog.cloudflare.com/clef-decision-models/"
change_kind: material
importance: 0.72
confidence: high
evidence_ids:
  - "cloudflare-blog--962aa10ad52cf1e3"
trend_signals:
  - deterministic decision models replacing generative LLMs for routing
  - edge-hosted bot and content classification
  - open-source lightweight agent decision primitives
backfilled: false
---

## Summary

Cloudflare launched Clef and Clef-flash, two open-source non-autoregressive decision models hosted on Workers AI and available under an Apache 2.0 license on Hugging Face. Built on frozen Qwen backbones with vision capabilities and a 64k context window, the models output structured probabilities rather than free-form text. Cloudflare is using the architecture internally for threat intelligence and bot detection while rolling out reinforcement learning fine-tuning services for enterprise agent workflows.

## Insight

By replacing token-by-token autoregressive generation with parallel schema scoring over base model representations, decision models dramatically compress inference latency and eliminate non-deterministic parsing issues in automated routing and security triage pipelines.

## Implication

Autonomous web agents and edge security filters can execute programmatic decisions—such as tool selection, request routing, or bot classification—at edge latency without routing traffic through heavyweight generative LLMs.

## Why it matters

As web scraping, bot defense, and agentic interactions accelerate, deploying sub-100ms structured classifier models directly to edge infrastructure shifts how platforms detect automated traffic and how autonomous agents navigate the web.

## Evidence

- [Primary source](https://blog.cloudflare.com/clef-decision-models/)
- Evidence ID: `cloudflare-blog--962aa10ad52cf1e3`
