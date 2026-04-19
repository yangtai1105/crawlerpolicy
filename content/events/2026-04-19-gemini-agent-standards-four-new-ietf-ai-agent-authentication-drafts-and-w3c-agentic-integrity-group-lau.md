---
slug: four-new-ietf-ai-agent-authentication-drafts-and-w3c-agentic-integrity-group-lau
title: "Four new IETF AI agent authentication drafts and W3C agentic integrity group launched (March–April 2026)"
source: gemini-agent-standards
pillar: agent
detected_at: 2026-04-19T21:06:01.962496+00:00
source_url: ""
change_kind: material
importance: 0.75
---

## Implication

This burst of standards activity signals convergence on AI agent authentication as a critical infrastructure gap. The presence of at least two competing AIP drafts (Singla's decentralized-identity-focused variant and the policy-enforcement variant) alongside WIMSE/OAuth approaches suggests the standards community is exploring multiple solution architectures—a healthy sign but one that practitioners must monitor for eventual consolidation. The shift from the policy-file model (`agents.txt`) toward cryptographic identity protocols and W3C DID integration indicates the ecosystem is moving beyond simple declaration formats toward machine-verifiable, delegation-capable identity systems. The W3C community group's focus on audit trails reflects growing enterprise demand for accountability in agentic systems. For publishers and platform operators, this means bot authentication and agent identity verification will likely transition from voluntary (if any) to expected within 12–18 months; teams should begin evaluating which architectural model (centralized OAuth/WIMSE, decentralized DID-based, or hybrid) aligns with their infrastructure and risk posture.

## What changed

[Four new or updated IETF Internet-Drafts on AI agent authentication and authorization have appeared in the past 30 days](https://datatracker.ietf.org/doc/draft-klrc-aiagent-auth/01/): (1) an updated AI Agent Authentication and Authorization draft (`draft-klrc-aiagent-auth-01`, March 30, 2026) proposing WIMSE and OAuth 2.0 foundations; (2) an HTTP Message Signatures architecture draft for bot identity verification (`draft-meunier-web-bot-auth-architecture-05`, March 2, 2026); (3) a new Agent Identity Protocol (AIP) for decentralized identity using W3C DIDs and capability-based authorization (`draft-singla-agent-identity-protocol-00`, April 16, 2026); and (4) a separate Agent Identity Protocol draft for agentic authentication and policy enforcement (`draft-aip-agent-identity-protocol-00`, March 16, 2026). Concurrently, [W3C launched a new Agentic Integrity Verification Specification Community Group](https://www.w3.org/community/aivs/) on April 5, 2026, to standardize cryptographic proof formats for AI agent session auditing. Meanwhile, [the `agents.txt` Internet-Draft expired on April 10, 2026](https://www.reddit.com/r/AI_Agents/comments/1c0152j/the_agent_discovery_problem_11_ietf_drafts_15/) without renewal, signaling deprioritization of that particular policy-file approach within standards bodies.

