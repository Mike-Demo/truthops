# TruthOps report — case `smoke3`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: FALSE**
**Recommended posture:** Deny with evidence
**Neatlogs trace ID:** `83c016c983bb2adbb4b82bf989df9ff9`

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| claim | **mostly_false** | 0.95 → 0.95 |

## Key messages

- Claim 'President Trump ended eight wars.': MOSTLY FALSE (34/100).
-   Notes: Smoke test 3: kernel of truth, unsupportable number.

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-claim-1` [fixture] supports `claim` — score 0.64 (reliability 0.8 × relevance 0.8) | primary=True | SYNTHETIC fixture
- `ev-claim-2` [fixture] contradicts `claim` — score 0.9 (reliability 0.9 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-claim-alex-3` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: How many wars has President Trump ended? - BBC | https://www.bbc.com/news/articles/c5y3599gx4qo
- `ev-claim-alex-4` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: FACT FOCUS: Trump says he's ended eight wars. His numbers are off | https://apnews.com/article/trump-wars-fact-focus-a75eca5184bd45acbf9f46ff9822514f

## Contrarian challenges

- **claim**: agreed=True; confidence 0.95 → 0.95

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
