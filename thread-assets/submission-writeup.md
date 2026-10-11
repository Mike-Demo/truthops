# TruthOps — neatHack 2026 Submission Writeup (DRAFT — Demo to review)

> Submission window: Mon Oct 12, 8:30 AM–1:25 PM CDT.
> Submit via: X quote-post of the official neatlogs submission post.
> Video: narrated demo, 3 min or less — NOT YET RECORDED (script: docs/demo-script.md).

---

## TruthOps — Autonomous Trust Operations

Viral misinformation — especially AI-generated imagery — spreads faster than human fact-checkers can respond. Existing tools flag a claim as "possible misinformation" and stop, leaving comms teams to do the investigation by hand.

TruthOps closes the loop. It's an autonomous agent that investigates high-risk claims against primary sources, stress-tests its own findings through adversarial review, and produces evidence-backed response plans behind a human approval gate. Nothing auto-publishes.

**One run, start to finish:** an allegation enters → a sniff test triages it → the claim is decomposed into atomic checkable claims → evidence is gathered (primary sources, photo forensics, AI-text screening) → a contrarian agent tries to tear the case apart → a director synthesizes a verdict → a response plan is drafted → publish/post/notify all wait on a human. Every step is traced; every run ends in a signed, tamper-evident evidence package.

## The agent (how it improved)

The agent got sharper during the build, and the traces prove it:

- **Failure recovery is designed in, not demoed around.** Mid-run, a primary-source fetch fails with HTTP 503. State is preserved, the agent retries, and the run completes — deterministically, every time. The 503 and the retry are visible in the trace and the audit trail.
- **It argues with itself.** A contrarian review pass challenges the initial conclusion. On the Northstar benchmark case it disagreed twice, forcing targeted re-verification; confidence on one claim dropped 99 → 65, and both numbers stay in the report.
- **It degrades honestly.** When an adapter can't fire (no images to acquire, no tools discovered), the pipeline says so and continues instead of faking a result. Adapter status and spend are printed on every run.

## Sponsor tools

- **neatlogs** — every pipeline run is distributed-traced. The integration had a real debugging story: initial runs returned null trace IDs because Neatlogs hands back an OpenTelemetry span, so the ID has to be read from `span.get_span_context().trace_id` and formatted as 32 hex chars. Fixed, verified, and every calibration run now emits a trace ID. (Sample: smoke1 `aa3d1547e87988e35baf6403c534e18f`.)
- **Entire** — three checkpoints tie commits to the sessions behind them, under `refs/entire/checkpoints/QS/`: `01M4KHFZSP4K7Z61RJTTK1SFQS` (initial build), `01M4MKACK4KDW0HTYAF58ARS9K` (full live suite + README), `01M4P6SRGGCG2GSHYEPAZQYR71` (live-run recordings, PDF/A regen, honesty pass).
- **cfo.ai** — a real business plan, not a slide: $0.994 per full investigation, $0.02 Cloudflare pre-screen sniff; tier pricing $499/$1,499/$3,999 with 88–90% modeled gross margins; runway modeled to Mar-2028. B-roll of the model is in the repo.

## Calibration (honest numbers)

28 claims run end to end with live adapters. The 8 smoke claims: 7/8 landed in their requested bands — claim 6 (Cuban deportations) scored 78/100 against an 80–90 band, 2 points under, still inside the pipeline's MOSTLY_TRUE 75–90 range. The 20 community claims (CNN/AP/Reuters fact checks): 18/20 in band; the two misses scored 35 where the band was higher — the pipeline penalizes "true but misleading," which is the designed behavior. All 28 live runs matched their fixture verdicts exactly.

## Links

- Repo (public, MIT — all commits inside the event window): https://github.com/Mike-Demo/truthops
- Live dashboard: https://truthops-demo.space.fast/
- Calibration claims (per-claim verdicts, evidence, traces, Gists): https://truthops-demo.space.fast/claims.html
- Reproduce: `git clone https://github.com/Mike-Demo/truthops && cd truthops && python -m truthops run --case smoke1` (zero-dependency fixture run; no keys needed)
- Demo video: ≤3 min narrated (recording Sunday) — link goes here

## Built in public

Build log, calibration write-ups, and run videos posted across X, Threads, LinkedIn, tweet.app, and Instagram under #neatHack, plus a Discord show-and-tell thread that sourced the 20 community claims.

---

*Built solo by Mike "Demo" Demopoulos (they/them), seat 589, team MikeDemo — neatHack 2026, Oct 10–12.*
