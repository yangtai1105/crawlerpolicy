---
slug: agent-standards-digest-shifted-to-operational-focus-new-draft-on-anonymous-bot-a
title: "Agent standards digest shifted to operational focus; new draft on anonymous bot auth; agents.txt rebranded as agent-manifest.txt"
source: gemini-agent-standards
pillar: agent
detected_at: 2026-04-19T21:11:53.844421+00:00
source_url: ""
change_kind: material
importance: 0.65
---

## Implication

This update reflects a shift from cataloging all concurrent initiatives (a snapshot of fragmentation) to tracking active momentum and new proposals—practical for practitioners choosing between emerging standards. The emergence of [Anonymous Bot Authentication](https://datatracker.ietf.org/doc/draft-rescorla-anonymous-webbotauth/) indicates the standards community is now addressing a distinct use case: website operators who wish to rate-limit or gate agents without collecting persistent identity data, potentially lowering friction for benign automated traffic. The [agent-manifest.txt rebranding](https://dev.to/jasper/agent-manifesttxt-a-proposed-web-standard-for-ai-agents-formerly-agentstxt-2026-403h) is a material clarification—it moves away from the robots.txt analogy (a permission model) toward a capability declaration model, addressing concerns that agents.txt conflated discovery with policy. However, the removal of the HTTP Message Signatures and policy-enforcement AIP entries from the digest may signal either deprioritization or that they've been absorbed into the WIMSE/OAuth-centric draft-klrc framework. The drop of llms.txt commentary suggests community consensus that it remains informal, not a standards-track item. Overall, this reflects the third month of sustained IETF/W3C convergence (per prior items from March–April 2026), but with now clearer separation between identity, rate-limiting, and capability-declaration concerns.

## What changed

[The digest scope was narrowed](https://dev.to/kanywst/ai-agent-authentication-authorization-deep-dive-reading-draft-klrc-aiagent-auth-00-5d1) from tracking "most important distinct items" to focusing on "new or updated" activity over the last 30 days. The [draft-meunier-web-bot-auth-architecture](https://datatracker.ietf.org/doc/draft-meunier-web-bot-auth-architecture/05/) and [draft-aip-agent-identity-protocol](https://datatracker.ietf.org/doc/draft-aip-agent-identity-protocol/) entries were removed entirely. A new entry for [Anonymous Bot Authentication (ABA) draft-rescorla-anonymous-webbotauth-00](https://datatracker.ietf.org/doc/draft-rescorla-anonymous-webbotauth/) (April 8, 2026) was added, introducing a privacy-preserving rate-limiting mechanism. The [agents.txt proposal was renamed to agent-manifest.txt](https://dev.to/jasper/agent-manifesttxt-a-proposed-web-standard-for-ai-agents-formerly-agentstxt-2026-403h) in March 2026 to signal a capability-manifest function rather than a discovery file. The statement that "no new or updated standards-body activity on llms.txt" was found was removed.

