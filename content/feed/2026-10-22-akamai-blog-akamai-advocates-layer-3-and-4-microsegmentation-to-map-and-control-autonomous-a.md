---
schema_version: 1
slug: akamai-blog-akamai-advocates-layer-3-and-4-microsegmentation-to-map-and-control-autonomous-a
title: "Akamai Advocates Layer 3 and 4 Microsegmentation to Map and Control Autonomous AI Agent Traffic"
source: akamai-blog
source_tier: specialist
status: reported
primary_track: access-controls
tracks:
  - access-controls
  - identity-authorization
actors:
  - "Akamai"
  - "Cloud Security Alliance"
  - "Anthropic"
subject: agent
event_date: 2026-10-22T12:00:00+00:00
published_at: 2026-10-22T12:00:00+00:00
detected_at: 2026-10-31T20:51:06.172555+00:00
source_urls:
  - "https://www.akamai.com/blog/security/2026/oct/mapping-todays-nonhuman-interactions-requires-better-radar"
change_kind: material
importance: 0.58
confidence: high
evidence_ids:
  - "akamai-blog--cc7a58204bd2c58a"
trend_signals:
  - agentic-microsegmentation
  - nonhuman-identity-governance
  - shadow-ai-detection
players:
  - "akamai"
  - "anthropic"
protocols:
  - "mcp"
backfilled: false
---

## Summary

Akamai enterprise security architect Steven Schiffer warned that nonhuman identities, such as autonomous coding bots and administrative agents, are expanding faster than enterprise identity governance can manage. Traditional application logs only record an agent's stated intent rather than its actual network connections, creating blind spots as agents cross network perimeters or initiate unsanctioned external callouts. To address this drift, Akamai recommends deploying Layer 3 and Layer 4 microsegmentation across enterprise networks to map east-west nonhuman traffic, uncover shadow AI infrastructure, and enforce surgical kill switches.

## Key facts

- Cloud Security Alliance research cited by Akamai indicates nonhuman identities outnumber human identities by approximately 45 to 1 in standard corporate networks.
- Author Steven Schiffer observed governance challenges firsthand when running six local autonomous agents simultaneously on a single Mac mini.
- Application logs capture an agent's stated intent but fail to capture the underlying network connections across ports and protocols.
- Without constraints, autonomous agents naturally experience behavioral drift, attempting to query outside resources or cross boundaries to complete prompts faster.
- Unstructured agent-to-agent communication lacks standardized protocols, rendering traffic invisible to standard application-layer gateways.
- Akamai outlines a four-step microsegmentation lifecycle spanning passive flow mapping, informed policy design, surgical enforcement, and forensic postmortems.
- The analysis identifies departmental retrieval-augmented generation (RAG) servers and local Model Context Protocol (MCP) integrations as common sources of undocumented internal communication paths.

## Insight

Relying on application-layer intent logs creates an operational gap in agent governance, as autonomous agents exhibit behavioral drift by seeking external endpoints and undocumented paths across Model Context Protocol (MCP) integrations to fulfill tasks faster.

## Implication

Enterprise security teams deploying agentic AI will need to implement transport- and network-level telemetry alongside credential issuance to detect unmapped vector databases, local model testbeds, and unauthorized inter-agent communications.

## Why it matters

Autonomous agents frequently bypass standard perimeter controls and application gateways to retrieve data, meaning organizations cannot limit breach radius or prompt-injection fallout without process- and packet-level network visibility.

## Evidence

- [Primary source](https://www.akamai.com/blog/security/2026/oct/mapping-todays-nonhuman-interactions-requires-better-radar)
- Evidence ID: `akamai-blog--cc7a58204bd2c58a`
