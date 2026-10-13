---
schema_version: 1
slug: datadome-blog-datadome-benchmark-finds-65-3-of-21-491-tested-sites-fail-to-stop-automated-bots
title: "DataDome Benchmark Finds 65.3% of 21,491 Tested Sites Fail to Stop Automated Bots and Spoofed AI Agents"
source: datadome-blog
source_tier: specialist
status: reported
primary_track: measurement-economics
tracks:
  - measurement-economics
  - access-controls
  - platform-ecosystem
actors:
  - "DataDome"
  - "GPTBot"
  - "ClaudeBot"
subject: both
event_date: 2026-10-13T14:58:05+00:00
published_at: 2026-10-13T14:58:05+00:00
detected_at: 2026-10-13T15:36:53.900599+00:00
source_urls:
  - "https://datadome.co/threat-research/state-of-bot-and-agent-security-report-industry-protection-rates/"
change_kind: material
importance: 0.76
confidence: high
evidence_ids:
  - "datadome-blog--42fa450a86dba89a"
trend_signals:
  - agent-identity-spoofing
  - decline-of-user-agent-trust
  - intent-based-filtering
players:
  - "datadome"
backfilled: false
---

## Summary

In its 2026 bot and agent security report, DataDome tested 21,491 websites across 15 industries against 10 bot types, finding that 65.3% of sites failed to block any test bots and only 2.4% achieved full protection. Over 70% of audited websites permitted access to requests simply asserting user-agent strings for GPTBot or ClaudeBot without verifying authenticity. The study also revealed that organizational size and traffic tiers do not correlate with better defenses, with top 1,000 traffic sites showing a 64.4% failure rate.

## Insight

Relying on declarative user-agent matching creates a dual vulnerability: honest bots face crude blocklists while malicious scrapers and spoofed agents trivially bypass controls simply by asserting trusted identity tokens.

## Implication

Operators relying solely on robots.txt and naive user-agent filtering will remain exposed to spoofed AI traffic, forcing an industry transition toward network fingerprinting, reverse DNS validation, and behavioral intent analysis across web endpoints and APIs.

## Why it matters

As low-cost bot-as-a-service frameworks proliferate, the collapse of identity-based perimeter defenses highlights how unverified user-agent governance fails to protect proprietary content and web infrastructure.

## Evidence

- [Primary source](https://datadome.co/threat-research/state-of-bot-and-agent-security-report-industry-protection-rates/)
- Evidence ID: `datadome-blog--42fa450a86dba89a`
