---
schema_version: 1
slug: datadome-blog-datadome-profiles-agentic-commerce-footprints-for-meta-muse-openai-dots-and-inst
title: "DataDome Profiles Agentic Commerce Footprints for Meta Muse, OpenAI Dots, and Instinct"
source: datadome-blog
source_tier: specialist
status: reported
primary_track: access-controls
tracks:
  - access-controls
  - identity-authorization
  - platform-ecosystem
  - measurement-economics
actors:
  - "DataDome"
  - "Meta"
  - "OpenAI"
  - "Instinct"
  - "Cloudflare"
  - "Fastly"
subject: agent
event_date: 2026-10-27T14:38:58+00:00
published_at: 2026-10-27T14:38:58+00:00
detected_at: 2026-10-28T14:52:45.308044+00:00
source_urls:
  - "https://datadome.co/threat-research/instinct-muse-dots-are-already-shopping-online/"
change_kind: material
importance: 0.72
confidence: high
evidence_ids:
  - "datadome-blog--9f49770024268e27"
trend_signals:
  - agentic-commerce
  - residential-proxy-agent-routing
  - client-side-agent-fingerprinting
  - intent-based-access-control
players:
  - "datadome"
  - "meta"
  - "openai"
  - "cloudflare"
  - "fastly"
protocols:
  - "web-bot-auth"
backfilled: false
---

## Summary

Bot mitigation vendor DataDome published research analyzing how autonomous shopping agents Instinct, OpenAI's Dots, and Meta's Muse interact with e-commerce checkout funnels. All three agents successfully completed end-to-end purchases on a demo site, demonstrating execution methods spanning cloud browser sandboxes to residential proxy rotation. DataDome announced client-side detection and intent-based controls for these agents after logging tens of millions of shopping requests across its customer base in October 2026.

## Key facts

- DataDome tested three shopping agents—Instinct (via WhatsApp), Dots (OpenAI), and Muse (Meta)—each completing a purchase of a $149.99 mechanical keyboard ($161.99 after tax and shipping) on a demo e-commerce store.
- Meta's Muse does not declare a custom user-agent, published IP range, or signed requests, but exhibits near-identical client-side sandbox signals across sessions that mimic standard desktop Chrome on Linux.
- OpenAI's Dots runs Chrome on cloud virtual machines allowing user takeover, while Instinct relies on residential proxies and can switch IP addresses and hardware profiles within the same session.
- From October 17 to October 23, 2026, DataDome observed 22.1 million requests from Muse (59.2% Cloudflare, 21.3% Fastly), 1.4 million from Dots (99.9% Cloudflare), and 2.6 million from Instinct (tracked starting October 19).
- Sensitive endpoints (forms, login, cart, and payment) accounted for 12.3% of Dots requests, 10.7% of Muse requests, and 9.2% of Instinct requests, with general browsing representing the remaining 88% to 91%.
- DataDome reported tracking approximately 25 billion AI agent requests in Q3 2026, up 41.5% from Q2, with agentic browser traffic growing 4.7x in September 2026.

## Insight

Consumer shopping agents present a distinct architectural challenge from indexing crawlers: they navigate sensitive transactional endpoints (logins, carts, payment gateways) without declaring identity headers, using execution models ranging from identifiable cloud VMs to residential proxies that rotate IPs and hardware fingerprints mid-session.

## Implication

Retailers relying on binary bot blocking risk terminating legitimate customer-directed sales, forcing anti-bot vendors and web platforms toward behavioral intent analysis and granular per-action policies rather than simple IP or user-agent allowlists.

## Why it matters

As major AI platforms deploy delegated agents to browse and buy on behalf of users, the line between harmful automated scraping and authorized customer transactions is blurring at the checkout page.

## Evidence

- [Primary source](https://datadome.co/threat-research/instinct-muse-dots-are-already-shopping-online/)
- Evidence ID: `datadome-blog--9f49770024268e27`
