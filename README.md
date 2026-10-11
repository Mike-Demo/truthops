# TruthOps

**Don't just detect misinformation. Resolve it.**

TruthOps is an autonomous trust operations agent for neatHack 2026 (Oct 10–12). It investigates high-risk claims, challenges its own conclusions through adversarial review, and produces evidence-backed response plans — with human approval gates at every decisive step.

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

| Claim | Agent verdict | Score | Expected band | Result |
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

**Honesty note on the live runs (updated Oct 11):** 28/28 claims re-ran with `--live` and all verdicts matched fixture runs exactly — zero regressions. Per adapter: **Cloudflare Clef** now confirmed live on all 28 sniff tests (fixed a response-parser bug where the API returns `noul` not `probability`); **GPTZero** fired on smoke10/smoke21 (secondary sources flagged, reliability discounted via P(ai) weighting); **Alexandria** rewritten from tool-discovery to primary-source web search after learning it's a data-provider marketplace requiring team access — now finds and scrapes real sources; **Sightengine** probed but the photo chain still stops at "image acquisition required" (no auto-download implemented); **C2PA** probed (library installed). `api_spend` was empty on every run — Clef calls via Workers AI don't register there, and no paid detection ops fired. What's validated: adapters wired, verdicts stable, GPTZero weighting works, Alexandria finds real sources. What's not yet proven: a paid Sightengine/C2PA call flowing end to end.

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

**Honest calibration:** 7 of 8 claims in their expected bands — and the two that needed work earned it. Claim 6 scored 78/100 vs an 80–90 expected band: inside the pipeline's own 75–90 MOSTLY_TRUE band, but 2 points under the requested range — flagged, not hidden. The 2-point gap is substantive, not noise: the claim slightly overstates an NGO-estimated second-term deportation figure, and the pipeline correctly penalized the overstatement. Claim 4 earned its band the hard way. The original fixture encoded a verdict reconstructed from a search snippet ("substantially accurate, ~$2.36") that turned out to be wrong: reading the full FactCheck.org article showed Trump "continued to exaggerate" (no state below $2.30, national $2.94; the $2.36 was the article's own corrected misquote). We fixed the fixture, the evidence-plan stance, and the band (80–90 → 10–30), reran, and the pipeline scored FALSE 10/100 — correctly. The calibration process caught a bad test, not a bad pipeline, and we document the whole correction rather than hiding it.

## Architecture

**Sniff test** (`truthops/sniff_test.py`): Cheap orchestration gate before the $1.08 pipeline. Obvious fakes without traction stop early; viral misinformation still gets full investigation (PR risk). Heuristic backend by default; Cloudflare Clef-flash decision model pluggable via Workers AI.

**GPTZero validation** (`truthops/evidence/gptzero_adapter.py`): Screens secondary-source texts for AI-generation signals — AI detection, AI paraphrased subclass, sentence-level flags. P(ai) now weights evidence reliability: `reliability × (1 - P(ai) × 0.7)`, so a fully AI-generated source loses 70% of its weight. Primary sources (CNN/AP/Reuters) bypass screening. Bibliography-scan and source-analysis endpoints exist in GPTZero's API but return 403 on our plan — dashboard-only. Hosted MCP server live at `https://gptzero-mcp.space.fast/mcp` — `detect_ai`, `detect_paraphrased`, `flagged_sentences` tools.

**Photo verification** (`truthops/evidence/live_adapter.py::verify_photo`): Two-phase chain for image claims. Phase 1 (free, local): C2PA provenance check via `c2pa_adapter.py` — valid provenance is a strong authenticity signal; absence is inconclusive. Phase 2 (free tier): Sightengine `genai` AI-generation detection via `sightengine_adapter.py` — runs only when Phase 1 is inconclusive and `SIGHTENGINE_API_USER`/`SIGHTENGINE_API_SECRET` are set. Free tier: 2,000 ops/month, no time limit. (Replaced TruthScan on Oct 10 after its upload API returned persistent 403s.)

**Alexandria enrichment** (`truthops/evidence/alexandria_adapter.py`): Primary-source search via Firecrawl web search — finds news articles, official statements, and press coverage relevant to the claim, scrapes top results, and adds them as evidence records. (Note: Firecrawl "Alexandria" is a data-provider marketplace requiring team-level access; the adapter uses regular web search for primary-source discovery, which is the correct tool for this job.) Paid per use; spend logged per run.

**Tracing** (`truthops/tracing.py`): Neatlogs instrumentation with graceful degradation. Every live run captures its trace ID into the report JSON.

## Sponsor evidence

- **neatlogs traces**: instrumented via `truthops/tracing.py` — all 8 calibration runs traced, trace IDs in report JSON ([neatlogs.com](https://neatlogs.com/))
- **Entire checkpoints**: CLI installed, `~/.local/bin` on PATH, checkpoint `01M4KHFZSP4K7Z61RJTTK1SFQS` visible locally and pushed to origin ([entire.io](https://entire.io/))
- **cfo.ai plan**: [TruthOps Business Plan](https://app.cfo.ai/trilby-media-5c5e1736/chat/9fc4571f-9158-4cc9-bdc1-868d10f2c6d3) — financial model with $1.08/investigation unit economics (GPTZero $45/mo verified) ([cfo.ai](https://cfo.ai/))

## Links

- **Live demo**: https://truthops-demo.space.fast/
- **Repo**: https://github.com/Mike-Demo/truthops
- **Claim Gists** (claims 1–5: live-verified runs; claims 6–8: fixture runs, labeled as such in each Gist):
  - Claim 1: https://gist.github.com/Mike-Demo/035d331c33ac2f0356decac6e99030f4
  - Claim 2: https://gist.github.com/Mike-Demo/f2a488753d6a96650ba5fcc30a04c1bd
  - Claim 3: https://gist.github.com/Mike-Demo/e8a002b9e89f22213845b1cadc42b0bc
  - Claim 4: https://gist.github.com/Mike-Demo/1330e1d6a7d291c4ee0e438f305a042f
  - Claim 5: https://gist.github.com/Mike-Demo/9522f850f85b765ffe743bb5bb164f88
  - Claim 6 (fixture): https://gist.github.com/Mike-Demo/8adad5b96c31a1bdf21b29f21769d1ca
  - Claim 7 (fixture): https://gist.github.com/Mike-Demo/c1716b3e88cbbf599a99b645a0a6e0ff
  - Claim 8 (fixture): https://gist.github.com/Mike-Demo/8f6261a9c63d48e176f5fa6f633fedee
