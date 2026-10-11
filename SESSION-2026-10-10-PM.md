# TruthOps neatHack — Session Log 2026-10-10 (afternoon)

## AgentID Auth — COMPLETE ✅
- Token-exchange proxy built and deployed: `https://truthops-auth.space.fast/`
  - Source: `~/workspace/truthops-auth/handler.js`
  - `POST /exchange` takes `{code, code_verifier, redirect_uri}`, uses `client_secret` via `client_secret_basic`
  - CORS locked to `https://truthops-demo.space.fast`
  - Health: `secret_configured: true`
- Client secret: Demo regenerated in AgentID console, pasted in chat, set via `sf env set AGENTID_CLIENT_SECRET --value-from-stdin --secret --space truthops-auth`. Never written to file.
- AgentID console has NO `none` token-auth option (only `client_secret_basic`/`client_secret_post`) — proxy is required, not optional.
- Console URLs fixed by Demo: redirect URI → `/auth/callback.html`, Terms/Privacy/Login/API-key URLs → real truthops-demo/mcp URLs.
- **End-to-end sign-in VERIFIED**: browser PKCE → AgentID authorize → inbox authorization via AgentMail API (`POST /v0/inboxes/<redacted>/authorize` with one-time token) → callback → proxy exchange → session. Composer unlocks, sign-out re-locks.
- AgentID sign-in flow note: agent-native — the authorize page shows a curl command for inbox authorization, not a password form. Pre-authorized identities auto-advance.

## Demo Site Branding — COMPLETE ✅
- Firefly-generated logo (hex shield + magnifying glass + checkmark, cyan on navy). Watermark cropped, padding equalized.
- Files: `logo.jpg`, `logo-animated.gif` (pulse, 58KB), `favicon.jpg`, `social-card.jpg` (1200×630 OG card)
- Animated GIF in site header, favicon on all pages, OG + Twitter Card meta tags
- `robots.txt` with `Disallow: /` + `noindex, nofollow` meta tags (demo is unlisted)

## Export Features — COMPLETE ✅
Results page (`results.html`) has three export buttons:
1. **Markdown** — client-side download, editable
2. **PDF/A (signed)** — `truthops-northstar-report.pdf` (37KB, PDF/A-3b, XMP metadata, PAdES-signed with self-signed cert). Built by `build_pdfa.py` (WeasyPrint + endesive). Note: PDF/A prohibits encryption per ISO 19005 — signature is the archival "lock."
3. **GitHub Gist** — https://gist.github.com/Mike-Demo/21e196b39b17bd53cda884e041532f68 (public). Created with a 30-day gist-scoped token Demo pasted in chat, used transiently, never stored.

## Demo Videos — COMPLETE ✅
- `demo-walkthrough.mp4` (20s) — first end-to-end run
- `demo-full-run.mp4` (27s) — full run from logged out + all three exports on camera
- Both live at `https://truthops-demo.space.fast/<filename>`

## Alexandria Skill — COMPLETE ✅
- Created `~/workspace/skills/alexandria/SKILL.md` — default skill for dev research
- Firecrawl CLI installed globally (`firecrawl-cli` 1.26.3), auth persists from Oct 9 setup
- Workflow: `firecrawl search --sources alexandria` (free) → `firecrawl find-tools` (free) → `firecrawl scrape --alexandria` (paid, report cost)
- Finding: Alexandria has NO PDF generation capabilities (data layer, not service marketplace)

## Neatlogs / Master — CURRENT ✅
- Repo clean, pushed. Only `.entire/settings.json` modified (intentionally uncommitted).
- Neatlogs tracing in `truthops/tracing.py` with graceful degradation. Northstar trace `56854be2d90692200e737e2b802fe1f0` recorded.

## PENDING (not started)
1. **Live-credit calibration runs** — 5 claims with real API keys, one at a time, validating spend vs cfo.ai model:
   - Per-investigation: Starter $2.364 / Professional $1.154 / Enterprise $0.964
   - TruthScan: 25 free/mo, then $24/mo for 1,000, $0.03 excess
   - Claims: (1) Mamdani/Epstein photos 0–5, (2) Trump SSA audit 10–20, (3) Trump 8 wars 30–45, (4) Gas <$2.30 80–90, (5) Mamdani NYC mayor 90–100
   - Pipeline currently uses FixtureAdapter — needs live adapter wiring for GPTZero/TruthScan/Alexandria
   - TruthScan API key: pasted transiently Oct 10, NOT stored — will need again
   - Claim 4 still needs FactCheck.org article verification
2. **Demo video** (≤3 min) — after live runs
3. **Monday submission** — window 8:30 AM–1:25 PM CDT Oct 12
4. **Entire hook PATH** — CLI not on hook PATH, checkpoint visibility unverified
5. **Workbook cleanup** — local spreadsheet needs per-tier GPTZero rewrite to match cfo.ai
6. **Social/X** — PARKED until Demo reopens
