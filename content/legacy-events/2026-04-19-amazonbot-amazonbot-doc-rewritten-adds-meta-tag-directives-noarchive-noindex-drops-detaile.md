---
slug: amazonbot-doc-rewritten-adds-meta-tag-directives-noarchive-noindex-drops-detaile
title: "Amazonbot doc rewritten: adds meta-tag directives (noarchive/noindex), drops detailed robots.txt field listing and 24-hour refresh SLA"
source: amazonbot
pillar: crawler
detected_at: 2026-04-19T18:36:49.010383+00:00
source_url: https://developer.amazon.com/amazonbot
change_kind: material
importance: 0.82
---

## What changed

The page was substantially rewritten: (1) branding shifted from "Amazonbot" to "Amazon crawlers" throughout; (2) a new paragraph explicitly states that Amazon crawlers honor link-level `rel=nofollow` and page-level robots meta tags — `noarchive` (explicitly glossed as "do not use the page for model training"), `noindex`, and `none`; (3) the previous detailed enumeration of supported robots.txt fields (user-agent, allow, disallow, sitemap) was removed, as was the explicit 24-hour robots.txt change-response SLA and the multi-host cross-blocking example.

## Implication

The addition of `noarchive` with an explicit "do not use the page for model training" gloss is the most significant change for site operators — it gives a documented, page-level opt-out mechanism for AI/LLM training by Amazon. The removal of the 24-hour SLA and the loss of the `sitemap` directive mention are minor regressions in transparency. Site operators who relied on the sitemap directive being honored should verify behavior independently.

## Raw diff

<details><summary>View diff</summary>

```diff
--- prev
+++ curr
@@ -1,14 +1,12 @@
-Amazonbot respects the robots.txt protocol, honors the user-agent and the allow/disallow directives, enabling webmasters to manage how crawlers access their site. Amazonbot attempts to read robots.txt files at the host level (for example example.com), so it looks for robots.txt at example.com/robots.txt. If a domain has multiple hosts, then we will honor robots rules exposed under each host. For example, in this scenario, if there is also a site.example.com host, it will look for robots.txt at example.com/robots.txt and also at site.example.com/robots.txt. If example.com/robots.txt blocks Amazonbot, but there are no robots.txt files on site.example.com or page.example.com, then Amazonbot cannot crawl example.com (blocked by its robots.txt), but will crawl site.example.com and page.example.com.
-In the event Amazonbot cannot fetch robots.txt due to IP or user agent blocking, parsing errors, network timeouts, or any other non-successful status codes (such as 3XX, 4XX or 5XX), Amazonbot will attempt to refetch robots.txt or use a cached copy from the last 30 days. If both these approaches fail, Amazonbot will behave as if robots.txt does not exist and will crawl the site. When accessible, Amazonbot will respond to changes in robots.txt files within 24 hours.
-Amazonbot honors the "Robots Exclusion protocol" defined at (
-https://www.rfc-editor.org/rfc/rfc9309.html
-) and recognizes the following fields. The field names are interpreted as case-insensitive. However the values for each of these fields are case-sensitive.
-user-agent
-: identifies which crawler the rules apply to.
-allow
-: a URL path that may be crawled.
-disallow
-: a URL path that may not be crawled.
-sitemap
-: the complete URL of a sitemap.
-Note: Amazonbot does not currently support the crawl-delay directive
+Amazon respects the
+Robots Exclusion Protocol
+, honoring the user-agent and the allow/disallow directives. Amazon will fetch host-level robots.txt files or use a cached copy from the last 30 days. When a file can’t be fetched, Amazon will behave as if it does not exist.
+Amazon attempts to read robots.txt files at the host level (for example
+example.com
+), so it looks for robots.txt at
+example.com/robots.txt
+. If a domain has multiple hosts, then we will honor robots rules exposed under each host. For example, if there is also a
+site.example.com
+host, it will look for robots.txt at
+site.example.com/robots.txt
+When Amazon crawlers access web pages they respect the link-level rel=nofollow directive, and page level robots meta tags of noarchive (do not use the page for model training), noindex (do not index the page) and none (do not index the page). Amazon crawlers do not support the crawl-delay directive.
```

</details>
