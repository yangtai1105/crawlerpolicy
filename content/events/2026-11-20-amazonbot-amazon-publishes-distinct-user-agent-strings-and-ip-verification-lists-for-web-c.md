---
schema_version: 2
slug: amazon-publishes-distinct-user-agent-strings-and-ip-verification-lists-for-web-c
title: "Amazon Publishes Distinct User Agent Strings and IP Verification Lists for Web Crawlers and Live User Agent"
source: amazonbot
source_tier: primary
primary_track: access-controls
tracks:
  - access-controls
  - standards-protocols
actors:
  - "Amazon"
event_date: 2026-11-20T16:43:41.099471+00:00
published_at: 2026-11-20T16:43:41.099471+00:00
detected_at: 2026-11-20T16:43:41.099471+00:00
source_url: "https://developer.amazon.com/amazonbot"
change_kind: material
importance: 0.65
confidence: high
evidence_ids:
  - "amazonbot--5df8b957536e3481"
---

## Development

Amazon updated its crawler documentation to publish specific browser-formatted user agent strings and dedicated IP address listing pages for Amazonbot, Amzn-SearchBot, and Amzn-User. The additions provide network administrators and webmasters with explicit endpoints to verify incoming requests from Amazon's automated crawlers and its live user-directed fetcher.

## Key facts

- Amazon published example user agent strings formatted with Chrome and Safari compatibility tokens for Amazonbot/0.1, Amzn-SearchBot/0.1, and Amzn-User/0.1.
- Dedicated published IP address directory URLs were added for [Amazonbot](https://developer.amazon.com/amazonbot/ip-addresses/), [Amzn-SearchBot](https://developer.amazon.com/amazonbot/searchbot-ip-addresses/), and [Amzn-User](https://developer.amazon.com/amazonbot/live-ip-addresses/).
- Amazonbot is used to improve services and "may be used to train Amazon AI models."
- Amzn-SearchBot and Amzn-User do not crawl content for generative AI model training.
- Because Amzn-User is initiated by a user for live information fetches, Amazon notes it "may not follow all robots.txt directives."
- Automated crawling from these user agents respects the Robots Exclusion Protocol's allow and disallow directives, but Amazon explicitly does not support the crawl-delay directive.

## Why it matters

Clear differentiation and IP verification prevent spoofing and allow publishers to selectively block Amazon's AI model training crawler while permitting search indexing or live Alexa user query responses.

## Trend impact

- ip-based-crawler-verification
- segmented-bot-identities
- user-agent-differentiation

## Evidence

- [Primary source](https://developer.amazon.com/amazonbot)
- Evidence ID: `amazonbot--5df8b957536e3481`

<details><summary>View raw diff</summary>

```diff
--- prev
+++ curr
@@ -1,11 +1,67 @@
-Amazon Web Search crawlers
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
+Fire OS Developer Docs
+Home
+Develop
+Test
+Publish
+Monetize
+Engage users
+Device specifications
+Resources
+Documentation Index
+Fetch the complete documentation index at:
+/llms.txt
+Use this file to discover all available pages before exploring further.
+Skip to main content
 This page describes how webmasters can control Amazonbot, Amzn-SearchBot, and Amzn-User interactions with their site. Each user agent setting is independent of the others, and may take ~24 hours for our systems to reflect changes.
 Amazonbot
 Amazonbot is used to improve our products and services. This helps us provide more accurate information to customers and may be used to train Amazon AI models.
+Example User Agent String
+:
+Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Amazonbot/0.1) Chrome/W.X.Y.Z Safari/537.36
+Published IP Addresses
+:
+https://developer.amazon.com/amazonbot/ip-addresses/
 Amzn-SearchBot
 Amzn-SearchBot is used to improve search experiences in Amazon products and services. By permitting Amzn-SearchBot access to your website, your content is eligible to appear in search experiences such as Alexa. If robots.txt files don’t mention Amzn-SearchBot but allow other search bots, Amzn-SearchBot will crawl in accordance with the robots.txt directives given to other search bots. Amzn-SearchBot does not crawl content for generative AI model training.
+Example User Agent String
+:
+Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Amzn-SearchBot/0.1) Chrome/W.X.Y.Z Safari/537.36
+Published IP Addresses
+:
+https://developer.amazon.com/amazonbot/searchbot-ip-addresses/
 Amzn-User
 Amzn-User supports user actions, such as responding to Alexa queries that require up-to-date information. For example, when a customer asks a question, Amzn-User may fetch live information from the web to provide accurate answers on the user’s behalf. Because actions taken by Amzn-User can be initiated by a user, it may not follow all robots.txt directives.Amzn-User does not crawl content for generative AI model training.
+Example User Agent String
+:
+Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Amzn-User/0.1) Chrome/W.X.Y.Z Safari/537.36
+Published IP Addresses
+:
+https://developer.amazon.com/amazonbot/live-ip-addresses/
 Our Approach to Robots.txt
 Automated crawling from these listed user agents respects the
 Robots Exclusion Protocol
@@ -20,6 +76,7 @@
 site.example.com/robots.txt
 .
 When these user agents access web pages they respect the link-level rel=nofollow directive, and page level robots meta tags of noarchive (do not use the page for model training), noindex (do not index the page) and none (do not index the page). They do not support the crawl-delay directive.
+Contact Us
 If you are a content owner or publisher and have questions, please contact us at
 amazonbot@amazon.com
 . Always include any relevant domain names in your message.
@@ -27,4 +84,40 @@
 If you allow Amazonbot on your robots.txt, you may be eligible for benefits with Amazon Content Partners. Amazon Content Partners gives independent content creators a +1% affiliate commission boost on eligible sales, free hosting credits, and AI traffic management tools — all in one program. Learn more at
 contentpartners.amazon.com
 .
-Last updated: Oct 26, 2026
+Last modified on
+October 26, 2026
+Was this page helpful?
+Yes
+No
+⌘
+I
+Back to Top
+Follow us:
+Resources
+Appstore developer blog
+Technical documentation
+Amazon Developer Huddle
+Supported devices
+Amazon Fire TV
+Fire tablets
+Other services & APIs
+Small Business Accelerator Program
+Developer Promotions Console
+Alexa for video publishers
+Login with Amazon
+Frustration-Free Setup
+Amazon Incentives API
+Amazon Merch on Demand
+Amazon Music
+Fire TV Partners
+Support
+Appstore Developer Community
+FAQs
+Contact us
+Legal
+Terms & agreements
+Privacy Notice
+© 2010-2026, Amazon.com, Inc. or its affiliates. All Rights Reserved.
+Terms
+Amazon Developer Blog
+Contact Us
```

</details>
