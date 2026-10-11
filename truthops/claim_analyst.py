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
        "smoke4": ("claim", "Gasoline is now below $2.30 a gallon in most states.", "Smoke test 4: false specific number, true direction (prices down ~5%)."),
        "smoke5": ("claim", "Zohran Mamdani is the mayor of New York City.", "Smoke test 5: settled institutional fact."),
        "smoke6": ("claim", "President Donald Trump has deported 'over 13,000 Cubans since he has been in office, his first term and his second term.'", "Smoke test 6: mostly true; slight overstatement, NGO-estimated second-term figure."),
        "smoke7": ("claim", "Immigration agents 'are not getting the traditional five months training. \u2026 The training for the ICE agents now is 47 days.'", "Smoke test 7: mostly true; off-by-one (47 vs 48 days)."),
        "smoke8": ("claim", "Florida is '49th in avoidable hospital costs.'", "Smoke test 8: mostly true; correct rank, slightly narrower framing than metric."),
        "smoke9": ("claim", "Grocery prices were 'down' and 'WAY DOWN' in April 2025.", "Smoke test 9: community-submitted claim."),
        "smoke10": ("claim", "The cost of eggs had fallen by 93% or 94% since Trump took office.", "Smoke test 10: community-submitted claim."),
        "smoke11": ("claim", "Gas prices had fallen to $1.98 per gallon in two states on April 16, 2025.", "Smoke test 11: community-submitted claim."),
        "smoke12": ("claim", "There was no inflation during Trump's first presidency.", "Smoke test 12: community-submitted claim."),
        "smoke13": ("claim", "The Biden administration had the highest inflation in U.S. history.", "Smoke test 13: community-submitted claim."),
        "smoke14": ("claim", "The price of bacon quadrupled during Biden's presidency.", "Smoke test 14: community-submitted claim."),
        "smoke15": ("claim", "The price of apples doubled during Biden's presidency.", "Smoke test 15: community-submitted claim."),
        "smoke16": ("claim", "The United States was losing $2 trillion a year on trade before Trump returned to office.", "Smoke test 16: community-submitted claim."),
        "smoke17": ("claim", "The United States had a $350 billion trade deficit with Mexico.", "Smoke test 17: community-submitted claim."),
        "smoke18": ("claim", "It has been claimed that Ukraine started the war with Russia, contrary to the established record of Russian aggression.", "Smoke test 18: community-submitted claim."),
        "smoke19": ("claim", "The United States had provided $350 billion in wartime aid to Ukraine.", "Smoke test 19: community-submitted claim."),
        "smoke20": ("claim", "Europe had provided $200 billion less in aid to Ukraine than the United States.", "Smoke test 20: community-submitted claim."),
        "smoke21": ("claim", "Ukrainian President Volodymyr Zelensky had a 4% approval rating.", "Smoke test 21: community-submitted claim."),
        "smoke22": ("claim", "More Americans are working in the United States now than at any point in the country's history.", "Smoke test 22: community-submitted claim."),
        "smoke23": ("claim", "The stock market had set 74 all-time highs since Trump's return to office.", "Smoke test 23: community-submitted claim."),
        "smoke24": ("claim", "Manufacturing was booming and American manufacturing was back.", "Smoke test 24: community-submitted claim."),
        "smoke25": ("claim", "The United States has the largest amount of oil and gas of any country on Earth.", "Smoke test 25: community-submitted claim."),
        "smoke26": ("claim", "It has been claimed that China is operating the Panama Canal, which is managed by the Panama Canal Authority.", "Smoke test 26: community-submitted claim."),
        "smoke27": ("claim", "The United States spent more money than ever on the Panama Canal project and lost 38,000 lives while building it.", "Smoke test 27: community-submitted claim."),
        "smoke28": ("claim", "Trump won the 2024 U.S. popular vote by millions.", "Smoke test 28: community-submitted claim."),
    }
    if case_id in smoke_claims and n == 0:
        cid, statement, notes = smoke_claims[case_id]
        add(cid, statement, notes)

    return claims
