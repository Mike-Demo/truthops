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
    "smoke6": [("fixture://smoke6/politifact", "supports", 1.0)],
    "smoke7": [("fixture://smoke7/politifact", "supports", 1.0)],
    "smoke8": [("fixture://smoke8/politifact", "supports", 1.0)],
    "smoke9": [("fixture://smoke9/factcheck", "contradicts", 1.0)],
    "smoke10": [("fixture://smoke10/factcheck", "contradicts", 1.0)],
    "smoke11": [("fixture://smoke11/factcheck", "contradicts", 1.0)],
    "smoke12": [("fixture://smoke12/factcheck", "contradicts", 1.0)],
    "smoke13": [("fixture://smoke13/factcheck", "contradicts", 1.0)],
    "smoke14": [("fixture://smoke14/factcheck", "contradicts", 1.0)],
    "smoke15": [("fixture://smoke15/factcheck", "contradicts", 1.0)],
    "smoke16": [("fixture://smoke16/factcheck", "contradicts", 1.0)],
    "smoke17": [("fixture://smoke17/factcheck", "contradicts", 1.0)],
    "smoke18": [("fixture://smoke18/factcheck", "contradicts", 1.0)],
    "smoke19": [("fixture://smoke19/factcheck", "contradicts", 1.0)],
    "smoke20": [("fixture://smoke20/factcheck", "contradicts", 1.0)],
    "smoke21": [("fixture://smoke21/factcheck", "contradicts", 1.0)],
    "smoke22": [
        ("fixture://smoke22/reporting-support", "supports", 0.8),
        ("fixture://smoke22/factcheck-contra", "contradicts", 1.0),
    ],
    "smoke23": [
        ("fixture://smoke23/reporting-support", "supports", 0.8),
        ("fixture://smoke23/factcheck-contra", "contradicts", 1.0),
    ],
    "smoke24": [
        ("fixture://smoke24/reporting-support", "supports", 0.8),
        ("fixture://smoke24/factcheck-contra", "contradicts", 1.0),
    ],
    "smoke25": [
        ("fixture://smoke25/reporting-support", "supports", 0.8),
        ("fixture://smoke25/factcheck-contra", "contradicts", 1.0),
    ],
    "smoke26": [("fixture://smoke26/factcheck", "contradicts", 1.0)],
    "smoke27": [
        ("fixture://smoke27/reporting-support", "supports", 0.8),
        ("fixture://smoke27/factcheck-contra", "contradicts", 1.0),
    ],
    "smoke28": [("fixture://smoke28/reporting", "supports", 1.0)],
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
                # AI-generation signals. High P(ai) reduces the source's
                # reliability weight — AI-generated text is less trustworthy
                # as evidence. Skipped gracefully when unavailable or the
                # text is too short.
                if not rec["is_primary_source"]:
                    with tracing.span("evidence.gptzero_screen", claim_id=claim_id,
                                      evidence_id=rec["evidence_id"]):
                        screenable = gptzero_adapter.extract_scannable_text(doc)
                        screening = gptzero_adapter.screen_text(screenable)
                    rec["ai_screening"] = screening
                    if screening:
                        p_ai = screening.get("p_ai", 0) or 0
                        # Weight reliability down by P(ai): a fully AI-generated
                        # source (P=1.0) loses 70% of its reliability weight.
                        # Human-written (P~0) is unaffected.
                        ai_discount = 1.0 - (p_ai * 0.7)
                        old_rel = rec["reliability"]
                        rec["reliability"] = round(old_rel * ai_discount, 3)
                        rec["score"] = round(rec["reliability"] * relevance, 3)
                        self.state.log_event(
                            "evidence_validated",
                            f"{rec['evidence_id']}: GPTZero screen -> "
                            f"{screening['predicted_class']} "
                            f"(P(ai)={screening['p_ai']}, "
                            f"confidence={screening['confidence']}) — "
                            f"reliability {old_rel} -> {rec['reliability']}",
                            claim_id=claim_id, evidence_id=rec["evidence_id"],
                        )
                        print(f"  [validate] {rec['evidence_id']}: GPTZero flags "
                              f"source as {screening['predicted_class'].upper()} "
                              f"(P(ai)={screening['p_ai']}) — reliability "
                              f"{old_rel} -> {rec['reliability']}")
                records.append(rec)
                self.state.data["evidence"][rec["evidence_id"]] = rec
                self.state.log_event(
                    "evidence_scored",
                    f"{rec['evidence_id']}: {stance} (reliability={reliability}, "
                    f"relevance={relevance}, score={score})",
                    claim_id=claim_id, evidence_id=rec["evidence_id"],
                )
                print(f"  [evidence] {rec['evidence_id']} {stance} "
                      f"| rel={rec['reliability']} x relv={relevance} -> score={rec['score']} "
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
                    print("    Use alexandria_adapter.search_primary_sources(query) for live investigations")
            self.state.save()
            return records

    def _gather_live_enrichment(self, claim_id, records):
        """Execute live adapters for enrichment. Records spend."""
        la = self.live_adapter
        claim_text = self.state.data.get("claims", {}).get(claim_id, {}).get("statement", "")

        # Alexandria: search for primary sources that support/disprove the claim
        if la.is_live("alexandria"):
            try:
                with tracing.span("evidence.alexandria_search", claim_id=claim_id):
                    sources = alexandria_adapter.search_primary_sources(
                        claim_text[:200], max_results=3)
                print(f"  [live] Alexandria found {len(sources)} primary sources")
                for src in sources[:2]:  # limit to 2 for cost control
                    url = src.get("url", "")
                    if not url:
                        continue
                    with tracing.span("evidence.alexandria_scrape",
                                      claim_id=claim_id, url=url):
                        scraped = alexandria_adapter.scrape_source(url)
                    content = (scraped.get("content", "") if scraped
                               else src.get("snippet", ""))
                    la.log_spend("alexandria", "search+scrape",
                                 note=f"url={url[:60]}")
                    print(f"  [live] Alexandria source: {src.get('title', '')[:60]}")
                    # Convert to evidence record
                    rec = {
                        "evidence_id": f"ev-{claim_id}-alex-{len(records)+1}",
                        "claim_id": claim_id,
                        "source": "alexandria",
                        "label": f"Alexandria: {src.get('title', url)[:80]}",
                        "url": url,
                        "stance": "neutral",  # stance TBD by analyst
                        "reliability": 0.7,
                        "relevance": 0.6,
                        "score": round(0.7 * 0.6, 3),
                        "is_primary_source": True,
                        "summary": content[:220] if content else src.get("snippet", "")[:220],
                    }
                    records.append(rec)
                    self.state.data["evidence"][rec["evidence_id"]] = rec
            except Exception as e:
                print(f"  [live] Alexandria enrichment failed: {e} — continuing with fixtures")
                self.state.log_event("live_enrichment_failed",
                                     f"Alexandria: {e}", claim_id=claim_id)

        # Photo verification: if claim mentions photos/images, acquire the image
        # and run the C2PA -> Sightengine chain via LiveAdapter.verify_photo().
        if la.is_live("c2pa") and any(w in claim_text.lower()
                                        for w in ["photo", "image", "picture", "photograph"]):
            try:
                with tracing.span("evidence.photo_acquire", claim_id=claim_id):
                    image_url, image_bytes = self._acquire_claim_image(
                        claim_text, claim_id)
                if image_bytes:
                    print(f"  [live] Photo acquired ({len(image_bytes)} bytes) — "
                          f"running C2PA/Sightengine chain")
                    with tracing.span("evidence.photo_verify", claim_id=claim_id):
                        photo_result = la.verify_photo(image_bytes, image_url)
                    self._add_photo_evidence(claim_id, records,
                                             photo_result, image_url)
                else:
                    print(f"  [live] Photo claim detected — no fetchable image "
                          f"found for C2PA/Sightengine chain")
                    self.state.log_event("photo_verification_pending",
                                         "Claim mentions photos but no image "
                                         "bytes acquired",
                                         claim_id=claim_id)
            except Exception as e:
                print(f"  [live] Photo verification failed: {e} — continuing")
                self.state.log_event("photo_verification_failed", str(e),
                                     claim_id=claim_id)

    def _acquire_claim_image(self, claim_text, claim_id):
        """Find and download an image related to the claim.

        Returns (image_url, image_bytes) or (None, None) if no image found.
        Strategy: search for the claim topic + image, take the first
        fetchable image URL from results.
        """
        import urllib.request
        import urllib.parse

        # Search for images related to the claim
        query = claim_text[:150] + " photo image"
        image_url = None

        # Try Firecrawl search for image URLs
        try:
            result = firecrawl_adapter.search(query, limit=5)
            # Handle dict response format: {'data': {'web': [...]}}
            items = []
            if isinstance(result, dict):
                items = result.get("data", {}).get("web", [])
            elif isinstance(result, list):
                items = result
            for r in items:
                if isinstance(r, str):
                    url = r
                else:
                    url = r.get("url", "")
                # Look for direct image links
                if any(url.lower().endswith(ext)
                       for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
                    image_url = url
                    break
            # If no direct image URL, try scraping the first result for images
            if not image_url and items:
                first = items[0]
                page_url = first if isinstance(first, str) else first.get("url", "")
                if page_url:
                    image_url = self._extract_image_from_page(page_url)
        except Exception:
            pass

        if not image_url:
            return None, None

        # Download the image
        try:
            req = urllib.request.Request(
                image_url,
                headers={"User-Agent": "TruthOps/1.0 (fact-checking research)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if not content_type.startswith("image/"):
                    return None, None
                image_bytes = resp.read()
                # Sanity check: not too small, not too large (50MB max)
                if len(image_bytes) < 1024 or len(image_bytes) > 50 * 1024 * 1024:
                    return None, None
                return image_url, image_bytes
        except Exception:
            return None, None

    def _extract_image_from_page(self, page_url):
        """Scrape a web page for the first suitable image URL."""
        import urllib.request
        import re

        try:
            req = urllib.request.Request(
                page_url,
                headers={"User-Agent": "TruthOps/1.0 (fact-checking research)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            # Look for og:image first (usually the main article image)
            og_match = re.search(
                r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
                html, re.IGNORECASE)
            if og_match:
                return og_match.group(1)

            # Fall back to first <img> with a reasonable URL
            for img_match in re.finditer(
                    r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE):
                src = img_match.group(1)
                if src.startswith("http") and any(
                        ext in src.lower() for ext in
                        [".jpg", ".jpeg", ".png", ".webp"]):
                    # Skip tiny icons/logos
                    if any(skip in src.lower() for skip in
                           ["logo", "icon", "avatar", "1x1", "pixel"]):
                        continue
                    return src
        except Exception:
            pass
        return None

    def _add_photo_evidence(self, claim_id, records, photo_result, image_url):
        """Convert C2PA/Sightengine results into evidence records."""
        # Phase 1: C2PA provenance
        p1 = photo_result.get("phase1")
        if p1 and not p1.get("skipped"):
            rec = {
                "evidence_id": f"ev-{claim_id}-c2pa-1",
                "claim_id": claim_id,
                "source": "c2pa",
                "label": f"C2PA provenance: {image_url[:60]}",
                "url": image_url,
                "stance": ("contradicts" if p1.get("fabrication_proof")
                           else "supports" if p1.get("supports_claims")
                           else "neutral"),
                "reliability": p1.get("source_reliability", 0.5),
                "relevance": 0.8,
                "score": round(p1.get("source_reliability", 0.5) * 0.8, 3),
                "is_primary_source": p1.get("is_primary_source", False),
                "summary": p1.get("summary", "")[:220],
                "fabrication_proof": p1.get("fabrication_proof", False),
            }
            records.append(rec)
            self.state.data["evidence"][rec["evidence_id"]] = rec
            print(f"  [live] C2PA evidence: {rec['stance']} "
                  f"(rel={rec['reliability']})")

        # Phase 2: Sightengine AI detection
        p2 = photo_result.get("phase2")
        if p2 and not p2.get("skipped"):
            rec = {
                "evidence_id": f"ev-{claim_id}-sightengine-1",
                "claim_id": claim_id,
                "source": "sightengine",
                "label": f"Sightengine AI detection: {image_url[:60]}",
                "url": image_url,
                "stance": ("contradicts" if p2.get("fabrication_proof")
                           else "supports" if p2.get("supports_claims")
                           else "neutral"),
                "reliability": p2.get("source_reliability", 0.5),
                "relevance": 0.9,
                "score": round(p2.get("source_reliability", 0.5) * 0.9, 3),
                "is_primary_source": p2.get("is_primary_source", False),
                "summary": p2.get("summary", "")[:220],
                "fabrication_proof": p2.get("fabrication_proof", False),
            }
            records.append(rec)
            self.state.data["evidence"][rec["evidence_id"]] = rec
            print(f"  [live] Sightengine evidence: {rec['stance']} "
                  f"(rel={rec['reliability']}) — {p2.get('summary', '')[:80]}")

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
