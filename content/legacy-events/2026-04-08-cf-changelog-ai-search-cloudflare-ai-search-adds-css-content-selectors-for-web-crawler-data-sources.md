---
slug: cloudflare-ai-search-adds-css-content-selectors-for-web-crawler-data-sources
title: "Cloudflare AI Search adds CSS content selectors for web crawler data sources"
source: cf-changelog-ai-search
pillar: agent
detected_at: 2026-04-08T08:00:00+00:00
source_url: "https://developers.cloudflare.com/changelog/post/2026-04-09-ai-search-content-selectors/"
change_kind: material
importance: 0.65
---

## News

[Cloudflare AI Search now supports CSS content selectors](https://developers.cloudflare.com/ai-search/) for website data sources, allowing developers to define which parts of crawled pages are extracted and indexed. The feature lets users pair CSS selectors with URL glob patterns to isolate relevant content while filtering out navigation, sidebars, footers, and other boilerplate. Configuration is available via dashboard or [API](https://developers.cloudflare.com/ai-search/configuration/data-source/website/#content-selectors), with selectors evaluated in order (first match wins) and a maximum of 10 entries per instance.

## Why it matters

This capability materially improves the precision and efficiency of AI Search indexing by reducing noise from page structural elements that don't contain substantive content. Publishers and search-application builders can now optimize index quality without pre-processing crawled HTML, lowering operational overhead and improving retrieval relevance. The feature is particularly valuable for multi-page sites with consistent layout patterns (e.g., blogs, documentation) where boilerplate extraction was previously manual or absent. It advances Cloudflare's competitive positioning in the agent-infrastructure space by enabling finer-grained control over what content reaches language models.

