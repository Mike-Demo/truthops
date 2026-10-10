"""Deterministic fixture adapter — the PRIMARY evidence source.

Serves the SYNTHETIC northstar case files for fixture:// URLs. All data is
synthetic and labeled as such; this adapter is the deterministic backbone of
the hackathon demo benchmark.
"""

import json
import os

FIXTURES_BASE = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")

# fixture:// URL -> fixture file (built dynamically from all fixture dirs)
def _build_url_map():
    url_map = {}
    if not os.path.isdir(FIXTURES_BASE):
        return url_map
    for case_id in sorted(os.listdir(FIXTURES_BASE)):
        case_dir = os.path.join(FIXTURES_BASE, case_id)
        if not os.path.isdir(case_dir):
            continue
        for fname in sorted(os.listdir(case_dir)):
            if not fname.endswith(".json"):
                continue
            # fixture://<case>/<doc-name> where doc-name strips .json and _ -> -
            doc = fname[:-5].replace("_", "-")
            url_map[f"fixture://{case_id}/{doc}"] = os.path.join(case_dir, fname)
    return url_map

URL_MAP = _build_url_map()


class FixtureAdapter:
    name = "fixture"
    label = "SYNTHETIC fixtures (deterministic)"

    def fetch(self, url):
        path = URL_MAP.get(url)
        if not path:
            raise KeyError(f"fixture adapter: unknown URL {url}")
        with open(path) as f:
            return json.load(f)

    def search(self, query):
        """Return fixture documents relevant to a query (simple keyword match)."""
        results = []
        for url, path in URL_MAP.items():
            if url.endswith("/case"):
                continue
            with open(path) as f:
                doc = json.load(f)
            blob = json.dumps(doc).lower()
            if any(tok in blob for tok in query.lower().split()):
                results.append({"url": url, "document": doc})
        return results
