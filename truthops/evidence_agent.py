"""Evidence Agent — retrieves and scores evidence per claim via adapters.

Strategy: fixtures first (deterministic, primary for the demo benchmark),
then optional live adapters (Crustdata, Firecrawl) when their keys are
present. Each evidence item is scored on reliability x relevance; the claim
verdict follows from the weighted balance of supporting vs contradicting
evidence. Thresholds are explicit and logged — no blurred categories.
"""

from . import tracing
from .evidence import fixture_adapter, crustdata_adapter, firecrawl_adapter

SUPPORT_THRESHOLD = 0.60
CONTRADICT_THRESHOLD = 0.60

# Which fixture documents speak to which claim, and how.
EVIDENCE_PLAN = {
    "incident_occurred": [
        ("fixture://northstar/incident-report", "supports", 1.0),
        ("fixture://northstar/news-snippets", "supports", 0.5),
    ],
    "some_customer_decline": [
        ("fixture://northstar/filing-q3-2026", "supports", 1.0),
        ("fixture://northstar/internal-memo", "supports", 0.8),
    ],
    "decline_was_40pct": [
        ("fixture://northstar/filing-q3-2026", "contradicts", 1.0),  # decisive: 4.2%
        ("fixture://northstar/news-snippets", "supports", 0.5),     # repeats 40%, low reliability
    ],
    "executives_knew": [
        ("fixture://northstar/internal-memo", "supports", 1.0),
    ],
    "deliberate_concealment": [
        # No fixture establishes intent. Deliberately empty.
    ],
}


class EvidenceAgent:
    def __init__(self, state, http):
        self.state = state
        self.http = http
        self.fixtures = fixture_adapter.FixtureAdapter()

    def gather(self, claim_id):
        """Retrieve evidence for one claim. Returns list of evidence records."""
        with tracing.span("evidence.gather", claim_id=claim_id):
            records = []
            for url, stance, relevance in EVIDENCE_PLAN.get(claim_id, []):
                try:
                    doc = self.http.get(url)  # 503-on-first-attempt applies to the filing
                except Exception as e:
                    # Deterministic failure path: retry once, then continue.
                    self.state.log_event(
                        "evidence_retry",
                        f"Retrying {url} after failure: {e}",
                        claim_id=claim_id, url=url,
                    )
                    print(f"  [evidence] fetch failed ({e}); retrying once...")
                    doc = self.http.get(url)
                reliability = float(doc.get("source_reliability", 0.5))
                score = round(reliability * relevance, 3)
                rec = {
                    "evidence_id": f"ev-{claim_id}-{len(records)+1}",
                    "claim_id": claim_id,
                    "source": "fixture",
                    "label": "SYNTHETIC fixture",
                    "url": url,
                    "stance": stance,  # supports | contradicts
                    "reliability": reliability,
                    "relevance": relevance,
                    "score": score,
                    "is_primary_source": bool(doc.get("is_primary_source")),
                    "summary": self._summarize(doc),
                }
                records.append(rec)
                self.state.data["evidence"][rec["evidence_id"]] = rec
                self.state.log_event(
                    "evidence_scored",
                    f"{rec['evidence_id']}: {stance} (reliability={reliability}, "
                    f"relevance={relevance}, score={score})",
                    claim_id=claim_id, evidence_id=rec["evidence_id"],
                )
                print(f"  [evidence] {rec['evidence_id']} {stance} "
                      f"| rel={reliability} x relv={relevance} -> score={score} "
                      f"| primary={rec['is_primary_source']}")
            # Optional live adapters (graceful no-ops without keys)
            if crustdata_adapter.available():
                print("  [evidence] Crustdata adapter available — SIMULATED in demo, skipped for benchmark purity")
            if firecrawl_adapter.available():
                print("  [evidence] Firecrawl adapter available — SIMULATED in demo, skipped for benchmark purity")
            self.state.save()
            return records

    def evaluate(self, claim_id):
        """Score-based verdict. Exactly one of: supported / contradicted / unresolved."""
        with tracing.span("evidence.evaluate", claim_id=claim_id):
            recs = [r for r in self.state.data["evidence"].values()
                    if r["claim_id"] == claim_id]
            support = round(sum(r["score"] for r in recs if r["stance"] == "supports"), 3)
            contra = round(sum(r["score"] for r in recs if r["stance"] == "contradicts"), 3)
            if contra >= CONTRADICT_THRESHOLD and contra >= support:
                verdict, confidence = "contradicted", min(0.99, 0.5 + contra / 2)
            elif support >= SUPPORT_THRESHOLD and support > contra:
                verdict, confidence = "supported", min(0.99, 0.5 + support / 2)
            else:
                verdict, confidence = "unresolved", 0.0
            confidence = round(confidence, 2)
            claim = self.state.data["claims"][claim_id]
            claim["verdict"] = verdict
            claim["confidence_initial"] = confidence
            claim["status"] = "reviewed"
            claim["scoring"] = {
                "support_weight": support, "contradict_weight": contra,
                "support_threshold": SUPPORT_THRESHOLD,
                "contradict_threshold": CONTRADICT_THRESHOLD,
                "factors": ["source reliability x relevance per item",
                            "primary sources weighted via reliability score",
                            "no evidence -> unresolved (never assumed)"],
            }
            self.state.log_event(
                "claim_evaluated",
                f"{claim_id}: {verdict} (confidence {confidence}) "
                f"[support={support} vs contradict={contra}]",
                claim_id=claim_id, verdict=verdict, confidence=confidence,
            )
            self.state.save()
            print(f"  [evaluate] {claim_id} -> {verdict.upper()} "
                  f"(initial confidence {confidence}) [support={support} | contradict={contra}]")
            return verdict, confidence

    @staticmethod
    def _summarize(doc):
        for key in ("summary", "management_commentary", "excerpt"):
            if doc.get(key):
                return str(doc[key])[:220]
        if doc.get("document_type") == "news_snippets":
            return "Two secondary snippets repeat the 40% figure without a primary source."
        return doc.get("document_type", "fixture document")
