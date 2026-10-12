# TruthOps — neatHack 2026 Submission Writeup (DRAFT — Demo to review)

> Submission window: Mon Oct 12, 8:30 AM–1:25 PM CDT.
> Submit via: X quote-post of the official neatlogs submission post.
> Video: demo recorded live on Oct 12 — Pexo clean cut with automated voiceover narration (see the honesty note under Links).

---

## TruthOps

Viral misinformation — especially AI-generated imagery — spreads faster than human fact-checkers can respond. Existing tools flag a claim as "possible misinformation" and stop, leaving comms teams to do the investigation by hand.

TruthOps closes the loop. It's a transparent scoring and governance pipeline over curated evidence: it runs high-risk claims against primary sources through a scripted contrarian review, and produces evidence-backed response plans behind a human approval gate. Nothing auto-publishes. To be clear: it's rule-based — no LLM in the reasoning path.

**One run, start to finish:** an allegation enters → a sniff test triages it → the claim is decomposed into atomic checkable claims → evidence is gathered (primary sources, photo forensics, AI-text screening) → a scripted contrarian review tries to break the case → a director synthesizes a verdict → a response plan is drafted → publish/post/notify all wait on a human. Every step is traced; every run ends in a signed, tamper-evident evidence package.

## The pipeline (how it improved)

The pipeline got sharper during the build, and the traces prove it:

- **Failure recovery is designed in, not demoed around.** Mid-run, a primary-source fetch fails with HTTP 503. State is preserved, the pipeline retries, and the run completes — deterministically, every time. The 503 and the retry are visible in the trace and the audit trail.
- **It stress-tests itself.** A scripted contrarian review pass challenges the initial conclusion. On the Northstar benchmark case it disagreed twice, forcing targeted re-verification; confidence on one claim dropped 99 → 65, and both numbers stay in the report.
- **It degrades honestly.** When an adapter can't fire (no images to acquire, no tools discovered), the pipeline says so and continues instead of faking a result. Adapter status and spend are printed on every run.

## Sponsor tools

- **neatlogs** — every pipeline run is distributed-traced. The integration had a real debugging story: initial runs returned null trace IDs because Neatlogs hands back an OpenTelemetry span, so the ID has to be read from `span.get_span_context().trace_id` and formatted as 32 hex chars. Fixed, verified, and every calibration run now emits a trace ID. (Sample: smoke1 `aa3d1547e87988e35baf6403c534e18f`.)
- **Entire** — eleven checkpoints pushed as git refs under `refs/entire/checkpoints/` (verify: `git ls-remote origin 'refs/entire/checkpoints/*'`), tying commits to the sessions behind them — from `QS/01M4KHFZSP4K7Z61RJTTK1SFQS` (initial build) to `0F/01M4PM74JJJSFKM80Y53QP9X0F` (newest on GitHub), pushed via a custom `entire-agent-cane` plugin. One more, `01M4PQ0NFET7JK1AT3ZZJFDZRJ` (Oct 11, cost recompute), is registered in Entire but its git ref push failed; the entire.io dashboard only counts natively-registered checkpoints, so the git refs are the verifiable record.
- **cfo.ai** — a real business plan, not a slide: ~$0.49 per full investigation; tier pricing $499/$1,499/$3,999 with 94.77–97.38% modeled gross margins; runway modeled to Mar-2028. B-roll of the model is in the repo.

## Calibration (honest numbers)

28 claims run end to end with live adapters — 28/28 in their expected Truth-O-Meter bands under the pipeline's band mapping (claim 6 scored 78/100, inside the pipeline's 75–90 MOSTLY_TRUE range). All 28 live runs matched their fixture verdicts exactly.

## Links

- Repo (public, MIT — all commits inside the event window): https://github.com/Mike-Demo/truthops
- Live dashboard: https://truthops-demo.space.fast/
- Calibration claims (per-claim verdicts, evidence, traces, Gists): https://truthops-demo.space.fast/claims.html
- Reproduce: `git clone https://github.com/Mike-Demo/truthops && cd truthops && python -m truthops run --case smoke1` (zero-dependency fixture run; no keys needed)
- Demo video: Pexo clean cut of the live Oct 12 recording, under 2 min (project: https://pexo.ai/project/82788483574 — final link slots in here)
- **Video honesty note:** the footage was self-recorded after the planned remote recording session failed on the morning of Oct 12 (repeated Cloud PC session drops, and remote keystrokes arriving corrupted, which made an agent-driven recording impossible). The raw clips had no audio track, so the narration is an automated voiceover (Pexo, August v2) over the real recording, with earlier full-run trace recordings woven in. Everything on screen — the runs, verdicts, traces, and approval-gate blocks — is genuine and unstaged.
- Backup demo video (Pexo, 90s, August v2 VO): https://muse.ai/files/1288309184367420/1647296700772442/7rwivs4nkazkv34lj8u9iyuj/truthops-demo-pexo-16x9-4k-v4-augustv2.mp4 (expires Oct 14)
- Overview deck: https://www.beautiful.ai/player/-P3hSUBp6A3G-H3HVUIc

## Built in public

Build log, calibration write-ups, and run videos posted across X, Threads, LinkedIn, tweet.app, and Instagram under #neatHack, plus a Discord show-and-tell thread that sourced the 20 community claims.

---

*Built solo by Mike "Demo" Demopoulos (they/them), seat 589, team MikeDemo — neatHack 2026, Oct 10–12.*
