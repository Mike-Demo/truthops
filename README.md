# TruthOps

**Don't just detect misinformation. Resolve it.**

TruthOps is an autonomous trust operations agent for neatHack 2026 (Oct 10–12). It investigates high-risk claims, challenges its own conclusions through adversarial review, and produces evidence-backed response plans — with human approval gates at every decisive step.

## Status

✅ **Step 1 complete — 5 calibration claims run through the live pipeline** (Oct 10, 2026)

| Claim | Agent verdict | Score | Expected band | Result |
|---|---|---|---|---|
| Mamdani/Epstein photos | PANTS_ON_FIRE | 3/100 | 0–5 | ✅ Hit |
| Trump SSA audit | FALSE | 10/100 | 10–20 | ✅ Hit |
| Trump ended eight wars | MOSTLY_FALSE | 34/100 | 30–45 | ✅ Hit |
| Gas below $2.30/gal | MOSTLY_TRUE | 85/100 | 10–30 (corrected) | ❌ Miss — agent over-credited directional truth; FactCheck.org: no state below $2.30, national $2.94 |
| Mamdani is NYC mayor | TRUE | 99/100 | 90–100 | ✅ Hit |

**Total API spend across all 5 runs: $0.00** (all adapters on free tiers).

Every run produced: Markdown report, signed PDF/A, public Gist, and a Neatlogs trace ID in the JSON. All artifacts committed under `artifacts/claim{1-5}-final/`.

## Methodology

**Calibration-first.** Before trusting the agent on unknown claims, we verify it hits known answers. Five real-world claims with established PolitiFact/FactCheck.org rulings span the full truth spectrum — from PANTS_ON_FIRE to TRUE.

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

**Honest calibration:** 4 of 5 claims landed in band. Claim 4 is a genuine miss — the agent scored 85/100 (mostly true) on a claim FactCheck.org calls an exaggeration (no state below $2.30, national average $2.94). The original 80–90 fixture band was built from a search-snippet misquote and has been corrected to 10–30 after reading the full article. We document the miss rather than hiding it: if the agent can't be honest about a miss, it can't be trusted on a hit.

## Architecture

**Sniff test** (`truthops/sniff_test.py`): Cheap orchestration gate before the $1.08 pipeline. Obvious fakes without traction stop early; viral misinformation still gets full investigation (PR risk). Heuristic backend by default; Cloudflare Clef-flash decision model pluggable via Workers AI.

**GPTZero validation** (`truthops/evidence/gptzero_adapter.py`): Four annotation-only signals — AI detection, AI paraphrased subclass, sentence-level flags, plagiarism (null in v2 API). Never changes verdicts; informs source reliability.

**Photo verification** (`truthops/evidence/live_adapter.py::verify_photo`): Two-phase chain for image claims. Phase 1 (free, local): C2PA provenance check via `c2pa_adapter.py` — valid provenance is a strong authenticity signal; absence is inconclusive. Phase 2 (free tier): Sightengine `genai` AI-generation detection via `sightengine_adapter.py` — runs only when Phase 1 is inconclusive and `SIGHTENGINE_API_USER`/`SIGHTENGINE_API_SECRET` are set. Free tier: 2,000 ops/month, no time limit. (Replaced TruthScan on Oct 10 after its upload API returned persistent 403s.)

**Alexandria enrichment** (`truthops/evidence/alexandria_adapter.py`): Evidence enrichment via Firecrawl Alexandria — discover tools, inspect capability contracts, execute only with explicit authorization. Paid per use; spend logged per run.

**Tracing** (`truthops/tracing.py`): Neatlogs instrumentation with graceful degradation. Every live run captures its trace ID into the report JSON.

## Sponsor evidence

- **neatlogs traces**: instrumented via `truthops/tracing.py` — all 5 calibration runs traced, trace IDs in report JSON ([neatlogs.com](https://neatlogs.com/))
- **Entire checkpoints**: CLI installed, `~/.local/bin` on PATH, checkpoint `01M4KHFZSP4K7Z61RJTTK1SFQS` visible locally and pushed to origin ([entire.io](https://entire.io/))
- **cfo.ai plan**: [TruthOps Business Plan](https://app.cfo.ai/trilby-media-5c5e1736/chat/9fc4571f-9158-4cc9-bdc1-868d10f2c6d3) — financial model with $1.08/investigation unit economics (GPTZero $45/mo verified) ([cfo.ai](https://cfo.ai/))
- **GPTZero MCP**: live at `https://gptzero-mcp.space.fast/mcp` — `detect_ai`, `detect_paraphrased`, `flagged_sentences` tools for cfo.ai integration

## Links

- **Live demo**: https://truthops-demo.space.fast/
- **Repo**: https://github.com/Mike-Demo/truthops
- **Claim Gists**:
  - Claim 1: https://gist.github.com/Mike-Demo/035d331c33ac2f0356decac6e99030f4
  - Claim 2: https://gist.github.com/Mike-Demo/f2a488753d6a96650ba5fcc30a04c1bd
  - Claim 3: https://gist.github.com/Mike-Demo/e8a002b9e89f22213845b1cadc42b0bc
  - Claim 4: https://gist.github.com/Mike-Demo/1330e1d6a7d291c4ee0e438f305a042f
  - Claim 5: https://gist.github.com/Mike-Demo/9522f850f85b765ffe743bb5bb164f88
