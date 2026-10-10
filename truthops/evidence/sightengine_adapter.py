"""Sightengine AI-generated image detection adapter.

Uses the `genai` model via Sightengine's check API. Free tier: 2,000 ops/month.

Credentials via SIGHTENGINE_API_USER / SIGHTENGINE_API_SECRET env vars.
API: https://api.sightengine.com/1.0/check.json
"""

import os
import json
import urllib.request
import urllib.parse

API_BASE = "https://api.sightengine.com/1.0/check.json"


def _creds(api_user=None, api_secret=None):
    user = api_user or os.environ.get("SIGHTENGINE_API_USER", "")
    secret = api_secret or os.environ.get("SIGHTENGINE_API_SECRET", "")
    return user, secret


def check_credits(api_user=None, api_secret=None) -> dict:
    """Sightengine has no credits endpoint; returns quota from a check response instead.

    Returns {"ok": True} if credentials are present; actual quota comes back
    in each check.json response as `request.operations`.
    """
    user, secret = _creds(api_user, api_secret)
    if not user or not secret:
        return {"ok": False, "error": "no Sightengine credentials"}
    return {"ok": True, "data": {"note": "quota reported per-check in request.operations"}}


def _encode_multipart(fields: dict, files: dict) -> tuple[bytes, str]:
    """Minimal multipart/form-data encoder."""
    boundary = "----sightengine-boundary-7d4a6d"
    lines = []
    for name, value in fields.items():
        lines.append(f"--{boundary}")
        lines.append(f'Content-Disposition: form-data; name="{name}"')
        lines.append("")
        lines.append(str(value))
    for name, (filename, content_type, data) in files.items():
        lines.append(f"--{boundary}")
        lines.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"')
        lines.append(f"Content-Type: {content_type}")
        lines.append("")
    body = b""
    # Build with bytes to handle binary cleanly
    parts = []
    for name, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        parts.append(f"{value}\r\n".encode())
    for name, (filename, content_type, data) in files.items():
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode())
        parts.append(f"Content-Type: {content_type}\r\n\r\n".encode())
        parts.append(data)
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), boundary


def scan_image(image_bytes: bytes, api_user=None, api_secret=None,
               filename: str = "image.jpg",
               content_type: str = "image/jpeg") -> dict:
    """
    Scan an image with Sightengine's genai model.

    Returns:
        {
            "ai_probability": float | None,
            "verdict": str,
            "detail": str,
            "raw": dict,
        }
    """
    user, secret = _creds(api_user, api_secret)
    if not user or not secret:
        return {"ai_probability": None, "verdict": "unavailable",
                "detail": "No Sightengine credentials", "raw": {}}
    try:
        fields = {
            "models": "genai",
            "api_user": user,
            "api_secret": secret,
        }
        files = {"media": (filename, content_type, image_bytes)}
        body, boundary = _encode_multipart(fields, files)
        req = urllib.request.Request(
            API_BASE, data=body, method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())

        if data.get("status") != "success":
            return {"ai_probability": None, "verdict": "error",
                    "detail": f"Sightengine error: {data.get('error', {}).get('message', 'unknown')}",
                    "raw": data}

        genai = data.get("type", {}).get("ai_generated")
        if genai is None:
            return {"ai_probability": None, "verdict": "unavailable",
                    "detail": "No genai result in response", "raw": data}

        ops = data.get("request", {}).get("operations")
        verdict = ("ai_generated" if genai >= 0.5 else "likely_real")
        return {
            "ai_probability": round(float(genai), 4),
            "verdict": verdict,
            "detail": f"Sightengine genai={genai:.2%} ({ops} op{'s' if ops != 1 else ''} used)",
            "raw": data,
        }
    except Exception as e:
        return {"ai_probability": None, "verdict": "error",
                "detail": f"Sightengine request failed: {str(e)[:200]}", "raw": {}}


def verify_photo(image_path: str, api_user=None, api_secret=None) -> dict:
    """Compatibility wrapper matching the old photo-adapter interface."""
    try:
        with open(image_path, "rb") as f:
            data = f.read()
    except OSError as e:
        return {"ai_probability": None, "verdict": "error",
                "detail": f"Cannot read image: {e}", "raw": {}}
    return scan_image(data, api_user=api_user, api_secret=api_secret,
                      filename=image_path.rsplit("/", 1)[-1])


def scan_to_evidence(result: dict, image_url: str = "") -> dict:
    """Convert a Sightengine result into a TruthOps evidence record."""
    prob = result.get("ai_probability")
    if prob is None:
        return {
            "document_type": "sightengine_ai_detection",
            "is_primary_source": False,
            "source_reliability": 0.0,
            "supports_claims": [],
            "contradicts_claims": [],
            "url": image_url or "sightengine://scan",
            "summary": f"Sightengine scan unavailable: {result.get('detail', '')}",
        }
    if prob >= 0.8:
        return {
            "document_type": "sightengine_ai_detection",
            "is_primary_source": True,
            "source_reliability": 0.85,
            "supports_claims": [],
            "contradicts_claims": ["image_authentic"],
            "url": image_url or "sightengine://scan",
            "summary": f"Sightengine: AI-generated with probability {prob:.2f}. {result.get('detail', '')}",
            "fabrication_proof": True,
            "scan": result,
        }
    elif prob <= 0.2:
        return {
            "document_type": "sightengine_ai_detection",
            "is_primary_source": True,
            "source_reliability": 0.85,
            "supports_claims": ["image_authentic"],
            "contradicts_claims": [],
            "url": image_url or "sightengine://scan",
            "summary": f"Sightengine: likely authentic (AI probability {prob:.2f}). {result.get('detail', '')}",
            "scan": result,
        }
    return {
        "document_type": "sightengine_ai_detection",
        "is_primary_source": False,
        "source_reliability": 0.5,
        "supports_claims": [],
        "contradicts_claims": [],
        "url": image_url or "sightengine://scan",
        "summary": f"Sightengine: inconclusive (AI probability {prob:.2f}). {result.get('detail', '')}",
        "scan": result,
    }
