---
slug: amazon-expands-crawler-doc-to-three-distinct-bots-with-explicit-ai-training-disc
title: "Amazon expands crawler doc to three distinct bots with explicit AI training disclosures and new UA strings"
source: amazonbot
pillar: crawler
detected_at: 2026-04-19T21:35:19.602033+00:00
source_url: "https://developer.amazon.com/amazonbot"
change_kind: material
importance: 0.82
---

## What changed

The [Amazonbot developer page](https://developer.amazon.com/amazonbot) was substantially overhauled: it now documents **three separate crawlers** — `Amazonbot` (general; explicitly "may be used to train Amazon AI models"), `Amzn-SearchBot` (search/Alexa/Rufus; explicitly "does not crawl content for generative AI model training"), and `Amzn-User` (live user queries; also "does not crawl content for generative AI model training") — each with its own UA string and published IP address list. New UA strings are confirmed: `Amazonbot/0.1` (Chrome/119), `Amzn-SearchBot/0.1` (Chrome/119), and `Amzn-User/0.1` (Chrome/119). The page also adds recognition of the `noarchive` meta tag ("do not use the page for model training") alongside `noindex` and `none`, and drops the previous `sitemap` field documentation.

## Implication

Webmasters now have three independently targetable user-agents to allow/block via robots.txt, with clear semantics: blocking `Amzn-SearchBot` opts out of Alexa/Rufus search surfaces, while blocking `Amazonbot` is the relevant opt-out for AI model training. The explicit `noarchive` support for model-training exclusion is a new page-level opt-out mechanism. IP address lists for all three bots are now published at [Amazonbot IPs](https://developer.amazon.com/amazonbot/ip-addresses/), [SearchBot IPs](https://developer.amazon.com/amazonbot/searchbot-ip-addresses/), and [live IPs](https://developer.amazon.com/amazonbot/live-ip-addresses/).

## Raw diff

<details><summary>View diff</summary>

```diff
--- prev
+++ curr
@@ -1,14 +1,100 @@
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
+Alexa
+Amazon Appstore
+Ring
+AWS
+Documentation
+Console
+as
+Settings
+Sign out
+Notifications
+Alexa
+Amazon Appstore
+Ring
+AWS
+Documentation
+Support
+Contact Us
+My Cases
+Console
+Support
+Contact Us
+My Cases
+as
+Settings
+Sign out
+Webmasters can manage how their sites and content are used by Amazon with the following web crawlers. Amazon honors industry standard opt-out directives. Each setting is independent of the others, and may take ~24 hours for our systems to reflect changes.
+Amazonbot
+Amazonbot is used to improve our products and services. This helps us provide more accurate information to customers and may be used to train Amazon AI models.
+User Agent String:
+Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Amazonbot/0.1; +
+https://developer.amazon.com/support/amazonbot
+) Chrome/119.0.6045.214 Safari/537.36
+Published IP Addresses:
+https://developer.amazon.com/amazonbot/ip-addresses/
+Amzn-SearchBot
+Amzn-SearchBot is used to improve search experiences in Amazon products and services. By permitting Amzn-SearchBot access to your website, your content is eligible to appear in search experiences such as Alexa and Rufus. Amzn-SearchBot does not crawl content for generative AI model training.
+User Agent String:
+Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Amzn-SearchBot/0.1) Chrome/119.0.6045.214 Safari/537.36
+Published IP Addresses:
+https://developer.amazon.com/amazonbot/searchbot-ip-addresses/
+Amzn-User
+Amzn-User supports user actions, such as responding to Alexa queries that require up-to-date information. For example, when a customer asks a question, Amzn-User may fetch live information from the web to provide accurate answers on the user’s behalf.
+Amzn-User does not crawl content for generative AI model training.
+User Agent String:
+Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Amzn-User/0.1) Chrome/119.0.6045.214 Safari/537.36
+Published IP Addresses:
+https://developer.amazon.com/amazonbot/live-ip-addresses/
+Our Approach to Robots.txt
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
+Contact Us
+If you are a content owner or publisher and have questions, please contact us at
+amazonbot@amazon.com
+. Always include any relevant domain names in your message.
+Back to Top
+Follow us:
+Legal
+Terms and agreement
+Amazon Developers Service Portal terms of use
+Program Materials license agreement
+Amazon Appstore
+Developer portal
+Amazon Fire TV
+Fire tablets
+Alexa
+Developer portal
+Alexa Skills Kit
+Alexa Voice Service
+Alexa Fund
+Other services & APIs
+Login with Amazon
+Amazon Data Portability
+Amazon Merch on Demand
+Frustration-Free Setup
+Amazon Incentives API
+Amazon Music
+Just Walk Out technology by Amazon
+Blogs
+Appstore Developer blog
+Alexa Developer blog
+Alexa Science blog
+Support
+Amazon Developer support
+Appstore Developer Community
+Alexa Skills community
+FAQs
+© 2010-2026, Amazon.com, Inc. or its affiliates. All Rights Reserved.
+Terms
+Amazon Developer Blog
+Contact Us
```

</details>
