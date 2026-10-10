"""Sniff test — cheap pre-screen before the expensive investigation pipeline.

A full TruthOps investigation costs ~$1.08 (LLM + Firecrawl + GPTZero).
The sniff test costs ~$0.02 and answers: is this allegation worth the full spend?

Decision backend (pluggable):
- heuristic (default): regex + structural rules. Zero API cost. High precision,
  low recall — only stops the slam dunks.
- clef (planned): Cloudflare's open-source decision model (Apache 2.0) via
  Workers AI. Returns typed probabilities (e.g. investigable: 0.97) in ~40ms
  (clef-flash) without burning LLM tokens. See
  https://blog.cloudflare.com/clef-decision-models. Requires
  CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN. Falls back to heuristic
  when credentials are absent.

Short-circuit rules (either backend):
- OBVIOUSLY_FAKE + no traction → STOP. Don't spend $1.08 on nonsense.
- OBVIOUSLY_FAKE + traction → PROCEED. Viral fakes are a PR risk; investigate.
- COHERENT → PROCEED. Worth the full pipeline.

The sniff test never concludes a claim. It only decides whether the
expensive pipeline runs. A stopped allegation is logged as
'sniff_rejected' with its reason — never as a verdict.
"""

from __future__ import annotations

import os
import re

from . import tracing

# Heuristic patterns for obviously-fake claims. These are cheap string
# matches — no API calls. High precision, low recall by design: the sniff
# test should only stop the slam dunks.
_OBVIOUS_FAKE_PATTERNS = [
    r"\bmoon is made of cheese\b",
    r"\bflat earth\b.*\bproof\b",
    r"\blizard people\b",
    r"\bchemtrails\b.*\bmind control\b",
    r"\bbigfoot\b.*\bceo\b",
    r"\btime traveler\b.*\bpredicted\b",
    r"\b5g\b.*\b(chip|microchip)\b.*\bvaccine\b",
]

# Minimum viable allegation: must name SOME entity and SOME assertion.
# Below this, there's nothing to investigate.
_MIN_CHARS = 40


def _clef_available() -> bool:
    """True when Cloudflare Workers AI credentials are present."""
    return bool(os.environ.get("CLOUDFLARE_ACCOUNT_ID")
                and os.environ.get("CLOUDFLARE_API_TOKEN"))


def _clef_decide(allegation: str) -> tuple[float, str] | None:
    """Ask Clef-flash via Workers AI. Returns (fake_score, reason) or None."""
    import json
    import urllib.request

    account = os.environ["CLOUDFLARE_ACCOUNT_ID"]
    token = os.environ["CLOUDFLARE_API_TOKEN"]
    url = (f"https://api.cloudflare.com/client/v4/accounts/{account}"
           f"/ai/run/@cf/cloudflare/clef-flash")
    body = json.dumps({
        "state": allegation,
        "questions": {
            "investigable": {
                "type": "noul",
                "instructions": "Is this a coherent, specific claim about a named entity that could be investigated with evidence?",
            },
            "obviously_fake": {
                "type": "noul",
                "instructions": "Is this obviously false on its face (known hoax, physically impossible, incoherent)?",
            },
        },
    }).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "TruthOps/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read())
    except Exception:
        return None
    try:
        answers = payload["result"]["answers"]
        p_fake = float(answers["obviously_fake"]["probability"])
        p_inv = float(answers["investigable"]["probability"])
        # Fake score: high when obviously_fake is likely AND investigable is not.
        score = p_fake * (1.0 - p_inv * 0.5)
        return round(score, 3), f"clef-flash: p(fake)={p_fake:.2f}, p(investigable)={p_inv:.2f}"
    except (KeyError, TypeError, ValueError):
        return None


def _heuristic_fake_score(text: str) -> tuple[float, str]:
    """Return (score 0..1, reason). Score near 1 = obviously fake."""
    lowered = text.lower()
    for pat in _OBVIOUS_FAKE_PATTERNS:
        if re.search(pat, lowered):
            return 0.95, f"matches known hoax template: {pat}"
    # Incoherent: too short to be an investigable claim.
    if len(text.strip()) < _MIN_CHARS:
        return 0.90, f"allegation too short ({len(text.strip())} chars) to investigate"
    # ALL CAPS rants with no named entity are rarely actionable.
    if text.isupper() and len(text) > 20:
        return 0.70, "all-caps with no structured claim"
    return 0.0, ""


def _fake_score(text: str) -> tuple[float, str, str]:
    """Return (score, reason, backend). Prefers Clef when available."""
    if _clef_available():
        result = _clef_decide(text)
        if result is not None:
            score, reason = result
            return score, reason, "clef-flash"
    score, reason = _heuristic_fake_score(text)
    return score, reason, "heuristic"


def sniff(allegation: str, traction_signals: dict | None = None) -> dict:
    """Run the sniff test. Returns a decision dict.

    traction_signals: optional dict like {"mentions": 1500, "trending": True}.
    When traction is significant, even an obviously-fake allegation proceeds
    — viral fakes carry real PR risk.
    """
    with tracing.span("sniff_test", allegation_chars=len(allegation)):
        fake_score, fake_reason, backend = _fake_score(allegation)
        traction = traction_signals or {}
        mentions = int(traction.get("mentions", 0) or 0)
        trending = bool(traction.get("trending", False))
        has_traction = mentions >= 100 or trending

        if fake_score >= 0.85 and not has_traction:
            decision = {
                "proceed": False,
                "reason": f"sniff_rejected: {fake_reason}; no traction signal",
                "fake_score": fake_score,
                "has_traction": False,
                "estimated_cost": 0.02,
            }
        elif fake_score >= 0.85 and has_traction:
            decision = {
                "proceed": True,
                "reason": (f"obviously fake ({fake_reason}) BUT has traction "
                           f"({mentions} mentions) — viral fakes need a response plan"),
                "fake_score": fake_score,
                "has_traction": True,
                "estimated_cost": 1.10,
            }
        else:
            decision = {
                "proceed": True,
                "reason": "passed sniff test — coherent allegation, full pipeline warranted",
                "fake_score": fake_score,
                "has_traction": has_traction,
                "estimated_cost": 1.10,
            }
        print(f"[sniff] proceed={decision['proceed']} — {decision['reason']}")
        return decision
