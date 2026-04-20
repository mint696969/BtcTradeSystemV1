# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_operator_tactic_context.py
# desc: Thin consumer-side normalizer for optional tactic proposal context in AI Operator.

from __future__ import annotations


def build_operator_tactic_context(tactic_payload: dict | None) -> dict:
    if not isinstance(tactic_payload, dict):
        return {}

    diagnostics = dict(tactic_payload.get("diagnostics") or {})
    parameter_trace = dict(diagnostics.get("parameter_trace") or {})
    selection_trace = dict(diagnostics.get("selection_trace") or {})

    primary_tactic_key = str(tactic_payload.get("primary_tactic_key") or "").strip()
    proposal_state = str(tactic_payload.get("proposal_state") or "").strip()
    scenario_regime = str(tactic_payload.get("scenario_regime") or "").strip()

    normalized = {
        "primary_tactic_key": primary_tactic_key or "unknown",
        "proposal_state": proposal_state or "unknown",
        "scenario_regime": scenario_regime or "unknown",
        "profile_kind": str(parameter_trace.get("profile_kind") or "").strip()
        or "unknown",
        "rollback_ready": bool(tactic_payload.get("rollback_ready")),
        "review_needed": bool(tactic_payload.get("review_needed")),
        "selection_bias_tags": tuple(selection_trace.get("selection_bias_tags") or ()),
    }

    if normalized["primary_tactic_key"] == "unknown":
        return {}
    return normalized