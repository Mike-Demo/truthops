"""
TruthScan adapter for TruthOps — Phase 2 of photo verification.

Phase 1 (C2PA): check provenance. If absent or inconclusive, Phase 2 (TruthScan):
AI image detection via TruthScan's API.

API: https://detect-image.truthscan.com
Flow: GET /get-presigned-url (apikey header) → PUT image → POST /detect (key in body)
      → POST /query (poll for results)

Key is passed at call time or via TRUTHSCAN_API_KEY env var. Never committed.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request

API_BASE = "https://detect-image.truthscan.com"


def _key(api_key: str | None) -> str:
    return api_key or os.environ.get("TRUTHSCAN_API_KEY", "")


def check_credits(api_key: str | None = None) -> dict:
    """Check remaining credits. Read-only, no scan consumed."""
    key = _key(api_key)
    if not key:
        return {"ok": False, "error": "no API key"}
    try:
        req = urllib.request.Request(
            API_BASE + "/check-user-credits",
            headers={"apikey": key},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"ok": True, "data": json.loads(resp.read())}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def scan_image(image_bytes: bytes, api_key: str | None = None,
               filename: str = "image.jpg",
               content_type: str = "image/jpeg",
               poll_timeout: int = 120) -> dict:
    """
    Full 3-step scan: presigned URL → upload → detect → poll.

    Returns:
        {
            "ai_probability": float | None,
            "verdict": str,
            "detail": str,
            "document_id": str | None,
            "raw": dict,
        }
    """
    key = _key(api_key)
    if not key:
        return {"ai_probability": None, "verdict": "unavailable",
                "detail": "No TruthScan API key", "document_id": None, "raw": {}}
    try:
        # Step 1: presigned URL
        req = urllib.request.Request(
            f"{API_BASE}/get-presigned-url?file_name={filename}",
            headers={"apikey": key},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            up = json.loads(resp.read())
        presigned_url = up["presigned_url"]
        file_path = up["file_path"]

        # Step 2: upload
        put = urllib.request.Request(
            presigned_url, data=image_bytes, method="PUT",
            headers={"Content-Type": content_type, "x-amz-acl": "private"},
        )
        with urllib.request.urlopen(put, timeout=60):
            pass

        # Step 3: submit for detection
        body = json.dumps({
            "key": key,
            "url": f"https://ai-image-detector-prod.nyc3.digitaloceanspaces.com/{file_path}",
            "generate_heatmap": False,
            "generate_preview": False,
            "generate_analysis_details": True,
        }).encode()
        det = urllib.request.Request(
            API_BASE + "/detect", data=body, method="POST",
            headers={"Content-Type": "application/json", "accept": "application/json"},
        )
        with urllib.request.urlopen(det, timeout=30) as resp:
            job = json.loads(resp.read())
        doc_id = job.get("id")

        # Step 4: poll /query
        deadline = time.time() + poll_timeout
        result = {}
        while time.time() < deadline:
            qbody = json.dumps({"id": doc_id}).encode()
            q = urllib.request.Request(
                API_BASE + "/query", data=qbody, method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(q, timeout=30) as resp:
                result = json.loads(resp.read())
            status = result.get("status", "")
            if status in ("completed", "done", "success", "failed", "error"):
                break
            time.sleep(5)

        # Normalize
        prob = (result.get("ai_probability") or result.get("ai_score")
                or result.get("probability") or result.get("ai_confidence"))
        if prob is not None and prob > 1:
            prob = prob / 100.0
        verdict = result.get("verdict", result.get("classification",
                    result.get("result", "uncertain")))
        return {
            "ai_probability": prob,
            "verdict": verdict,
            "detail": result.get("explanation", result.get("message", ""))[:300],
            "document_id": doc_id,
            "raw": result,
        }
    except Exception as e:
        return {"ai_probability": None, "verdict": "error",
                "detail": str(e)[:200], "document_id": None, "raw": {}}


def scan_to_evidence(result: dict, image_url: str = "") -> dict:
    """Convert a TruthScan result into a TruthOps evidence record."""
    prob = result.get("ai_probability")
    if prob is None:
        return {
            "document_type": "truthscan_ai_detection",
            "is_primary_source": False,
            "source_reliability": 0.0,
            "supports_claims": [],
            "contradicts_claims": [],
            "url": image_url or "truthscan://scan",
            "summary": f"TruthScan scan unavailable: {result.get('detail', '')}",
        }
    if prob >= 0.8:
        return {
            "document_type": "truthscan_ai_detection",
            "is_primary_source": True,
            "source_reliability": 0.85,
            "supports_claims": [],
            "contradicts_claims": ["image_authentic"],
            "url": image_url or "truthscan://scan",
            "summary": f"TruthScan: AI-generated with probability {prob:.2f}. {result.get('detail', '')}",
            "fabrication_proof": True,
            "scan": result,
        }
    elif prob <= 0.2:
        return {
            "document_type": "truthscan_ai_detection",
            "is_primary_source": True,
            "source_reliability": 0.85,
            "supports_claims": ["image_authentic"],
            "contradicts_claims": [],
            "url": image_url or "truthscan://scan",
            "summary": f"TruthScan: likely authentic (AI probability {prob:.2f}). {result.get('detail', '')}",
            "scan": result,
        }
    else:
        return {
            "document_type": "truthscan_ai_detection",
            "is_primary_source": False,
            "source_reliability": 0.5,
            "supports_claims": [],
            "contradicts_claims": [],
            "url": image_url or "truthscan://scan",
            "summary": f"TruthScan: inconclusive (AI probability {prob:.2f}). {result.get('detail', '')}",
            "scan": result,
        }
