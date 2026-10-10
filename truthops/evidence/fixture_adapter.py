"""Deterministic fixture adapter — the PRIMARY evidence source.

Serves the SYNTHETIC northstar case files for fixture:// URLs. All data is
synthetic and labeled as such; this adapter is the deterministic backbone of
the hackathon demo benchmark.
"""

import json
import os

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "northstar")

# fixture:// URL -> fixture file
URL_MAP = {
    "fixture://northstar/case": "case.json",
    "fixture://northstar/incident-report": "incident_report.json",
    "fixture://northstar/filing-q3-2026": "filing_q3_2026.json",
    "fixture://northstar/internal-memo": "internal_memo.json",
    "fixture://northstar/news-snippets": "news_snippets.json",
}


class FixtureAdapter:
    name = "fixture"
    label = "SYNTHETIC fixtures (deterministic)"

    def fetch(self, url):
        filename = URL_MAP.get(url)
        if not filename:
            raise KeyError(f"fixture adapter: unknown URL {url}")
        path = os.path.join(FIXTURE_DIR, filename)
        with open(path) as f:
            return json.load(f)

    def search(self, query):
        """Return fixture documents relevant to a query (simple keyword match)."""
        results = []
        for url, filename in URL_MAP.items():
            if url == "fixture://northstar/case":
                continue
            path = os.path.join(FIXTURE_DIR, filename)
            with open(path) as f:
                doc = json.load(f)
            blob = json.dumps(doc).lower()
            if any(tok in blob for tok in query.lower().split()):
                results.append({"url": url, "document": doc})
        return results
