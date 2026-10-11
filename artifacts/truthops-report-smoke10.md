# TruthOps report — case `smoke10`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: FALSE**
**Recommended posture:** Deny with evidence

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| decline_was_40pct | **false** | 0.97 → 0.97 |

## Key messages

- Claim 'The enterprise customer decline was 93%.': FALSE (10/100).
-   Notes: Atomic fact: is the specific magnitude correct?

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-decline_was_40pct-1` [fixture] contradicts `decline_was_40pct` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-decline_was_40pct-2` [fixture] supports `decline_was_40pct` — score 0.2 (reliability 0.4 × relevance 0.5) | primary=False | SYNTHETIC fixture

## Contrarian challenges

- **decline_was_40pct**: agreed=True; confidence 0.97 → 0.97
