---
slug: openai-publishes-full-crawler-bot-documentation-page-with-four-ua-strings-includ
title: "OpenAI publishes full crawler/bot documentation page with four UA strings, including new OAI-AdsBot"
source: gptbot
pillar: crawler
detected_at: 2026-04-19T21:35:19.602033+00:00
source_url: "https://developers.openai.com/api/docs/bots"
change_kind: material
importance: 0.85
---

## What changed

The [OpenAI crawlers page](https://developers.openai.com/api/docs/bots) was created from scratch (previously empty), documenting four user agents: **OAI-SearchBot/1.3** (`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36; compatible; OAI-SearchBot/1.3; +https://openai.com/searchbot`), **OAI-AdsBot/1.0** (`Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-AdsBot/1.0; +https://openai.com/adsbot`) — a newly disclosed bot for validating ChatGPT ad landing pages — **GPTBot/1.3**, and **ChatGPT-User/1.0**. The page also clarifies that if a site allows both OAI-SearchBot and GPTBot, OpenAI may deduplicate crawls, and that robots.txt changes take ~24 hours to propagate.

## Implication

**OAI-AdsBot** is a net-new disclosure: webmasters were previously unaware of this agent visiting ad landing pages submitted to ChatGPT. Because it is explicitly exempt from training data use and only visits pages submitted as ads, it requires no robots.txt opt-out — but site operators should expect and log traffic from this UA. The consolidated page also confirms GPTBot and OAI-SearchBot are now both at version 1.3, and provides canonical IP-range JSON endpoints ([searchbot.json](https://openai.com/searchbot.json), [gptbot.json](https://openai.com/gptbot.json), [chatgpt-user.json](https://openai.com/chatgpt-user.json)) that firewall/allowlist configurations should reference.

## Raw diff

<details><summary>View diff</summary>

```diff
--- prev
+++ curr
@@ -0,0 +1,29 @@
+OpenAI uses web crawlers (“robots”) and user agents to perform actions for its products, either automatically or triggered by user request. OpenAI uses OAI-SearchBot and GPTBot robots.txt tags to enable webmasters to manage how their sites and content work with AI. Each setting is independent of the others – for example, a webmaster can allow OAI-SearchBot in order to appear in search results while disallowing GPTBot to indicate that crawled content should not be used for training OpenAI’s generative AI foundation models. If your site has allowed both bots, we may use the results from just one crawl for both use cases to avoid duplicative crawling. For search results, please note it can take ~24 hours from a site’s robots.txt update for our systems to adjust.
+User agent
+Description & details
+OAI-SearchBot
+OAI-SearchBot is for search. OAI-SearchBot is used to surface websites in search results in ChatGPT’s search features. Sites that are opted out of OAI-SearchBot will not be shown in ChatGPT search answers, though can still appear as navigational links. To help ensure your site appears in search results, we recommend allowing OAI-SearchBot in your site’s robots.txt file and allowing requests from our published IP ranges below.
+Full user-agent string:
+Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36; compatible; OAI-SearchBot/1.3; +https://openai.com/searchbot
+Published IP addresses:
+https://openai.com/searchbot.json
+OAI-AdsBot
+OAI-AdsBot is used to validate the safety of web pages submitted as ads on ChatGPT. When you submit an ad, OpenAI may visit the landing page to ensure it complies with our policies. We may also use content from the landing page to determine when it’s most relevant to show the ad to users. OAI-AdsBot only visits pages submitted as ads, and the data collected by OAI-AdsBot is not used to train generative AI foundation models.
+Full user-agent string:
+Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-AdsBot/1.0; +https://openai.com/adsbot
+GPTBot
+GPTBot is used to make our generative AI foundation models more useful and safe. It is used to crawl content that may be used in training our generative AI foundation models. Disallowing GPTBot indicates a site’s content should not be used in training generative AI foundation models.
+Full user-agent string:
+Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.3; +https://openai.com/gptbot
+Published IP addresses:
+https://openai.com/gptbot.json
+ChatGPT-User
+OpenAI also uses ChatGPT-User for certain user actions in ChatGPT and
+Custom GPTs
+. When users ask ChatGPT or a CustomGPT a question, it may visit a web page with a ChatGPT-User agent. ChatGPT users may also interact with external applications via
+GPT Actions
+. ChatGPT-User is not used for crawling the web in an automatic fashion. Because these actions are initiated by a user, robots.txt rules may not apply. ChatGPT-User is not used to determine whether content may appear in Search. Please use OAI-SearchBot in robots.txt for managing Search opt outs and automatic crawl.
+Full user-agent string:
+Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot
+Published IP addresses:
+https://openai.com/chatgpt-user.json
```

</details>
