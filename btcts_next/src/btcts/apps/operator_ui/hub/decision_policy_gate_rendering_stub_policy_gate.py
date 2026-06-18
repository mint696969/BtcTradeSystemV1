# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_rendering_stub_policy_gate.py
# desc: Read-only policy/status gate for a future static rendering stub of decision ledger policy gate visibility. No rendering implementation, commands, runtime wiring, decision append, writes, mode apply, grants, or broker behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping, Tuple

from btcts.apps.operator_ui.hub.decision_policy_gate_visibility import (
    DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY,
    build_decision_policy_gate_dashboard_registry_visibility_packet,
)

LOGIC_VERSION = "operator_ui_decision_policy_gate_rendering_stub_policy_gate.s148.v1"
POLICY_SCOPE = "operator_ui_read_only_rendering_stub_policy_gate"

REQUIRED_PLAN_REFERENCES = (
    "docs/architecture/OPERATOR_UI_DECISION_POLICY_GATE_READ_ONLY_RENDERING_PLAN_2026-06-18.md",
    "btcts.apps.operator_ui.hub.decision_policy_gate_visibility.build_decision_policy_gate_dashboard_registry_visibility_packet",
    "btcts.apps.operator_ui.components.autotrade_decision_ledger_policy_gate_display.build_autotrade_decision_ledger_policy_gate_display_packet",
)
SAFE_FIELD_GROUPS = (
    "gate_identity",
    "safety_state",
    "operator_policy_state",
    "required_approvals",
    "required_guards",
    "non_permissions",
    "blockers_warnings",
    "registry_visibility",
    "source_metadata",
)
NON_PERMISSIONS = (
    "no_ui_rendering_implementation_in_s148",
    "no_command_buttons_in_s148",
    "no_forms_or_toggles_in_s148",
    "no_runtime_wiring_in_s148",
    "no_decision_append_in_s148",
    "no_live_shadow_behavior_modification_in_s148",
    "no_persist_true_path_in_s148",
    "no_mode_apply_in_s148",
    "no_prearmed_grant_execution_in_s148",
    "no_broker_or_private_api_in_s148",
    "no_external_api_or_collector_import_in_s148",
)


@dataclass(frozen=True)
class DecisionPolicyGateRenderingStubPolicyGate:
    gate_id: str
    gate_state: str
    policy_scope: str = POLICY_SCOPE
    source_key: str = DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY
    rendering_plan_acknowledged: bool = False
    static_read_only_stub_requested: bool = False
    visibility_packet_available: bool = False
    source_entry_available: bool = False
    health_page_visible: bool = False
    future_widget_page_visible: bool = False
    rendering_stub_policy_gate_only: bool = True
    rendering_stub_allowed: bool = False
    ui_rendering_implementation_allowed: bool = False
    command_buttons_allowed: bool = False
    forms_or_toggles_allowed: bool = False
    runtime_wiring_allowed: bool = False
    required_plan_references: Tuple[str, ...] = REQUIRED_PLAN_REFERENCES
    safe_field_groups: Tuple[str, ...] = SAFE_FIELD_GROUPS
    non_permissions: Tuple[str, ...] = NON_PERMISSIONS
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    not_runtime_wiring: bool = True
    not_ui_rendering: bool = True
    no_command_buttons: bool = True
    decision_append_allowed: bool = False
    decision_ledger_integration_allowed: bool = False
    live_shadow_behavior_change_allowed: bool = False
    persist_true_allowed: bool = False
    would_append_shadow_decision: bool = False
    would_apply_mode: bool = False
    would_execute_prearmed_grant: bool = False
    would_write_runtime_artifact: bool = False
    would_write_preview_status_artifact: bool = False
    would_send_to_broker: bool = False
    broker_execution_requested: bool = False
    mode_apply_requested: bool = False
    command_ledger_append_requested: bool = False
    approval_append_requested: bool = False

    @property
    def closed(self) -> bool:
        return self.gate_state == "blocked"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["required_plan_references"] = list(self.required_plan_references)
        data["safe_field_groups"] = list(self.safe_field_groups)
        data["non_permissions"] = list(self.non_permissions)
        data["blockers"] = list(self.blockers)
        data["warnings"] = list(self.warnings)
        data["closed"] = self.closed
        data["logic_version"] = LOGIC_VERSION
        return data


def _payload(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _tuple_text(value: Any) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value else ()
    try:
        return tuple(str(item) for item in value if str(item))
    except TypeError:
        text = str(value)
        return (text,) if text else ()


def _unique(values: list[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


def _dangerous_payload_blockers(prefix: str, data: Mapping[str, Any]) -> list[str]:
    checks = {
        "rendering_stub_allowed": "rendering_stub_allowance",
        "ui_rendering_implementation_allowed": "ui_rendering_implementation_allowance",
        "command_buttons_allowed": "command_buttons_allowance",
        "forms_or_toggles_allowed": "forms_or_toggles_allowance",
        "runtime_wiring_allowed": "runtime_wiring_allowance",
        "decision_append_allowed": "decision_append_allowance",
        "decision_ledger_integration_allowed": "decision_ledger_integration_allowance",
        "live_shadow_behavior_change_allowed": "live_shadow_behavior_change_allowance",
        "persist_true_allowed": "persist_true_allowance",
        "would_append_shadow_decision": "shadow_decision_append",
        "would_apply_mode": "mode_apply",
        "would_execute_prearmed_grant": "prearmed_grant_execution",
        "would_write_runtime_artifact": "runtime_artifact_write",
        "would_write_preview_status_artifact": "preview_status_artifact_write",
        "would_send_to_broker": "broker_send",
        "broker_execution_requested": "broker_execution_request",
        "mode_apply_requested": "mode_apply_request",
        "command_ledger_append_requested": "command_ledger_append_request",
        "approval_append_requested": "approval_append_request",
    }
    blockers: list[str] = []
    for attr, code in checks.items():
        if bool(data.get(attr, False)):
            blockers.append(f"{prefix}_{code}_not_allowed")
    if data.get("read_only", True) is not True:
        blockers.append(f"{prefix}_not_read_only")
    if data.get("non_executing", True) is not True:
        blockers.append(f"{prefix}_not_non_executing")
    return blockers


def build_decision_policy_gate_rendering_stub_policy_gate(
    visibility_packet: Mapping[str, Any] | None = None,
    *,
    rendering_plan_acknowledged: bool = False,
    static_read_only_stub_requested: bool = False,
) -> DecisionPolicyGateRenderingStubPolicyGate:
    if visibility_packet is None:
        packet = build_decision_policy_gate_dashboard_registry_visibility_packet()
    else:
        packet = _payload(visibility_packet)
    blockers: list[str] = ["s148_policy_gate_does_not_authorize_rendering_implementation"]
    warnings: list[str] = []

    if not packet:
        blockers.append("visibility_packet_missing")
    else:
        blockers.extend(_tuple_text(packet.get("blockers")))
        warnings.extend(_tuple_text(packet.get("warnings")))
        blockers.extend(_dangerous_payload_blockers("visibility_packet", packet))
        if packet.get("source_entry_available") is not True:
            blockers.append("visibility_source_entry_missing")
        if packet.get("health_page_visible") is not True:
            warnings.append("health_page_visibility_missing")
        if packet.get("future_widget_page_visible") is not True:
            warnings.append("future_widget_visibility_missing")

    if not rendering_plan_acknowledged:
        blockers.append("rendering_plan_acknowledgement_missing")
    if static_read_only_stub_requested:
        blockers.append("static_read_only_stub_request_not_authorized_in_s148")

    blocked_tuple = _unique(blockers)
    warning_tuple = _unique(warnings)
    return DecisionPolicyGateRenderingStubPolicyGate(
        gate_id=f"{LOGIC_VERSION}:{DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY}",
        gate_state="blocked" if blocked_tuple else "review",
        rendering_plan_acknowledged=bool(rendering_plan_acknowledged),
        static_read_only_stub_requested=bool(static_read_only_stub_requested),
        visibility_packet_available=bool(packet),
        source_entry_available=bool(packet.get("source_entry_available")) if packet else False,
        health_page_visible=bool(packet.get("health_page_visible")) if packet else False,
        future_widget_page_visible=bool(packet.get("future_widget_page_visible")) if packet else False,
        rendering_stub_policy_gate_only=True,
        rendering_stub_allowed=False,
        ui_rendering_implementation_allowed=False,
        command_buttons_allowed=False,
        forms_or_toggles_allowed=False,
        runtime_wiring_allowed=False,
        required_plan_references=REQUIRED_PLAN_REFERENCES,
        safe_field_groups=SAFE_FIELD_GROUPS,
        non_permissions=NON_PERMISSIONS,
        blockers=blocked_tuple,
        warnings=warning_tuple,
        read_only=True,
        non_executing=True,
        not_runtime_wiring=True,
        not_ui_rendering=True,
        no_command_buttons=True,
        decision_append_allowed=False,
        decision_ledger_integration_allowed=False,
        live_shadow_behavior_change_allowed=False,
        persist_true_allowed=False,
        would_append_shadow_decision=False,
        would_apply_mode=False,
        would_execute_prearmed_grant=False,
        would_write_runtime_artifact=False,
        would_write_preview_status_artifact=False,
        would_send_to_broker=False,
        broker_execution_requested=False,
        mode_apply_requested=False,
        command_ledger_append_requested=False,
        approval_append_requested=False,
    )
