# TruthOps report — case `smoke7`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: TRUE**
**Recommended posture:** Affirm with evidence

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| claim | **mostly_true** | 0.94 → 0.94 |

## Key messages

- Claim 'Immigration agents 'are not getting the traditional five months training. … The ...': MOSTLY TRUE (88/100).
-   Notes: Smoke test 7: mostly true; off-by-one (47 vs 48 days).

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-claim-1` [fixture] supports `claim` — score 0.88 (reliability 0.88 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-claim-alex-2` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: DHS Sets the Record Straight About ICE Law Enforcement Training ... | https://www.dhs.gov/news/2026/02/23/dhs-sets-record-straight-about-ice-law-enforcement-training-debunks-falsehoods
- `ev-claim-alex-3` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: ICE officer training cut to only 47 days? You can't make this stuff up… | https://www.facebook.com/MarkWarnerVa/videos/ice-officer-training-cut-to-only-47-days-you-cant-make-this-stuff-up/1688243962582661/

## Contrarian challenges

- **claim**: agreed=True; confidence 0.94 → 0.94

## Audit trail

- [sniff] proceed=True — passed sniff test — coherent allegation, full pipeline warranted (backend=clef-flash)
- Decomposed into 1 atomic claims: ['claim']
- [director] claim: next action = gather — no evidence yet — gather before any judgment
- [director] claim: next action = evaluate — evidence phase complete — evaluate the claim
- [director] claim: next action = escalate — initial verdict reached — escalate to contrarian for adversarial review
- Response plan built: TRUE. All external actions BLOCKED pending approval.
- External action 'publish' BLOCKED — awaiting human approval.
- External action 'post' BLOCKED — awaiting human approval.
- External action 'notify' BLOCKED — awaiting human approval.

## Adapter status


**API spend:** $0.00 — no paid calls this run
