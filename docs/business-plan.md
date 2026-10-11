# TruthOps Business Plan (cfo.ai export)

**Source:** cfo.ai Business Plan workspace (Trilby Media)
**Workspace:** https://app.cfo.ai/trilby-media-5c5e1736/chat/9fc4571f-9158-4cc9-bdc1-868d10f2c6d3 (requires sign-in)
**Exported:** Oct 11, 2026
**Note:** The cfo.ai workspace went through multiple revisions during the Oct 10 session. Figures below are the stable set reconciled from screenshots. See [RECONCILIATION.md](../thread-assets/cfo-broll/RECONCILIATION.md) for the full iteration history and conflicting figures.

## Pricing Tiers

| Tier | Monthly Price | Included Investigations | Overage |
|------|---------------|------------------------|---------|
| Starter | $499 | 25 | $12/investigation |
| Professional | $1,499 | 150 | $12/investigation |
| Enterprise | $3,999 | 400 | $12/investigation |

## Unit Economics

| Metric | Value |
|--------|-------|
| Pipeline cost per investigation | **$1.08** (modeled — source of truth) |
| Observed API spend (demo runs) | $0.00 |
| Tier gross margins | 88.01% / 88.17% / 90.07% |
| Fixed burn | $3,375/month |

## Runway

- **Horizon:** 18 months (Oct 2026 – Mar 2028)
- **Model:** Iterative financial planning in cfo.ai; runway figures varied across revisions (see RECONCILIATION.md). Stable inputs: tier pricing above, $3,375/mo fixed burn, $1.08/investigation pipeline cost.

## Cost Breakdown ($1.08/investigation)

The $1.08 modeled cost covers:
- Cloudflare Clef-flash sniff test gate (~$0.02)
- Firecrawl web search + scraping (Alexandria primary sources)
- GPTZero AI-text screening (secondary sources)
- Sightengine image forensics (photo claims)
- neatlogs trace export

## Revenue Model

SaaS subscriptions with investigation-based tiers. Overage at $12/investigation provides expansion revenue. Target: trust & safety teams, newsrooms, platform integrity groups investigating high-risk misinformation claims.

## Key Assumptions

1. Pipeline cost stays near $1.08 as volume scales (Firecrawl + detector API pricing stable)
2. Fixed burn of $3,375/mo covers infrastructure (SpaceFast hosting, domain, tooling)
3. No headcount modeled in v1 — founder-operated
4. 18-month horizon assumes steady tier mix; enterprise tier drives margin expansion to 90%+
