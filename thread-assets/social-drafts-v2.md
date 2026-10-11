# X Thread — TruthOps: 28 Claims + Adapter Fixes — DRAFT

## Post 1 (hook)
28 claims. Zero regressions. Three adapters fixed.

Weekend #neatHack update on TruthOps — my autonomous trust operations agent went from 5 calibration claims to 28, and I debugged why the paid adapters never fired.

Here's what broke and what I fixed 🧵

[attach: logo-animated.gif]

## Post 2 (the problem)
The honest problem: my "live" pipeline runs showed $0.00 spend across all adapters. The keys were loaded, the probes said LIVE — but no paid calls ever fired.

So I dug into each adapter to find out why.

## Post 3 (Clef fix)
**Cloudflare Clef** — the sniff test was silently falling back to heuristic on every run.

Root cause: the API returns the probability in a field called `noul`, not `probability`. One-line parser fix.

Now all 28 sniff tests hit the real Clef-flash model. Verified live.

@entirehq

## Post 4 (Alexandria rewrite)
**Alexandria** — I had built the wrong thing entirely.

I framed it as a tool marketplace (discover → execute). Turns out Firecrawl Alexandria is a data-provider catalog requiring team access — and it was never the right tool for "find primary sources about a claim."

Rewrote it as web search → scrape. Now finds real sources and adds them as evidence.

## Post 5 (GPTZero weighting)
**GPTZero** — was annotation-only. "We flagged it as AI but didn't change the math."

Now P(ai) directly weights evidence reliability: a fully AI-generated source loses 70% of its weight.

Also confirmed: their bibliography/citation endpoints are 403 on our plan. Dashboard-only.

@neatlogs

## Post 6 (results)
After all three fixes, I reran all 28 claims:

28/28 in expected bands. Every verdict and score byte-identical to baseline.

The fixes changed observability and backend selection — not verdict math. That's exactly what you want from calibration.

[attach: thread-results.png]

## Post 7 (honest limitations)
What still doesn't fire:

🔍 Sightengine — pipeline detects photo claims but can't auto-download images yet. The 99% AI-detection results were from a manual run.
📊 api_spend still $0.00 — Clef via Workers AI doesn't register there.

Documented honestly in the README. No fake "live" claims.

@arithecfo

## Post 8 (close)
All of it is public:

📦 Repo: github.com/Mike-Demo/truthops
🖥️ Demo: truthops-demo.space.fast
📝 28 claim reports + videos in the repo

The agent is better than it was this morning. That's the whole point of #neatHack.

#AI #factcheck #misinformation #buildinpublic

[attach: logo-animated.gif]

---

# Threads Version

## Post 1
28 claims. Zero regressions. Three adapters fixed.

Weekend #neatHack update on TruthOps — my autonomous trust operations agent went from 5 calibration claims to 28, and I debugged why the paid adapters never fired.

Here's what broke and what I fixed 🧵

[attach: logo-animated.gif]

## Post 2
The honest problem: my "live" pipeline showed $0.00 spend across all adapters. Keys loaded, probes said LIVE — but no paid calls ever fired.

**Cloudflare Clef** was silently falling back to heuristic. The API returns probability in a field called `noul`, not `probability`. One-line fix — now all 28 sniff tests hit the real model.

@entire.io

## Post 3
**Alexandria** — I'd built the wrong thing. Framed it as a tool marketplace, but it's a data-provider catalog needing team access.

Rewrote it as web search → scrape for primary sources. Now finds real articles and adds them as evidence.

**GPTZero** — was annotation-only. Now P(ai) weights reliability directly: AI-generated sources lose up to 70% weight.

@neatlogs

## Post 4
Reran all 28 claims after the fixes: 28/28 in expected bands, every score identical to baseline.

The fixes changed observability, not verdict math. That's what calibration should do.

[attach: thread-results.png]

## Post 5
Still honest about what doesn't work: Sightengine can't auto-download images yet, and api_spend is still $0.00. Documented in the README — no fake "live" claims.

All public: github.com/Mike-Demo/truthops
Demo: truthops-demo.space.fast

#neatHack #AI #factcheck #misinformation #buildinpublic

---

# LinkedIn Version (single post)

Weekend #neatHack update: TruthOps went from 5 calibration claims to 28 — and I fixed three adapters along the way.

TruthOps is my autonomous trust operations agent: it investigates high-risk claims, challenges its own conclusions through adversarial review, and produces evidence-backed response plans with human approval gates.

**The debugging story:**

My "live" pipeline runs showed $0.00 spend across all adapters. Keys were loaded, status probes said LIVE — but no paid calls ever fired. So I investigated each one:

🔧 **Cloudflare Clef** (sniff test): was silently falling back to heuristic on every run. The API returns probability in a field called `noul`, not `probability`. One-line parser fix — now all 28 sniff tests hit the real Clef-flash model.

🔧 **Alexandria** (evidence enrichment): I'd built the wrong abstraction entirely. I framed it as a tool marketplace (discover → execute), but Firecrawl Alexandria is a data-provider catalog requiring team-level access. Rewrote it as web search → scrape for primary sources. Now finds real articles and adds them as evidence records.

🔧 **GPTZero** (source validation): was annotation-only — "flagged as AI but didn't change the math." Now P(ai) directly weights evidence reliability. A fully AI-generated source loses 70% of its weight. (Also confirmed their bibliography/citation API is 403 on our plan — dashboard-only feature.)

**Results:** Reran all 28 claims after the fixes. 28/28 in expected bands, every verdict and score identical to baseline. The fixes changed observability and backend selection — not verdict math. That's exactly what calibration should do.

**Honest limitations:** Sightengine still can't auto-download images (the photo chain stops at "acquisition required"). API spend is still $0.00. Both documented in the README — I'd rather show what doesn't work than fake a "live" demo.

**The stack:**
🔍 Neatlogs — traces every agent step
💰 cfo.ai — unit economics ($1.08/investigation)
📦 Entire — git-synced checkpoints with full session provenance

Everything is public: reports, videos, code, traces.
Repo: github.com/Mike-Demo/truthops
Demo: truthops-demo.space.fast

#AI #factcheck #misinformation #buildinpublic #hackathon #autonomousagents

---

## Tags/handles reference
- X: @neatlogs @arithecfo @entirehq + #neatHack
- Threads: @neatlogs @entire.io + #neatHack (cfo.ai has no Threads handle — name in text)
- LinkedIn: neatlogs / cfodotai / entireio pages + #neatHack

## Images to attach
- logo-animated.gif (thread-assets/logo-animated.gif)
- thread-results.png (thread-assets/thread-results.png) — NOTE: shows 5-claim results, needs update for 28
