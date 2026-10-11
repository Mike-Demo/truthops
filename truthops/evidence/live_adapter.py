"""Live adapter — wires real evidence adapters into the TruthOps pipeline.

Used with `python -m truthops run --case <id> --live`. The benchmark evidence
plan stays fixture-backed (deterministic, comparable across runs); the live
adapters enrich via their own call paths:

- GPTZero: AI-text screening on secondary sources (evidence_agent calls
  gptzero_adapter.screen_text directly; auth via the stored custom.gptzero
  connector through the gptzero-scan CLI — no env var needed).
- Sightengine: Phase-2 photo AI detection (SIGHTENGINE_API_USER/_SECRET env vars).
- C2PA: Phase-1 photo provenance, local via c2pa-python (no key).
- Alexandria: evidence enrichment via Firecrawl CLI auth (27 categories).

Each adapter degrades gracefully and independently: if its credential or
dependency is missing, that adapter reports "fixture" mode and its live path
is skipped. Nothing here raises on missing keys.

Spend tracking: every billable live call should go through
LiveAdapter.log_spend() so the run's JSON report carries per-adapter
credits/calls/cost. No live calls are made by this module itself.
"""

from __future__ import annotations

import os

from .fixture_adapter import FixtureAdapter
from . import gptzero_adapter, sightengine_adapter, c2pa_adapter, alexandria_adapter


class LiveAdapter:
    name = "live"
    label = "Live adapters (fixture-backed evidence, live enrichment)"

    def __init__(self):
        self.fixtures = FixtureAdapter()
        self.spend_log: list[dict] = []
        self._status = self._probe()

    # -- HttpClient interface (fixture-backed) ---------------------------
    def fetch(self, url):
        return self.fixtures.fetch(url)

    def search(self, query):
        return self.fixtures.search(query)

    # -- availability probing (no network, no spend) ---------------------
    def _probe(self) -> dict:
        status = {}

        # GPTZero: CLI presence; auth is via the stored connector.
        if gptzero_adapter.available():
            status["gptzero"] = {
                "mode": "live",
                "detail": "gptzero-scan CLI present; auth via stored connector",
            }
        else:
            status["gptzero"] = {
                "mode": "fixture",
                "detail": "gptzero-scan CLI missing — AI screening skipped",
            }

        # Sightengine: needs SIGHTENGINE_API_USER + SIGHTENGINE_API_SECRET env vars.
        if os.environ.get("SIGHTENGINE_API_USER") and os.environ.get("SIGHTENGINE_API_SECRET"):
            status["sightengine"] = {
                "mode": "live",
                "detail": "Sightengine credentials set — photo AI detection available",
            }
        else:
            status["sightengine"] = {
                "mode": "fixture",
                "detail": "Sightengine credentials not set — photo scans skipped",
            }

        # C2PA: local library, no key.
        try:
            import c2pa  # noqa: F401
            status["c2pa"] = {
                "mode": "live",
                "detail": "c2pa-python installed — provenance checks available",
            }
        except ImportError:
            status["c2pa"] = {
                "mode": "fixture",
                "detail": "c2pa-python not installed — provenance checks skipped",
            }

        # Alexandria: Firecrawl CLI auth.
        if alexandria_adapter.available():
            status["alexandria"] = {
                "mode": "live",
                "detail": "firecrawl-cli available — primary-source search callable (paid per use)",
            }
        else:
            status["alexandria"] = {
                "mode": "fixture",
                "detail": "firecrawl-cli unavailable — enrichment skipped",
            }

        return status

    def status(self) -> dict:
        """Per-adapter live/fixture status. Safe to call repeatedly."""
        return self._status

    def is_live(self, adapter: str) -> bool:
        return self._status.get(adapter, {}).get("mode") == "live"

    def print_status(self):
        print("  [live] adapter status:")
        for name, info in self._status.items():
            mark = "LIVE" if info["mode"] == "live" else "fixture"
            print(f"    {name:12s} {mark:8s} — {info['detail']}")

    # -- spend tracking ---------------------------------------------------
    def log_spend(self, adapter: str, operation: str, calls: int = 1,
                  credits: float = 0.0, usd: float = 0.0, note: str = ""):
        """Record one billable (or free) live-adapter call."""
        self.spend_log.append({
            "adapter": adapter,
            "operation": operation,
            "calls": calls,
            "credits": credits,
            "usd": round(usd, 4),
            "note": note,
        })

    def spend_summary(self) -> dict:
        """Aggregate spend per adapter for the run report."""
        summary: dict[str, dict] = {}
        for entry in self.spend_log:
            name = entry["adapter"]
            agg = summary.setdefault(name, {"calls": 0, "credits": 0.0,
                                            "usd": 0.0, "operations": []})
            agg["calls"] += entry["calls"]
            agg["credits"] += entry["credits"]
            agg["usd"] = round(agg["usd"] + entry["usd"], 4)
            if entry["operation"] not in agg["operations"]:
                agg["operations"].append(entry["operation"])
        return summary

    # -- photo verification chain (C2PA -> Sightengine) -------------------
    def verify_photo(self, image_bytes: bytes, image_url: str = "") -> dict:
        """Two-phase photo verification. Returns evidence-ready dicts.

        Phase 1 (free, local): C2PA provenance.
        Phase 2 (free tier): Sightengine AI detection — only when Phase 1 is
        inconclusive AND Sightengine credentials are configured. Never spends
        without the credentials.
        """
        out: dict = {"phase1": None, "phase2": None, "spend_usd": 0.0}

        # Phase 1: C2PA (free)
        p1 = c2pa_adapter.check_provenance(image_bytes)
        out["phase1"] = c2pa_adapter.provenance_to_evidence(p1, image_url)
        self.log_spend("c2pa", "check_provenance", note=p1.get("signal", ""))

        # Phase 2: Sightengine — only if Phase 1 didn't verify AND creds exist.
        if p1.get("signal") != "provenance_verified" and self.is_live("sightengine"):
            scan = sightengine_adapter.scan_image(image_bytes)
            out["phase2"] = sightengine_adapter.scan_to_evidence(scan, image_url)
            # Sightengine free tier: 2,000 ops/month, no time limit.
            self.log_spend("sightengine", "scan_image",
                           note=f"verdict={scan.get('verdict')}")
        elif p1.get("signal") != "provenance_verified":
            out["phase2"] = {"skipped": True,
                             "reason": "Sightengine credentials not set"}
        return out
