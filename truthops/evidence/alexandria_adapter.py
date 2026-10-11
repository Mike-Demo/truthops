"""Alexandria adapter — primary-source search for TruthOps.

Uses the Firecrawl CLI to search the web for primary sources (news articles,
official statements, press releases) that support or disprove a claim.

This is a VALIDATION/ENRICHMENT signal: Alexandria results annotate evidence
but never directly change verdicts. Graceful no-op when CLI is missing or
calls fail.

Usage:
    from truthops.evidence import alexandria_adapter
    sources = alexandria_adapter.search_primary_sources("Trump grocery prices claim")
    # -> [{"title": ..., "url": ..., "snippet": ..., "published": ...}]
"""

from __future__ import annotations

import re
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


def search_primary_sources(query: str, max_results: int = 5) -> list[dict]:
    """Search the web for primary sources relevant to a claim.

    Returns list of {title, url, snippet}. Never raises; returns [] on failure.
    """
    try:
        p = subprocess.run(
            CLI + ["search", query, "--limit", str(max_results)],
            capture_output=True, text=True, timeout=TIMEOUT_S,
        )
    except Exception:
        return []
    if p.returncode != 0:
        return []
    return _parse_search_output(p.stdout, max_results)


def _parse_search_output(output: str, max_results: int) -> list[dict]:
    """Parse firecrawl-cli search text output into source dicts."""
    sources = []
    # Results are separated by blank lines; each starts with a title line
    # followed by "  URL: <url>" and then content.
    blocks = re.split(r"\n\s*\n", output)
    for block in blocks:
        if len(sources) >= max_results:
            break
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        if not lines:
            continue
        # Skip header blocks
        if lines[0].startswith("===") or lines[0] == "No results found.":
            continue
        url = ""
        title = lines[0]
        snippet_lines = []
        for line in lines[1:]:
            m = re.match(r"URL:\s*(\S+)", line)
            if m:
                url = m.group(1)
            elif not line.startswith("[") and len(line) > 20:
                snippet_lines.append(line)
        if not url:
            continue
        # Clean title: strip markdown artifacts
        title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)[:200]
        sources.append({
            "title": title,
            "url": url,
            "snippet": " ".join(snippet_lines)[:500],
        })
    return sources


def scrape_source(url: str) -> dict | None:
    """Scrape a single URL for full content. Returns {url, content} or None."""
    try:
        p = subprocess.run(
            CLI + ["scrape", url, "--formats", "markdown"],
            capture_output=True, text=True, timeout=TIMEOUT_S,
        )
    except Exception:
        return None
    if p.returncode != 0:
        return None
    # Content follows the URL line; take everything after first blank line
    text = p.stdout.strip()
    if len(text) < 100:
        return None
    return {"url": url, "content": text[:5000]}


# Category hints for TruthOps evidence gathering
CATEGORY_HINTS = {
    "company": "Company records, filings, funding, firmographics",
    "finance": "Market prices, financial statements, ownership",
    "news": "News coverage from press and newswires",
    "jobs": "Job postings (executive hires/departures)",
    "knowledge": "Encyclopedic/reference facts",
    "digital-intelligence": "Website traffic, audience, competitive intel",
}
