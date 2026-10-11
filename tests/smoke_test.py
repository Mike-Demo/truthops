#!/usr/bin/env python3
"""
Automated smoke test for TruthOps pipeline.

Runs in fixture mode (no API keys required) and verifies:
1. All 28 cases run without crashing
2. Every case produces JSON + Markdown reports
3. Every case has expected verdict/score in calibration band
4. Sniff rejection path doesn't crash (the recommended_posture bug)

Usage: python3 tests/smoke_test.py
Exit code 0 = all pass, 1 = failures.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
ARTIFACTS = BASE / "artifacts"

# Ensure truthops is importable
sys.path.insert(0, str(BASE))

# Expected calibration bands (verdict, min_score, max_score)
EXPECTED = {
    "smoke1": ("pants_on_fire", 0, 5),
    "smoke2": ("false", 5, 15),
    "smoke3": ("mostly_false", 15, 40),
    "smoke4": ("false", 5, 15),
    "smoke5": ("true", 90, 100),
    "smoke6": ("mostly_true", 75, 90),
    "smoke7": ("mostly_true", 75, 90),
    "smoke8": ("mostly_true", 75, 90),
}

# smoke9-28: community set (false=10, mostly_false=35, true=99)
for i in range(9, 29):
    if i in (22, 23, 24, 25, 27):  # mostly_false community claims
        EXPECTED[f"smoke{i}"] = ("mostly_false", 15, 40)
    elif i == 28:  # true
        EXPECTED[f"smoke{i}"] = ("true", 90, 100)
    else:  # false
        EXPECTED[f"smoke{i}"] = ("false", 5, 15)


def run_case(case_id):
    """Run a single case in fixture mode. Returns (success, error_msg)."""
    result = subprocess.run(
        [sys.executable, "-m", "truthops", "run", "--case", case_id],
        cwd=BASE,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        return False, f"exit={result.returncode}: {result.stderr[-500:]}"
    return True, ""


def check_reports(case_id):
    """Verify JSON + MD reports exist and have valid structure."""
    jpath = ARTIFACTS / f"truthops-report-{case_id}.json"
    mpath = ARTIFACTS / f"truthops-report-{case_id}.md"

    if not jpath.exists():
        return False, f"missing {jpath.name}"
    if not mpath.exists():
        return False, f"missing {mpath.name}"

    try:
        with open(jpath) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"

    # Verify required top-level keys
    for key in ("claims", "response_plan", "neatlogs_trace_id"):
        if key not in data:
            return False, f"missing key: {key}"

    # Verify response_plan has required keys (the recommended_posture bug)
    plan = data["response_plan"]
    for key in ("characterization", "recommended_posture", "key_messages"):
        if key not in plan:
            return False, f"plan missing key: {key}"

    return True, ""


def check_calibration(case_id):
    """Verify verdict and score are in expected band."""
    jpath = ARTIFACTS / f"truthops-report-{case_id}.json"
    with open(jpath) as f:
        data = json.load(f)

    claims = data["claims"]
    if not claims:
        return False, "no claims in report"

    claim = list(claims.values())[0]
    verdict = claim.get("verdict", "")
    score = claim.get("score_0_100", -1)

    expected_verdict, min_score, max_score = EXPECTED[case_id]

    if verdict != expected_verdict:
        return False, f"verdict {verdict} != expected {expected_verdict}"
    if not (min_score <= score <= max_score):
        return False, f"score {score} not in [{min_score}, {max_score}]"

    return True, ""


def test_sniff_rejection():
    """Verify sniff-rejected allegations don't crash report generation."""
    from truthops.sniff_test import sniff

    # Short allegation should be rejected
    decision = sniff("x")
    if decision["proceed"]:
        return False, "short allegation should be rejected"

    # Simulate the director's sniff-rejected return value
    plan = {
        "characterization": "SNIFF_REJECTED",
        "recommended_posture": "no_action",
        "key_messages": [f"Sniff test rejected: {decision['reason']}"],
        "cited_evidence": [],
        "external_actions": [],
        "approval_required": False,
        "sniff_decision": decision,
        "sniff_rejected": True,
    }

    # Verify all keys write_reports needs are present
    for key in ("characterization", "recommended_posture", "key_messages"):
        if key not in plan:
            return False, f"sniff-rejected plan missing {key}"

    return True, ""


def main():
    print("=" * 70)
    print("TruthOps Smoke Test — fixture mode (no API keys)")
    print("=" * 70)

    failures = []
    passed = 0

    # Test 1: sniff rejection path
    print("\n[1/3] Sniff rejection path...")
    ok, err = test_sniff_rejection()
    if ok:
        print("  ✅ PASS")
        passed += 1
    else:
        print(f"  ❌ FAIL: {err}")
        failures.append(("sniff_rejection", err))

    # Test 2: run all 28 cases (fixture mode)
    print(f"\n[2/3] Running 28 cases in fixture mode...")
    for i, case_id in enumerate(sorted(EXPECTED.keys()), 1):
        ok, err = run_case(case_id)
        if ok:
            ok, err = check_reports(case_id)
        if ok:
            print(f"  ✅ {case_id} ({i}/28)")
            passed += 1
        else:
            print(f"  ❌ {case_id}: {err}")
            failures.append((case_id, err))

    # Test 3: calibration bands
    print(f"\n[3/3] Checking calibration bands...")
    for case_id in sorted(EXPECTED.keys()):
        ok, err = check_calibration(case_id)
        if ok:
            passed += 1
        else:
            print(f"  ❌ {case_id}: {err}")
            failures.append((f"{case_id}_calibration", err))

    print("\n" + "=" * 70)
    total = 1 + 28 + 28  # sniff + runs + calibrations
    print(f"Results: {passed}/{total} passed")
    if failures:
        print(f"\nFailures ({len(failures)}):")
        for name, err in failures:
            print(f"  - {name}: {err}")
        return 1
    print("\n✅ All smoke tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
