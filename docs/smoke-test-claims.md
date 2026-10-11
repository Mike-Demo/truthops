# TruthOps Smoke Test: 5-Claim Calibration Set (0 → 100)

**Prepared:** October 10, 2026 · **Purpose:** Smoke-test TruthOps' 0–100 trust scoring across the full truth spectrum
**Method note:** Alexandria has no fact-check provider capability (verified via 5 free discovery queries: "fact check verified claims," "news fact checking," "AP news articles," "politifact factcheck.org claim ratings," "associated press" — 0 relevant capabilities; only unrelated news providers returned). No paid Alexandria calls were made. Claims below were gathered via standard Firecrawl web search (7 searches × 2 credits = 14 credits) plus 2 page scrapes against AP/FactCheck.org, with verdicts taken from the publishers' own reporting.

**How to use:** Feed each claim to TruthOps blind. Expected band = the score a well-calibrated system should produce. A healthy system lands all 5 inside their bands and orders them 1 < 2, 4 < 3 < 5 (Claims 2 and 4 are both low-end; Claim 4 was corrected Oct 10 — see below).

---

## Claim 1 — Expected: 0–5 (False)

**Claim:** "Photographs circulating online show New York City Mayor Zohran Mamdani posing alongside Jeffrey Epstein."

**AP verdict:** False — the images are AI-generated. AP's fact check walks through how they know (generative-AI artifacts and provenance analysis).

**Source:** AP Fact Check — "Images of NYC Mayor Mamdani with Jeffrey Epstein are AI-generated. Here's how we know"
https://apnews.com/video/images-of-nyc-mayor-mamdani-with-jeffrey-epstein

**Why this tests the floor:** Fabricated visual evidence with a definitive technical debunk. A score above ~10 here means the system is overweighting virality or underweighting forensic verdicts.

---

## Claim 2 — Expected: 10–20 (False)

**Claim:** "President Trump initiated an internal audit of the Social Security Administration."

**AP verdict:** False — AP's Not Real News desk: "A story posted by borntobebright.com falsely claims that Trump initiated an internal audit of the Social Security Administration."

**Source:** AP — "NOT REAL NEWS: A look at what didn't happen this week"
https://apnews.com/general-news-television-d75bf1c487c54e52bd532323f9d6d293

**Why this tests low-end discrimination:** Single-source fabrication (one junk site) vs. Claim 1's multi-signal forensic debunk. Should score slightly above Claim 1 only if the system credits "no corroboration anywhere" less harshly than positive proof of fabrication.

---

## Claim 3 — Expected: 30–45 (Misleading)

**Claim:** "President Trump ended eight wars."

**AP verdict:** Listed among "false and misleading claims" in AP's Fact Focus on Trump's 2025 record-review remarks (slug: fact-check-trump-rigged-election-eight-wars-inflation).

**Source:** AP — "Trump highlights familiar false claims as he reviews 2025"
https://apnews.com/article/fact-check-trump-rigged-election-eight-wars-inflation-220f515728383d5205c3748259b2cc0f

**Why this tests the middle:** Kernel of truth (U.S. diplomatic involvement in several 2025 ceasefire efforts) wrapped in an unsupportable quantification ("eight wars ended"). A good system lands mid-band: not 0 (there was real diplomacy), not 70 (the number doesn't survive scrutiny). This is the claim most likely to expose overconfidence in either direction.

---

## Claim 4 — Expected: 10–30 (False — corrected Oct 10, 2026)

**Claim:** "Gasoline is now below $2.30 a gallon in most states." (Trump, 2026 State of the Union)

**FactCheck.org verdict:** False/exaggeration — "Trump continued to exaggerate the decline in gasoline prices." As of Feb. 24, 2026, **no U.S. state** had an average regular-gasoline price below $2.30 (AAA state data; Oklahoma was closest at $2.37). The nationwide average was **$2.94** (EIA, week ending Feb. 23).

**Source:** FactCheck.org — "FactChecking Trump's State of the Union Address" (Feb 2026)
https://www.factcheck.org/2026/02/factchecking-trumps-state-of-the-union-address/

**Correction history (important):** An earlier draft of this calibration doc reconstructed the verdict from a search snippet as "substantially accurate directionally, ~$2.36." That was wrong. The $2.36 figure comes from FactCheck.org's own correction note: *"Correction, Feb. 25: We have corrected Trump's quote about the price of gasoline. He said gasoline is 'now below $2.30 a gallon in most states,' not $2.36."* The full article was pulled and read on Oct 10, 2026 to resolve this. Lesson: never lock a fixture band from a snippet.

**Why this tests low-end nuance:** The claim has a true directional component (prices fell ~5%, about 17 cents, since Trump took office) wrapped around a specific numerical assertion that is false in every state. A good system lands low but not at 0 — it should distinguish "directionally down" from "the stated number is wrong." Scoring above ~50 here means the system is overweighting directional truth and underweighting the specific factual claim being tested. (This is exactly what TruthOps did on Oct 10 — 85/100, MOSTLY_TRUE — a genuine calibration miss, documented honestly in the run report.)

---

## Claim 5 — Expected: 90–100 (True — calibration anchor)

**Claim:** "Zohran Mamdani is the mayor of New York City."

**Verification:** AP's own reporting refers to him as "NYC Mayor Mamdani" (same AP Fact Check desk as Claim 1); consistent across AP election coverage.

**Source:** AP News — apnews.com/ap-fact-check (desk attribution); AP 2026 NYC election reporting.

**Why this tests the ceiling:** A settled, multiply-attested institutional fact. Anything below ~90 here indicates a systemic under-confidence bug (e.g., excessive hedging on all political claims). Note it pairs with Claim 1: the same AP article that debunks the photos affirms the office — a good system should be able to hold both.

---

## Scoring rubric for the smoke test

| Result | Interpretation |
|---|---|
| All 5 in band, correct order | Calibrated — proceed |
| Claims 1–2 above band | Under-skeptical of viral fabrications |
| Claim 3 near 0 or near 80 | Can't handle kernel-of-truth cases (overconfident both ways) |
| Claim 4 above ~50 | Overweighting directional truth vs. the specific factual assertion |
| Claim 5 below 90 | Systemic under-confidence / hedging bug |
| Any two adjacent claims inverted | Ranking failure — investigate evidence weighting |

## Limitations (be honest in the demo)
- AP's fact-check desk is debunk-oriented; it rarely publishes "True" verdicts, which is why Claims 4–5 lean on FactCheck.org and AP's own reporting usage rather than AP verdicts. Tiers are labeled per claim.
- Claim 4's band was corrected Oct 10 after reading the full FactCheck.org article (see correction history above). The original 80–90 band was built from a search snippet and was wrong.
- Alexandria note: re-run discovery before the hackathon demo; provider catalog changes frequently and a fact-check capability may appear.

---

## Supplement (2026-10-10): 3 more 80–90 band claims

All three rated **Mostly True** by PolitiFact — i.e., "accurate but needs clarification or additional information." Each tests whether TruthOps credits substantively-correct claims while docking for the specific imprecision.

### Claim 6 — Expected: 80–90 (Mostly true)

**Claim:** "President Donald Trump has deported 'over 13,000 Cubans since he has been in office, his first term and his second term.'" (Angie Nixon, Oct 4, 2026, CBS Miami interview)

**PolitiFact verdict:** Mostly True — "The statement is accurate but needs clarification or additional information." Federal data: ~3,400 Cubans deported in Trump's first term. Human Rights Watch estimated ~8,500 more in the second term as of Aug. 5 — totaling close to 12,000, with possibly more since. DHS did not confirm the second-term figure to PolitiFact.

**Source:** PolitiFact (Oct 9, 2026)
https://politifact.com/factchecks/2026/oct/09/angie-nixon/cubans-deportation-immigration-trump-nixon/

**What it tests:** Slight overstatement ("over 13,000" vs ~12,000 best estimate) plus reliance on an NGO estimate where official data is unavailable. A score of 100 ignores both; below 75 treats estimation as deception.

### Claim 7 — Expected: 80–90 (Mostly true)

**Claim:** Immigration agents "are not getting the traditional five months training. … The training for the ICE agents now is 47 days." (Sen. Mark Warner, Jan 11, 2026 interview)

**PolitiFact verdict:** Mostly True — "accurate but needs clarification." ICE acting director Todd Lyons confirmed training was shortened to six days a week for eight weeks = 48 days of training over a 56-day period (vs ~five months traditionally). Warner said 47; the documented figure is 48.

**Source:** PolitiFact (Jan 12, 2026)
https://politifact.com/factchecks/2026/jan/12/mark-warner/ice-training-requirements-trump-minneapolis/

**What it tests:** Off-by-one numerical precision on a substantively correct claim. Ideal calibration: high 80s — the single-day miss should cost a few points, not collapse the score.

### Claim 8 — Expected: 80–90 (Mostly true)

**Claim:** Florida is "49th in avoidable hospital costs." (David Jolly, June 11, 2026 speech)

**PolitiFact verdict:** Mostly True — "accurate but needs some additional information." Matches the Commonwealth Fund's June 2025 analysis ranking Florida 49th of 51 (states + DC) in "avoidable hospital use and cost." Caveat: the category includes data not exclusive to hospitals (e.g., Medicare spending, imaging costs).

**Source:** PolitiFact (June 24, 2026)
https://politifact.com/factchecks/2026/jun/24/david-jolly/david-jolly-florida-hospital-cost-governor-race/

**What it tests:** Correct number, slightly narrower framing than the underlying metric. Distinguishes systems that verify the cited statistic from those that also check whether the statistic means what the speaker implies.
