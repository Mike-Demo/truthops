# TruthOps report — case `smoke25`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: FALSE**
**Recommended posture:** Deny with evidence
**Neatlogs trace ID:** `3ee64b16f26f58df39e35f2d7c20b1cb`

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| claim | **mostly_false** | 0.97 → 0.97 |

## Key messages

- Claim 'The United States has the largest amount of oil and gas of any country on Earth.': MOSTLY FALSE (35/100).
-   Notes: Smoke test 25: community-submitted claim.

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-claim-1` [fixture] supports `claim` — score 0.76 (reliability 0.95 × relevance 0.8) | primary=True | SYNTHETIC fixture
- `ev-claim-2` [fixture] contradicts `claim` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-claim-alex-3` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: U.S. Holds Most Recoverable Oil Reserves | https://www.aogr.com/web-exclusives/exclusive-story/u.s.-holds-most-recoverable-oil-reserves
- `ev-claim-alex-4` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Oil Reserves by Country - Worldometer | https://www.worldometers.info/oil/oil-reserves-by-country/

## Contrarian challenges

- **claim**: agreed=True; confidence 0.97 → 0.97

## Audit trail

- [sniff] proceed=True — passed sniff test — coherent allegation, full pipeline warranted (backend=clef-flash)
- Decomposed into 1 atomic claims: ['claim']
- [director] claim: next action = gather — no evidence yet — gather before any judgment
- [director] claim: next action = evaluate — evidence phase complete — evaluate the claim
- [director] claim: next action = escalate — initial verdict reached — escalate to contrarian for adversarial review
- Response plan built: FALSE. All external actions BLOCKED pending approval.
- External action 'publish' BLOCKED — awaiting human approval.
- External action 'post' BLOCKED — awaiting human approval.
- External action 'notify' BLOCKED — awaiting human approval.

## Adapter status


**API spend:** $0.00 — no paid calls this run
