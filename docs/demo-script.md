# TruthOps — Demo Video Script (≤3 minutes)

Target: ~400 spoken words. Record the terminal run live; cut between the
beats below. Every beat below corresponds to real, visible output from
`python -m truthops run --case northstar`.

---

**[0:00–0:15] HOOK**
"Don't just detect misinformation. Resolve it. I'm Demo, solo builder of
TruthOps — a transparent scoring and governance pipeline over curated evidence. Existing tools flag a
viral claim as 'possible misinformation' and stop, leaving comms teams to
do the actual investigation by hand. TruthOps closes the loop."

**[0:15–0:35] THE CASE**
"Here's the benchmark: Northstar Cloud allegedly lost 40% of its enterprise
customers after a security incident — and concealed it. One allegation,
five atomic claims. Watch the Trust Director decompose it and choose its
next move per claim — gather, verify, escalate, or conclude. No fixed
pipeline."

**[0:35–1:30] THE RUN (live terminal)**
- Claims decompose on screen.
- "Mid-run, the primary filing fetch fails — HTTP 503. State is preserved,
  the agent retries, and recovers. That's not a demo trick; it's
  deterministic, every run."
- "Now the contrarian agent attacks the initial conclusion — and it
  disagrees twice. Each disagreement forces targeted re-verification, not
  a full re-run. Confidence on customer decline drops from 99 to 65
  percent. Both the initial and revised numbers stay in the report."
- "Final verdicts: incident — supported. Some decline — supported. The 40%
  figure — contradicted by the primary filing, which shows 4.2%. Deliberate
  concealment — unresolved; the agent refuses to assert intent without
  evidence. Overall characterization: misleading."
- "One more validation layer: the evidence agent screens secondary sources
  with GPTZero. The outlets spreading the 40% figure get flagged as likely
  AI-generated — a reliability note on the source, not a verdict input."
- "And before any of that runs, a sniff test gates the pipeline: a cheap
  decision-model check that stops obvious fakes before we spend a dollar on
  Firecrawl and GPTZero. The heuristic runs today; Cloudflare's open-source
  Clef decision model plugs in as the backend when we want typed
  probabilities instead of regex."

**[1:30–2:00] THE GATE**
"The response plan is drafted — but publish, post, and notify are all
blocked behind a human approval gate. The agent investigates; the human
decides. That's the line."

**[2:00–2:40] SPONSOR PROOF**
- "Every agent step is traced in neatlogs — the 503, the retry, the
  contrarian challenge, all as spans."
- "Entire checkpoints tie each commit to the session behind it."
- "And the business model is real: cfo.ai puts unit cost at 56 cents per
  investigation — six cents of that is Firecrawl evidence retrieval —
  with 94-plus percent gross margins."

**[2:40–3:00] CLOSE**
"TruthOps: don't just detect misinformation. Resolve it. Repo link below —
built solo at neatHack, October 2026."

---

## B-roll / overlay notes
- Overlay the final JSON report's claim table during [1:15–1:30].
- Overlay the neatlogs trace view during [2:00–2:15].
- Overlay the Entire checkpoint during [2:15–2:25].
- Overlay the cfo.ai unit-economics table during [2:25–2:40].
- Keep the terminal font large (18pt+) for legibility.
