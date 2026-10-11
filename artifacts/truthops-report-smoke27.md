# TruthOps report — case `smoke27`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: FALSE**
**Recommended posture:** Deny with evidence

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| claim | **mostly_false** | 0.97 → 0.97 |

## Key messages

- Claim 'The United States spent more money than ever on the Panama Canal project and los...': MOSTLY FALSE (35/100).
-   Notes: Smoke test 27: community-submitted claim.

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-claim-1` [fixture] supports `claim` — score 0.76 (reliability 0.95 × relevance 0.8) | primary=True | SYNTHETIC fixture
- `ev-claim-2` [fixture] contradicts `claim` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-claim-alex-3` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: FactChecking Trump's Inaugural Address | https://www.factcheck.org/2025/01/factchecking-trumps-inaugural-address/
- `ev-claim-alex-4` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: overstating the real number of U.S.-born workers who died during ... | https://www.facebook.com/democracynow/posts/trump-claimed-38000-americans-were-killed-building-the-panama-canal-overstating-/1067757928492853/

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
