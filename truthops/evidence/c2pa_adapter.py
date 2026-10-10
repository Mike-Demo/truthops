"""
C2PA provenance adapter for TruthOps.

Phase 1 of photo verification: check C2PA Content Credentials.
- If an image has valid C2PA provenance: strong signal of authenticity (who created it, when, with what tool).
- If an image has NO C2PA data: not proof of fake, but absence of provenance (most AI generators strip or never embed it).
- If C2PA data is present but INVALID: strong signal of tampering.

Phase 2 (planned): TruthScan API for AI-generation detection on images without C2PA data.
"""

from __future__ import annotations

import io


def check_provenance(image_bytes: bytes) -> dict:
    """
    Check C2PA provenance in image bytes.

    Returns:
        {
            "has_c2pa": bool,
            "valid": bool | None,       # None if no C2PA data
            "issuer": str | None,        # who signed it
            "created": str | None,       # when
            "tool": str | None,          # generating/editing tool
            "signal": "provenance_verified" | "no_provenance" | "provenance_invalid",
            "detail": str,
        }
    """
    try:
        import c2pa
    except ImportError:
        return {
            "has_c2pa": False,
            "valid": None,
            "issuer": None,
            "created": None,
            "tool": None,
            "signal": "checker_unavailable",
            "detail": "c2pa-python not installed",
        }

    try:
        reader = c2pa.Reader(stream=io.BytesIO(image_bytes))
        manifest = reader.get_active_manifest()
        if not manifest:
            return {
                "has_c2pa": False,
                "valid": None,
                "issuer": None,
                "created": None,
                "tool": None,
                "signal": "no_provenance",
                "detail": "No C2PA Content Credentials found in image. "
                           "Absence of provenance is not proof of fabrication, "
                           "but most AI generators do not embed C2PA data.",
            }

        # Extract key fields
        issuer = None
        try:
            claim = manifest.get("claim", {})
            issuer = claim.get("issuer") or manifest.get("issuer")
        except Exception:
            pass

        tool = None
        try:
            for assertion in manifest.get("assertions", []):
                label = assertion.get("label", "")
                if "actions" in label:
                    actions = assertion.get("data", {}).get("actions", [])
                    if actions:
                        tool = actions[0].get("softwareAgent", {}).get("name")
                        break
        except Exception:
            pass

        return {
            "has_c2pa": True,
            "valid": True,  # c2pa.Reader validates on parse; raises on invalid
            "issuer": issuer,
            "created": manifest.get("claim", {}).get("created"),
            "tool": tool,
            "signal": "provenance_verified",
            "detail": f"C2PA Content Credentials present and valid. "
                      f"Issuer: {issuer or 'unknown'}. Tool: {tool or 'unknown'}.",
        }
    except Exception as e:
        err = str(e).lower()
        if any(s in err for s in ("no c2pa", "not found", "no manifest", "no such file",
                                    "io error", "invalid image", "unsupported format",
                                    "could not", "unable to", "manifestnotfound",
                                    "no jumbf", "no claim")):
            return {
                "has_c2pa": False,
                "valid": None,
                "issuer": None,
                "created": None,
                "tool": None,
                "signal": "no_provenance",
                "detail": "No C2PA Content Credentials found in image. "
                           "Absence of provenance is not proof of fabrication, "
                           "but most AI generators do not embed C2PA data.",
            }
        return {
            "has_c2pa": True,
            "valid": False,
            "issuer": None,
            "created": None,
            "tool": None,
            "signal": "provenance_invalid",
            "detail": f"C2PA data present but failed validation: {e}. "
                      "This is a strong tampering signal.",
        }


def provenance_to_evidence(result: dict, image_url: str = "") -> dict:
    """Convert a C2PA check result into a TruthOps evidence record."""
    signal = result["signal"]
    if signal == "provenance_verified":
        return {
            "document_type": "c2pa_provenance",
            "is_primary_source": True,
            "source_reliability": 0.95,
            "supports_claims": ["image_authentic"],
            "contradicts_claims": [],
            "url": image_url or "c2pa://manifest",
            "summary": result["detail"],
            "provenance": result,
        }
    elif signal == "provenance_invalid":
        return {
            "document_type": "c2pa_provenance",
            "is_primary_source": True,
            "source_reliability": 0.9,
            "supports_claims": [],
            "contradicts_claims": ["image_authentic"],
            "url": image_url or "c2pa://manifest",
            "summary": result["detail"],
            "provenance": result,
            "fabrication_proof": True,
        }
    else:  # no_provenance or checker_unavailable
        return {
            "document_type": "c2pa_provenance",
            "is_primary_source": False,
            "source_reliability": 0.5,
            "supports_claims": [],
            "contradicts_claims": [],
            "url": image_url or "c2pa://none",
            "summary": result["detail"],
            "provenance": result,
            "note": "Absence of C2PA data is weak evidence — route to Phase 2 (TruthScan) for AI detection.",
        }
