"""Firecrawl adapter — web search + scrape for evidence retrieval.

REST v2 API at https://api.firecrawl.dev/v2. Auth: Authorization: Bearer
<FIRECRAWL_API_KEY from env>.

Graceful no-op when the key is absent: `available()` returns False and the
Evidence Agent skips it. In the demo run this integration is SIMULATED
(the benchmark case is resolved from fixtures); the adapter below is real
code and has been live-tested against the v2 search and scrape endpoints.
"""

import json
import os
import urllib.request

API_BASE = "https://api.firecrawl.dev/v2"
LABEL = "SIMULATED integration in demo (adapter is live-capable)"


def available():
    return bool(os.environ.get("FIRECRAWL_API_KEY"))


def _post(path, payload):
    key = os.environ.get("FIRECRAWL_API_KEY")
    if not key:
        raise RuntimeError("FIRECRAWL_API_KEY not set")
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        API_BASE + path, data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def _results(response):
    """Normalize v2/search response shapes: data.web (current) or data list (legacy)."""
    data = response.get("data") or {}
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("web") or data.get("results") or data.get("organic") or []
    return []


def search(query, limit=5):
    """Live web search. Returns the raw v2/search response dict."""
    return _post("/search", {"query": query, "limit": limit})


def scrape(url, formats=("markdown",)):
    """Live page scrape. Returns the raw v2/scrape response dict."""
    return _post("/scrape", {"url": url, "formats": list(formats)})


def to_evidence(result_item, claim_id):
    """Normalize one search result into an evidence record."""
    return {
        "evidence_id": f"fc-{abs(hash(result_item.get('url', ''))) % 10**8}",
        "claim_id": claim_id,
        "source": "firecrawl",
        "label": LABEL,
        "url": result_item.get("url"),
        "title": result_item.get("title"),
        "snippet": (result_item.get("markdown") or result_item.get("description") or "")[:500],
        "reliability": 0.5,  # web results start at medium; verified by cross-check
        "is_primary_source": False,
    }
