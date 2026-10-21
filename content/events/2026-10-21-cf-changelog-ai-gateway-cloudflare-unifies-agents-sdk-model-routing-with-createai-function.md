---
schema_version: 2
slug: cloudflare-unifies-agents-sdk-model-routing-with-createai-function
title: "Cloudflare Unifies Agents SDK Model Routing with createAI Function"
source: cf-changelog-ai-gateway
source_tier: primary
primary_track: platform-ecosystem
tracks:
  - platform-ecosystem
actors:
  - "Cloudflare"
event_date: 2026-10-21T00:00:00+00:00
published_at: 2026-10-21T00:00:00+00:00
detected_at: 2026-10-21T13:28:44.196458+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-10-21-createai/"
change_kind: material
importance: 0.45
confidence: high
evidence_ids:
  - "cf-changelog-ai-gateway--8f0caccb1b2dbb46"
---

## Development

Cloudflare introduced the createAI function in its Agents SDK, consolidating workers-ai-provider and ai-gateway-provider into a unified interface for AI SDK and Pi AI. The update allows developers to query Workers AI models, AI Gateway catalog models, dynamic routes, and third-party vendor models through a single invocation pattern. Cloudflare announced that the legacy provider libraries are feature-frozen and deprecated.

## Key facts

- Cloudflare released the [createAI](https://developers.cloudflare.com/agents/models/) function in its Agents SDK supporting the [AI SDK](https://developers.cloudflare.com/agents/models/ai-sdk/) and [Pi AI](https://developers.cloudflare.com/agents/models/pi-ai/).
- The createAI function unifies workers-ai-provider and ai-gateway-provider, both of which are now feature-frozen and deprecated.
- The function supports Workers AI models (@cf/ IDs), the [AI Gateway catalog](https://developers.cloudflare.com/ai/models/), [dynamic routes](https://developers.cloudflare.com/ai-gateway/features/dynamic-routing/) (dynamic/<route>), and vendor models routed to AI Gateway's [provider-native endpoint](https://developers.cloudflare.com/ai-gateway/usage/providers/).
- Supported operational features include model fallbacks, mid-answer stream resumption via bindings, caching, logging, metadata, retries, byokAlias, zdr, and vendorKey.
- Developers can authenticate via the env.AI Worker binding or an account ID and API token for external access.
- AI Search capabilities previously invoked via createAISearch in workers-ai-provider were relocated to createAISearchNamespace in [ai-search-provider](https://developers.cloudflare.com/ai-search/agent-sdks/ai-sdk/).

## Why it matters

Autonomous agent reliability depends heavily on robust fallback routing and observability. Unifying agent model access with gateway middleware simplifies the operational overhead of managing multi-model failovers and client attribution across distributed infrastructure.

## Trend impact

- agent-middleware-consolidation
- ai-gateway-routing

## Evidence

- [Primary source](https://developers.cloudflare.com/changelog/post/2026-10-21-createai/)
- Evidence ID: `cf-changelog-ai-gateway--8f0caccb1b2dbb46`

