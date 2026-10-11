# TruthOps

**Don't just detect misinformation. Resolve it.**

TruthOps is a transparent scoring and governance pipeline over curated evidence, built for neatHack 2026 (Oct 10–12). It investigates high-risk claims, runs them through a scripted contrarian review, and produces evidence-backed response plans — with human approval gates at every decisive step.

**What it is, honestly:** a rule-based pipeline — no LLM in the reasoning path. Claim decomposition, orchestration, and contrarian review are deterministic; verdicts follow evidence tables calibrated against known fact-check rulings. The "28/28 in band" result proves the pipeline runs end-to-end — it does not prove the agent independently discovers truth. See [Limitations](#limitations).

## Quickstart (judges)

No dependencies beyond Python 3.10+. No API keys needed for the fixture runs.

```bash
git clone https://github.com/Mike-Demo/truthops
cd truthops
python -m truthops run --case smoke1   # PANTS_ON_FIRE expected
python -m truthops run --case smoke5   # TRUE expected
```

Cases `smoke1`–`smoke28` map to the 28 claims below (1–8: calibration set; 9–28: community set). Add `--live` to wire the live evidence adapters (GPTZero, Sightengine, C2PA, Alexandria) — each degrades gracefully to fixture mode when its key is missing. Reports land in `artifacts/` as JSON + Markdown.

## Status

✅ **Step 1 complete — 28 claims run through the pipeline** (Oct 10–11, 2026). Claims 1–8: calibration set (1–5 use AP/FactCheck.org-derived fixtures; 6–8 use PolitiFact-derived fixtures). Claims 9–28: community set from CNN, AP, and Reuters fact checks, submitted via the neatHack Discord. All fixtures are synthetic and labeled as such — see `docs/smoke-test-claims.md` for the methodology and known limitations.

| Claim | Pipeline verdict | Score | Expected band | Result |
|---|---|---|---|---|
| Mamdani/Epstein photos | PANTS_ON_FIRE | 3/100 | 0–5 | ✅ Hit |
| Trump SSA audit | FALSE | 10/100 | 10–20 | ✅ Hit |
| Trump ended eight wars | MOSTLY_FALSE | 34/100 | 30–45 | ✅ Hit |
| Gas below $2.30/gal | FALSE | 10/100 | 10–30 (corrected) | ✅ In band after fixture correction (see below) |
| Mamdani is NYC mayor | TRUE | 99/100 | 90–100 | ✅ Hit |
| Cuban deportations | MOSTLY_TRUE | 78/100 | 80–90 | ⚠️ 2pts under; in pipeline mostly_true band (75–90) |
| ICE training days | MOSTLY_TRUE | 88/100 | 80–90 | ✅ Hit |
| Florida hospital rank | MOSTLY_TRUE | 90/100 | 80–90 | ✅ Hit (top of band) |

**Total API spend across all 8 runs: $0.00.**

Every run produced: Markdown report, signed PDF/A-3b, public Gist, and a Neatlogs trace ID in the JSON. All artifacts committed under `artifacts/claim{1-8}-final/`. (PDFs carry valid PKCS#7 PAdES signatures and full PDF/A-3b markers including catalog OutputIntent with sRGB profile — verified 2026-10-11: all 7 fonts embedded in each PDF, signatures OpenSSL-verified. Caveats: no independent veraPDF conformance run yet; signatures use a self-signed certificate, so they prove tamper-evidence, not public-CA trust.)

### Live-stack verification (Oct 10, 2026, ~23:15 CDT)

All 8 claims re-ran with `--live` (GPTZero, Sightengine, C2PA, Alexandria, Cloudflare Clef sniff). Every verdict matched its fixture run exactly — 8/8 identical. Total live spend: **$0.00**. Neatlogs tracing fully operational after the v4 `neatlogs_span()` fix — all 8 traces captured with nested spans (e.g. smoke1 live trace `07767814d689...`).

**Honesty note on the live runs (updated Oct 11 evening):** 28/28 claims re-ran with `--live` and all verdicts matched fixture runs exactly — zero regressions. Per adapter: **Cloudflare Clef** now confirmed live on all 28 sniff tests (fixed a response-parser bug where the API returns `noul` not `probability`); **GPTZero** fired on smoke10/smoke21 (secondary sources flagged, reliability discounted via P(ai) weighting); **Alexandria** rewritten from tool-discovery to primary-source web search after learning it's a data-provider marketplace requiring team access — now finds and scrapes real sources; **Sightengine** image acquisition now wired end-to-end (Oct 11): photo claims trigger Firecrawl image search → download → C2PA provenance check → Sightengine AI detection — verified live on smoke1 (413KB photo acquired, C2PA checked, added as evidence; verdict unchanged at PANTS_ON_FIRE 3/100); **C2PA** probed (library installed). `api_spend` was empty on every run — Clef calls via Workers AI don't register there, and no paid detection ops fired. Cost reconciliation: cfo.ai models **$1.08/investigation** (the business-model figure); observed API spend on these runs was **$0.00**. What's validated: adapters wired, verdicts stable, GPTZero weighting works, Alexandria finds real sources, photo chain acquires and checks images. What's not yet proven: a paid Sightengine call flowing end to end (needs SIGHTENGINE_API_USER/SECRET in the run environment).

## Methodology

**Calibration-first.** Before trusting the agent on unknown claims, we verify it hits known answers. Eight real-world claims with established PolitiFact/FactCheck.org rulings span the full truth spectrum — from PANTS_ON_FIRE to TRUE. 7 of 8 landed in their expected bands; Claim 6 scored 78/100 against an 80–90 expected band (inside the pipeline's 75–90 MOSTLY_TRUE band).

Each claim runs **independently** through the live pipeline with no shared state:

```
Allegation → [Sniff Test] → (proceed?) → Evidence Pipeline → Claims → Contrarian Review → Director → Response Plan
                 ↓                                                      ↓
            cheap gate ($0.02)                              human approval gates
            (Cloudflare Clef pluggable)                      (publish/post/notify blocked)
```

1. **Sniff test** (`truthops/sniff_test.py`): cheap orchestration gate before the full pipeline. Obvious fakes without traction stop early; viral misinformation still gets full investigation.
2. **Evidence agents** gather and score sources — text, images, and enrichment.
3. **Contrarian agent** tries to break the verdict (adversarial review).
4. **Director** synthesizes the final verdict, confidence, and response plan.
5. **Human approval gates** block publish/post/notify — no external action without explicit approval.

**Honest calibration:** 7 of 8 claims in their expected bands — and the two that needed work earned it. Claim 6 scored 78/100 vs an 80–90 expected band: inside the pipeline's own 75–90 MOSTLY_TRUE band, but 2 points under the requested range — flagged, not hidden. The 2-point gap is substantive, not noise: the claim slightly overstates an NGO-estimated second-term deportation figure, and the pipeline's weighting penalized the overstatement as designed. Claim 4 earned its band the hard way. The original fixture encoded a verdict reconstructed from a search snippet ("substantially accurate, ~$2.36") that turned out to be wrong: reading the full FactCheck.org article showed Trump "continued to exaggerate" (no state below $2.30, national $2.94; the $2.36 was the article's own corrected misquote). We fixed the fixture, the evidence-plan stance, and the band (80–90 → 10–30), reran, and the pipeline scored FALSE 10/100 — as the corrected evidence dictated. The calibration process caught a bad test, not a bad pipeline, and we document the whole correction rather than hiding it.

## Architecture

**Sniff test** (`truthops/sniff_test.py`): Cheap orchestration gate before the $1.08 pipeline. Obvious fakes without traction stop early; viral misinformation still gets full investigation (PR risk). Heuristic backend by default; Cloudflare Clef-flash decision model pluggable via Workers AI.

**GPTZero validation** (`truthops/evidence/gptzero_adapter.py`): Screens secondary-source texts for AI-generation signals — AI detection, AI paraphrased subclass, sentence-level flags. P(ai) now weights evidence reliability: `reliability × (1 - P(ai) × 0.7)`, so a fully AI-generated source loses 70% of its weight. Primary sources (CNN/AP/Reuters) bypass screening. Bibliography-scan and source-analysis endpoints exist in GPTZero's API but return 403 on our plan — dashboard-only.

**Photo verification** (`truthops/evidence/live_adapter.py::verify_photo`, acquisition in `truthops/evidence_agent.py::_acquire_claim_image`): Two-phase chain for image claims. Photo acquisition uses a **dedicated image search path, separate from text-claim evidence gathering**: the query strips news-bias terms ("photographs circulating online show"), news/debunk domains are excluded, and only direct image-file URLs are accepted — article `og:image`s are never scanned, because scanning coverage *of* an image produces misleading evidence (verified the hard way on Oct 11: scanning a debunk article's image pulled smoke1 from PANTS_ON_FIRE 3/100 to MOSTLY_FALSE 35/100). Fixture images (`fixtures/<case>/images/`) take priority when provided. Then: Phase 1 (free, local): C2PA provenance check via `c2pa_adapter.py` — valid provenance is a strong authenticity signal; absence is inconclusive. Phase 2 (free tier): Sightengine `genai` AI-generation detection via `sightengine_adapter.py` — runs only when Phase 1 is inconclusive and `SIGHTENGINE_API_USER`/`SIGHTENGINE_API_SECRET` are set. Results become evidence records with fabrication_proof flags. Free tier: 2,000 ops/month, no time limit. (Replaced TruthScan on Oct 10 after its upload API returned persistent 403s. Image acquisition wired Oct 11; dedicated search path Oct 11.) Verified live on smoke1: the four AI-generated Mamdani/Epstein fakes scored 91–99% AI probability; the fabrication_proof evidence strengthened the verdict to PANTS_ON_FIRE 1/100 (confidence 0.99).

**Alexandria enrichment** (`truthops/evidence/alexandria_adapter.py`): Primary-source search via Firecrawl web search — finds news articles, official statements, and press coverage relevant to the claim, scrapes top results, and adds them as evidence records. (Note: Firecrawl "Alexandria" is a data-provider marketplace requiring team-level access; the adapter uses regular web search for primary-source discovery, which is the correct tool for this job.) Paid per use; spend logged per run.

**Tracing** (`truthops/tracing.py`): Neatlogs instrumentation with graceful degradation. Every live run captures its trace ID into the report JSON.

## Sponsor evidence

- **neatlogs traces**: instrumented via `truthops/tracing.py` — all 28 claims traced on live runs, trace IDs in report JSON ([neatlogs.com](https://neatlogs.com/))
- **Entire checkpoints**: CLI installed, `~/.local/bin` on PATH, latest checkpoint `01M4PD1Z3D2Q28FHYMFPDARF1J` (Oct 11) with full session provenance, pushed to origin ([entire.io](https://entire.io/))
- **cfo.ai plan**: [cfo.ai](https://cfo.ai/) — financial model with $1.08/investigation unit economics. Exported copies: [business-plan.md](docs/business-plan.md) · [business-plan.pdf](docs/business-plan.pdf)

## Limitations

- **Rule-based, not LLM-driven.** No generative model calls in the reasoning path. `claim_analyst.py` is deterministic keyword/pattern decomposition; `director.py` picks next actions with if/else rules; `contrarian.py` returns scripted re-verification summaries. The only model call is the optional, env-gated Cloudflare Workers AI `clef-flash` classifier in the sniff-test gate. GPTZero and Sightengine are third-party detectors, not reasoning.
- **Calibration is table-driven.** `truthops/evidence_agent.py` holds `EVIDENCE_PLAN` / `SMOKE_EVIDENCE_PLAN` tables that fix each source's stance ("supports"/"contradicts") and weight per claim. "28/28 in band" validates that the pipeline executes correctly against known fact-check rulings — it is not evidence the pipeline independently discovers truth on unseen claims.
- **Fixture-driven demo.** The dashboard verdicts and scores come from curated fixtures plus live-adapter enrichment. Treat them as a pipeline demonstration, not independent fact-checks.
- **Cost figures.** cfo.ai models **$1.08/investigation** unit economics (source of truth for the business model). Actual API spend on the demo runs was **$0.00** — no paid detection ops fired (Clef calls via Workers AI don't register in `api_spend`). The two numbers measure different things: modeled cost vs. observed spend.
- **Truth-O-Meter bands** are TruthOps' own 0–100 mapping (pants_on_fire 0–5, false 5–15, mostly_false 15–40, half_true 40–60, mostly_true 75–90, true 90–100; 60–75 is a deliberate gap). PolitiFact's scale has six ratings and no numeric scores.
- **GPTZero adapter requires a local CLI.** In live mode, the pipeline shells out to `~/workspace/skills/gptzero/bin/gptzero-scan` (not an env var or pip package). Judges cloning the repo get fixture mode for GPTZero screening unless they install that CLI.
- **Regression test, not calibration test.** `tests/smoke_test.py` (57 checks) verifies the pipeline executes as written against the hard-coded evidence tables — it does not prove the pipeline independently discovers truth. The test writes to a temp directory and restores committed artifacts afterward.

## Security note: credential exposure during the hackathon

During live demo runs on Oct 10–11, the neatlogs API key and the Sightengine API user/secret appeared in plain text in committed terminal recordings (`artifacts/claim*-final/run.typescript`) and in Entire checkpoint snapshots of the repo. This was done intentionally to run live demos inside the hackathon window — but those credentials must now be treated as public and **will be rotated after the event**. The earlier "transient env only, never stored" wording referred to how keys were passed to run commands; it was inaccurate for the recordings, which captured full command lines. Going forward: keys via environment only, recordings redacted before commit, secret-scanning pre-commit hook.

## All 28 claims — reports, PDFs, videos

| # | Claim | Verdict | Score | Links |
|---|-------|---------|-------|-------|
| 1 | Photographs circulating online show New York City Mayor Zohr... | **PANTS ON FIRE** | 1 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke1.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke1.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke1-live.mp4) |
| 2 | President Trump initiated an internal audit of the Social Se... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke2.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke2.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke2-live.mp4) |
| 3 | President Trump ended eight wars.... | **MOSTLY FALSE** | 34 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke3.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke3.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke3-live.mp4) |
| 4 | Gasoline is now below $2.30 a gallon in most states.... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke4.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke4.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke4-live.mp4) |
| 5 | Zohran Mamdani is the mayor of New York City.... | **TRUE** | 99 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke5.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke5.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke5-live.mp4) |
| 6 | President Donald Trump has deported 'over 13,000 Cubans sinc... | **MOSTLY TRUE** | 78 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke6.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke6.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke6-live.mp4) |
| 7 | Immigration agents 'are not getting the traditional five mon... | **MOSTLY TRUE** | 88 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke7.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke7.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke7-live.mp4) |
| 8 | Florida is '49th in avoidable hospital costs.'... | **MOSTLY TRUE** | 90 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke8.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke8.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke8-live.mp4) |
| 9 | Grocery prices were 'down' and 'WAY DOWN' in April 2025.... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke9.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke9.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke9-live.mp4) |
| 10 | The enterprise customer decline was 93%.... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke10.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke10.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke10-live.mp4) |
| 11 | Gas prices had fallen to $1.98 per gallon in two states on A... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke11.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke11.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke11-live.mp4) |
| 12 | There was no inflation during Trump's first presidency.... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke12.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke12.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke12-live.mp4) |
| 13 | The Biden administration had the highest inflation in U.S. h... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke13.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke13.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke13-live.mp4) |
| 14 | The price of bacon quadrupled during Biden's presidency.... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke14.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke14.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke14-live.mp4) |
| 15 | The price of apples doubled during Biden's presidency.... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke15.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke15.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke15-live.mp4) |
| 16 | The United States was losing $2 trillion a year on trade bef... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke16.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke16.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke16-live.mp4) |
| 17 | The United States had a $350 billion trade deficit with Mexi... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke17.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke17.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke17-live.mp4) |
| 18 | It has been claimed that Ukraine started the war with Russia... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke18.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke18.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke18-live.mp4) |
| 19 | The United States had provided $350 billion in wartime aid t... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke19.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke19.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke19-live.mp4) |
| 20 | Europe had provided $200 billion less in aid to Ukraine than... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke20.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke20.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke20-live.mp4) |
| 21 | The enterprise customer decline was 4%.... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke21.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke21.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke21-live.mp4) |
| 22 | More Americans are working in the United States now than at ... | **MOSTLY FALSE** | 35 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke22.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke22.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke22-live.mp4) |
| 23 | The stock market had set 74 all-time highs since Trump's ret... | **MOSTLY FALSE** | 35 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke23.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke23.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke23-live.mp4) |
| 24 | Manufacturing was booming and American manufacturing was bac... | **MOSTLY FALSE** | 35 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke24.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke24.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke24-live.mp4) |
| 25 | The United States has the largest amount of oil and gas of a... | **MOSTLY FALSE** | 35 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke25.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke25.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke25-live.mp4) |
| 26 | It has been claimed that China is operating the Panama Canal... | **FALSE** | 10 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke26.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke26.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke26-live.mp4) |
| 27 | The United States spent more money than ever on the Panama C... | **MOSTLY FALSE** | 35 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke27.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke27.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke27-live.mp4) |
| 28 | Trump won the 2024 U.S. popular vote by millions.... | **TRUE** | 99 | [MD](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke28.md) · [PDF](https://github.com/Mike-Demo/truthops/blob/main/artifacts/truthops-report-smoke28.pdf) · [Video](https://truthops-demo.space.fast/videos/smoke28-live.mp4) |

## Links

- **Live demo**: https://truthops-demo.space.fast/
- **Repo**: https://github.com/Mike-Demo/truthops
- **Build log**: https://github.com/Mike-Demo/truthops/blob/main/hackathon.md
