# TruthOps report — case `smoke1`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: FALSE**
**Recommended posture:** Deny with evidence

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| claim | **pants_on_fire** | 0.97 → 0.97 |

## Key messages

- Claim 'Photographs circulating online show New York City Mayor Zohran Mamdani posing al...': PANTS ON FIRE (3/100).
-   Notes: Smoke test 1: AI-generated photo fabrication.

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-claim-1` [fixture] contradicts `claim` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture

## Contrarian challenges

- **claim**: agreed=True; confidence 0.97 → 0.97

## Photo verification (live)

Two-phase chain: C2PA provenance → Sightengine AI detection.

| Image | C2PA | Sightengine AI probability | Assessment |
|---|---|---|---|
| img1.jpg | No provenance | 18% | Likely authentic or edited (not fully AI-generated) |
| img2.jpg | No provenance | 99% | AI-generated |
| img3.jpg | No provenance | 99% | AI-generated |
| img4.jpg | No provenance | 99% | AI-generated |

**Interpretation:** 3 of 4 circulating images are AI-generated with 99% confidence. img1 scores low on full-generation detection (18%) — consistent with a real photo that was edited/composited, or a different generator. Combined with the absence of C2PA provenance on all four, the photographic evidence supports the PANTS_ON_FIRE verdict.

**API spend (photo verification):** 4 C2PA checks ($0.00) + 4 Sightengine scans ($0.00, free tier: 20 ops used of 2,000/mo)

**Neatlogs trace:** `aa3d1547e87988e35baf6403c534e18f`
