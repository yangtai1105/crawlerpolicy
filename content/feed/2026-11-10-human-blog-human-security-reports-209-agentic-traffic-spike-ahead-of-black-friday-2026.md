---
schema_version: 1
slug: human-blog-human-security-reports-209-agentic-traffic-spike-ahead-of-black-friday-2026
title: "HUMAN Security Reports 209% Agentic Traffic Spike Ahead of Black Friday 2026"
source: human-blog
source_tier: specialist
status: reported
primary_track: measurement-economics
tracks:
  - measurement-economics
  - access-controls
  - identity-authorization
  - platform-ecosystem
actors:
  - "HUMAN Security"
subject: both
event_date: 2026-11-10T00:00:00+00:00
published_at: 2026-11-10T00:00:00+00:00
detected_at: 2026-11-13T15:56:00.186978+00:00
source_urls:
  - "https://www.humansecurity.com/learn/blog/black-friday-2026-bot-traffic-predictions/"
change_kind: material
importance: 0.72
confidence: high
evidence_ids:
  - "human-blog--ddb55490259b2a0a"
trend_signals:
  - ai-agent-e-commerce-surge
  - agentic-traffic-differentiation
  - pre-holiday-account-takeover-spikes
players:
  - "human-security"
backfilled: false
---

## Summary

HUMAN Security's Satori Threat Intelligence team projected record holiday AI shopping traffic after measuring a 209.7% month-over-month surge in agentic web requests in September 2026. Telemetry from the 2025 holiday period revealed that while total agentic volume rose 23.8% during Black Friday week, weekly block rates fell to 4.7%, indicating that most agent traffic reflected legitimate consumer shopping rather than malicious activity. The report cautions that defensive systems must simultaneously manage acute account takeover spikes, which captured up to 23% of all login attempts immediately before Black Friday 2025.

## Key facts

- HUMAN Defense Platform telemetry recorded a 209.7% month-over-month jump in agentic traffic in September 2026, driven by broader adoption, new agent deployments, and improved detection.
- During Black Friday week in 2025, agentic traffic grew 23.8% over the previous week, while the weekly block rate dropped to 4.7% (down from 5.3%), demonstrating that the vast majority of agent requests were legitimate consumer activity.
- On November 27, 2025, the day before Black Friday, blocked account takeover (ATO) attempts spiked to 23% of all login attempts, roughly five times the 4.2% daily average of the preceding weeks.
- Blocked ATO attempts reached 18.6% of all login attempts on November 29, 2025, representing 6.6 times the 2.6% rate recorded in the weeks following the holiday period.
- HUMAN identified newly launched AI shopping agents—including Muse, Grok Agent, and Claude Duet—as factors expanding automated baseline traffic across retail endpoints.
- Authors Aviad Kaiserman and Lindsay Kaye emphasized that 'deciding what to allow or block requires knowing who (or what) is on your site and the context behind each interaction.'

## Insight

Automated traffic filtering is evolving from a binary human-versus-bot model into a three-way triage among human users, hostile bots, and authorized consumer AI agents. Because legitimate shopping agents spike in tandem with peak retail demand and carry low block rates, indiscriminate bot mitigation risks dropping high-intent, revenue-generating customer transactions.

## Implication

Retailers and security platforms must adjust bot management policies to authenticate and accommodate emerging AI shopping agents without lowering defenses against AI-scaled credential stuffing and lookalike phishing sites.

## Why it matters

As delegated AI agents handle larger shares of product discovery and purchasing, e-commerce sites that rely on crude automation blocks risk rejecting paying customers during their most critical revenue window.

## Evidence

- [Primary source](https://www.humansecurity.com/learn/blog/black-friday-2026-bot-traffic-predictions/)
- Evidence ID: `human-blog--ddb55490259b2a0a`
