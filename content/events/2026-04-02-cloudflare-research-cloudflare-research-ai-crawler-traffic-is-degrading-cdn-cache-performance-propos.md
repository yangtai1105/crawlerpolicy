---
slug: cloudflare-research-ai-crawler-traffic-is-degrading-cdn-cache-performance-propos
title: "Cloudflare Research: AI Crawler Traffic Is Degrading CDN Cache Performance, Proposes AI-Aware Cache Architecture"
source: cloudflare-research
pillar: agent
detected_at: 2026-04-02T21:00:00+00:00
source_url: https://blog.cloudflare.com/rethinking-cache-ai-humans/
change_kind: material
importance: 0.72
---

## What changed

Cloudflare published a new research blog post (co-authored with ETH Zurich, presented at ACM SoCC 2025) revealing that 32% of traffic across its network is automated, with AI crawlers now the dominant AI bot type at 80% of self-identified AI bot traffic. The post presents empirical data showing that AI crawlers—characterized by high unique URL ratios (70–100%), broad content diversity, and crawling inefficiency (high 404/redirect rates)—are materially degrading CDN cache hit rates by churning long-tail content and displacing human-traffic-optimized cache entries. Real-world impacts are documented across Wikipedia (50% multimedia bandwidth surge), SourceHut, Read the Docs, Fedora, and Diaspora. Cloudflare proposes two near-term mitigations: switching cache replacement algorithms from LRU to SIEVE or S3FIFO for mixed traffic, and experimenting with ML-based caching; and a longer-term separate cache tier architecture routing AI and human traffic to distinct CDN layers. The post also references existing Cloudflare products (AI Crawl Control, Pay Per Crawl, AI Index, Markdown for Agents) as partial solutions already deployed.

## Implication

Publishers and infrastructure operators should treat AI crawler traffic as a first-class infrastructure concern, not merely a content-rights issue—its scan-style access patterns actively degrade cache hit rates and increase origin egress costs for human users. The endorsement of SIEVE/S3FIFO over LRU as cache replacement algorithms for mixed workloads is an actionable near-term signal for CDN operators and self-hosters who tune cache behavior. The proposal for a dedicated AI cache tier represents a meaningful architectural direction that, if adopted by Cloudflare at scale, would change how publishers configure CDN behavior and how AI crawler operators negotiate access. Agent-infrastructure practitioners building RAG pipelines should be aware that their crawling patterns are being studied and may face tiered latency treatment or queue-based admission controls as CDN vendors adapt. The open internship call and academic publication suggest this is an active, funded research direction rather than a one-time blog post.

