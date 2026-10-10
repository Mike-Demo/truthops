"""Trust Director — adaptive orchestration.

The Director does NOT run a fixed pipeline. For each claim it chooses the
NEXT action based on current state: gather more evidence, verify a source,
escalate to the contrarian, or conclude. Every decision is logged with its
rationale. The loop ends when every claim is concluded or no action can
advance the state.
"""

from . import tracing
from .claim_analyst import decompose
from .evidence_agent import EvidenceAgent
from .contrarian import Contrarian
from .response_planner import build_plan, ApprovalGate
from .sniff_test import sniff


class Director:
    def __init__(self, state, http):
        self.state = state
        self.http = http
        self.evidence_agent = EvidenceAgent(state, http)
        self.contrarian = Contrarian(state, self.evidence_agent)
        self.gate = ApprovalGate(state)

    # -- adaptive policy -------------------------------------------------
    def next_action(self, claim_id):
        """Choose the next action for a claim from its current state."""
        claim = self.state.data["claims"][claim_id]
        recs = [r for r in self.state.data["evidence"].values()
                if r["claim_id"] == claim_id]
        reviewed = any(r["claim_id"] == claim_id
                       for r in self.state.data["contrarian_reviews"])

        if claim["status"] == "concluded":
            return None
        if claim["verdict"] is None:
            # Not yet evaluated. Gather at most once, then evaluate
            # (even with zero evidence — that yields 'unresolved').
            if not recs and claim.get("gather_attempts", 0) == 0:
                return ("gather", "no evidence yet — gather before any judgment")
            return ("evaluate",
                    "evidence phase complete — evaluate the claim")
        if not reviewed:
            return ("escalate", "initial verdict reached — escalate to contrarian for adversarial review")
        return ("conclude", "contrarian review complete — conclude the claim")

    def decide(self, claim_id, action, rationale):
        self.state.data["director_decisions"].append(
            {"claim_id": claim_id, "action": action, "rationale": rationale})
        self.state.log_event("director_decision",
                             f"[director] {claim_id}: next action = {action} — {rationale}",
                             claim_id=claim_id, action=action)
        print(f"[director] {claim_id}: next action = {action}")
        print(f"           rationale: {rationale}")

    # -- run --------------------------------------------------------------
    def run_case(self, allegation, case_id, traction_signals=None):
        with tracing.span("director.run_case", case_id=case_id):
            self.state.data["case_id"] = case_id
            print(f"\n[director] investigating allegation: {allegation}\n")
            # Sniff test FIRST — cheap gate before the $1.08 pipeline.
            decision = sniff(allegation, traction_signals)
            self.state.log_event("sniff_test",
                                 f"[sniff] proceed={decision['proceed']} — {decision['reason']}")
            self.state.save()
            if not decision["proceed"]:
                print(f"[director] sniff test rejected — skipping full pipeline "
                      f"(est. cost ${decision['estimated_cost']:.2f})")
                return {"characterization": "SNIFF_REJECTED",
                        "sniff_decision": decision,
                        "sniff_rejected": True}
            claims = decompose(allegation, case_id)
            for c in claims:
                self.state.data["claims"][c["claim_id"]] = c
            self.state.log_event("claims_decomposed",
                                 f"Decomposed into {len(claims)} atomic claims: "
                                 f"{[c['claim_id'] for c in claims]}")
            self.state.save()
            for c in claims:
                print(f"[director] claim registered: {c['claim_id']} — {c['statement']}")

            for c in claims:
                cid = c["claim_id"]
                print(f"\n{'='*70}\n[director] working claim: {cid}\n{'='*70}")
                while True:
                    nxt = self.next_action(cid)
                    if nxt is None:
                        break
                    action, rationale = nxt
                    self.decide(cid, action, rationale)
                    if action == "gather":
                        self.state.data["claims"][cid]["status"] = "gathering"
                        self.state.data["claims"][cid]["gather_attempts"] = \
                            self.state.data["claims"][cid].get("gather_attempts", 0) + 1
                        self.evidence_agent.gather(cid)
                    elif action == "evaluate":
                        self.state.data["claims"][cid]["status"] = "verifying"
                        self.evidence_agent.evaluate(cid)
                    elif action == "escalate":
                        self.contrarian.review(cid)
                    elif action == "conclude":
                        self.state.data["claims"][cid]["status"] = "concluded"
                        self.state.log_event("claim_concluded", f"{cid} concluded.", claim_id=cid)
                        self.state.save()
                        break

            print(f"\n{'='*70}\n[director] all claims concluded — building response plan\n{'='*70}")
            plan = build_plan(self.state)
            print(f"[director] overall characterization: {plan['characterization']}")
            print(f"[director] recommended posture: {plan['recommended_posture']}")
            for m in plan["key_messages"]:
                print(f"  • {m}")
            print("\n[director] attempting external actions (expect the gate to block):")
            for ext in plan["external_actions"]:
                result = self.gate.request(ext["action"], {"target": ext["target"]})
                ext["status"] = result["status"]
            return plan
