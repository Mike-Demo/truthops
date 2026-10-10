"""Alexandria adapter — generic Firecrawl Alexandria integration for TruthOps.

Provides access to all 27 Alexandria categories (companies, finance, news,
jobs, knowledge, etc.) via the Firecrawl CLI. Used for evidence enrichment:
company records, financial statements, news coverage, and more.

This is a VALIDATION/ENRICHMENT signal: Alexandria results annotate evidence
but never directly change verdicts. Graceful no-op when CLI is missing or
calls fail.

Usage:
    from truthops.evidence import alexandria_adapter
    # Discover tools for a need
    tools = alexandria_adapter.discover("company funding rounds")
    # Execute a specific provider/capability
    result = alexandria_adapter.execute("fireround/rounds/search", {"query": "..."})
"""

from __future__ import annotations

import json
import subprocess

CLI = ["npx", "-y", "firecrawl-cli@latest"]
TIMEOUT_S = 120


def available() -> bool:
    """True if firecrawl-cli can run."""
    try:
        p = subprocess.run(
            CLI + ["--version"], capture_output=True, text=True, timeout=15
        )
        return p.returncode == 0
    except Exception:
        return False


def discover(need: str, max_results: int = 5) -> list[dict]:
    """Discover Alexandria tools for a given need.

    Returns list of {provider, capability, description}.
    Never raises; returns [] on failure.
    """
    try:
        p = subprocess.run(
            CLI + ["search", need, "--sources", "alexandria"],
            capture_output=True, text=True, timeout=TIMEOUT_S,
        )
    except Exception:
        return []
    if p.returncode != 0:
        return []
    # Parse the text output for provider/capability pairs
    tools = []
    lines = p.stdout.split("\n")
    i = 0
    while i < len(lines) and len(tools) < max_results:
        line = lines[i].strip()
        # Tool ref lines look like "  fireround/rounds/search" (no leading ===, no colon)
        if line and "/" in line and not line.startswith(("=", "Inspect", "Use", "Finding", "No results")):
            # Must be a bare ref (no spaces before the slash part, or starts with spaces then ref)
            parts = line.split(None, 1)
            ref = parts[0]
            if "/" in ref and not ref.startswith("http"):
                segs = ref.split("/")
                if len(segs) >= 2:
                    # Description is on the next non-empty line
                    desc = ""
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines):
                        desc = lines[j].strip()[:200]
                    tools.append({
                        "ref": "/".join(segs),
                        "provider": segs[0],
                        "capability": "/".join(segs[1:]),
                        "description": desc,
                    })
        i += 1
    return tools


def execute(ref: str, options: dict) -> dict | None:
    """Execute an Alexandria provider/capability.

    Args:
        ref: "provider/capability" (e.g. "fireround/rounds/search")
        options: Input JSON for the tool

    Returns parsed result dict or None on failure. Never raises.
    """
    try:
        p = subprocess.run(
            CLI + ["scrape", "--alexandria", ref,
                   "--options", json.dumps(options)],
            capture_output=True, text=True, timeout=TIMEOUT_S,
        )
    except Exception:
        return None
    if p.returncode != 0:
        return None
    try:
        # Output contains JSON mixed with log lines; find the JSON
        out = p.stdout
        start = out.find('{"success"')
        if start < 0:
            return None
        # Find matching brace (simplified: take to end, try parse)
        data = json.loads(out[start:])
        return data
    except Exception:
        return None


# Category hints for TruthOps evidence gathering
CATEGORY_HINTS = {
    "company": "Company records, filings, funding, firmographics",
    "finance": "Market prices, financial statements, ownership",
    "news": "News coverage from press and newswires",
    "jobs": "Job postings (executive hires/departures)",
    "knowledge": "Encyclopedic/reference facts",
    "digital-intelligence": "Website traffic, audience, competitive intel",
}
