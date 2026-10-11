# TruthOps — neatHack 2026 build log

## Project
**TruthOps** — a transparent scoring and governance pipeline over curated evidence that investigates high-risk claims against primary sources, stress-tests its own findings through contrarian adversarial review, and produces evidence-backed response plans behind a human approval gate. Nothing auto-publishes.

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
- Pipeline cost per investigation: **$1.08** full pipeline (cfo.ai modeled unit economics); **$0.02** Cloudflare pre-screen sniff. Observed API spend on demo runs: $0.00.
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
- All 8 smoke tests re-run end to end with live keys (keys passed via transient env vars for the run; terminal recordings captured full command lines including keys — see Security note): 8/8 verdicts matched, $0.00 spend. Terminal sessions rendered to video: 8 landscape + 8 vertical 9:16 + 8 vertical 4K (`thread-assets/live-runs/`).
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
- Repo: https://github.com/Mike-Demo/truthops
- Entire checkpoint: `01M4PHSFBERDKGY9W4KWSZQPT5` (latest; 11 checkpoints total)
- 28 claim reports + PDFs + videos: see claims page
- Social: building in public — all posts below tagged #neatHack (Bluesky intentionally skipped)
- Outstanding: 2–3 min narrated demo video (Pexo 60s sizzle exists), final submission writeup, video-scripts 7/8 correction

### Building in public — post links
| Date (UTC) | Channel | URL |
|---|---|---|
| 2026-10-10 22:37 | Threads | https://www.threads.net/t/18114750797024028 |
| 2026-10-11 00:37 | X (@Mike_demo) | https://x.com/Mike_demo/status/2109080832052768818 |
| 2026-10-11 00:37 | X (@Mike_demo) | https://x.com/Mike_demo/status/2109080849622704140 |
| 2026-10-11 00:45 | LinkedIn | https://www.linkedin.com/posts/mikedemopoulos_neathack-neathack-ai-share-7514846562733436929-l1CJ/ |
| 2026-10-11 01:17–01:22 | Tweet (@demo) | https://app.tweet.app/post/b88da994-65aa-4399-b23b-ad57c6b45f26 (+ 14 more in chain) |
| 2026-10-11 ~06:45 | Tumblr | https://mike-demo.tumblr.com/post/830156270610825216/built-truthops-during-neathack-2026-this |
| 2026-10-11 13:36 | Threads | https://www.threads.net/t/18210214120322392 |
| 2026-10-11 15:33 | X (@Mike_demo) | https://x.com/Mike_demo/status/2109306448278679807 |
| 2026-10-11 15:45 | LinkedIn | https://www.linkedin.com/posts/mikedemopoulos_neathack-ai-factcheck-ugcPost-7515072095375048704-p3Xe/ |
| 2026-10-11 16:39 | Threads | https://www.threads.net/t/18124125554475080 |
| 2026-10-11 17:52 | Tumblr | https://mike-demo.tumblr.com/post/830201336332222464/how-does-an-autonomous-trust-operations-agent |
| 2026-10-11 18:28 | X (@Mike_demo) | https://x.com/Mike_demo/status/2109350422519447668 |
| 2026-10-11 18:45 | LinkedIn | https://www.linkedin.com/posts/mikedemopoulos_neathack-ai-factcheck-ugcPost-7515116262344081408-bgYX/ |
| 2026-10-11 19:56 | Tweet (@demo) | https://app.tweet.app/post/c6e59a5d-9ddc-4dc5-8d8e-337e519d191b |
| 2026-10-11 21:00 | X (@Mike_demo) | https://x.com/Mike_demo/status/2109388734001021339 |
| 2026-10-11 21:00 | X (@Mike_demo) | https://x.com/Mike_demo/status/2109388746130936300 |

## 2026-10-11 afternoon — community claims (smoke9–28)
- 20 claims from CNN, AP, Reuters fact checks via Discord show-and-tell. Fixtures + pipeline code extended. All 20 ran with live keys: 18/20 in expected bands (13× FALSE 10/100, 5× MOSTLY_FALSE 35/100, 1× TRUE 99/100). smoke22/23 scored 35 vs higher bands — pipeline penalizes "true but misleading." 40 videos (landscape + vertical). Claims page now shows 28 claims.

## 2026-10-11 evening — adapter debugging + fixes

**The $0.00 mystery.** Live runs showed $0.00 spend across all adapters despite keys being loaded and status probes saying LIVE. Investigation of each adapter:

1. **Cloudflare Clef (sniff test)** — was silently falling back to heuristic on every run. Root cause: the response parser expected the probability in a field called `probability`; Clef returns it in `noul`. One-line fix in `truthops/sniff_test.py`. Now all 28 sniff tests hit the real `clef-flash` model.

2. **Alexandria (evidence enrichment)** — the original design was wrong. It was built as a tool marketplace (discover → execute), but Firecrawl Alexandria is a data-provider marketplace requiring team-level access. Rewrote `truthops/evidence/alexandria_adapter.py` as web search → scrape for primary sources. Now finds 3 real sources per claim.

3. **GPTZero (source validation)** — was annotation-only ("flagged as AI but didn't change the math"). Implemented P(ai) reliability discount: `reliability × (1 - P(ai) × 0.7)` in `truthops/evidence_agent.py`. A fully AI-generated source loses 70% of its weight. Verified on smoke10: AI-flagged source dropped 0.4 → 0.12. (Bibliography/citation API confirmed 403 on our plan — dashboard-only feature.)

4. **Sightengine (photo forensics)** — the pipeline detected photo claims but stopped at "image acquisition required." Wired end-to-end Oct 11 evening: `_acquire_claim_image()` searches via Firecrawl, downloads the image (og:image preferred, size/safety checks), then runs the C2PA → Sightengine chain via `LiveAdapter.verify_photo()`. Verified live on smoke1: 413KB photo acquired from ABC7 article, C2PA checked (no provenance, as expected), added as evidence record. Verdict unchanged at PANTS_ON_FIRE 3/100 — no regression.

**Proof run (Oct 11 ~3:50 PM):** All 28 claims re-ran with live keys after adapter fixes. 28/28 in expected bands, zero regressions. **Traced rerun (Oct 11 ~4:00 PM):** All 28 re-ran with NEATLOGS_API_KEY set — 28/28 trace IDs captured. Reports, PDFs regenerated.

**Entire checkpoints (Oct 11):** `01M4PAFW1VD6GMP8A5W2GAW9V2` → `7afa104` → `b51ba79` (traced rerun) → `aef3807` (Sightengine wiring) → `01M4PD1Z3D2Q28FHYMFPDARF1J` → `9e95694` (smoke1 C2PA evidence).

## 2026-10-11 evening — photo forensics completion + honesty pass

### Photo forensics: two bugs, one fix
The Sightengine wiring had a critical bug: `_acquire_claim_image()` grabbed the `og:image` from the ABC7 *debunk article* (not the actual claimed photo). Sightengine correctly said "likely authentic" (it was the news photo), and the evidence pulled smoke1 from PANTS_ON_FIRE 3/100 to MOSTLY_FALSE 35/100 — a regression caused by scanning the wrong image.

**Fix (per Demo's direction: "Have photo search be its own search path"):** Dedicated image search path in `_acquire_claim_image()` — strips news-bias words (photographs/circulating/online/show/claimed), excludes news/debunk domains, accepts ONLY direct image file URLs (.jpg/.png/.webp), never scrapes article og:images, skips cleanly when the actual claimed image can't be found.

**Fixture images:** Demo uploaded the 4 actual Mamdani/Epstein fake photos. Scanned directly: **91%, 99%, 99%, 99% AI probability** (Sightengine). Copied to `fixtures/smoke1/images/img1-4.jpg`. Pipeline checks fixture dir FIRST. Verified: smoke1 loads img1, Sightengine flags **93% AI, fabrication_proof=True, stance=contradicts** — verdict strengthened to **PANTS_ON_FIRE 1/100 (confidence 0.99)**.

**Vault limitation discovered:** Secure Vault surrogate exchange only injects single header/query-param values; Sightengine needs two separate form fields (`api_user` + `api_secret`) — cannot be bridged. Pipeline still needs keys as env vars for runs. Connector `custom.sightengine` created; stored credential cannot be used by the pipeline.

### Full sweep with photo forensics (GitHub `4e8e40f`)
28/28 claims re-ran. All verdicts/scores match baseline except smoke1 (3→1, photo forensics). Zero regressions. Terminal log at `thread-assets/final-run-2026-10-11.log` (sanitized).

### Audit review (TruthOps-final-audit.pdf)
External audit prepared Oct 11 4:35 PM. Findings: **1 Critical, 5 High, 9 Medium, 3 Low. Provisional score ~53/100, potentially 75+ with fixes.**
- **C1 (Critical):** Live neatlogs + Sightengine credentials in 5 public terminal recordings (`artifacts/claim*-final/run.typescript`) and 5 Entire checkpoint refs. **Keys were exposed on purpose for the hack** (confirmed). Remediation: rotate post-event + incident note (documented in README security note).
- **H1:** Calibration is circular — `SMOKE_EVIDENCE_PLAN` hard-codes stances/weights. "28/28 in band" proves execution, not truth-discovery. Fair.
- **H2:** Agent is rule-based — no LLM in reasoning path. "Autonomous agent" overclaims. Fair — README reframed.
- **H3:** Live footage showed tracing OFF — **outdated** (fixed by traced rerun).
- **H4:** Demo video doesn't meet requirement — **biggest remaining gap** (no narrated 2-3 min video yet).
- **H5:** Dashboard had no honesty labelling — **fixed** (fixture-driven banner on claims page).
- **M1:** Cost figures conflicted ($1.08 / $0.994 / $0.56 / $0.00) — **fixed** ($1.08 = cfo.ai modeled source of truth; $0.00 = observed spend).

### Honesty pass (GitHub `98f7053`, Entire `01M4PG6TV2ZDFJN4XSMZRPCVZM`)
- README.md: "autonomous trust operations agent" → "transparent scoring and governance pipeline over curated evidence"; explicit rule-based disclosure; new Limitations section; Security note documenting credential exposure (intentional for hack, rotation post-event).
- site/claims.html: amber banner — "⚠️ Fixture-driven demo: scores follow recorded evidence calibrated against known fact-checks; analysis is rule-based." "$0.00 API Spend" → "Observed API Spend".
- hackathon.md + site/index.html: $0.994 → $1.08 cost fix.
- Demo site redeployed with banner live.

### Site data refresh (GitHub `933f553`)
claims.html embedded data was stale (pre-photo-forensics scores). Regenerated from latest JSON reports — smoke1 now shows 1/100 with new trace ID. Site redeployed and verified (200s on both pages).

### README claims table (GitHub `c991fd1`)
All 28 claims table added to README — each with verdict, score, and links to markdown report, PDF, and terminal video on GitHub.

## Entire checkpoints (complete list)
All materialized to GitHub ref namespace `refs/entire/checkpoints/QS/`:
1. `01M4KHFZSP4K7Z61RJTTK1SFQS` (Oct 10) — initial build session
2. `01M4MKACK4KDW0HTYAF58ARS9K` → `eeb1591bb397` (Oct 10) — full live suite + README
3. `01M4P6SRGGCG2GSHYEPAZQYR71` → `439723d` (Oct 11) — live-run recordings, PDF/A regen
4. `01M4PAFW1VD6GMP8A5W2GAW9V2` → `7afa104` (Oct 11) — traced rerun
5. `01M4PD1Z3D2Q28FHYMFPDARF1J` → `9e95694` (Oct 11) — Sightengine chain + smoke1 C2PA
6. `01M4PG6TV2ZDFJN4XSMZRPCVZM` → `98f7053` (Oct 11) — honesty pass

## Remaining work (priority order)
1. **Narrated 2–3 min demo video** — doesn't exist; 20% judging category; must cover agent + neatlogs (live trace) + Entire (checkpoint resolving to commit) + cfo.ai (pricing/costs/revenue/runway); end on human gate + PDF report; state on camera that pipeline is rule-based.
2. **Final submission writeup** — `thread-assets/submission-writeup.md` still DRAFT. Submission = public X quote-post of official neatlogs post with team, name, project, repo, demo link. Window: Oct 12, 8:30 AM–1:25 PM CDT; plan to submit by ~12:30 PM CDT.
3. **Rotate exposed keys after the event** (neatlogs + Sightengine at minimum).
4. **PressMaster**: trim 4 over-length X posts during review; drafts in Review/Approval pending.
5. **Bluesky URL** — still missing.
6. Optional (audit mediums): automated smoke test, move mp4s out of git, CSP headers, remove AgentMail address from SESSION-2026-10-10-PM.md, fix sniff-rejection `recommended_posture` crash, document GPTZero local-CLI dependency.
7. After hackathon: rotate ALL pasted API keys (Sightengine, Cloudflare, Crustdata, Firecrawl, GPTZero, neatlogs, Firecrawl).
