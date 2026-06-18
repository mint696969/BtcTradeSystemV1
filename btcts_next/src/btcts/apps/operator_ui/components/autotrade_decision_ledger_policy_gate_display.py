# path: ./btcts_next/src/btcts/apps/operator_ui/components/autotrade_decision_ledger_policy_gate_display.py
# desc: Read-only Operator/UI display packet for AutoTradeDecisionLedgerIntegrationPolicyGate. No Streamlit rendering, runtime wiring, commands, decision append, mode apply, grant execution, artifact write, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.autotrade.decision_ledger_policy_gate import AutoTradeDecisionLedgerIntegrationPolicyGate

AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT = {
    "section_type": "autotrade_decision_ledger_policy_gate_display_packet",
    "source_type": "autotrade_decision_ledger_policy_gate",
    "dashboard_role": "operator_ui_read_only_display",
    "read_only_contract": True,
    "non_executing": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "no_command_buttons": True,
    "decision_ledger_integration_allowed": False,
    "decision_append_allowed": False,
    "live_shadow_behavior_change_allowed": False,
    "persist_true_allowed": False,
    "would_append_shadow_decision": False,
    "would_apply_mode": False,
    "would_execute_prearmed_grant": False,
    "would_write_runtime_artifact": False,
    "would_write_preview_status_artifact": False,
    "would_send_to_broker": False,
    "broker_execution_requested": False,
    "mode_apply_requested": False,
    "command_ledger_append_requested": False,
    "approval_append_requested": False,
}


def _payload(gate: AutoTradeDecisionLedgerIntegrationPolicyGate | Mapping[str, Any] | None) -> dict[str, Any]:
    if gate is None:
        return {}
    if isinstance(gate, Mapping):
        return dict(gate)
    return gate.to_dict()


def _text(value: Any, fallback: str = "unknown") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _bool_token(value: Any) -> str:
    return "true" if bool(value) else "false"


def _tuple_text(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    try:
        return tuple(str(item) for item in value if str(item))
    except TypeError:
        text = str(value)
        return (text,) if text else ()


def _severity(state: str) -> str:
    if state == "blocked":
        return "blocked"
    if state == "review":
        return "review"
    if state == "open":
        return "review"
    return "unavailable"


def decision_ledger_policy_gate_compact_line(gate: AutoTradeDecisionLedgerIntegrationPolicyGate | Mapping[str, Any] | None) -> str:
    data = _payload(gate)
    if not data:
        return "decision_ledger_policy_gate unavailable / display_only"
    return (
        "decision_ledger_policy_gate="
        f"{_text(data.get('gate_state'))} / "
        f"decision_append_allowed={_bool_token(data.get('decision_append_allowed'))} / "
        f"live_shadow_change_allowed={_bool_token(data.get('live_shadow_behavior_change_allowed'))} / "
        f"persist_true_allowed={_bool_token(data.get('persist_true_allowed'))} / display_only"
    )


def decision_ledger_policy_gate_snapshot_lines(gate: AutoTradeDecisionLedgerIntegrationPolicyGate | Mapping[str, Any] | None) -> tuple[str, ...]:
    data = _payload(gate)
    if not data:
        return (
            "gate_available=false",
            "display_state=unavailable",
            "read_only_contract=true",
            "not_runtime_wiring=true",
            "not_ui_rendering=true",
            "no_command_buttons=true",
        )

    blockers = _tuple_text(data.get("blockers"))
    warnings = _tuple_text(data.get("warnings"))
    required_approvals = _tuple_text(data.get("required_approvals"))
    required_guards = _tuple_text(data.get("required_guards"))
    non_permissions = _tuple_text(data.get("non_permissions"))
    lines = [
        "gate_available=true",
        "display_state=" + _severity(_text(data.get("gate_state"), "unavailable")),
        "gate_id=" + _text(data.get("gate_id")),
        "generated_at=" + _text(data.get("generated_at")),
        "requested_scope=" + _text(data.get("requested_scope")),
        "source_preflight_id=" + _text(data.get("source_preflight_id")),
        "source_context_id=" + _text(data.get("source_context_id")),
        "preflight_state=" + _text(data.get("preflight_state")),
        "context_state=" + _text(data.get("context_state")),
        "operator_policy_acknowledged=" + _bool_token(data.get("operator_policy_acknowledged")),
        "explicit_operator_approval=" + _bool_token(data.get("explicit_operator_approval")),
        "decision_ledger_integration_allowed=" + _bool_token(data.get("decision_ledger_integration_allowed")),
        "decision_append_allowed=" + _bool_token(data.get("decision_append_allowed")),
        "live_shadow_behavior_change_allowed=" + _bool_token(data.get("live_shadow_behavior_change_allowed")),
        "persist_true_allowed=" + _bool_token(data.get("persist_true_allowed")),
        "required_approval_count=" + str(len(required_approvals)),
        "required_guard_count=" + str(len(required_guards)),
        "non_permission_count=" + str(len(non_permissions)),
        "blocker_count=" + str(len(blockers)),
        "warning_count=" + str(len(warnings)),
        "read_only=true",
        "non_executing=true",
        "policy_gate_only=" + _bool_token(data.get("policy_gate_only")),
        "would_append_shadow_decision=" + _bool_token(data.get("would_append_shadow_decision")),
        "would_apply_mode=" + _bool_token(data.get("would_apply_mode")),
        "would_execute_prearmed_grant=" + _bool_token(data.get("would_execute_prearmed_grant")),
        "would_write_runtime_artifact=" + _bool_token(data.get("would_write_runtime_artifact")),
        "would_write_preview_status_artifact=" + _bool_token(data.get("would_write_preview_status_artifact")),
        "would_send_to_broker=" + _bool_token(data.get("would_send_to_broker")),
        "broker_execution_requested=" + _bool_token(data.get("broker_execution_requested")),
        "mode_apply_requested=" + _bool_token(data.get("mode_apply_requested")),
        "command_ledger_append_requested=" + _bool_token(data.get("command_ledger_append_requested")),
        "approval_append_requested=" + _bool_token(data.get("approval_append_requested")),
        "read_only_contract=true",
        "not_runtime_wiring=true",
        "not_ui_rendering=true",
        "no_command_buttons=true",
    ]
    if required_approvals:
        lines.append("required_approvals=" + ",".join(required_approvals))
    if required_guards:
        lines.append("required_guards=" + ",".join(required_guards))
    if non_permissions:
        lines.append("non_permissions=" + ",".join(non_permissions))
    if blockers:
        lines.append("blockers=" + ",".join(blockers))
    if warnings:
        lines.append("warnings=" + ",".join(warnings))
    return tuple(lines)


def build_autotrade_decision_ledger_policy_gate_display_packet(
    gate: AutoTradeDecisionLedgerIntegrationPolicyGate | Mapping[str, Any] | None,
) -> dict[str, Any]:
    data = _payload(gate)
    gate_state = _text(data.get("gate_state"), "unavailable") if data else "unavailable"
    required_approvals = _tuple_text(data.get("required_approvals")) if data else ()
    required_guards = _tuple_text(data.get("required_guards")) if data else ()
    non_permissions = _tuple_text(data.get("non_permissions")) if data else ()
    blockers = _tuple_text(data.get("blockers")) if data else ()
    warnings = _tuple_text(data.get("warnings")) if data else ()
    return {
        **AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT,
        "gate_available": bool(data),
        "display_state": _severity(gate_state),
        "gate_state": gate_state,
        "gate_id": data.get("gate_id") if data else None,
        "generated_at": data.get("generated_at") if data else None,
        "requested_scope": data.get("requested_scope") if data else None,
        "source_preflight_id": data.get("source_preflight_id") if data else None,
        "source_context_id": data.get("source_context_id") if data else None,
        "preflight_state": data.get("preflight_state") if data else None,
        "context_state": data.get("context_state") if data else None,
        "operator_policy_acknowledged": bool(data.get("operator_policy_acknowledged")) if data else False,
        "explicit_operator_approval": bool(data.get("explicit_operator_approval")) if data else False,
        "required_approvals": required_approvals,
        "required_guards": required_guards,
        "non_permissions": non_permissions,
        "blockers": blockers,
        "warnings": warnings,
        "compact_line": decision_ledger_policy_gate_compact_line(gate),
        "snapshot_lines": decision_ledger_policy_gate_snapshot_lines(gate),
    }
