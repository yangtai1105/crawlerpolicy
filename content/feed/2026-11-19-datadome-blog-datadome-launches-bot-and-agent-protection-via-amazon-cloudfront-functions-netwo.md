---
schema_version: 1
slug: datadome-blog-datadome-launches-bot-and-agent-protection-via-amazon-cloudfront-functions-netwo
title: "DataDome launches bot and agent protection via Amazon CloudFront Functions network calls"
source: datadome-blog
source_tier: specialist
status: reported
primary_track: access-controls
tracks:
  - access-controls
  - platform-ecosystem
  - measurement-economics
actors:
  - "DataDome"
  - "Amazon Web Services"
subject: both
event_date: 2026-11-19T14:26:41+00:00
published_at: 2026-11-19T14:26:41+00:00
detected_at: 2026-11-19T17:05:06.465696+00:00
source_urls:
  - "https://datadome.co/changelog/datadome-is-first-bot-agent-trust-partner-to-support-network-calls-on-cloudfront-functions/"
change_kind: material
importance: 0.65
confidence: high
evidence_ids:
  - "datadome-blog--fc474466054217d1"
trend_signals:
  - edge-native bot mitigation
  - AI agent traffic filtering
  - TLS fingerprint inspection
players:
  - "datadome"
  - "amazon"
backfilled: false
---

## Summary

DataDome announced general availability for its bot and agent trust management integration using network calls on Amazon CloudFront Functions. The edge-computing integration enables real-time threat evaluation directly within CloudFront request event handlers rather than requiring Lambda@Edge. The company reports the architecture scales up to 10 million requests per second and cuts AWS serverless compute costs by up to 60%.

## Key facts

- DataDome announced general availability of its integration with network calls on Amazon CloudFront Functions (CF2).
- The deployment operates alongside existing AWS Lambda@Edge configurations without requiring customers to replace existing setups immediately.
- Early estimates indicate up to 60% lower AWS CloudFront serverless computing costs for customers migrating from Lambda@Edge.
- The CloudFront Functions integration scales up to 10 million requests per second.
- The integration provides edge signals including JA3 and JA4 TLS fingerprints across request traffic to detect malicious bots and AI agents.
- More than 60% of DataDome customers use a CDN security layer alongside DataDome.
- DataDome was also named a launch partner for AWS Marketplace Buyer Contact Share to streamline customer onboarding.

## Insight

By shifting third-party security lookups into lightweight CDN edge functions enabled by asynchronous network calls, bot mitigation vendors can eliminate heavier serverless runtimes like Lambda@Edge while accessing edge signals like JA3 and JA4 TLS fingerprints.

## Implication

AWS-hosted sites can enforce low-latency bot and AI agent filtering at higher traffic volumes with substantially lower compute overhead ahead of high-traffic shopping periods.

## Why it matters

Edge bot defenses often create a cost and latency penalty for operators; enabling network-capable edge function checks lowers compute costs while maintaining deep traffic inspection against automated crawlers and AI agents.

## Evidence

- [Primary source](https://datadome.co/changelog/datadome-is-first-bot-agent-trust-partner-to-support-network-calls-on-cloudfront-functions/)
- Evidence ID: `datadome-blog--fc474466054217d1`
