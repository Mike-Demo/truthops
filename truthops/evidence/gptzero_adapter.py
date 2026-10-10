"""GPTZero adapter — AI-generated content screening as a validation signal.

Wraps the workspace `gptzero-scan` CLI (which authenticates via the stored
custom.gptzero connector; no raw key is ever handled here). Used to screen
secondary-source texts (news snippets, social posts) for AI-generation
signals, which inform source reliability assessment.

Four signal families (all annotation-only):
1. ai_detection — is this text AI-generated? (p_ai, predicted_class)
2. ai_paraphrased — was AI text rewritten to evade detection? (subclass)
3. sentence_level — which specific sentences are AI-flagged?
4. plagiarism — not in the v2 predict API; null (manual dashboard review)

This is a VALIDATION signal, not a verdict input: it annotates evidence
records but never changes scoring thresholds. Graceful no-op when the CLI
is missing, text is too short (<250 chars per GPTZero's own guidance), or
the API call fails.
"""

from __future__ import annotations

import json
import os
import subprocess

CLI_PATH = os.path.expanduser("~/workspace/skills/gptzero/bin/gptzero-scan")
MIN_CHARS = 250
TIMEOUT_S = 90


def available() -> bool:
    """True if the gptzero-scan CLI exists and is executable."""
    return os.path.isfile(CLI_PATH) and os.access(CLI_PATH, os.X_OK)


def screen_text(text: str) -> dict | None:
    """Screen one text for AI-generation signals.

    Returns a dict with four signal families:
    - ai_detection: p_ai, predicted_class, confidence
    - ai_paraphrased: subclass detection (was AI text rewritten to hide it?)
    - sentence_level: count of AI-flagged sentences + highest-risk sentence
    - plagiarism: null (not in v2 predict API; use dashboard for manual review)

    Returns None when skipped/failed. Never raises.
    """
    if not text or len(text.strip()) < MIN_CHARS:
        return None
    if not available():
        return None
    try:
        proc = subprocess.run(
            [CLI_PATH, "--text", text.strip(), "--json"],
            capture_output=True, text=True, timeout=TIMEOUT_S,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    try:
        payload = json.loads(proc.stdout)
    except Exception:
        return None
    try:
        doc = payload["documents"][0]

        # 1. AI detection (base signal)
        p_ai = round(float(doc.get("completely_generated_prob", 0.0)), 3)

        # 2. AI paraphrased (subclass — was it rewritten to evade detection?)
        subclass = doc.get("subclass", {}) or {}
        ai_sub = (subclass.get("ai") or {})
        paraphrased_prob = None
        paraphrased_class = None
        try:
            probs = ai_sub.get("class_probabilities", {}) or {}
            paraphrased_prob = round(float(probs.get("ai_paraphrased", 0.0)), 3)
            paraphrased_class = str(ai_sub.get("predicted_class", ""))
        except (TypeError, ValueError):
            pass

        # 3. Sentence-level: flag the riskiest sentences
        sentences = doc.get("sentences", []) or []
        flagged = []
        for s in sentences:
            try:
                gp = float(s.get("generated_prob", 0.0))
                if gp >= 0.7:
                    flagged.append({
                        "sentence": str(s.get("sentence", ""))[:120],
                        "p_ai": round(gp, 3),
                    })
            except (TypeError, ValueError):
                continue
        flagged.sort(key=lambda x: x["p_ai"], reverse=True)

        return {
            "p_ai": p_ai,
            "predicted_class": str(doc.get("predicted_class", "unknown")),
            "confidence": str(doc.get("confidence_category", "unknown")),
            "ai_paraphrased_prob": paraphrased_prob,
            "ai_paraphrased_class": paraphrased_class,
            "flagged_sentences": flagged[:3],
            "flagged_count": len(flagged),
            "plagiarism": None,  # not in v2 predict API
            "scanned_chars": len(text.strip()),
        }
    except Exception:
        return None


def extract_scannable_text(doc: dict) -> str:
    """Pull the longest narrative text out of a fixture/source document."""
    parts: list[str] = []
    # news-snippet style: list of {text}
    snippets = doc.get("snippets")
    if isinstance(snippets, list):
        for s in snippets:
            if isinstance(s, dict) and s.get("text"):
                parts.append(str(s["text"]))
    for key in ("body", "text", "content", "statement"):
        v = doc.get(key)
        if isinstance(v, str) and len(v) > 50:
            parts.append(v)
    # join short parts so combined text can clear the minimum length
    return " ".join(p.strip() for p in parts if p and p.strip())
