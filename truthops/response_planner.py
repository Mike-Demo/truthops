"""Response Planner — drafts the response recommendation.

Produces a response plan with recommended posture, key messages, and cited
evidence. EXTERNAL ACTIONS (publish / post / notify) are never executed here:
they go through the approval gate, which BLOCKS them until a human explicitly
approves. The gate is loud by design.
"""

from . import tracing

EXTERNAL_ACTIONS = ("publish", "post", "notify")


class ApprovalGate:
    BLOCKED_MESSAGE = (
        "⛔ APPROVAL GATE: external action '{action}' is BLOCKED.\n"
        "   A human must explicitly approve before TruthOps publishes, posts, or notifies.\n"
        "   Run with --approve '<action>' (human-initiated) to release a single action."
    )

    def __init__(self, state):
        self.state = state

    def request(self, action, payload=None):
        """Attempt an external action. Blocked unless explicitly approved."""
        gate = self.state.data["approval_gate"]
        if gate["status"] != "APPROVED" or action not in gate.get("approved_actions", []):
            print(self.BLOCKED_MESSAGE.format(action=action))
            self.state.log_event(
                "approval_blocked",
                f"External action '{action}' BLOCKED — awaiting human approval.",
                action=action,
            )
            self.state.save()
            return {"action": action, "status": "BLOCKED", "payload": payload}
        print(f"  [gate] external action '{action}' APPROVED by {gate['approved_by']} — executing (SIMULATED).")
        self.state.log_event("approval_executed", f"External action '{action}' executed.", action=action)
        self.state.save()
        return {"action": action, "status": "EXECUTED_SIMULATED", "payload": payload}

    def approve(self, actions, approver="human"):
        import time
        self.state.data["approval_gate"] = {
            "status": "APPROVED",
            "approved_by": approver,
            "approved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "approved_actions": list(actions),
        }
        self.state.log_event("approval_granted", f"Human approved actions: {actions}")
        self.state.save()


def build_plan(state):
    with tracing.span("response.build_plan"):
        claims = state.data["claims"]
        verdicts = {cid: c["verdict"] for cid, c in claims.items()}

        if verdicts.get("decline_was_40pct") == "contradicted":
            characterization = "MISLEADING"
            posture = "Correct the record with primary-source evidence"
        elif verdicts.get("incident_occurred") == "contradicted":
            characterization = "FALSE"
            posture = "Deny with evidence"
        else:
            characterization = "UNRESOLVED"
            posture = "Acknowledge investigation is ongoing"

        plan = {
            "characterization": characterization,
            "recommended_posture": posture,
            "key_messages": [
                "A security incident did occur on 2026-07-14 and was disclosed on 2026-07-16 (incident report).",
                "Enterprise customer decline was 4.2% (2,380 -> 2,280), per the Q3 2026 filing — not 40%.",
                "The 40% figure circulating online is contradicted by the primary filing.",
                "No direct evidence of deliberate concealment was found; intent is not asserted.",
            ],
            "cited_evidence": [
                {"evidence_id": eid, "url": r["url"], "label": r["label"]}
                for eid, r in state.data["evidence"].items()
                if r["is_primary_source"]
            ],
            "external_actions": [
                {"action": "publish", "target": "company blog / press statement", "status": "BLOCKED"},
                {"action": "post", "target": "official social channels", "status": "BLOCKED"},
                {"action": "notify", "target": "enterprise customers", "status": "BLOCKED"},
            ],
            "approval_required": True,
        }
        state.log_event("response_planned",
                        f"Response plan built: {characterization}. All external actions BLOCKED pending approval.")
        state.save()
        return plan
