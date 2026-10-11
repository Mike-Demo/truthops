# TruthOps report — case `smoke8`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: TRUE**
**Recommended posture:** Affirm with evidence

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| claim | **mostly_true** | 0.93 → 0.93 |

## Key messages

- Claim 'Florida is '49th in avoidable hospital costs.'': MOSTLY TRUE (90/100).
-   Notes: Smoke test 8: mostly true; correct rank, slightly narrower framing than metric.

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-claim-1` [fixture] supports `claim` — score 0.86 (reliability 0.86 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-claim-alex-2` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Florida FY 2025–26 Budget Summary: Health | https://www.floridapolicy.org/posts/health
- `ev-claim-alex-3` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Florida - Commonwealth Fund | https://www.commonwealthfund.org/datacenter/florida

## Contrarian challenges

- **claim**: agreed=True; confidence 0.93 → 0.93

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
