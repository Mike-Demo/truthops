# TruthOps — neatHack 2026 build log

## Project
**TruthOps** — an autonomous trust-operations agent that investigates high-risk claims against primary sources, stress-tests its own findings through contrarian adversarial review, and produces evidence-backed response plans behind a human approval gate. Nothing auto-publishes.

Problem addressed: viral misinformation (especially AI-generated imagery) spreads faster than human fact-checkers can respond. TruthOps gives a newsroom, campaign, or brand a repeatable, auditable pipeline: sniff test → evidence gathering → photo forensics → weighted evaluation → contrarian review → director verdict → human gate → signed report.

## Team
- Mike "Demo" Demopoulos (they/them) — builder

## Stack
- **Agent:** Python CLI (`python -m truthops run --case <name>`), zero-dependency fixture runs; optional `--live` enables real adapters
- **Adapters:** GPTZero (AI-text detection via CLI), Sightengine (image AI-detection), C2PA (provenance, local), Alexandria via Firecrawl (enrichment), Cloudflare Workers AI / Clef-flash (sniff gate + economics)
- **Dashboard:** static SpaceFast site — https://truthops-demo.space.fast/ (precomputed outputs; "Run investigation" is a staged animation, not a live pipeline)
- **MCP server:** JavaScript on SpaceFast, AgentID-protected — https://truthops-mcp.space.fast/mcp (`submit_allegation` is a queueing stub, does not execute the pipeline)
- **Calibration claims page:** https://truthops-demo.space.fast/claims.html — per-claim verdicts, evidence, traces, Gists, clone-and-run instructions
- **Repo:** https://github.com/Mike-Demo/truthops (public, MIT)

## neatlogs — tracing
- Neatlogs v4 SDK integrated for distributed tracing of every pipeline run.
- Debugging story: initial runs showed `neatlogs_trace_id: null` — Neatlogs returns an OpenTelemetry span, so the ID must be read from `span.get_span_context().trace_id` and formatted as 32 hex chars. Fixed and verified.
- Every calibration run emits a trace ID and flushes cleanly. Example traces:
  - smoke1 `2214a1399682b529e2bf82723e0cbe1c`, smoke1 (Oct 10 clean) `aa3d1547e87988e35baf6403c534e18f`
  - Full suite (Oct 11): `07767814d689`, `6dbaded47df6`, `98c526f76a98`, `52f40958d95f`, `8499d366a14a`, `ed7aecfc5ac7`, `f9dec7f40b43`, `dfb7158b5d68`
- Missing SDK degrades gracefully (warning only, pipeline continues).

## Entire — checkpoints
Three checkpoints, all materialized to GitHub ref namespace `refs/entire/checkpoints/QS/`:
1. `01M4KHFZSP4K7Z61RJTTK1SFQS` (Oct 10) — initial build session
2. `01M4MKACK4KDW0HTYAF58ARS9K` → `eeb1591bb397` (Oct 10) — full live suite + README
3. `01M4P6SRGGCG2GSHYEPAZQYR71` → `439723d` (Oct 11) — live-run recordings, PDF/A regen, README honesty pass
- Created via custom `entire-agent-cane` plugin + `entire session attach` (Entire has no direct checkpoint-create for non-integrated agents).

## cfo.ai — unit economics
- TruthOps Business Plan workspace (Trilby Media account) models tier pricing, costs, revenue, runway.
- Pipeline cost per investigation: **$0.994** full pipeline; **$0.02** Cloudflare pre-screen sniff.
- Sightengine: 2,000 free ops/month; modeled shared cost $0/$0/$29/mo at 25/100/400-customer scale.
- Tier pricing $499/$1,499/$3,999 (25/150/400 investigations); $12 overage; modeled gross margins 88–90%.
- Runway outputs: base minimum cash $1,861 (Feb 2027); Mar-2028 ending cash $91,534 / $22,892 / $228,819 (base/conservative/upside).
- B-roll video of the model: `thread-assets/cfo-broll/cfo-broll-v2.mp4` (v1 had stale TruthScan figures — TruthScan was replaced by Sightengine mid-build).

## Build log

### 2026-10-10
- Scaffolded repo: director, evidence pipeline, claims engine, contrarian review, response planner.
- Northstar synthetic case created; dashboard + MCP + auth proxy deployed to SpaceFast.
- Entire plugin `entire-agent-cane` built; checkpoint 1 created.
- Sightengine replaced TruthScan (403/400 failures); C2PA chain wired.
- Claims 1–5 calibrated; claim 4 fixture corrected after FactCheck.org re-read (band 80–90 → 10–30; rerun FALSE 10/100).
- Claims 6–8 added (proposed PolitiFact claims). Full 8-claim `--live` suite: all verdicts matched fixtures, $0.00 spend.
- Checkpoint 2 created after live suite + README.

### 2026-10-11
- README honesty pass: 8 claims (not 5), 7/8 in expected bands (claim 6: 78/100 vs 80–90 requested band, inside pipeline MOSTLY_TRUE 75–90), live-run limitations documented, judge quickstart added and verified in bare Python 3.12 venv (no pip install, no keys, no sign-in).
- All 8 claim PDFs regenerated as PDF/A-1 with sRGB OutputIntent + PAdES signatures, each OpenSSL-verified. (veraPDF conformance not independently run; profile was PIL-generated minimal sRGB — WeasyPrint's standard `sRGB2014.icc` available for a future pass.)
- Claims page shipped with per-claim "How the agent got here" demos (sniff → evidence → contrarian → director).
- All 8 smoke tests re-run end to end with live keys (transient env only, never stored): 8/8 verdicts matched, $0.00 spend. Terminal sessions rendered to video: 8 landscape + 8 vertical 9:16 + 8 vertical 4K (`thread-assets/live-runs/`).
- Pexo 60s pipeline explainer produced (16:9, 9:16, 1:1, 4K).
- Social: 5 PressMaster drafts (X, Threads, LinkedIn, YouTube Shorts, Instagram) with live-run video, publish-ready; Discord show-and-tell post asking for test claims.
- Pushed to GitHub main: `439723d`. Checkpoint 3 created.

## Demo
- Dashboard: https://truthops-demo.space.fast/
- Calibration claims: https://truthops-demo.space.fast/claims.html
- Reproduce: `git clone https://github.com/Mike-Demo/truthops && cd truthops && python -m truthops run --case smoke1`
- MCP: https://truthops-mcp.space.fast/mcp (AgentID-protected; `submit_allegation` queues, does not run pipeline)

## Calibration results (honest)
| Claim | Verdict | Score | Expected band | In band? |
|---|---|---|---|---|
| smoke1 Mamdani/Epstein photos | PANTS_ON_FIRE | 3/100 | low | ✅ |
| smoke2 Trump SSA audit | FALSE | 10/100 | 0–20 | ✅ |
| smoke3 Trump ended eight wars | MOSTLY_FALSE | 34/100 | 25–45 | ✅ |
| smoke4 Gas below $2.30 | FALSE | 10/100 | 10–30 | ✅ |
| smoke5 Mamdani is NYC mayor | TRUE | 99/100 | 90–100 | ✅ |
| smoke6 Cuban deportations | MOSTLY_TRUE | 78/100 | 80–90 | ⚠️ 2pts under; inside pipeline band 75–90 |
| smoke7 ICE training days | MOSTLY_TRUE | 88/100 | 80–90 | ✅ |
| smoke8 Florida hospital rank | MOSTLY_TRUE | 90/100 | 80–90 | ✅ |

7/8 in requested bands. 8/8 live runs matched fixture verdicts exactly.

## Known limitations
- Dashboard "Run investigation" is a staged animation; real pipeline is the CLI.
- `--live` probes adapters but `api_spend` is empty: Alexandria found 0 tools, paid Sightengine op didn't fire, unclear whether Cloudflare Clef or heuristic fallback answered. Live mode verifies wiring and verdict stability, not end-to-end billing.
- Claim 6 misses its requested band by 2 points (78 vs 80–90).
- PDF/A: no independent veraPDF conformance run; self-signed PAdES cert (tamper evidence, not public-CA trust).
- Gists for claims 6–8 are fixture runs, labeled as such.

## Submission
- Window: Monday Oct 12, 2026, 8:30 AM–1:25 PM CDT.
- Repo: https://github.com/Mike-Demo/truthops @ `439723d`
- Entire checkpoint: `01M4P6SRGGCG2GSHYEPAZQYR71`
- 8 public Gists (claim reports): see claims page
- Social: earlier batch published (X, Threads, LinkedIn, tweet.app, Instagram); Bluesky URL pending
- Outstanding: 2–3 min narrated demo video (Pexo 60s sizzle exists), final submission writeup, video-scripts 7/8 correction, Bluesky URL
