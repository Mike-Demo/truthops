"""GPTZero adapter — AI-generated content screening as a validation signal.

Wraps the workspace `gptzero-scan` CLI (which authenticates via the stored
custom.gptzero connector; no raw key is ever handled here). Used to screen
secondary-source texts (news snippets, social posts) for AI-generation
signals, which inform source reliability assessment.

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

    Returns {"p_ai": float, "predicted_class": str, "confidence": str,
    "scanned_chars": int} or None when skipped/failed. Never raises.
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
        return {
            "p_ai": round(float(doc.get("completely_generated_prob", 0.0)), 3),
            "predicted_class": str(doc.get("predicted_class", "unknown")),
            "confidence": str(doc.get("confidence_category", "unknown")),
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
