---
schema_version: 2
slug: google-formally-documents-six-user-triggered-fetchers-and-abuse-reporting-workfl
title: "Google Formally Documents Six User-Triggered Fetchers and Abuse Reporting Workflows"
source: google-user-triggered-fetchers
source_tier: primary
primary_track: access-controls
tracks:
  - access-controls
  - platform-ecosystem
actors:
  - "Google"
event_date: 2026-11-23T19:53:27.881652+00:00
published_at: 2026-11-23T19:53:27.881652+00:00
detected_at: 2026-11-23T19:53:27.881652+00:00
source_url: "https://developers.google.com/search/docs/crawling-indexing/google-user-triggered-fetchers"
change_kind: material
importance: 0.65
confidence: high
evidence_ids:
  - "google-user-triggered-fetchers--ec688633c7fe780b"
---

## Development

Google updated its user-triggered fetchers registry to document six additional services, including Google App Engine, Google Apps Script, Google Cloud Tasks, Google Image Proxy, Google Web Preview, and PageSpeed Insights. The documentation details the exact User-Agent strings, runtime behaviors, and Cloud abuse reporting mechanisms for these fetchers. Because these requests operate upon user or developer action, they fall under Google's policy of generally bypassing robots.txt rules.

## Key facts

- Google added six fetchers to its user-triggered fetcher list: Google App Engine, Google Apps Script, Google Cloud Tasks, Google Image Proxy, Google Web Preview, and PageSpeed Insights.
- User-triggered fetchers are initiated by users within Google products and 'generally ignore robots.txt rules.'
- Google App Engine requests append 'AppEngine-Google; (+http://code.google.com/appengine; appid: APPID)' to any custom User-Agent, where 'APPID' identifies the specific project.
- Google Apps Script requests use the token 'Mozilla/5.0 (compatible; Google-Apps-Script; beanserver; +https://script.google.com; id: SCRIPT_ID)', allowing targets to identify the initiating script.
- Abuse reports for App Engine and Apps Script must be submitted through the 'Report suspected abuse on Google Cloud' form, including the appid or script ID, source IP address, and timestamp.
- Google Cloud Tasks dispatches requests with the User-Agent 'Google-Cloud-Tasks' for endpoints configured in Cloud Tasks HTTP target queues.
- Google Image Proxy fetches external images embedded in emails and documents using 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)'.
- PageSpeed Insights audits run via mobile and desktop Chrome-Lighthouse user agents fetching target pages and subresources from pagespeed.web.dev.

## Why it matters

User-triggered fetchers bypass robots.txt exclusions by design. Documenting exact User-Agent patterns and script identifiers allows site operators to track specific tenant origins and submit actionable abuse reports against offending Google Cloud projects.

## Trend impact

- proxy attribution transparency
- user-agent granular auditing
- abuse reporting integration

## Evidence

- [Primary source](https://developers.google.com/search/docs/crawling-indexing/google-user-triggered-fetchers)
- Evidence ID: `google-user-triggered-fetchers--ec688633c7fe780b`

<details><summary>View raw diff</summary>

```diff
--- prev
+++ curr
@@ -62,6 +62,60 @@
 It uses IP ranges from
 user-triggered-agents.json
 .
+Google App Engine
+User-Agent in HTTP requests
+AppEngine-Google; (+http://code.google.com/appengine; appid: APPID)
+Appended to any custom
+User-Agent
+set by the app.
+Associated products
+Requests initiated by applications hosted on Google App Engine Standard Environment
+using the
+URL Fetch service
+,
+where
+APPID
+identifies the App Engine project. To report abusive requests
+from an App Engine app, use the
+Report suspected abuse on Google Cloud
+form and include the
+appid
+value (
+https://APPID.appspot.com
+,
+omitting any
+s~
+prefix), source IP address, and timestamp.
+Google Apps Script
+User-Agent in HTTP requests
+Mozilla/5.0 (compatible; Google-Apps-Script; beanserver; +https://script.google.com; id: SCRIPT_ID)
+Associated products
+Google Apps Script fetches external URLs and APIs on behalf of user-created scripts
+calling the
+UrlFetchApp
+service across Google Workspace. To report abusive requests, use the
+Report suspected abuse on Google Cloud
+form and include the full
+User-Agent
+string (with
+id: SCRIPT_ID
+), source IP address, and timestamp.
+Google Cloud Tasks
+User-Agent in HTTP requests
+Google-Cloud-Tasks
+Associated products
+Google Cloud Tasks dispatches asynchronous HTTP requests and scheduled webhooks to
+target endpoints configured by developers in
+Cloud Tasks HTTP target queues
+.
+Google Image Proxy
+User-Agent in HTTP requests
+Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)
+Associated products
+Google Image Proxy fetches external images embedded in emails and documents when a user
+opens them (for example,
+images in emails on Gmail
+to protect users from image-based security and privacy risks).
 Google Messages
 User-Agent in HTTP requests
 GoogleMessages
@@ -98,6 +152,36 @@
 Mozilla/5.0 (compatible; Google-Site-Verification/1.0)
 Associated products
 Google Site Verifier fetches Search Console verification tokens.
+Google Web Preview
+User-Agent in HTTP requests
+Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko; Google Web Preview)
+Chrome/
+W.X.Y.Z
+Safari/537.36
+Associated products
+Google Web Preview fetches web pages on demand to generate link preview thumbnails when
+users attach or share URLs in Google products such as
+Google Classroom
+.
+PageSpeed Insights
+User-Agent in HTTP requests
+Mobile agent
+Mozilla/5.0 (Linux; Android 11; moto g power (2022)) AppleWebKit/537.36 (KHTML, like Gecko)
+Chrome/
+W.X.Y.Z
+Mobile Safari/537.36 Chrome-Lighthouse
+Desktop agent
+Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)
+Chrome/
+W.X.Y.Z
+Safari/537.36 Chrome-Lighthouse
+Associated products
+The PageSpeed Insights user agent fetches web pages and their subresources when a user
+runs a performance and quality audit in
+PageSpeed Insights
+(
+pagespeed.web.dev
+).
 Send feedback
 Except as otherwise noted, the content of this page is licensed under the
 Creative Commons Attribution 4.0 License
@@ -106,4 +190,4 @@
 . For details, see the
 Google Developers Site Policies
 . Java is a registered trademark of Oracle and/or its affiliates.
-Last updated 2026-08-19 UTC.
+Last updated 2026-11-23 UTC.
```

</details>
