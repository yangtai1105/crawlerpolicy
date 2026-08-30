---
slug: anthropic-publishes-ip-range-list-for-crawler-verification-replacing-we-do-not-p
title: "Anthropic publishes IP range list for crawler verification, replacing \"we do not publish IP ranges\" statement"
source: claudebot
pillar: crawler
detected_at: 2026-04-19T21:35:19.602033+00:00
source_url: "https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler"
change_kind: material
importance: 0.72
---

## What changed

The previous text explicitly stated "we do not currently publish IP ranges, as we use service provider public IPs. This may change in the future." The [current page](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-the-web) replaces that sentence with: "If a crawler has a source IP address on this list, it indicates that the crawler is coming from Anthropic" — referencing a linked IP allowlist. A "Subscribe to updates" notification form and a new related article ("Claude in Chrome Permissions Guide") were also added.

## Implication

Site operators can now verify whether a request claiming to be ClaudeBot actually originates from Anthropic by checking the published IP list — a significant operational change for those using IP-based firewall rules or abuse reporting. The prior blanket disclaimer that IP blocking was unreliable due to unpublished ranges has been superseded; however, Anthropic still cautions that robots.txt remains the recommended opt-out mechanism.

## Raw diff

<details><summary>View diff</summary>

```diff
--- prev
+++ curr
@@ -1,7 +1,4 @@
 Skip to main content
-All Collections
-Privacy & Legal
-Does Anthropic crawl data from the web, and how can site owners block the crawler?
 Does Anthropic crawl data from the web, and how can site owners block the crawler?
 Updated over a week ago
 As per industry standard, Anthropic uses a variety of robots to gather data from the public web for model development, to search the web, and to retrieve web content at users’ direction. Anthropic uses different robots to enable website owner transparency and choice. Below is information on the three robots that Anthropic uses and how to set your site preferences to enable those you want to access your content and limit those you don’t.
@@ -38,18 +35,22 @@
 To block a Bot from your entire website, add this to the robots.txt file in your top-level directory. Please do this for every subdomain that you wish to opt out from. An example of this is:
 User-agent: ClaudeBot
 Disallow: /
-Opting out of being crawled by Anthropic Bots requires modifying the robots.txt file in the manner above. Alternate methods like blocking IP address(es) from which Anthropic Bots operates may not work correctly or persistently guarantee an opt-out, as doing so impedes our ability to read your robots.txt file. Additionally, we do not currently publish IP ranges, as we use service provider public IPs. This may change in the future.
+Opting out of being crawled by Anthropic Bots requires modifying the robots.txt file in the manner above. Alternate methods like blocking IP address(es) from which Anthropic Bots operates may not work correctly or persistently guarantee an opt-out, as doing so impedes our ability to read your robots.txt file. If a crawler has a source IP address on
+this list
+, it indicates that the crawler is coming from Anthropic.
 You can learn more about our data handling practices and commitments at our
 Help Center
 . If you have further questions, or believe that our Bots may be malfunctioning, please reach out to
-claudebot@anthropic.com
+[email protected]
 . Please reach out from an email that includes the domain you are contacting us about, as it is otherwise difficult to verify reports.
+You can be notified of substantial changes to this article by clicking here and completing the form:
+Subscribe to updates
 Related Articles
 Reporting, Blocking, and Removing Content from Claude
-How can I access the Anthropic API?
-How to Get Support
-Does Anthropic act as a Data Processor or Controller?
+How to get support
+Does Anthropic Act as a Data Processor or Controller?
 Reporting, Blocking, and Removing Content from Claude
+Claude in Chrome Permissions Guide
 Did this answer your question?
 😞
 😐
```

</details>
