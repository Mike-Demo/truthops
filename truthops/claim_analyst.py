"""Claim Analyst — decomposes an allegation into atomic, checkable claims.

For the demo this is a deterministic, rule-based decomposition (keyword and
pattern driven). Each atomic claim gets a stable id, a plain-text statement,
and a verdict slot that starts as 'pending'.
"""

import re


def decompose(allegation, case_id="northstar"):
    text = allegation.lower()
    claims = []
    n = 0

    def add(cid, statement, notes=""):
        claims.append({
            "claim_id": cid,
            "statement": statement,
            "status": "pending",          # pending -> gathering -> verifying -> reviewed -> concluded
            "verdict": None,             # PolitiFact Truth-O-Meter: pants_on_fire | false |
                                       # mostly_false | half_true | mostly_true | true | unresolved
            "confidence_initial": None,
            "confidence_revised": None,
            "notes": notes,
        })

    if "security incident" in text or "breach" in text:
        n += 1
        add("incident_occurred",
            "A security incident occurred at Northstar Cloud.",
            "Atomic fact: did the incident happen at all?")
    if re.search(r"lost\s+(\d+% of\s+)?(enterprise\s+)?customers", text):
        n += 1
        add("some_customer_decline",
            "Northstar Cloud lost enterprise customers after the incident.",
            "Atomic fact: was there any post-incident decline?")
    m = re.search(r"(\d+)%", text)
    if m:
        n += 1
        add("decline_was_40pct",
            f"The enterprise customer decline was {m.group(1)}%.",
            "Atomic fact: is the specific magnitude correct?")
    if "executive" in text or "knew" in text or "leadership" in text:
        n += 1
        add("executives_knew",
            "Northstar Cloud executives knew about the customer decline.",
            "Atomic fact: was leadership aware?")
    elif "concealed" in text:
        # concealment implies knowledge; still decompose it separately
        n += 1
        add("executives_knew",
            "Northstar Cloud executives knew about the customer decline.",
            "Implied by the concealment allegation; checked separately.")
    if "concealed" in text or "cover" in text or "hid" in text:
        n += 1
        add("deliberate_concealment",
            "Northstar Cloud deliberately concealed the impact of the incident.",
            "Atomic fact: is there direct evidence of intent to deceive?")

    # Smoke-test calibration cases: single atomic claim per case
    smoke_claims = {
        "smoke1": ("claim", "Photographs circulating online show New York City Mayor Zohran Mamdani posing alongside Jeffrey Epstein.", "Smoke test 1: AI-generated photo fabrication."),
        "smoke2": ("claim", "President Trump initiated an internal audit of the Social Security Administration.", "Smoke test 2: single-source fabrication."),
        "smoke3": ("claim", "President Trump ended eight wars.", "Smoke test 3: kernel of truth, unsupportable number."),
        "smoke4": ("claim", "Gasoline is now below $2.30 a gallon in most states.", "Smoke test 4: mostly true, minor imprecision."),
        "smoke5": ("claim", "Zohran Mamdani is the mayor of New York City.", "Smoke test 5: settled institutional fact."),
    }
    if case_id in smoke_claims and n == 0:
        cid, statement, notes = smoke_claims[case_id]
        add(cid, statement, notes)

    return claims
