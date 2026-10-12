# TruthOps Business Plan (cfo.ai export)

**Source:** cfo.ai Business Plan workspace (Trilby Media)
**Workspace:** https://app.cfo.ai/trilby-media-5c5e1736/chat/9fc4571f-9158-4cc9-bdc1-868d10f2c6d3 (requires sign-in)
**Exported:** Oct 11, 2026 (recomputed — see Figure History below)
**Note:** The cfo.ai workspace went through multiple revisions Oct 10–11. The figures below are recomputed from the latest cfo.ai cost build with the inapplicable LLM line item removed (the pipeline is rule-based — no LLM in the reasoning path). See [RECONCILIATION.md](../thread-assets/cfo-broll/RECONCILIATION.md) for the raw iteration history.

## Pricing Tiers

| Tier | Monthly Price | Included Investigations | Overage |
|------|---------------|------------------------|---------|
| Starter | $499 | 25 | $12/investigation |
| Professional | $1,499 | 150 | $12/investigation |
| Enterprise | $3,999 | 400 | $12/investigation |

## Unit Economics (recomputed: $0.494/investigation pipeline, $0.523 effective)

| Tier | Variable cost at full usage | Gross profit / account / mo | Gross margin |
|------|----------------------------|----------------------------|--------------|
| Starter | $13.06/mo (25 × $0.5226) | $485.94 | **97.38%** |
| Professional | $78.39/mo (150 × $0.5226) | $1,420.61 | **94.77%** |
| Enterprise | $209.03/mo (400 × $0.5226) | $3,789.97 | **94.77%** |

Math: ($499 − $13.06)/$499 = 97.38%; ($1,499 − $78.39)/$1,499 = 94.77%; ($3,999 − $209.03)/$3,999 = 94.77%.
Each $12 overage earns **$11.48** gross profit before payment fees.

| Metric | Value |
|--------|-------|
| Pipeline cost per investigation | **$0.49** (recomputed — source of truth; effective $0.52 with pre-screen) |
| Observed API spend (demo runs) | $0.00 |
| Fixed burn | $3,375/month |

## Cost Breakdown ($0.494/investigation)

From the Oct 11 cfo.ai cost build, **with the $0.50 "LLM inference" line removed** (stale assumption — the pipeline calls no LLM in its reasoning path):
- GPTZero AI-text screening (secondary sources): $0.430
- Firecrawl web search + scraping (primary sources): $0.064
- **Pipeline subtotal: $0.494**
- Cloudflare Clef-flash sniff test gate: $0.020 per allegation ÷ 70% acceptance = **$0.0286 per billable investigation**
- **Effective cost per billable investigation: $0.5226**
- Sightengine image forensics: within free tier at modeled volumes; C2PA provenance checks run locally (free)

## Revenue Model

SaaS subscriptions with investigation-based tiers. Overage at $12/investigation ($11.48 gross profit each) provides expansion revenue. Target: trust & safety teams, newsrooms, platform integrity groups investigating high-risk misinformation claims.

Per-account monthly revenue at full usage: $499 / $1,499 / $3,999. cfo.ai did not model a specific tier mix — the runway scenarios below use its customer-ramp forecast, not a fixed mix.

## Runway (base case)

- **Horizon:** 18 months (Oct 2026 – Mar 2028)
- **Minimum cash:** $3,718 (Feb 2027)
- **Ending cash:** $97,612 (Mar 2028)
- Fixed burn $3,375/mo. Conservative scenario needs ~$2,844 additional coverage at the trough. Runway figures come from the cfo.ai model iterations and vary by scenario — see Figure History. Lower unit costs in this recomputation improve all scenarios vs. the $1.08 basis.

## Key Assumptions

1. Pipeline cost stays near $0.49 as volume scales (Firecrawl + detector API pricing stable)
2. Fixed burn of $3,375/mo covers infrastructure (SpaceFast hosting, domain, tooling)
3. No headcount modeled in v1 — founder-operated
4. 18-month horizon assumes steady customer ramp; enterprise tier drives margin expansion
5. Sightengine stays within free-tier operations at modeled volumes (30% photo incidence, C2PA bypass where available)

## Figure History (why older exports disagree)

| Iteration | When | Cost basis | Margins (S / P / E) | Status |
|-----------|------|-----------|---------------------|--------|
| Early | Oct 10 | Unstated blended basis | 88.01% / 88.17% / 90.07% | Superseded — basis never documented |
| Workbook import | Oct 10 eve | $1.084 (incl. $0.52 GPTZero) | 94.57% / 89.15% / 89.16% | Superseded by recomputation below |
| cfo.ai morning revision | Oct 11 | $0.994 ($0.50 LLM + $0.064 Firecrawl + $0.43 GPTZero) | 94.88% / 89.77% / 89.77% | Superseded — contained stale LLM line |
| **Recomputed (this export)** | Oct 11 eve | **$0.494** ($0.064 + $0.43, LLM removed) | **97.38% / 94.77% / 94.77%** | **Current** |

**What changed in this recomputation:** the Oct 11 cfo.ai build included a $0.50/investigation "LLM inference" line item. TruthOps calls no LLM in its reasoning path (see README Limitations), so that line is removed. Everything else is carried over unchanged from the latest cfo.ai state.

**Honesty note:** cfo.ai is an iterative planning tool, not an audited financial statement. Margins above are modeled gross margins at full tier usage. No independent verification of vendor pricing was performed beyond the pipeline's observed $0.00 demo spend.
