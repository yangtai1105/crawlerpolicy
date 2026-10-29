---
schema_version: 1
slug: perplexitybot-perplexity-updates-waf-guidance-with-bot-specific-ip-matching-and-cloudflare-ski
title: "Perplexity updates WAF guidance with bot-specific IP matching and Cloudflare Skip rules"
source: perplexitybot
source_tier: primary
status: verified
primary_track: access-controls
tracks:
  - access-controls
  - search-discovery
  - platform-ecosystem
actors:
  - "Perplexity"
  - "Cloudflare"
  - "AWS"
subject: both
event_date: 2026-10-29T14:58:01.749807+00:00
published_at: 2026-10-29T14:58:01.749807+00:00
detected_at: 2026-10-29T14:58:01.749807+00:00
source_urls:
  - "https://docs.perplexity.ai/guides/bots"
change_kind: material
importance: 0.45
confidence: high
evidence_ids:
  - "perplexitybot--50f120be2e951f1c"
trend_signals:
  - WAF-level AI crawler bypass complexity
  - Differentiation between background indexing bots and user-agent bots
development_slug: perplexity-updates-waf-guidance-with-bot-specific-ip-matching-and-cloudflare-ski
players:
  - "perplexity"
  - "cloudflare"
  - "amazon"
protocols:
  - "robots-txt"
backfilled: false
---

## Summary

Perplexity updated its documentation instructing webmasters on how to configure Web Application Firewalls for its crawlers. The guidance shifts from single combined rules to matching PerplexityBot and Perplexity-User against distinct IP ranges. For Cloudflare, it specifies using Skip actions rather than Allow, noting that Bot Fight Mode cannot be bypassed via custom WAF rules.

## Key facts

- Perplexity instructs webmasters to match each bot (PerplexityBot and Perplexity-User) against its own distinct IP ranges rather than combining them into a single condition.
- Cloudflare WAF configuration instructions were changed from setting rule actions to 'Allow' to setting them to 'Skip'.
- Perplexity specifies that Cloudflare's 'Bot Fight Mode can’t be skipped with WAF custom rules' and can still challenge Perplexity bots even if the custom rule matches.
- Cloudflare Skip rules can be configured to bypass features including 'All remaining custom rules', 'All managed rules', 'All rate limiting rules', or 'All Super Bot Fight Mode rules'.
- On Cloudflare, Perplexity notes that free plans allow only one custom IP list, which 'isn’t enough for both bots' to reference separately via lists like ip.src in $perplexitybot.
- For AWS WAF, Perplexity specifies creating distinct IP sets and separate AND rules for PerplexityBot and Perplexity-User with lower priority numbers so they evaluate first.

## Insight

AI crawlers increasingly require granular network-level configurations because blended user-agent checks fail when automated and user-directed bots operate from separate IP infrastructure and encounter distinct mitigation tiers like Bot Fight Mode.

## Implication

Site operators on free Cloudflare tiers face added configuration friction due to single custom list limits, while administrators using Cloudflare Bot Fight Mode must note that standard custom rules will still challenge Perplexity bots.

## Why it matters

As sites aggressively block AI agents by default at the firewall, crawler operators must provide precise, vendor-specific WAF instructions to ensure intended access is not silently dropped by managed edge defenses.

## Evidence

- [Primary source](https://docs.perplexity.ai/guides/bots)
- Evidence ID: `perplexitybot--50f120be2e951f1c`

<details><summary>View observed change</summary>

```diff
--- prev
+++ curr
@@ -1,54 +1,65 @@
 We strive to improve our service every day by delivering the best search experience possible. To achieve this, we collect data using web crawlers (“robots”) and user agents that gather and index information from the internet, operating either automatically or in response to user requests. Webmasters can use the following robots.txt tags to manage how their sites and content interact with Perplexity. Each setting works independently, and it may take up to 24 hours for our systems to reflect changes.
 WAF Configuration
-If you’re using a Web Application Firewall (WAF) to protect your site, you may need to explicitly whitelist Perplexity’s bots to ensure they can access your content. Below are configuration guidelines for popular WAF providers.
+If you’re using a Web Application Firewall (WAF) to protect your site, you may need to explicitly allow Perplexity’s bots to ensure they can access your content. Below are configuration guidelines for popular WAF providers.
 Cloudflare WAF
 To configure Cloudflare WAF to allow Perplexity bots:
-Navigate to WAF settings
+Navigate to security rules
 In your Cloudflare dashboard, go to
 Security
 →
-WAF
+Security rules
 .
 Create a new rule
-Click on
+Select
+Create rule
+→
 Custom rules
-and create a new rule to allow Perplexity bots.
+.
 Configure rule conditions
-Set up a rule that combines both User-Agent and IP address conditions:
-Field
-: User Agent
-Operator
-: Contains
-Value
-:
-PerplexityBot
-OR
-Perplexity-User
-AND
-Field
-: IP Source Address
-Operator
-: Is in
-Value
-: Use the IP ranges from the official endpoints listed below
+Each bot has its own IP ranges, so match each User-Agent against its own IP ranges. Select
+Edit expression
+and enter:
+Replace each placeholder with the current ranges from the official endpoints listed below, separated by spaces, for example
+{192.0.2.0/24 198.51.100.7/32}
+. When the published ranges change, update them in this rule.
+On paid plans, you can instead store each bot’s ranges in an IP list and reference it, for example
+ip.src in $perplexitybot
+. You then update the lists rather than the rule. Free plans allow only one custom list, which isn’t enough for both bots.
 Set rule action
 Set the action to
-Allow
-to ensure these requests bypass other security rules.
+Skip
+and select the security features these requests should bypass, such as
+All remaining custom rules
+,
+All managed rules
+,
+All rate limiting rules
+, or
+All Super Bot Fight Mode rules
+.
+Order the rule
+Place this rule above any custom rules that block or challenge requests. A Skip rule only bypasses rules that run after it.
+Cloudflare’s Bot Fight Mode can’t be skipped with WAF custom rules. If Bot Fight Mode is enabled, it can still challenge Perplexity bots that match this rule.
 AWS WAF
-For AWS WAF configuration, create IP sets and string match conditions:
+For AWS WAF configuration, create IP sets and rules that match them together with the User-Agent header:
 Create IP sets
-In the AWS WAF console, create IP sets for both PerplexityBot and Perplexity-User using the IP addresses from the official endpoints listed below.
-Create string match conditions
-Create string match conditions for the User-Agent headers:
+In the AWS WAF console, create an IP set for PerplexityBot and one for Perplexity-User using the IP addresses from the official endpoints listed below.
+Create allow rules
+For each bot, create a rule with an
+AND
+statement that combines:
+An IP set match statement that uses the bot’s IP set
+A string match statement on the
+User-Agent
+header that contains
 PerplexityBot
+or
 Perplexity-User
-Create allow rules
-Create rules that combine the IP sets with the corresponding User-Agent strings, and set the action to
+Set the rule action to
 Allow
 .
-Associate with Web ACL
-Associate these rules with your Web ACL and ensure they have higher priority than blocking rules.
+Add the rules to your web ACL
+Add these rules to your web ACL and give them lower priority numbers than your blocking rules, so AWS WAF evaluates them first.
 IP Address Sources
 Always use the most current IP ranges from the official JSON endpoints. These addresses are updated regularly and should be the source of truth for your WAF configurations.
 Set up automated processes to periodically fetch and update your WAF rules with the latest IP ranges from these endpoints to ensure continuous access for Perplexity bots.
```

</details>
