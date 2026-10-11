# neatlogs Tracing Proof — TruthOps

**Integration:** https://github.com/Mike-Demo/truthops/blob/main/truthops/tracing.py
**Dashboard:** https://neatlogs.com (traces viewable with project API key)
**Exported:** Oct 11, 2026

## What was traced

Every TruthOps pipeline run emits OpenTelemetry spans to neatlogs. Each of the 28 calibration claims ran end-to-end with live tracing enabled — **28/28 trace IDs captured**.

Spans cover the full pipeline:
- `sniff_test` — Cloudflare Clef-flash gate
- `evidence_gathering` — per-source spans (fixtures, GPTZero screening, Alexandria search, Sightengine)
- `photo_forensics` — C2PA + Sightengine AI detection (photo claims)
- `contrarian_review` — scripted adversarial challenge
- `director_verdict` — weighted scoring → Truth-O-Meter verdict
- `approval_gate` — human approval check (BLOCKED by default)

## Trace IDs (28/28)

| Claim | Trace ID | Verdict | Score |
|-------|----------|---------|-------|
| smoke1 | `58fd5ddd35424e8716f8dda25a55d1cb` | pants_on_fire | 1 |
| smoke2 | `9b6d1038f52aee57f0f5925c6c21d105` | false | 10 |
| smoke3 | `83c016c983bb2adbb4b82bf989df9ff9` | mostly_false | 34 |
| smoke4 | `9b3e2804f621e822913e74b2b60964df` | false | 10 |
| smoke5 | `a305ac812603a4cce4a905ea02409d43` | true | 99 |
| smoke6 | `e1d537f027e6822c4e0f14aa52eef8b8` | mostly_true | 78 |
| smoke7 | `ef04ea4550fb104c1d71c92ffd37d78d` | mostly_true | 88 |
| smoke8 | `6c6ad276061aa0116d6dfddcdeba3ead` | mostly_true | 90 |
| smoke9 | `14f5613552ef9bd25fa6ead1a991f854` | false | 10 |
| smoke10 | `e0db217e0e51b16ea3e8f2b968d31f6c` | false | 10 |
| smoke11 | `32fdcf08620d3c9446505331490ad98b` | false | 10 |
| smoke12 | `73c23592e94af5e303cf1f1339714022` | false | 10 |
| smoke13 | `ce16c2d4eb13b8ab9d41a68fecbb53de` | false | 10 |
| smoke14 | `bf4168b8f77bfaccd7236edade0e150c` | false | 10 |
| smoke15 | `7966416da3f51dc32fae0e33700834c9` | false | 10 |
| smoke16 | `8a2e37404c749da9ef43f2857b4c6f47` | false | 10 |
| smoke17 | `e2d51651b5335ef2ab426dd882530e4c` | false | 10 |
| smoke18 | `1e747e81aaf3bfd88fc2b1b10aab7475` | false | 10 |
| smoke19 | `fd9b61668b10e6c6609f6f1f848aa2a6` | false | 10 |
| smoke20 | `0485e328244771a74edcd77a3e13a120` | false | 10 |
| smoke21 | `5ee34705cf67c5abba2defc0df230c7c` | false | 10 |
| smoke22 | `5f6d010a4c173ac80e56fe9c3f2aa6d0` | mostly_false | 35 |
| smoke23 | `e7f4efee6284d75c3fceb4b67990a29a` | mostly_false | 35 |
| smoke24 | `371dacc7e9e18631b75134fa38f74b67` | mostly_false | 35 |
| smoke25 | `3ee64b16f26f58df39e35f2d7c20b1cb` | mostly_false | 35 |
| smoke26 | `6b8917f108caf2d3457d8fcd1db37788` | false | 10 |
| smoke27 | `9c0321f8bfbf7788b2ba093c270c72d8` | mostly_false | 35 |
| smoke28 | `45020f72b2d5877da7dfe2e18f166149` | true | 99 |

## How to verify

1. Each trace ID above appears in the corresponding `artifacts/truthops-report-smoke{N}.json` under `neatlogs_trace_id`.
2. The dashboard at https://truthops-demo.space.fast/claims.html shows the first 16 chars of each trace ID on every claim card.
3. Paste any full trace ID into the neatlogs dashboard search to see the span waterfall.

## Code references

- `truthops/tracing.py` — OpenTelemetry setup, neatlogs exporter, `get_tracer()` / span helpers
- `truthops/__main__.py` — trace ID captured per run, written to report JSON header
- Trace ID format: 32-char hex (OpenTelemetry `span.get_span_context().trace_id`)

## Notes

- The neatlogs API key used during the hackathon was intentionally exposed in terminal recordings (documented in README Security note). It will be rotated after the event.
- Early footage (smoke7-live.mp4) shows "traces disabled" — it predates the tracing fix. All 28 current reports carry live trace IDs.
