# TruthOps report — case `smoke28`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: TRUE**
**Recommended posture:** Affirm with evidence
**Neatlogs trace ID:** `45020f72b2d5877da7dfe2e18f166149`

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| claim | **true** | 0.97 → 0.97 |

## Key messages

- Claim 'Trump won the 2024 U.S. popular vote by millions.': TRUE (99/100).
-   Notes: Smoke test 28: community-submitted claim.

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-claim-1` [fixture] supports `claim` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-claim-alex-2` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Trump Won the Popular Vote, Contrary to Claims Online | https://www.factcheck.org/2024/11/trump-won-the-popular-vote-contrary-to-claims-online/
- `ev-claim-alex-3` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Popular vote: How Trump's 77.3 million ranks among past ... | https://www.livenowfox.com/news/presidents-most-popular-votes-trump-2024

## Contrarian challenges

- **claim**: agreed=True; confidence 0.97 → 0.97

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
