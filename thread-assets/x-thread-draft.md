# X Thread Draft — TruthOps Calibration (Step 1 Complete)

## Post 1 (hackathon intro)
I'm at #neatHack 2026 this weekend building TruthOps — an autonomous trust operations agent.

Don't just detect misinformation. Resolve it.

It investigates high-risk claims, challenges its own conclusions through adversarial review, and produces evidence-backed response plans — with human approval gates at every decisive step.

[attach: logo-animated.gif]

## Post 2 (setup)
The stack for the weekend:

🔍 @neatlogs — traces every agent step, replayable runs
💰 @arithecfo — unit economics modeling ($1.08/investigation)
📦 @entirehq — git-synced checkpoints, full session provenance

Plus: GPTZero (text AI detection), Sightengine (image forensics), C2PA (provenance), Firecrawl Alexandria (evidence enrichment).

AgentID auth, signed PDF/A reports, public Gists per investigation.

## Post 3 (methodology)
My testing methodology: I calibrated against 5 real-world claims with known PolitiFact/FactCheck.org rulings, spanning the full truth spectrum — from PANTS_ON_FIRE to TRUE.

Each claim runs through my live pipeline independently: sniff test → evidence gathering → contrarian challenge → director verdict. No shared state between runs.

If the agent can't hit known answers, it can't be trusted on unknown ones.

## Post 4 (results opener)
🧵 Step 1 results — 5 calibration claims, all through the live pipeline:

[attach: thread-results.png]

Total API spend: $0.00. Every run traced in @neatlogs, checkpointed via @entirehq.

## Post 5
Claim 1: "Photos show NYC Mayor Mamdani with Epstein"

The agent rated: PANTS_ON_FIRE (3/100) 🔥

Photo forensics: 3 of 4 circulating images scored 99% AI-generated via Sightengine. The 4th scored 18% — likely an edited real photo. Zero C2PA provenance on all four.

## Post 6
Claim 2: "Trump initiated an internal SSA audit"
→ The agent rated FALSE (10/100) ✅

Claim 3: "Trump ended eight wars"
→ The agent rated MOSTLY_FALSE (34/100) ✅

Both landed squarely in their expected calibration bands.

## Post 7
Claim 4: "Gas below $2.30 in most states"
→ The agent rated MOSTLY_TRUE (85/100) ⚠️

Hit the expected band — BUT @factcheckdotorg rates the underlying claim FALSE (no state averages that low; national avg $2.94).

Honest calibration means flagging the miss, not hiding it. The fixture band is under review.

## Post 8
Claim 5: "Mamdani is NYC mayor"
→ The agent rated TRUE (99/100) ✅

Clean hit. The pipeline knows a true claim when it sees one.

## Post 9 (pipeline)
How my agent works:

1. Sniff test ($0.02 gate) — kills obvious fakes early
2. Evidence agents gather + score sources
3. Contrarian agent tries to break the verdict
4. Director synthesizes + human approval gates block publish/post/notify

Every investigation produces: Markdown report, signed PDF/A, public Gist, @neatlogs trace ID in the JSON.

[attach: thread-demo.gif]

## Post 10 (close)
5/5 claims processed. 4/5 bands hit clean, 1 flagged honestly.

Every artifact is public: reports, signed PDFs, Gists, traces.

Repo: github.com/Mike-Demo/truthops
Demo: truthops-demo.space.fast

Next: step 2. #neatHack #AI #factcheck #misinformation
[attach: logo-animated.gif]

---

## Tags/hashtags to use
- @neatlogs, @arithecfo, @entirehq, @factcheckdotorg
- #neatHack #neatHack2026 #AI #factcheck #misinformation #buildinpublic

## Gist links (for replies if asked)
- Claim 1: https://gist.github.com/Mike-Demo/035d331c33ac2f0356decac6e99030f4
- Claim 2: https://gist.github.com/Mike-Demo/f2a488753d6a96650ba5fcc30a04c1bd
- Claim 3: https://gist.github.com/Mike-Demo/e8a002b9e89f22213845b1cadc42b0bc
- Claim 4: https://gist.github.com/Mike-Demo/1330e1d6a7d291c4ee0e438f305a042f
- Claim 5: https://gist.github.com/Mike-Demo/9522f850f85b765ffe743bb5bb164f88
