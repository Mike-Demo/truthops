"""TruthOps CLI:  python -m truthops run --case northstar [--approve publish,post]

Runs the full trust-operations loop end to end and writes the final report
(JSON + markdown) to artifacts/. External actions stay BLOCKED unless the
human passes --approve explicitly.
"""

import argparse
import json
import os
import sys
import time

from .state import RunState
from .infra.http import HttpClient
from .evidence.fixture_adapter import FixtureAdapter
from .director import Director
from . import tracing

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_allegation(case_id):
    path = os.path.join(BASE, "fixtures", case_id, "case.json")
    with open(path) as f:
        return json.load(f)["allegation"]


def write_reports(state, plan, case_id):
    os.makedirs(os.path.join(BASE, "artifacts"), exist_ok=True)
    data = state.data
    report = {
        "label": "SYNTHETIC demo run — neatHack 2026",
        "run_id": data["run_id"],
        "case_id": case_id,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "claims": data["claims"],
        "evidence": data["evidence"],
        "contrarian_reviews": data["contrarian_reviews"],
        "director_decisions": data["director_decisions"],
        "http_attempts": data["http_attempts"],
        "response_plan": plan,
        "approval_gate": data["approval_gate"],
        "events": data["events"],
    }
    jpath = os.path.join(BASE, "artifacts", f"truthops-report-{case_id}.json")
    with open(jpath, "w") as f:
        json.dump(report, f, indent=2)

    lines = [
        f"# TruthOps report — case `{case_id}`",
        "",
        "> SYNTHETIC demo run — neatHack 2026. All fixture data is synthetic; "
        "live integrations (Crustdata, Firecrawl) were SIMULATED in this run.",
        "",
        f"**Overall characterization: {plan['characterization']}**",
        f"**Recommended posture:** {plan['recommended_posture']}",
        "",
        "## Claim verdicts",
        "",
        "| Claim | Verdict | Confidence (initial → revised) |",
        "|---|---|---|",
    ]
    for cid, c in data["claims"].items():
        lines.append(
            f"| {cid} | **{c['verdict']}** | {c['confidence_initial']} → {c['confidence_revised']} |")
    lines += ["", "## Key messages", ""]
    lines += [f"- {m}" for m in plan["key_messages"]]
    lines += ["", "## Approval gate", "",
              f"External actions: **{data['approval_gate']['status']}** — "
              "publish / post / notify all blocked pending explicit human approval.",
              "", "## Evidence (scored)", ""]
    for eid, r in data["evidence"].items():
        lines.append(
            f"- `{eid}` [{r['source']}] {r['stance']} `{r['claim_id']}` — "
            f"score {r['score']} (reliability {r['reliability']} × relevance {r['relevance']}) "
            f"| primary={r['is_primary_source']} | {r['label']}")
    lines += ["", "## Contrarian challenges", ""]
    for rev in data["contrarian_reviews"]:
        lines.append(
            f"- **{rev['claim_id']}**: agreed={rev['agreed']}; "
            f"confidence {rev['initial_confidence']} → {rev['revised_confidence']}")
        if rev.get("disagreement"):
            lines.append(f"  - challenge: {rev['disagreement']}")
            lines.append(f"  - re-verification: {rev['reverification']}")
    mpath = os.path.join(BASE, "artifacts", f"truthops-report-{case_id}.md")
    with open(mpath, "w") as f:
        f.write("\n".join(lines) + "\n")
    return jpath, mpath


def main(argv=None):
    parser = argparse.ArgumentParser(prog="truthops")
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("--case", required=True)
    run.add_argument("--approve", default="",
                     help="human-initiated: comma-separated external actions to approve")
    args = parser.parse_args(argv)

    tracing.init(workflow_name="truthops")
    with tracing.span("truthops.run", case=args.case):
        run_id = f"run-{time.strftime('%Y%m%d-%H%M%S')}"
        state_path = os.path.join(BASE, "artifacts", f".state-{args.case}.json")
        state = RunState(state_path)
        state.data["run_id"] = run_id
        state.data["case_id"] = args.case
        state.data["started_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        # Each CLI run is a fresh, deterministic demonstration: reset all
        # run-scoped state (a previous run's claims/evidence/counters must not
        # leak into this one, or the 503 -> recovery path won't reproduce).
        # Within the run, every mutation is still flushed to disk immediately,
        # so the simulated failure is survived with all prior evidence intact.
        for key in ("claims", "evidence", "http_attempts", "events",
                    "contrarian_reviews", "director_decisions"):
            state.data[key] = [] if key in ("events", "contrarian_reviews", "director_decisions") else {}
        state.data["approval_gate"] = {"status": "BLOCKED", "approved_by": None, "approved_at": None}
        state.log_event("run_started", f"TruthOps run {run_id} started for case '{args.case}'")

        if args.approve:
            from .response_planner import ApprovalGate
            ApprovalGate(state).approve(
                [a.strip() for a in args.approve.split(",") if a.strip()],
                approver="human-cli-flag")

        allegation = load_allegation(args.case)
        http = HttpClient(state, FixtureAdapter())
        director = Director(state, http)
        plan = director.run_case(allegation, args.case)

        jpath, mpath = write_reports(state, plan, args.case)
        print(f"\n[truthops] reports written:\n  {jpath}\n  {mpath}")
        tracing.flush()

    tracing.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
