"""JSON state store. Run state must survive the simulated 503 failure,
so every mutation is flushed to disk immediately."""

import copy
import json
import os
import time


class RunState:
    def __init__(self, path):
        self.path = path
        if os.path.exists(path):
            with open(path) as f:
                self.data = json.load(f)
        else:
            self.data = {
                "run_id": None,
                "case_id": None,
                "started_at": None,
                "claims": {},          # claim_id -> {text, status, evidence_ids, ...}
                "evidence": {},        # evidence_id -> {source, url, reliability, ...}
                "http_attempts": {},   # url -> attempt count (drives deterministic 503)
                "events": [],          # append-only log of state transitions
                "contrarian_reviews": [],
                "approval_gate": {"status": "BLOCKED", "approved_by": None, "approved_at": None},
                "director_decisions": [],
            }

    def save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.data, f, indent=2)
        os.replace(tmp, self.path)

    def log_event(self, kind, message, **fields):
        entry = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": kind, "message": message}
        entry.update(fields)
        self.data["events"].append(entry)
        self.save()
        return entry

    def snapshot(self):
        return copy.deepcopy(self.data)
