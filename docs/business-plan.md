# TruthOps Business Plan (cfo.ai export)

**Source:** cfo.ai Business Plan workspace (Trilby Media)
**Workspace:** https://app.cfo.ai/trilby-media-5c5e1736/chat/9fc4571f-9158-4cc9-bdc1-868d10f2c6d3 (requires sign-in)
**Exported:** Oct 11, 2026 (reconciled — see Figure History below)
**Note:** The cfo.ai workspace went through multiple revisions Oct 10–11. The figures below are the internally consistent set from the workbook-backed iteration ($1.084/investigation). See [RECONCILIATION.md](../thread-assets/cfo-broll/RECONCILIATION.md) for the full iteration history.

## Pricing Tiers

| Tier | Monthly Price | Included Investigations | Overage |
|------|---------------|------------------------|---------|
| Starter | $499 | 25 | $12/investigation |
| Professional | $1,499 | 150 | $12/investigation |
| Enterprise | $3,999 | 400 | $12/investigation |

## Unit Economics (workbook basis: $1.084/investigation, shown as $1.08)

| Tier | Variable cost at full usage | Gross profit / account / mo | Gross margin |
|------|----------------------------|----------------------------|--------------|
| Starter | $27.10/mo (25 × $1.084) | $471.90 | **94.57%** |
| Professional | $162.60/mo (150 × $1.084) | $1,336.40 | **89.15%** |
| Enterprise | $433.60/mo (400 × $1.084) | $3,565.40 | **89.16%** |

Math: ($499 − $27.10)/$499 = 94.57%; ($1,499 − $162.60)/$1,499 = 89.15%; ($3,999 − $433.60)/$3,999 = 89.16%.
Each $12 overage earns **$10.92** gross profit before payment fees.

| Metric | Value |
|--------|-------|
| Pipeline cost per investigation | **$1.08** (modeled — source of truth; workbook exact: $1.084) |
| Observed API spend (demo runs) | $0.00 |
| Fixed burn | $3,375/month |

## Cost Breakdown ($1.084/investigation, workbook basis)

Per the Oct 10 workbook import (cfo.ai screenshot, shot12):
- Blended GPTZero screening: ~$0.52
- Firecrawl web search + scraping (primary sources): remainder
- Cloudflare Clef-flash sniff test gate: ~$0.02
- Sightengine image forensics + neatlogs trace export: remainder

## Revenue Model

SaaS subscriptions with investigation-based tiers. Overage at $12/investigation ($10.92 gross profit each) provides expansion revenue. Target: trust & safety teams, newsrooms, platform integrity groups investigating high-risk misinformation claims.

Per-account monthly revenue at full usage: $499 / $1,499 / $3,999. cfo.ai did not model a specific tier mix — the runway scenarios below use its customer-ramp forecast, not a fixed mix.

## Runway (base case, $1.08 iteration)

- **Horizon:** 18 months (Oct 2026 – Mar 2028)
- **Minimum cash:** $3,718 (Feb 2027)
- **Ending cash:** $97,612 (Mar 2028)
- Fixed burn $3,375/mo. Conservative scenario needs ~$2,844 additional coverage at the trough. Figures varied across cfo.ai revisions — see Figure History.

## Key Assumptions

1. Pipeline cost stays near $1.08 as volume scales (Firecrawl + detector API pricing stable)
2. Fixed burn of $3,375/mo covers infrastructure (SpaceFast hosting, domain, tooling)
3. No headcount modeled in v1 — founder-operated
4. 18-month horizon assumes steady customer ramp; enterprise tier drives margin expansion

## Figure History (why older exports disagree)

| Iteration | When | Cost basis | Margins (S / P / E) | Status |
|-----------|------|-----------|---------------------|--------|
| Early | Oct 10 | Unstated blended basis | 88.01% / 88.17% / 90.07% | Superseded — basis never documented |
| Workbook import | Oct 10 eve | **$1.084** (incl. $0.52 GPTZero) | 94.57% / 89.15% / 89.16% | **Current headline basis** — used in README, site, video |
| Morning revision | Oct 11 | $0.994 ($0.50 LLM + $0.064 Firecrawl + $0.43 GPTZero) | 94.88% / 89.77% / 89.77% | Latest cfo.ai state — see caveat |

**Caveat on the Oct 11 revision:** its $0.50 "LLM inference cost per investigation" line item does not apply — the TruthOps pipeline is rule-based with no LLM in the reasoning path (see README Limitations). That line is a stale modeling assumption, not a real cost. Excluding it, the Oct 11 variable cost would be ~$0.49/investigation. The $1.08 workbook basis remains the cited figure until the model is re-run without the LLM line.

**Honesty note:** cfo.ai is an iterative planning tool, not an audited financial statement. Margins above are modeled gross margins at full tier usage. No independent verification of vendor pricing was performed beyond the pipeline's observed $0.00 demo spend.
