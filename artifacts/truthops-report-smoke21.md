# TruthOps report — case `smoke21`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: FALSE**
**Recommended posture:** Deny with evidence
**Neatlogs trace ID:** `5ee34705cf67c5abba2defc0df230c7c`

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| decline_was_40pct | **false** | 0.97 → 0.97 |

## Key messages

- Claim 'The enterprise customer decline was 4%.': FALSE (10/100).
-   Notes: Atomic fact: is the specific magnitude correct?

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-decline_was_40pct-1` [fixture] contradicts `decline_was_40pct` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-decline_was_40pct-2` [fixture] supports `decline_was_40pct` — score 0.06 (reliability 0.12 × relevance 0.5) | primary=False | SYNTHETIC fixture | GPTZero: ai (P(ai)=1.0)
- `ev-decline_was_40pct-alex-3` [alexandria] neutral `decline_was_40pct` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Enterprise's outdated technology hinders customer experience | https://www.facebook.com/groups/1351161114904309/posts/6711794188840948/
- `ev-decline_was_40pct-alex-4` [alexandria] neutral `decline_was_40pct` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Enterprise Holdings Helps Clarify Misunderstood 'Loss of Use' Fee | https://www.autorentalnews.com/news/enterprise-holdings-helps-clarify-misunderstood-loss-of-use-fee

## Contrarian challenges

- **decline_was_40pct**: agreed=True; confidence 0.97 → 0.97

## Audit trail

- [sniff] proceed=True — passed sniff test — coherent allegation, full pipeline warranted (backend=clef-flash)
- Decomposed into 1 atomic claims: ['decline_was_40pct']
- [director] decline_was_40pct: next action = gather — no evidence yet — gather before any judgment
- GET fixture://northstar/filing-q3-2026 -> 503 Service Unavailable (SIMULATED). State preserved; will retry.
- Retrying fixture://northstar/filing-q3-2026 after failure: HTTP 503 for fixture://northstar/filing-q3-2026: Service Unavailable (SIMULATED deterministic failure
- [director] decline_was_40pct: next action = evaluate — evidence phase complete — evaluate the claim
- [director] decline_was_40pct: next action = escalate — initial verdict reached — escalate to contrarian for adversarial review
- Response plan built: FALSE. All external actions BLOCKED pending approval.
- External action 'publish' BLOCKED — awaiting human approval.
- External action 'post' BLOCKED — awaiting human approval.
- External action 'notify' BLOCKED — awaiting human approval.

## Adapter status


**API spend:** $0.00 — no paid calls this run
