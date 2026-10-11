# TruthOps report — case `smoke1`

> LIVE run — neatHack 2026. Evidence is fixture-backed for benchmark comparability; live adapters enriched where available (see JSON report for per-adapter status and spend).

**Overall characterization: FALSE**
**Recommended posture:** Deny with evidence
**Neatlogs trace ID:** `unavailable`

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| claim | **pants_on_fire** | 0.99 → 0.99 |

## Key messages

- Claim 'Photographs circulating online show New York City Mayor Zohran Mamdani posing al...': PANTS ON FIRE (1/100).
-   Notes: Smoke test 1: AI-generated photo fabrication.

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-claim-1` [fixture] contradicts `claim` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-claim-alex-2` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Images of NYC Mayor Zohran Mamdani with Jeffrey Epstein are AI ... | https://abc7ny.com/post/images-nyc-mayor-zohran-mamdani-jeffrey-epstein-are-ai-generated-heres-how-know/18541733/
- `ev-claim-alex-3` [alexandria] neutral `claim` — score 0.42 (reliability 0.7 × relevance 0.6) | primary=True | Alexandria: Images of NYC Mayor Mamdani with Jeffrey Epstein are AI-generated ... | https://www.cbsnews.com/newyork/news/zohran-mamdani-jeffrey-epstein-ai-images-nyc/
- `ev-claim-c2pa-1` [c2pa] neutral `claim` — score 0.4 (reliability 0.5 × relevance 0.8) | primary=False | C2PA provenance: fixture://smoke1/images/img1.jpg
- `ev-claim-sightengine-1` [sightengine] contradicts `claim` — score 0.765 (reliability 0.85 × relevance 0.9) | primary=True | Sightengine AI detection: fixture://smoke1/images/img1.jpg

## Contrarian challenges

- **claim**: agreed=True; confidence 0.99 → 0.99

## Audit trail

- [sniff] proceed=True — passed sniff test — coherent allegation, full pipeline warranted (backend=heuristic)
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
