---
slug: chrome-s-ai-web-apis-enable-new-hardware-fingerprinting-technique-for-bot-detect
title: "Chrome's AI Web APIs Enable New Hardware Fingerprinting Technique for Bot Detection"
source: datadome-blog
pillar: ecosystem
detected_at: 2026-04-22T13:32:08+00:00
source_url: "https://datadome.co/threat-research/how-chromes-new-ai-web-apis-enable-hardware-fingerprinting/"
change_kind: material
importance: 0.76
---

## News

[Google introduced on-device AI APIs in Chrome](https://datadome.co/threat-research/how-chromes-new-ai-web-apis-enable-hardware-fingerprinting/) (Translator, Language Detector, and Summarizer in Chrome 138, with LanguageModel forthcoming in Chrome 148) that expose hardware capability thresholds—GPU VRAM, CPU cores, RAM, storage—allowing websites to query device API support availability. DataDome's analysis shows only 4% of global traffic can run the Summarizer API, and these APIs' availability states (unavailable, downloadable, available) create implicit hardware fingerprints. A forthcoming LanguageModel API will enable even more granular inference-timing fingerprinting via TTFT (time-to-first-token) and decode throughput measurements, allowing bot-detection teams to classify devices by actual performance rather than spoofable declarative properties.

## Why it matters

This represents a significant shift in bot-detection methodology—from passive property inspection to active performance testing. The timing-based fingerprinting approach raises the cost for attackers to maintain coherent spoofed hardware profiles, as they must either possess the claimed hardware, perfectly simulate AI inference patterns, or accept detectable inconsistencies. However, this also sharpens the privacy/functionality tension for Chrome: as local AI becomes standard, feature-enabling APIs increasingly leak hardware intelligence. The pattern continues DataDome's recent focus on AI-driven traffic segmentation and intent-based detection (see prior webinar on intent-based bot management); this news extends that positioning into a new technical frontier. For publishers and bot-defense practitioners, these APIs offer materially harder-to-spoof signals; for regulators and privacy advocates, they underscore browser-mediated fingerprinting risks as AI features proliferate.

