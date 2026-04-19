---
slug: datadome-publishes-agentic-commerce-webinar-takeaways-with-bot-traffic-agent-ide
title: "DataDome Publishes Agentic Commerce Webinar Takeaways with Bot-Traffic & Agent-Identity Data"
source: datadome-blog
pillar: ecosystem
detected_at: 2026-04-07T21:46:38+00:00
source_url: https://datadome.co/agent-trust-management/future-of-search-agentic-commerce-webinar-takeaways/
change_kind: material
importance: 0.65
---

## What changed

A new full-length blog post appeared in the DataDome feed (no prior content existed). The post summarizes a DataDome-hosted webinar on "agentic commerce," presenting five substantive takeaways backed by cited statistics: 73% of surveyed consumers have used AI assistants for product discovery; AI bot traffic grew 5.4× in 2025; AI-driven crawling produces roughly one site visit per 198 crawls versus one per six for Google; 80% of AI agents do not self-identify correctly; and the post specifically names Grok/xAI as an example of a poorly-behaved agent that fans a single request into 12 simultaneous calls across different IPs and user-agent strings. DataDome frames this as justification for its "Agent Trust Management" product line, emphasizing intent-based rather than binary block/allow policies.

## Implication

For publisher and agent-infrastructure practitioners, the crawl-to-visit ratio stat (1:198 vs. 1:6 for Google) is a concrete figure to use when scoping infrastructure costs and analytics-distortion risk from AI indexers. The Grok/xAI example highlights a real compliance gap: major AI labs are deploying crawlers that violate basic identification norms, forcing site operators to choose between blanket blocking (risking AI-visibility loss) or open access (accepting analytics pollution and potential abuse). The 80% agent mis-identification figure—if taken at face value—signals that robots.txt and user-agent-based access controls are largely ineffective in the current agent ecosystem. Security and SEO teams should note that DataDome is positioning "agent trust management" as a distinct product category separate from classic bot management, which may accelerate vendor landscape fragmentation in this space.

