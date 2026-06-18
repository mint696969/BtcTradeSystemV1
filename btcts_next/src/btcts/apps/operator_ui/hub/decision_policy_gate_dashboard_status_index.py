# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_dashboard_status_index.py
# desc: Pure data dashboard status index for decision policy gate visibility packets. No UI implementation, commands, runtime payload loading, writes, mode apply, grants, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_decision_ledger_policy_gate_display import (
    AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT,
    build_autotrade_decision_ledger_policy_gate_display_packet,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_static_section_model import (
    DECISION_POLICY_GATE_STATIC_SECTION_MODEL_CONTRACT,
    build_decision_policy_gate_static_section_model,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_static_section_registry_visibility import (
    STATIC_SECTION_REGISTRY_VISIBILITY_CONTRACT,
    build_decision_policy_gate_static_section_registry_visibility_packet,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility import (
    DECISION_POLICY_GATE_REGISTRY_VISIBILITY_CONTRACT,
    build_decision_policy_gate_dashboard_registry_visibility_packet,
)

INDEX_KEY = "decision_policy_gate_read_only_dashboard_status_index"

DECISION_POLICY_GATE_DASHBOARD_STATUS_INDEX_CONTRACT = {
    "index_key": INDEX_KEY,
    "index_type": "decision_policy_gate_read_only_dashboard_status_index",
    "dashboard_role": "operator_ui_read_only_status_index",
    "read_only_contract": True,
    "non_executing": True,
    "data_model_only": True,
    "status_index_only": True,
    "not_runtime_payload_loading": True,
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

INDEX_COMPONENTS = (
    "decision_policy_gate_display_packet",
    "decision_policy_gate_registry_visibility_packet",
    "decision_policy_gate_static_section_model",
    "decision_policy_gate_static_section_registry_visibility_packet",
)


def _payload(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _bool_token(value: Any) -> str:
    return "true" if bool(value) else "false"


def _entry(component_key: str, packet: Mapping[str, Any], *, available_key: str | None = None) -> dict[str, Any]:
    available = bool(packet.get(available_key)) if available_key else bool(packet)
    return {
        "component_key": component_key,
        "available": available,
        "source_key": packet.get("source_key") or packet.get("section_key") or packet.get("index_key"),
        "source_type": packet.get("source_type") or packet.get("section_type") or packet.get("visibility_packet_type"),
        "dashboard_role": packet.get("dashboard_role"),
        "read_only_contract": True,
        "non_executing": True,
        "data_model_only": bool(packet.get("data_model_only", True)),
        "not_runtime_payload_loading": True,
        "not_runtime_wiring": True,
        "not_ui_rendering": True,
        "no_command_buttons": True,
        "summary": packet.get("summary_line") or packet.get("compact_line") or component_key,
    }


def build_decision_policy_gate_dashboard_status_index_packet(
    display_packet: Mapping[str, Any] | None = None,
    registry_visibility_packet: Mapping[str, Any] | None = None,
    static_section_model: Mapping[str, Any] | None = None,
    static_section_registry_visibility_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    display = _payload(display_packet) or build_autotrade_decision_ledger_policy_gate_display_packet(None)
    registry_visibility = _payload(registry_visibility_packet) or build_decision_policy_gate_dashboard_registry_visibility_packet()
    static_registry_visibility = (
        _payload(static_section_registry_visibility_packet)
        or build_decision_policy_gate_static_section_registry_visibility_packet()
    )
    section_model = _payload(static_section_model) or build_decision_policy_gate_static_section_model(
        display,
        registry_visibility,
    )
    components = (
        _entry("decision_policy_gate_display_packet", display, available_key="gate_available"),
        _entry("decision_policy_gate_registry_visibility_packet", registry_visibility, available_key="source_entry_available"),
        _entry("decision_policy_gate_static_section_model", section_model, available_key="stub_policy_gate_available"),
        _entry("decision_policy_gate_static_section_registry_visibility_packet", static_registry_visibility, available_key="source_entry_available"),
    )
    visible_pages = tuple(str(item) for item in (static_registry_visibility.get("visible_pages") or registry_visibility.get("visible_pages") or ()) if item)
    return {
        **DECISION_POLICY_GATE_DASHBOARD_STATUS_INDEX_CONTRACT,
        "components": components,
        "component_count": len(components),
        "index_components": INDEX_COMPONENTS,
        "display_packet_contract": dict(AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT),
        "registry_visibility_contract": dict(DECISION_POLICY_GATE_REGISTRY_VISIBILITY_CONTRACT),
        "static_section_model_contract": dict(DECISION_POLICY_GATE_STATIC_SECTION_MODEL_CONTRACT),
        "static_section_registry_visibility_contract": dict(STATIC_SECTION_REGISTRY_VISIBILITY_CONTRACT),
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": bool(static_registry_visibility.get("health_page_visible") or registry_visibility.get("health_page_visible")),
        "future_widget_page_visible": bool(static_registry_visibility.get("future_widget_page_visible") or registry_visibility.get("future_widget_page_visible")),
        "display_packet_available": bool(display),
        "registry_visibility_packet_available": bool(registry_visibility),
        "static_section_model_available": bool(section_model),
        "static_section_registry_visibility_packet_available": bool(static_registry_visibility),
        "summary_line": (
            f"{INDEX_KEY}: components={len(components)} / "
            f"health_visible={_bool_token(static_registry_visibility.get('health_page_visible') or registry_visibility.get('health_page_visible'))} / "
            f"future_widget_visible={_bool_token(static_registry_visibility.get('future_widget_page_visible') or registry_visibility.get('future_widget_page_visible'))} / "
            "read_only_status_index"
        ),
    }
