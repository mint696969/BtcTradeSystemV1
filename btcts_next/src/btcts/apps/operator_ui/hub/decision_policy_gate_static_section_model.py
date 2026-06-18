# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_static_section_model.py
# desc: Pure data static read-only section model for decision ledger policy gate visibility. No UI rendering implementation, commands, runtime wiring, decision append, writes, mode apply, grants, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.hub.decision_policy_gate_rendering_stub_policy_gate import (
    DecisionPolicyGateRenderingStubPolicyGate,
    build_decision_policy_gate_rendering_stub_policy_gate,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility import (
    build_decision_policy_gate_dashboard_registry_visibility_packet,
)

SECTION_KEY = "decision_policy_gate_static_read_only_section"
SECTION_TITLE = "Decision Ledger Policy Gate"

DECISION_POLICY_GATE_STATIC_SECTION_MODEL_CONTRACT = {
    "section_key": SECTION_KEY,
    "section_type": "static_read_only_section_model",
    "source_type": "decision_policy_gate_visibility_and_stub_policy_gate",
    "dashboard_role": "operator_ui_static_read_only_section_model",
    "read_only_contract": True,
    "non_executing": True,
    "layout_decision_free": True,
    "data_model_only": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "no_command_buttons": True,
    "command_buttons_allowed": False,
    "forms_or_toggles_allowed": False,
    "runtime_wiring_allowed": False,
    "ui_rendering_implementation_allowed": False,
    "decision_append_allowed": False,
    "decision_ledger_integration_allowed": False,
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

SAFE_LABELS = (
    "DISPLAY ONLY",
    "READ ONLY",
    "NON EXECUTING",
    "DECISION APPEND NOT AUTHORIZED",
    "LIVE SHADOW CHANGE NOT AUTHORIZED",
    "PERSIST TRUE NOT AUTHORIZED",
    "BROKER EXECUTION NOT AUTHORIZED",
    "NO COMMAND BUTTONS",
)


def _payload(value: object | Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        data = to_dict()
        return dict(data) if isinstance(data, Mapping) else {}
    return {}


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


def _row(key: str, label: str, value: Any, *, severity: str = "info", safe: bool = True) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "value": value,
        "severity": severity,
        "safe_to_display": bool(safe),
        "read_only": True,
        "non_executing": True,
        "not_runtime_wiring": True,
        "no_command_buttons": True,
    }


def _list_rows(prefix: str, label: str, values: Any, *, severity: str = "info") -> tuple[dict[str, Any], ...]:
    items = _tuple_text(values)
    if not items:
        return (_row(prefix + ":none", label, "none", severity="muted"),)
    return tuple(_row(f"{prefix}:{idx}", label, item, severity=severity) for idx, item in enumerate(items, start=1))


def _severity_from_gate_state(state: Any) -> str:
    text = str(state or "").strip().lower()
    if text == "blocked":
        return "blocked"
    if text == "review":
        return "review"
    return "info"


def build_decision_policy_gate_static_section_model(
    display_packet: Mapping[str, Any] | None = None,
    visibility_packet: Mapping[str, Any] | None = None,
    stub_policy_gate: DecisionPolicyGateRenderingStubPolicyGate | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    display = _payload(display_packet)
    visibility = _payload(visibility_packet) or build_decision_policy_gate_dashboard_registry_visibility_packet()
    gate_obj = stub_policy_gate if stub_policy_gate is not None else build_decision_policy_gate_rendering_stub_policy_gate(visibility)
    gate = _payload(gate_obj)

    gate_state = gate.get("gate_state") or display.get("gate_state") or "unavailable"
    rows: list[dict[str, Any]] = [
        _row("section_title", "Section", SECTION_TITLE),
        _row("safety_labels", "Safety labels", ", ".join(SAFE_LABELS), severity="blocked"),
        _row("gate_state", "Policy gate state", gate_state, severity=_severity_from_gate_state(gate_state)),
        _row("display_state", "Display packet state", display.get("display_state", "unavailable"), severity=_severity_from_gate_state(display.get("display_state"))),
        _row("registry_source_visible", "Registry source visible", _bool_token(visibility.get("source_entry_available"))),
        _row("health_page_visible", "Health page visible", _bool_token(visibility.get("health_page_visible"))),
        _row("future_widget_page_visible", "Future-widget page visible", _bool_token(visibility.get("future_widget_page_visible"))),
        _row("rendering_stub_allowed", "Static section implementation allowed", _bool_token(gate.get("rendering_stub_allowed")), severity="blocked"),
        _row("ui_rendering_implementation_allowed", "UI implementation allowed", _bool_token(gate.get("ui_rendering_implementation_allowed")), severity="blocked"),
        _row("command_buttons_allowed", "Command buttons allowed", _bool_token(gate.get("command_buttons_allowed")), severity="blocked"),
        _row("forms_or_toggles_allowed", "Forms/toggles allowed", _bool_token(gate.get("forms_or_toggles_allowed")), severity="blocked"),
        _row("runtime_wiring_allowed", "Runtime wiring allowed", _bool_token(gate.get("runtime_wiring_allowed")), severity="blocked"),
        _row("decision_append_allowed", "Decision append allowed", _bool_token(gate.get("decision_append_allowed") or display.get("decision_append_allowed")), severity="blocked"),
        _row("live_shadow_behavior_change_allowed", "Live Shadow behavior change allowed", _bool_token(gate.get("live_shadow_behavior_change_allowed") or display.get("live_shadow_behavior_change_allowed")), severity="blocked"),
        _row("persist_true_allowed", "Persist true path allowed", _bool_token(gate.get("persist_true_allowed") or display.get("persist_true_allowed")), severity="blocked"),
        _row("source_key", "Source key", visibility.get("source_key") or gate.get("source_key") or "unknown"),
    ]
    rows.extend(_list_rows("required_approval", "Required approval", display.get("required_approvals"), severity="review"))
    rows.extend(_list_rows("required_guard", "Required guard", display.get("required_guards") or gate.get("required_plan_references"), severity="review"))
    rows.extend(_list_rows("non_permission", "Non-permission", display.get("non_permissions") or gate.get("non_permissions"), severity="blocked"))
    rows.extend(_list_rows("blocker", "Blocker", display.get("blockers") or gate.get("blockers"), severity="blocked"))
    rows.extend(_list_rows("warning", "Warning", display.get("warnings") or gate.get("warnings"), severity="review"))

    return {
        **DECISION_POLICY_GATE_STATIC_SECTION_MODEL_CONTRACT,
        "section_title": SECTION_TITLE,
        "safe_labels": SAFE_LABELS,
        "rows": tuple(rows),
        "row_count": len(rows),
        "summary_line": (
            f"{SECTION_TITLE}: gate={gate_state} / "
            f"decision_append_allowed={_bool_token(gate.get('decision_append_allowed') or display.get('decision_append_allowed'))} / "
            f"ui_implementation_allowed={_bool_token(gate.get('ui_rendering_implementation_allowed'))} / "
            "static_data_only"
        ),
        "display_packet_available": bool(display),
        "visibility_packet_available": bool(visibility),
        "stub_policy_gate_available": bool(gate),
    }
