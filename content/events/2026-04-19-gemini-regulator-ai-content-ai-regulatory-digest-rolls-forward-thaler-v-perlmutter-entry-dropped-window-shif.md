---
slug: ai-regulatory-digest-rolls-forward-thaler-v-perlmutter-entry-dropped-window-shif
title: "AI Regulatory Digest Rolls Forward: Thaler v. Perlmutter Entry Dropped, Window Shifts to March 20–April 19, 2026"
source: gemini-regulator-ai-content
pillar: ecosystem
detected_at: 2026-04-19T20:20:28.999309+00:00
source_url: ""
change_kind: material
importance: 0.62
---

## What changed

The digest has advanced its 30-day coverage window from roughly March 10–April 10 to March 20–April 19, 2026. The most substantive editorial change is the removal of the *Thaler v. Perlmutter* Supreme Court cert-denial item, which had affirmed the human-authorship requirement for U.S. copyright registration. The ordering of items also shifted: the UK TDM exception story now leads, while the European Parliament copyright report moves to second. Inline hyperlinks to primary sources (GOV.UK, European Parliament, Wilson Sonsini, FTC) replace the previous grounding-API redirect citations, providing more direct attribution. Descriptions of retained items are modestly condensed—for example, the White House framework entry drops the mention of federal protections for AI-generated digital replicas of voice and likeness—and the UK item now explicitly names the government's posture as "wait and see."

## Implication

The removal of the Thaler cert-denial item is the only substantive content loss: that ruling had practical relevance for anyone building or licensing AI-generated content, as it settled (for now) that purely AI-authored works cannot be registered under U.S. law. Publishers and agent-infrastructure teams relying on this digest as a policy signal tracker should note the gap and source that development independently. The condensation of the White House framework entry also omits the digital-replica/likeness-protection recommendation, which is directly relevant to media and synthetic-voice use cases. The shift to direct primary-source URLs is a positive reliability improvement. The "wait and see" framing now explicit in the UK item is editorially cleaner but does not represent a new fact—practitioners should treat the underlying policy position as unchanged.

## Raw diff

<details><summary>View diff</summary>

```diff
--- prev
+++ curr
@@ -1,36 +1,29 @@
-Here's a compact digest of important regulatory developments from the last 30 days concerning AI training data, AI crawlers, content licensing, and generative AI and copyright:
-1. **European Parliament Adopts Report on Copyright and Generative AI**
- On March 10, 2026, the European Parliament adopted a resolution on "Copyright and Generative Artificial Intelligence – Opportunities and Challenges." The report calls for clarifying and strengthening the EU copyright framework for generative AI, emphasizing that creators must retain control over their works used for AI training and downstream uses. It also proposes measures to disclose copyright-protected works used for AI training, support a collective licensing framework, and asserts that EU copyright rules should apply to generative AI models available in the EU, regardless of where the training takes place.
- * **Authoritative Source:** European Parliament (See "Texts adopted - Copyright and generative artificial intelligence – opportunities and challenges - Tuesday, 10 March 2026").
-2. **UK Government Drops Plans for Broad Text and Data Mining Exception**
- The UK government confirmed on March 18, 2026, that it will not introduce a broad copyright exception for text and data mining (TDM) with an opt-out mechanism for AI training. Instead, the existing copyright framework applies, meaning AI developers must obtain licenses to use copyrighted works for training unless a specific existing exception applies. The government will now allow industry-led licensing arrangements to develop and will monitor global legal developments before considering any legislative changes.
- * **Authoritative Source:** GOV.UK (See "Report on Copyright and Artificial Intelligence" published March 18, 2026).
-3. **Court of Rome Annuls Italian Garante's Fine Against OpenAI**
- On March 18, 2026, the Court of Rome annulled a €15 million fine and an order requiring OpenAI to conduct a media campaign about AI model training, which had been imposed by the Italian Data Protection Authority (Garante). The original enforcement action had alleged multiple GDPR violations related to the management of OpenAI's ChatGPT service, including processing personal data for training without an adequate legal basis and transparency failures.
- * **Authoritative Source:** While the full reasoning of the Court of Rome has not yet been published, the annulment was widely reported by legal news outlets on March 19, 2026, and March 31, 2026.
-4. **White House Releases National Policy Framework for AI, Addresses Copyright**
- On March 20, 2026, the White House released a National Policy Framework for Artificial Intelligence, which includes legislative recommendations concerning intellectual property rights. The framework suggests that Congress allow courts to resolve questions of fair use regarding AI training on copyrighted material and consider enabling licensing frameworks or collective rights systems. It also recommends establishing federal protections against the unauthorized distribution or commercial use of AI-generated digital replicas of an individual's voice, likeness, or other identifiable attributes, with exceptions for parody, satire, and news reporting.
- * **Authoritative Source:** Baker Botts (reporting on the White House framework, April 13, 2026).
-5. **US Supreme Court Denies Certiorari in Thaler v. Perlmutter AI Authorship Case**
- In March 2026, the U.S. Supreme Court denied Stephen Thaler's petition for a writ of certiorari in the case of *Thaler v. Perlmutter*. This decision effectively upholds the U.S. Copyright Office's denial of copyright registration for an artwork generated entirely by an artificial intelligence system, reinforcing the requirement for human authorship in copyrighted works under current U.S. law.
- * **Authoritative Source:** Anderson Kill P.C. (reporting on the case, April 6, 2026) and Copyrightlaws.com (reporting on the case, March 25, 2026).
-6. **FTC Announces Settlement with Air AI Technologies for Deceptive Marketing**
- On March 24, 2026, the Federal Trade Commission (FTC) announced a proposed settlement with Air AI Technologies, Inc., and its owners, resolving charges that the company deceptively marketed AI-related business support services. The FTC's complaint alleged false earnings claims and sham refund guarantees, violating the FTC Act and other rules. The proposed order includes an $18 million monetary judgment, largely suspended, and permanently bans the defendants from selling or marketing any business opportunity or making false claims.
- * **Authoritative Source:** Retail & Consumer Products Law Observer (reporting on FTC updates, April 10, 2026).
+Here is a compact digest of important regulatory actions and developments from the last 30 days (March 20, 2026, to April 19, 2026) concerning AI training data, AI crawlers, content licensing, or generative AI and copyright:
+1. **UK Government Drops Plans for Broad AI Copyright Exception**
+ The UK government published a report on copyright and artificial intelligence, confirming it will no longer pursue its previously preferred option of a broad exception to copyright infringement for text and data mining (TDM) with an opt-out mechanism. Instead, the government will adopt a "wait and see" approach, allowing industry-led licensing arrangements to develop and monitoring global legal developments before considering legislative changes.
+ Source: [GOV.UK](https://www.gov.uk/government/publications/report-on-copyright-and-artificial-intelligence)
+2. **European Parliament Adopts Report on Copyright and Generative AI**
+ The European Parliament adopted a report on "Copyright and generative artificial intelligence – opportunities and challenges," calling for stronger protections for copyright holders. The report emphasizes the need for transparency regarding copyrighted works used for AI training, fair remuneration for creators, and the establishment of new licensing frameworks.
+ Source: [European Parliament](https://www.europarl.europa.eu/doceo/document/A-10-2026-0019_EN.html)
+3. **Italian Court Annuls Garante's €15 Million Fine Against OpenAI**
+ On March 18, 2026, the Court of Rome annulled a €15 million fine and an order for a media campaign against OpenAI, which had been imposed by the Italian Data Protection Authority (Garante) for alleged GDPR violations related to ChatGPT's data processing for training. The court's full reasoning has not yet been published, and the Garante may appeal the decision.
+ Source: [Wilson Sonsini](https://www.wilsonsonsini.com/news/openai-prevails-in-landmark-italian-ai-and-gdpr-enforcement-case/)
+4. **US White House Releases National Policy Framework for Artificial Intelligence**
+ On March 20, 2026, the White House released a National Policy Framework for Artificial Intelligence, which includes legislative recommendations concerning intellectual property rights. The framework suggests allowing courts to resolve questions of fair use in AI training and encourages Congress to consider enabling licensing frameworks or collective rights systems for creators to negotiate compensation from AI providers.
+ Source: [Baker Botts](https://www.bakerbotts.com/thought-leadership/ai-legal-watch/2026/ai-legal-watch-april)
+5. **US FTC Announces Settlement for Deceptive AI Business Opportunity Marketing**
+ On March 24, 2026, the US Federal Trade Commission (FTC) announced a proposed settlement with Air AI Technologies, Inc. and its owners. The FTC's complaint alleged that the defendants deceptively marketed AI-related business support services with false earnings claims and sham refund guarantees to entrepreneurs and small businesses. The proposed order imposes an $18 million monetary judgment, largely suspended, and permanently bans the defendants from selling or marketing any business opportunity.
+ Source: [Federal Trade Commission](https://www.ftc.gov/news-events/news/press-releases/2026/03/air-ai-its-owners-will-be-banned-marketing-business-opportunities-settle-ftc-charges-company-misled-many)
 ## Cited sources
-1. [europa.eu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlF8sGV4oeL0xQoXKT4oD49A-zaS8UFG_rOW0zrPtyXhqAjL-xsqgR60l63EIYNte2uMUDjjARb_i6DOS-3IOQfXYcx6ozrPHRXTF1gyOvHIceb-Kk1s2zmf5wCZq8kvxClD4DZaxjaPg0Fr6iIS9JS14nd7sDI18TgAXAa1HF)
-2. [osborneclarke.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHprN4JxHxVx7sZwHjeDWBPwUtYshaQT9rvD9IQ4_yb-k4mZOsqYmL3PET1rQqAE1xMU84S3MKScCvk8wChQN3yNdqclU06vdzTIknbT07ZI9lLBVvSyyahL9tHrkuuy6mU64dHANEWnExOO5b0Et77n_TUPglgACKn2gUiFSWuBMtzbhNC3BdDFA0MAEdoeTlQHUzx7g==)
-3. [bakerbotts.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqbBsyNvYYokXN7VFmZa8vFJiOFPEZlbTaigGgbjfgzCiX87Nup_-IdGW6Qw1yf-q8u_IGlMjvmsNdKmGc4b_3kU_Wt5mtk1oaOl3Eg6CaREb6dQb0JmIH8isYlIx4EZQUHLg28it6QFh8H-eaSQzei4bjMiZCAkEqV1XRV6TnRoeGxYHGpVL9LiOQdiWNTTU9Yidzd42EBmoBTIiqrQu_aIV0FWD8DY7grKKqIVVkM7E=)
-4. [europa.eu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGF6xEo8d6CqXsBZKtktNz2oKPosiPoAzjm4y58ZYOZ8wn_7tQ8PT9lRgLiJ4EjpWYWosyhkoHDYpXz7Lq2oKLHZLW5BZkHW-A6kJmtX2kviuS5vCCOrH4r3DpZSwuPh4KSzsffbAQAdfXJ-RyE6u1MEh-vyZqfBFwFqYPnZozyog==)
-5. [dataguidance.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0W589Fl8jlxTJF6OQqxfTArcYzdtdDb-Ix8QYLXlNuv06CoQjaTxqXZxZJR1mFQoRy1IsMdozBlZ8UtOTlbrPl-lRGxeR3Icv1yCyUcoNfQvM8drygXmgGU7gIt0xb_k7CejApm8wNMjEZ50M9Ng7wh0qjrGHCz0bnK-6GzNemY_aXXHTk0_j5LRNIPRwO6E=)
-6. [jdsupra.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_T2AQAnfdzEfwbi_SM1zoo_YFd1Vl8J7g9lE8nK6IyjNKL7Okht6nn3ipTPu1bkgoQ8b8XSC-xB9-IjBpvTO2jGJwCr-b9xC5sgCMVBdDzbOmeFy72IQBi7m39FYIYX1xhcQme3d1FLO82aeHRpdbxmtTD9bJNX60eKfkkfymt3GXb5veAerx6vCF)
-7. [wolterskluwer.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWbKVeFyHbLdhhM8qf2YEDDQlzt7aVnQP73xOX0KNY_mlTHlV-lz9FaOM1_xbjAMd9FiC-gEwak9cwbCwt8QqcnnFjS7KnBYKmbBPyGTkuUli515F2Uk7bGRLk13Rk0X1fez2CsuctEZOx5I_dDPlw7eC4csnO7-hJJd8YB3Dy1hHmc9wAB0N8_oizwz12wpzgt8CXWzu0CwduRowkdwz1)
-8. [aoshearman.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoyZH9SVPKrIkKX2KcMWQfzWE9KfBDTeFsrChRbPYHheoQKHinrNeWaMetoPPNmmcFuogff814Y0fjz0KqF0NF0FK6DLwvm5OQXIQRhFxSP7e6shbpVeZno5wVvMHze_OQQcSbCODSsvJN-KItfvT1q1SignTeJj9DHgCz2iwpoDm1dHTuwRO_N6H1Z5tJej8mJhvP9UPy_w63tZN7TLYO)
-9. [www.gov.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuy9tOrWS7TLQh0Izb28im4TUKtuXclh4YDBy01RwJRTs3iELx3S2RfbJ187UM89zBRkMZa35Qbh4xiw38beYqj7R0SWzkbuI-ayyXM9Oc5w-d-JCmZixvryfhbbvvDgkyB0-DsXcX3Ekr7KPKqEj-5rq5Yyd3FYYdFj35hlfDGQd8oQkuFFDIwNQ9fvelvgSMlSUPAX1bv794eQ8WDQQVGQlYwBm9FR15Lj6oDkPSFeYCRVVjewedN9T80bifzjWMHkcrZEELVkgFB2uuhYDEJbjtTe-LrsRcb-TQ)
-10. [bratby.law](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXLdHA6Xe9Vlgt8eDzYREBxdb1TzufVWONa3uHq5ORdkfQL8zkvPRGni0M3tv5QyaZqzouYwaMSXErYvWJE-bRxZl2a-aqAqMrVc-YbJ1K9Vz-pTttoSTZO1n-2njYzsOmkWv3v1hnzSnnUVsG6zdVzY27z1AWTQ==)
-11. [crossborderdataforum.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGA1TCTT6lwbmACdAv5QNgMPo8y6Aeb6N9m44tj7rzbg_ESe_GGVdSpLedUQNDvwC07EfYcoe5qyyd1vyz_rC3FQNHDpePvW1VK6MnZiSr19GOUaWtRoZlwJvxg0MjJitmg10jlsNlFKCnsgjtdw_hsnUA6eBbyEPTuppc68u8v-OM1XLUqH-Q-rWUPCj7TXf4u2siKwUig_QocA14NzqB-XBdh0U0dM1RsTXvCN4e-tvKNXhA=)
-12. [wsgr.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiYZR_GnVnNsa-ufsNvm4QYTaZa3EtezZE7LuQVgE-_tdvt6i0esAip-WqQoMgLdQhYPatH4Hi95SxomjJywq47lVNl6EZoVE_G85x3uOG4LLUbsaj1mEawrg9LYeJA7WRb2zTcbsvWDWcUNXZmA466S9DxAKGJJZ6KcvIP_NSbS_w_AeV1L5AkvgjgKlOpJ19Re0xFMa3wzE_0ciEuWcynA==)
-13. [bakerbotts.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHM9i0W79b86qflnCaHsDMs_ngD_Z1-TXfzxjLolfEBVx1LZCDJnCVfUnJR8yrrZ0thg9ScCfJFlAL5S73gGTHxM_24I5sup4uiRMTxZoNee3tzTkbKuZEdHZ-jDnwL5yx-sBQpyKwTc1WxiQTn4HCp_80t3vJ4YEv1e9jsVUnHWfjCgvrUa1vgoyh69BHVlrwWjkV1ar6P)
-14. [andersonkill.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENZfaJlR6MQ2uNFPMMVeYTQiJRm8rdid_htKnTp2YG_msrTBeZheRFXwb4TDVW6QVxQpGoVWTMoSHFrgN0zLqosXzZG4FNsAZRrZQzbSuATqyn4OyxxsRSzmXK6Sa6-lpiBClMcxhFjNxdQUQgnI53PsUYjSs63U5tahI7ih0es0Jvf5MuqxbR3F1EBg7zyMgsoi2KAy7kCSo=)
-15. [copyrightlaws.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9Vi9vKLRrf1GlNxY6Ou5VLvBbqNpsLpCRmXIatV498oBVFYtqJjFwnjGnFXh0a0epmBiWbRhp7vhrJtIT-w63SzzMEC6oTxULxHeYGP7MnFSqSOXdV0jhYNqqOnbIhI3kbK_I9mVwsT1IpXhPwxp7a94hy75FK4oj-gLyQq10elycLRUJAntwjQkKDp9fRA==)
-16. [retailconsumerproductslaw.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHh_Z8s7VJrhzJgFOxvEoXrgCbyznv9SsHgmo5OxlzBzHy9-ZGBEVZopsGLFCHeu2RROvNuaFIY4dZE5jOsJUHsWRnBVv5tDqV9DvqyUBZP60T3IRDgHAzAD9aXA3nFp9Rs0GCQqWQNiOPnBe2c9B3k7UEJjFV_W5JaQag6aItrbSmbJXmhykE4wVlVoI3bMA==)
+1. [wolterskluwer.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECxTJtK3uRPPW9Qw1GuaueHhqmWsT5AQWoD_ptnqxJO7U6P3SJF_kbm9h_rP0TJEizqaURedIgd2e7deRDp6GhfdeLMusDKS1QaKpjPFNzpRlYF8DmOPnGgCrhm5lle57Y1X1JUwUfV6BoSUAUWSeqztJaLNic18pgnyKoc2H7Zwp5U1FG295F5dV1Pq08xbyKKElgLxyJm5W3oJHlDeOU)
+2. [aoshearman.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyyorHbEdYIp1-Eux0DxQVqcVTY-tEHsBleWgGxUrmSgvSlbDcHE2R0x8fmstl8dr5sG2PwhNiIZbZCWatupqNMqiwCJHzxLyEaDzqrsI0V0HLF5mIKwXduzOhBATNjx5b1_jsO54fuhFD0Jzq5rjg1fZxrKk2v69_wP_8yhzJFz5uqEbQ__VvHnYTUR3Qdml8Er32yuCLx5flI5I8OTNi)
+3. [www.gov.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZeieZFSB0QYHEf-46iKtCLuj_8sgwzMDXt0aSK-ljo467yMqwE305rCsuRqC0eAgfdIsuk9Zde4dm7TrM9zMGKzW8VzWpKMgMw4dFKhZJKDl5rROpS-ly7kC1-doRGk6D6M_1x9BkTOa_05A4qFWVwOIICsLLqxO4O7XsWuOUpWNBgOaWiirgAUaa6V1VuRO8waTYp4YLNuz-ZaqsYDhdMhBcNnU8Y2z1s0JjG7OZTQPO6gtDefZVQoLSe5rmCA6VzQTOmS4jNqCdzKVBVvrzVmx2_l-NAdZfTCMf)
+4. [osborneclarke.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG21Aalk-WCy7h-0ZrOqPgmHv03M0_pYlRLHkur2UXRc33geY0j-baTSJz-tJHAzbK25vSN_H88zIrRyH-RZ_4L-GLHuegSsw7253jysA1JOSWZRVxM9RwXuKV7xqew7g5X91KRGxoT5bS_WIKb88bnuhy2AM4PjkcH0BaPygGfTmz5wQmGR7l7WjZ6cUvMTH-ZkWuVIGXT)
+5. [bratby.law](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5RiVR1C9DXaK5Zh85jMhSPmww3vXOYyT6d7s6mj5Dxmm8hXAIak6PHr9vfTmWkPgJihlADMoWe7B5cmXMDJ0I90kks2Ken7OcidY_pQfkIih1CUIh8QLDOPs52ESdugFLTM698kNsz2I8B74YgmFhrDo5axMNXQ==)
+6. [europa.eu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa-dWf9r35Rt1Y5YDg8HPPyra69dc0Aa4V5qzSDLgRd_WQZIeaeE7L-Vro2pCA8HMet7T9KC92TasAKNRT3HsgeAnmjBXTeyNxFds1ps36wm3Jo2OBb3TskQ47exN9pGGVNJkr1utAK4O6ciZh1E--i7e6m1XrEyk1s9heugKYYA==)
+7. [jdsupra.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1gH5IM__YN0mJjoOHicKmLB3TQCHK38CtCi-4E0y2zVWHQb2qTUkXZHH53qPMNz70uLCt0tzCcA-A4pbXVvC0_It7BmDC8nyiqi0M5hUJRGTPFhHPKRKClaSlwdMdoFp6DreIrq175_MC1E6YopGfjc503H17JN6bZajK_s0xNJs8jFbxQ5UfKjQ=)
+8. [crossborderdataforum.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHi5X1iDr7GenaaNCx5-URkho41tiM6nnPXRDVgJNCgV4MzBB9OuYX6YO14heM_-uX50xADzDz7u8phqnvr_edcV7NRV0Ff_I6vxi5QAxj5yrSQLe2s6SILOBDuVIvSLIRtM4x_1Qga2Qf8JdW8HyHgAL0bd03RU44t3QKxdLU6ROwrcEM4xS1bnnoQHJMlNuJvRm1XeupwAZUReGnM5CW97TJ5pZix_G4ZgEd_ZU-30Qro2Uo=)
+9. [wsgr.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnUfUIscqbfkqzV1FTMCL8oWen0m6COPcDfjpyyB8Qowt1sSFxuee8XBcQLGnypx6D8fIhR0thLB7jZMPK3loKSek-nSieTTursah8IdKOu1sJZOmSXIEYAPW9juHV3U4fk3upca0cSvvaCfhirodigH5oWQWnlF1PwgJuBekVAKExkI1gxVweDpS_CzYRqR0M9sdgKg1E3SMfj3zC6mTv5w==)
+10. [alston.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERGXVjlrb1g2846gY0NYL1MFgkF_PqaSOf4ZmW0ei8CTaeeoNFkzwYX69HdT1D_dpM_6YvaVrPb19hmbfI4px1qO4n2-_doc_NgbE3G3JRdR4QwPrUopxLkZP9m56TUFNLDhWikwhMyLMjRgEo3hbYHsKyyS345j0W1tBSbV2eMJTQc9bTjVJzed4=)
+11. [bakerbotts.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuBfAsFIFBZ6WBqg5NsfmHIoJXkODmEQiqebxMwf0GGPJ9FwU7CUduYjc4bXVZIzO5w-5h6qCen70zM5W9TUpCbIIenDNzVIv5ECcgg1-GzAwRBO-hImOFBbN4PxBpXgZmleiIxvaYrrTSC0wVEbLa4uUroSS7D0lTj7gxjBnmIBKBlr8sqcwdgm6tEW68ooHY_eobOY1G)
+12. [retailconsumerproductslaw.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDYXwHC3chpBKGWi-pQuoSsQrLMDzPakLGHaIR1rgVnCx03cN_50tJGcaCn2T9Y1hmSNu4EZVeVUdjMJ05Is71ZB62FHpo4PWnlL9S9ywsxyNtwC_fIC5AH0dz6a2rsjXzXanlYXJ3UZChlG3AcNo6mRqcsjU7YscldMFKCJAYRxi_m0vIEXEazgoFsIL1bw==)
```

</details>
