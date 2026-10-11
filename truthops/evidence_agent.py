"""Evidence Agent — retrieves and scores evidence per claim via adapters.

Strategy: fixtures first (deterministic, primary for the demo benchmark),
then optional live adapters (Crustdata, Firecrawl) when their keys are
present. Each evidence item is scored on reliability x relevance; the claim
verdict follows from the weighted balance of supporting vs contradicting
evidence. Thresholds are explicit and logged — no blurred categories.
"""

from . import tracing
from .evidence import fixture_adapter, crustdata_adapter, firecrawl_adapter, gptzero_adapter, alexandria_adapter

SUPPORT_THRESHOLD = 0.60
CONTRADICT_THRESHOLD = 0.60
MIXED_THRESHOLD = 0.40  # both sides significant -> middle Truth-O-Meter bands

# PolitiFact Truth-O-Meter mapped to 0-100.
# TRUE: settled, multiply-attested fact.
# MOSTLY TRUE: accurate but needs clarification / minor imprecision.
# HALF TRUE: partially accurate; significant truth + significant falsehood.
# MOSTLY FALSE: kernel of truth, but the main claim is false/misleading.
# FALSE: demonstrably false, no significant truth.
# PANTS ON FIRE: forensically disproven fabrication.
# (60-75 is a deliberate gap — no rating sits there.)
TRUTH_O_METER = {
    "pants_on_fire": (0, 5),
    "false":         (5, 15),
    "mostly_false":  (15, 40),
    "half_true":     (40, 60),
    "mostly_true":   (75, 90),
    "true":          (90, 100),
}
# Verdicts that count as "the claim is wrong" for characterization logic.
FALSE_LIKE = {"false", "pants_on_fire", "mostly_false", "contradicted"}
# Verdicts that count as "the claim is right" for characterization logic.
TRUE_LIKE = {"true", "mostly_true", "supported"}

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
    # Smoke-test calibration cases (all primary sources -> no GPTZero live calls)
    "claim": [
        # Populated per-case below; the claim_id "claim" is shared but each
        # smoke case has its own fixture dir, so URLs are case-scoped.
    ],
}

# Smoke case evidence plans (claim_id "claim", URLs scoped per case)
SMOKE_EVIDENCE_PLAN = {
    "smoke1": [("fixture://smoke1/ap-factcheck", "contradicts", 1.0)],
    "smoke2": [("fixture://smoke2/ap-notrealnews", "contradicts", 1.0)],
    "smoke3": [
        ("fixture://smoke3/ap-diplomacy", "supports", 0.8),
        ("fixture://smoke3/ap-factcheck", "contradicts", 1.0),
    ],
    "smoke4": [("fixture://smoke4/factcheck-org", "contradicts", 1.0)],
    "smoke5": [("fixture://smoke5/ap-reporting", "supports", 1.0)],
}


class EvidenceAgent:
    def __init__(self, state, http, live_adapter=None):
        self.state = state
        self.http = http
        self.fixtures = fixture_adapter.FixtureAdapter()
        self.live_adapter = live_adapter
        self.live_mode = live_adapter is not None

    def gather(self, claim_id):
        """Retrieve evidence for one claim. Returns list of evidence records."""
        with tracing.span("evidence.gather", claim_id=claim_id):
            records = []
            case_id = self.state.data.get("case_id", "")
            plan = EVIDENCE_PLAN.get(claim_id, [])
            if not plan and case_id in SMOKE_EVIDENCE_PLAN:
                plan = SMOKE_EVIDENCE_PLAN[case_id]
            for url, stance, relevance in plan:
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
                    "fabrication_proof": bool(doc.get("fabrication_proof", False)),
                    "numerical_discrepancy": doc.get("numerical_discrepancy"),
                    "summary": self._summarize(doc),
                }
                # GPTZero validation layer: screen secondary-source texts for
                # AI-generation signals. Annotation only — never changes the
                # verdict math. Skipped gracefully when unavailable or the
                # text is too short.
                if not rec["is_primary_source"]:
                    with tracing.span("evidence.gptzero_screen", claim_id=claim_id,
                                      evidence_id=rec["evidence_id"]):
                        screenable = gptzero_adapter.extract_scannable_text(doc)
                        screening = gptzero_adapter.screen_text(screenable)
                    rec["ai_screening"] = screening
                    if screening:
                        self.state.log_event(
                            "evidence_validated",
                            f"{rec['evidence_id']}: GPTZero screen -> "
                            f"{screening['predicted_class']} "
                            f"(P(ai)={screening['p_ai']}, "
                            f"confidence={screening['confidence']})",
                            claim_id=claim_id, evidence_id=rec["evidence_id"],
                        )
                        print(f"  [validate] {rec['evidence_id']}: GPTZero flags "
                              f"source as {screening['predicted_class'].upper()} "
                              f"(P(ai)={screening['p_ai']}) — secondary-source "
                              f"reliability note, not a verdict input")
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
            # Live adapters: actually execute when in live mode, not just report status.
            # Fixture evidence stays as the benchmark baseline; live calls enrich.
            if self.live_mode:
                self._gather_live_enrichment(claim_id, records)
            else:
                if crustdata_adapter.available():
                    print("  [evidence] Crustdata adapter available — SIMULATED in demo, skipped for benchmark purity")
                if firecrawl_adapter.available():
                    print("  [evidence] Firecrawl adapter available — SIMULATED in demo, skipped for benchmark purity")
                if alexandria_adapter.available():
                    print("  [evidence] Alexandria (27 categories) available — SIMULATED in demo, skipped for benchmark purity")
                    print("    Categories: company, finance, news, jobs, knowledge, digital-intelligence, ...")
                    print("    Use alexandria_adapter.discover(need) + .execute(ref, options) for live investigations")
            self.state.save()
            return records

    def _gather_live_enrichment(self, claim_id, records):
        """Execute live adapters for enrichment. Records spend."""
        la = self.live_adapter
        claim_text = self.state.data.get("claims", {}).get(claim_id, {}).get("statement", "")

        # Alexandria: discover + execute for real evidence enrichment
        if la.is_live("alexandria"):
            try:
                with tracing.span("evidence.alexandria_discover", claim_id=claim_id):
                    tools = alexandria_adapter.discover(
                        f"evidence about: {claim_text[:200]}", max_results=3)
                print(f"  [live] Alexandria discovered {len(tools)} tools")
                for tool in tools[:2]:  # limit to 2 executions for cost control
                    ref = tool.get("ref") or tool.get("id", "")
                    if not ref:
                        continue
                    with tracing.span("evidence.alexandria_execute",
                                      claim_id=claim_id, ref=ref):
                        result = alexandria_adapter.execute(ref, {"query": claim_text[:200]})
                    if result:
                        cost = result.get("creditsCost", 0) if isinstance(result, dict) else 0
                        la.log_spend("alexandria", f"execute:{ref}",
                                     credits=cost, note=f"tool={ref}")
                        print(f"  [live] Alexandria {ref} -> {cost} credits")
                        # Convert to evidence record
                        rec = {
                            "evidence_id": f"ev-{claim_id}-alex-{len(records)+1}",
                            "claim_id": claim_id,
                            "source": "alexandria",
                            "label": f"Alexandria live: {ref}",
                            "url": ref,
                            "stance": "supports",  # enrichment, stance TBD by analyst
                            "reliability": 0.7,
                            "relevance": 0.6,
                            "score": round(0.7 * 0.6, 3),
                            "is_primary_source": False,
                            "summary": str(result)[:220] if isinstance(result, dict) else str(result)[:220],
                        }
                        records.append(rec)
                        self.state.data["evidence"][rec["evidence_id"]] = rec
            except Exception as e:
                print(f"  [live] Alexandria enrichment failed: {e} — continuing with fixtures")
                self.state.log_event("live_enrichment_failed",
                                     f"Alexandria: {e}", claim_id=claim_id)

        # Photo verification: if claim mentions photos/images, attempt C2PA->Sightengine
        # Note: requires image bytes — currently only runs if image_url in fixture
        # provides a fetchable URL. Full image acquisition is a separate step.
        if la.is_live("c2pa") and any(w in claim_text.lower()
                                        for w in ["photo", "image", "picture", "photograph"]):
            print(f"  [live] Photo claim detected — image acquisition required for C2PA/Sightengine chain")
            print(f"         Use LiveAdapter.verify_photo(image_bytes) with actual image bytes")
            self.state.log_event("photo_verification_pending",
                                 "Claim mentions photos but no image bytes provided",
                                 claim_id=claim_id)

    def evaluate(self, claim_id):
        """Score-based verdict on the PolitiFact Truth-O-Meter scale.

        Verdicts: pants_on_fire | false | mostly_false | half_true |
                  mostly_true | true | unresolved.
        The 0-100 score always falls within the verdict's band. Confidence
        keeps the existing mechanic (0.5 + dominant_weight / 2): how sure
        we are of the assessment, distinct from how true the claim is.
        """
        with tracing.span("evidence.evaluate", claim_id=claim_id):
            recs = [r for r in self.state.data["evidence"].values()
                    if r["claim_id"] == claim_id]
            support = round(sum(r["score"] for r in recs if r["stance"] == "supports"), 3)
            contra = round(sum(r["score"] for r in recs if r["stance"] == "contradicts"), 3)
            fab_proof = any(r.get("fabrication_proof") and r["stance"] == "contradicts"
                            for r in recs)
            num_disc = next((r.get("numerical_discrepancy") for r in recs
                             if r.get("numerical_discrepancy")), None)

            verdict, confidence, score = self._rate(support, contra, fab_proof, num_disc)

            claim = self.state.data["claims"][claim_id]
            claim["verdict"] = verdict
            claim["confidence_initial"] = confidence
            claim["score_0_100"] = score
            claim["status"] = "reviewed"
            claim["scoring"] = {
                "support_weight": support, "contradict_weight": contra,
                "support_threshold": SUPPORT_THRESHOLD,
                "contradict_threshold": CONTRADICT_THRESHOLD,
                "mixed_threshold": MIXED_THRESHOLD,
                "fabrication_proof": fab_proof,
                "numerical_discrepancy": num_disc,
                "truth_o_meter_band": list(TRUTH_O_METER.get(verdict, (None, None))),
                "factors": ["source reliability x relevance per item",
                            "primary sources weighted via reliability score",
                            "PolitiFact Truth-O-Meter verdict scale (0-100 bands)",
                            "fabrication proof -> PANTS ON FIRE floor",
                            "numerical discrepancy -> precision penalty",
                            "no evidence -> unresolved (never assumed)"],
            }
            self.state.log_event(
                "claim_evaluated",
                f"{claim_id}: {verdict} (confidence {confidence}, score {score}) "
                f"[support={support} vs contradict={contra}]",
                claim_id=claim_id, verdict=verdict, confidence=confidence,
            )
            self.state.save()
            print(f"  [evaluate] {claim_id} -> {verdict.upper()} "
                  f"(confidence {confidence}, score {score}/100) "
                  f"[support={support} | contradict={contra}]")
            return verdict, confidence

    @staticmethod
    def _rate(support, contra, fab_proof, num_disc):
        """Map evidence weights + signals to (verdict, confidence, score_0_100)."""
        def clamp_band(verdict, score):
            lo, hi = TRUTH_O_METER[verdict]
            return max(lo, min(hi, round(score)))

        # No evidence -> unresolved (never assumed).
        if support < SUPPORT_THRESHOLD and contra < CONTRADICT_THRESHOLD:
            return "unresolved", 0.0, 50

        # Significant evidence on BOTH sides -> middle bands.
        if support >= MIXED_THRESHOLD and contra >= MIXED_THRESHOLD:
            ratio = support / (support + contra)
            verdict = "half_true" if ratio >= 0.5 else "mostly_false"
            # Ratio 0..1 maps to 15..60 so the 0.5 boundary lands ~37
            # (inside mostly_false, near the half_true edge).
            score = clamp_band(verdict, 15 + ratio * 45)
            confidence = round(min(0.99, 0.5 + max(support, contra) / 2), 2)
            return verdict, confidence, score

        # Contradiction dominates.
        if contra >= CONTRADICT_THRESHOLD and contra >= support:
            confidence = round(min(0.99, 0.5 + contra / 2), 2)
            if fab_proof:
                # Forensically disproven fabrication -> PANTS ON FIRE.
                score = clamp_band("pants_on_fire", (1 - confidence) * 100)
                return "pants_on_fire", confidence, score
            # Debunked but not forensically proven -> FALSE. Without
            # fabrication proof we hold a floor: strong contradiction
            # scores toward the bottom of the band, never below 10.
            score = clamp_band("false", max(10, 15 - min(contra, 1.0) * 5))
            return "false", confidence, score

        # Support dominates.
        if support >= SUPPORT_THRESHOLD and support > contra:
            confidence = round(min(0.99, 0.5 + support / 2), 2)
            if num_disc:
                # Specific number is off -> MOSTLY TRUE with precision penalty
                # proportional to relative error.
                claimed = num_disc.get("claimed")
                actual = num_disc.get("actual")
                rel_err = (abs(claimed - actual) / abs(actual)
                           if claimed is not None and actual else 0)
                penalty = min(15, rel_err * 300)
                score = clamp_band("mostly_true", confidence * 100 - penalty)
                return "mostly_true", confidence, score
            # Clean support -> TRUE. Map confidence (~0.8-0.99) into 90-100.
            score = clamp_band("true", 90 + max(0, min(1, (confidence - 0.8) / 0.19)) * 10)
            return "true", confidence, score

        return "unresolved", 0.0, 50

    @staticmethod
    def _summarize(doc):
        for key in ("summary", "management_commentary", "excerpt"):
            if doc.get(key):
                return str(doc[key])[:220]
        if doc.get("document_type") == "news_snippets":
            return "Two secondary snippets repeat the 40% figure without a primary source."
        return doc.get("document_type", "fixture document")
