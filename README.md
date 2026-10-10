# TruthOps

**Don't just detect misinformation. Resolve it.**

TruthOps is an autonomous trust operations agent for neatHack 2026 (Oct 10–12). It investigates high-risk corporate claims, challenges its own conclusions through adversarial review, and produces evidence-backed response plans — with human approval gates at every decisive step.

## Problem statement

Companies face viral claims about their products, practices, and people every day. Existing tools flag "possible misinformation" and stop there — leaving communications and trust teams to manually gather evidence, evaluate risk, and draft responses under time pressure. TruthOps closes the loop: it investigates the claim against primary sources, stress-tests its own findings, and delivers a ready-to-approve response plan with cited evidence.

## Status

✅ MVP working — Northstar case resolves to MISLEADING with evidence-backed response plan. Sniff-test gate + 4-signal GPTZero validation live.

## Architecture

```
Allegation → [Sniff Test] → (proceed?) → Evidence Pipeline → Claims → Contrarian Review → Director → Response Plan
                 ↓                                                      ↓
            cheap gate ($0.02)                              human approval gates
            (Cloudflare Clef pluggable)                      (publish/post/notify blocked)
```

**Sniff test** (`truthops/sniff_test.py`): Cheap orchestration gate before the $1.08 pipeline. Obvious fakes without traction stop early; viral misinformation still gets full investigation (PR risk). Heuristic backend by default; Cloudflare Clef-flash decision model pluggable via Workers AI.

**GPTZero validation** (`truthops/evidence/gptzero_adapter.py`): Four annotation-only signals — AI detection, AI paraphrased subclass, sentence-level flags, plagiarism (null in v2 API). Never changes verdicts; informs source reliability.

## Sponsor evidence

- **neatlogs traces**: instrumented via `truthops/tracing.py` — keyed runs complete, SDK shutdown clean
- **Entire checkpoints**: support question posted in Discord #support (Oct 10) — awaiting team guidance on transcript-based checkpoint creation
- **cfo.ai plan**: [TruthOps Business Plan](https://app.cfo.ai/trilby-media-5c5e1736/chat/9fc4571f-9158-4cc9-bdc1-868d10f2c6d3) — financial model with $1.08/investigation unit economics (GPTZero $45/mo verified)
- **GPTZero MCP**: live at `https://gptzero-mcp.space.fast/mcp` — `detect_ai`, `detect_paraphrased`, `flagged_sentences` tools for cfo.ai integration
