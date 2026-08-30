---
slug: ccbot-ua-string-clarified-with-full-url-new-how-does-ccbot-fetch-a-web-page-sect
title: "CCBot UA string clarified with full URL, new \"How does CCBot fetch a web page?\" section added, ZStandard compression support added"
source: ccbot
pillar: crawler
detected_at: 2026-04-19T21:35:19.602033+00:00
source_url: "https://commoncrawl.org/faq"
change_kind: material
importance: 0.72
---

## What changed

Three substantive changes on the [Common Crawl FAQ](https://commoncrawl.org/faq): (1) The current UA string is now explicitly stated as `CCBot/2.0 (https://commoncrawl.org/faq/)` — the previous version only said the bot identifies as `CCBot/2.0` with contact info "sent along" but did not spell out the full string. (2) A new FAQ entry "How does CCBot fetch a web page?" documents that CCBot uses HTTP GET, supports HTTP/1.1 and HTTP/2 (HTTPS only for H2), IPv4 and IPv6, follows up to 4 redirects (5 for robots.txt per RFC 9309), does not execute JavaScript, and does not use cookies. (3) ZStandard (`zstd`) is added as a supported compression encoding alongside `gzip` and `Brotli`.

## Implication

Publishers and bot-detection operators should update their UA-matching rules: the canonical CCBot/2.0 string now includes a trailing URL `(https://commoncrawl.org/faq/)`, which differs from bare `CCBot/2.0`. The new fetch-behavior section is the first official documentation that CCBot does not run JavaScript and does not send cookies — relevant for server-side detection and for understanding what content CCBot will actually index. ZStandard support means servers may now negotiate `zstd` encoding with the crawler.

## Raw diff

<details><summary>View diff</summary>

```diff
--- prev
+++ curr
@@ -28,17 +28,34 @@
 to process and extract crawl candidates from our crawl database.
 This candidate list is sorted by host (domain name) and then distributed to a set of crawler servers.
 How does the Common Crawl CCBot identify itself?
+CCBot identifies itself via its
+UserAgent
+string as:
+‍
+CCBot/2.0 (https://commoncrawl.org/faq/)
 Our older bot identified itself with the
-User-Agent
-string
+UserAgent
+string:
+‍
 CCBot/1.0 (+https://commoncrawl.org/bot.html)
-, and the current version identifies itself as
-CCBot/2.0
-. We may increment the version number in the future.
-‍
-Contact information (a link to the FAQs) is sent along with the
-User-Agent
-string.
+We may increment the version number in the future.
+How does CCBot fetch a web page?
+CCBot is an automated crawler, checking first the
+robots.txt
+, and if crawling a page is allowed, fetches pages using
+HTTP
+GET
+requests.
+It supports both
+HTTP/1.1
+and
+HTTP/2
+, the latter only over TLS (
+https://
+). Connections over IPv4 and IPv6 are supported.
+CCBot follows up to four consecutive HTTP redirects, or up to five when fetching robots.txt in line with
+RFC 9309
+. Currently, JavaScript is not executed and Cookies are not used.
 Will the Common Crawl CCBot make my website slow for other users?
 The CCBot crawler has a number of algorithms designed to prevent undue load on web servers for a given domain.
 We have taken great care to ensure that our crawler will never cause web servers to slow down or be inaccessible to other users.
@@ -56,21 +73,19 @@
 For instance, to limit our crawler from request pages more than once every 2 seconds, add the following to your
 robots.txt
 file:
-‍
 User-agent: CCBot
 Crawl-delay: 2
 How can I block the Common Crawl CCBot?
 You configure your
 robots.txt
 file which uses the Robots Exclusion Protocol to block the crawler. Our bot’s exclusion
-User-Agent
+UserAgent
 string is:
 CCBot
 .
 Add these lines to your
 robots.txt
 file and our crawler will stop crawling your website:
-‍
 User-agent: CCBot
 Disallow: /
 We will periodically continue to check if the
@@ -96,7 +111,7 @@
 wait 24 hours
 before trying again.
 Please sleep between calls to our API (including if you run your script repeatedly in a loop), don't run multiple threads at once on the same IP, and don't use proxy networks. You should also ensure that you are using a properly formulated
-User-Agent
+UserAgent
 string (
 see RFC 9110
 ).
@@ -124,8 +139,10 @@
 GET
 requests. We also currently support the
 gzip
-and
+,
 Brotli
+, and
+ZStandard
 encoding formats.
 Why is the Common Crawl CCBot crawling pages I don’t have links to?
 The bot may have found your pages by following links from other sites.
@@ -168,6 +185,8 @@
 Get in touch
 The Data
 Overview
+CDXJ Index
+Columnar Index
 Web Graphs
 Latest Crawl
 Crawl Stats
@@ -178,10 +197,9 @@
 AI Agent
 Blog
 Examples
-Use Cases
 CCBot
 Infra Status
-Opt-out Registry
+Opt-Out Registry
 FAQ
 Community
 Research Papers
@@ -190,12 +208,11 @@
 Discord
 Collaborators
 About
+About
 Team
 Jobs
-Mission
-Impact
 Privacy Policy
 Terms of Use
 ©
-2025
+2026
 Common Crawl
```

</details>
