# TruthOps report — case `smoke22`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: FALSE**
**Recommended posture:** Deny with evidence

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| claim | **mostly_false** | 0.97 → 0.97 |

## Key messages

- Claim 'More Americans are working in the United States now than at any point in the cou...': MOSTLY FALSE (35/100).
-   Notes: Smoke test 22: community-submitted claim.

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-claim-1` [fixture] supports `claim` — score 0.76 (reliability 0.95 × relevance 0.8) | primary=True | SYNTHETIC fixture
- `ev-claim-2` [fixture] contradicts `claim` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-claim-alex-3` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: POTUS: “More Americans are working today in our country than at any ... | https://www.facebook.com/departmentoflabor/videos/potus-more-americans-are-working-today-in-our-country-than-at-any-time-by-far-in/4628794894067274/
- `ev-claim-alex-4` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Trump's Pointless Job Boast - FactCheck.org | https://www.factcheck.org/2019/01/trumps-pointless-job-boast/

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
