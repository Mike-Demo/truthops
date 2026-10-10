# TruthOps report — case `northstar`

> SYNTHETIC demo run — neatHack 2026. All fixture data is synthetic; live integrations (Crustdata, Firecrawl) were SIMULATED in this run.

**Overall characterization: MISLEADING**
**Recommended posture:** Correct the record with primary-source evidence

## Claim verdicts

| Claim | Verdict | Confidence (initial → revised) |
|---|---|---|
| incident_occurred | **true** | 0.99 → 0.99 |
| some_customer_decline | **true** | 0.99 → 0.65 |
| decline_was_40pct | **false** | 0.97 → 0.97 |
| executives_knew | **true** | 0.85 → 0.75 |
| deliberate_concealment | **unresolved** | 0.0 → 0.0 |

## Key messages

- A security incident did occur on 2026-07-14 and was disclosed on 2026-07-16 (incident report).
- Enterprise customer decline was 4.2% (2,380 -> 2,280), per the Q3 2026 filing — not 40%.
- The 40% figure circulating online is contradicted by the primary filing.
- No direct evidence of deliberate concealment was found; intent is not asserted.

## Approval gate

External actions: **BLOCKED** — publish / post / notify all blocked pending explicit human approval.

## Evidence (scored)

- `ev-incident_occurred-1` [fixture] supports `incident_occurred` — score 0.9 (reliability 0.9 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-incident_occurred-2` [fixture] supports `incident_occurred` — score 0.2 (reliability 0.4 × relevance 0.5) | primary=False | SYNTHETIC fixture
- `ev-some_customer_decline-1` [fixture] supports `some_customer_decline` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-some_customer_decline-2` [fixture] supports `some_customer_decline` — score 0.56 (reliability 0.7 × relevance 0.8) | primary=False | SYNTHETIC fixture
- `ev-decline_was_40pct-1` [fixture] contradicts `decline_was_40pct` — score 0.95 (reliability 0.95 × relevance 1.0) | primary=True | SYNTHETIC fixture
- `ev-decline_was_40pct-2` [fixture] supports `decline_was_40pct` — score 0.2 (reliability 0.4 × relevance 0.5) | primary=False | SYNTHETIC fixture
- `ev-executives_knew-1` [fixture] supports `executives_knew` — score 0.7 (reliability 0.7 × relevance 1.0) | primary=False | SYNTHETIC fixture

## Contrarian challenges

- **incident_occurred**: agreed=True; confidence 0.99 → 0.99
- **some_customer_decline**: agreed=False; confidence 0.99 → 0.65
  - challenge: The sole primary source (Q3 filing) shows only a 4.2% decline — within normal enterprise churn. The 'supported' verdict leans on an internal memo of simulated provenance plus a small absolute move. Force re-verification: confirm the absolute customer loss and downgrade confidence to reflect the thin margin.
  - re-verification: Re-verified primary filing (Q3 2026): 2,380 -> 2,280 enterprise customers = 100 accounts lost (4.2%). A real decline, but small; the internal memo's provenance is simulated. Verdict stays SUPPORTED; confidence revised down to reflect the thin margin.
- **decline_was_40pct**: agreed=True; confidence 0.97 → 0.97
- **executives_knew**: agreed=False; confidence 0.85 → 0.75
  - challenge: No primary source behind this verdict — only secondary evidence. Confidence is overstated; re-verify against a primary source or downgrade.
  - re-verification: Re-verification confirmed the initial scoring; confidence trimmed for caution.
- **deliberate_concealment**: agreed=False; confidence 0.0 → 0.0
  - challenge: Unresolved is a safe verdict. Challenge: is there really no evidence of intent, or did retrieval miss it? Re-verify with a broader sweep before accepting 'unresolved'.
  - re-verification: Re-verification sweep: no fixture contains direct evidence of intent to deceive. The 40% vs 4.2% gap is a factual error in the allegation; intent is never asserted without evidence. Verdict stays UNRESOLVED.
