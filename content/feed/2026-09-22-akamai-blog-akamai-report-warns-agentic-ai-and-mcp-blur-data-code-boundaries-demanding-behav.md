---
schema_version: 1
slug: akamai-blog-akamai-report-warns-agentic-ai-and-mcp-blur-data-code-boundaries-demanding-behav
title: "Akamai Report Warns Agentic AI and MCP Blur Data-Code Boundaries, Demanding Behavioral Runtime Governance"
source: akamai-blog
source_tier: specialist
status: reported
primary_track: access-controls
tracks:
  - access-controls
  - identity-authorization
  - standards-protocols
  - measurement-economics
actors:
  - "Akamai"
subject: agent
event_date: 2026-09-22T12:00:00+00:00
published_at: 2026-09-22T12:00:00+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_urls:
  - "https://www.akamai.com/blog/security/2026/sep/beyond-identity-governing-the-agentic-enterprise"
change_kind: material
importance: 0.68
confidence: high
evidence_ids:
  - "akamai-blog--d8d58ea63b884cb8"
trend_signals:
  - agentic-threat-governance
  - mcp-attack-surface-scrutiny
  - nonhuman-identity-inspection
players:
  - "akamai"
protocols:
  - "mcp"
backfilled: false
---

## Summary

Akamai released research accompanying its State of the Internet Security report, arguing that the shift toward autonomous AI agents requires moving beyond traditional Identity and Access Management to real-time behavioral governance across APIs. The study highlights security vulnerabilities introduced by the Model Context Protocol and uncontrolled enterprise browser extensions. Akamai found that over 40% of enterprise users have installed AI browser extensions, with 64% of those users experiencing permission changes on at least one extension within 12 months.

## Key facts

- More than 40% of enterprise users have installed AI browser extensions or tools, and 64% of those users had at least one AI extension change permissions within a year.
- Twenty-five percent of installed extensions altered their permissions within a 12-month window, and AI browser extensions are 60% more likely to have known vulnerabilities compared to other tools.
- Greater than 6% of AI chatbot conversations on enterprise devices contain sensitive enterprise data or information.
- Frontier AI capabilities compress the window required to discover system vulnerabilities from weeks down to hours.
- Akamai warned that the Model Context Protocol (MCP) provides the 'hands' for agentic AI to execute actions across APIs while blurring data and code boundaries, exposing systems to prompt injection and cross-server attacks.
- Akamai Director of Security Research Kimberly Gomez stated: 'It's no longer enough to verify who, or what, has access. Organizations must also govern what autonomous systems are allowed to do once they are inside.'

## Insight

Static identity verification is rendered insufficient when autonomous agents act through standard execution protocols like MCP, effectively collapsing the boundary between natural-language data and executable code at the enterprise edge.

## Implication

Security teams and CISOs will increasingly need to deploy edge-native API inspection, behavioral relational analysis, and AI Software Bills of Materials to constrain what autonomous nonhuman identities can execute post-authentication.

## Why it matters

As enterprise workflows adopt autonomous tooling and protocols like MCP, malicious prompt injections and hijacked agent logic pose direct operational risks that static perimeter and access controls cannot mitigate.

## Evidence

- [Primary source](https://www.akamai.com/blog/security/2026/sep/beyond-identity-governing-the-agentic-enterprise)
- Evidence ID: `akamai-blog--d8d58ea63b884cb8`
