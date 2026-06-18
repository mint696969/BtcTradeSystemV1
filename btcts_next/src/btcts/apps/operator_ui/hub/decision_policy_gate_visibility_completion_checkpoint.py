# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_completion_checkpoint.py
# desc: Pure data read-only completion checkpoint for decision policy gate Operator/UI visibility chain. No UI implementation, commands, runtime payload loading, writes, mode apply, grants, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.autotrade_decision_ledger_policy_gate_display import (
    AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_dashboard_status_index import (
    DECISION_POLICY_GATE_DASHBOARD_STATUS_INDEX_CONTRACT,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_dashboard_status_index_registry_visibility import (
    DASHBOARD_STATUS_INDEX_REGISTRY_VISIBILITY_CONTRACT,
    build_decision_policy_gate_dashboard_status_index_registry_visibility_packet,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_static_section_registry_visibility import (
    STATIC_SECTION_REGISTRY_VISIBILITY_CONTRACT,
    build_decision_policy_gate_static_section_registry_visibility_packet,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility import (
    DECISION_POLICY_GATE_REGISTRY_VISIBILITY_CONTRACT,
    build_decision_policy_gate_dashboard_registry_visibility_packet,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_chain_summary import (
    DECISION_POLICY_GATE_VISIBILITY_CHAIN_SUMMARY_CONTRACT,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_chain_summary_registry_visibility import (
    VISIBILITY_CHAIN_SUMMARY_REGISTRY_VISIBILITY_CONTRACT,
    build_decision_policy_gate_visibility_chain_summary_registry_visibility_packet,
)

CHECKPOINT_KEY = "decision_policy_gate_read_only_visibility_completion_checkpoint"

CHECKPOINT_COMPONENT_KEYS = (
    "decision_policy_gate_display_registry_visibility",
    "decision_policy_gate_static_section_registry_visibility",
    "decision_policy_gate_dashboard_status_index_registry_visibility",
    "decision_policy_gate_visibility_chain_summary_registry_visibility",
)

DECISION_POLICY_GATE_VISIBILITY_COMPLETION_CHECKPOINT_CONTRACT = {
    "checkpoint_key": CHECKPOINT_KEY,
    "checkpoint_type": "decision_policy_gate_read_only_visibility_completion_checkpoint_packet",
    "dashboard_role": "operator_ui_read_only_visibility_completion_checkpoint",
    "read_only_contract": True,
    "non_executing": True,
    "data_model_only": True,
    "checkpoint_only": True,
    "visibility_completion_checkpoint_only": True,
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


def _payload(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _bool_token(value: Any) -> str:
    return "true" if bool(value) else "false"


def _component(component_key: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    visible_pages = tuple(str(item) for item in (packet.get("visible_pages") or ()) if item)
    source_entry_available = bool(packet.get("source_entry_available"))
    health_visible = bool(packet.get("health_page_visible"))
    future_visible = bool(packet.get("future_widget_page_visible"))
    not_runtime_loaded = bool(packet.get("not_loaded_as_runtime_display_source", True))
    complete = source_entry_available and health_visible and future_visible and not_runtime_loaded
    return {
        "component_key": component_key,
        "visibility_packet_available": bool(packet),
        "source_entry_available": source_entry_available,
        "source_key": packet.get("source_key"),
        "source_type": packet.get("source_type"),
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": health_visible,
        "future_widget_page_visible": future_visible,
        "not_loaded_as_runtime_display_source": not_runtime_loaded,
        "read_only_contract": True,
        "non_executing": True,
        "data_model_only": bool(packet.get("data_model_only", True)),
        "not_runtime_payload_loading": True,
        "not_runtime_wiring": True,
        "not_ui_rendering": True,
        "no_command_buttons": True,
        "complete_for_read_only_visibility": complete,
    }


def build_decision_policy_gate_visibility_completion_checkpoint_packet(
    display_registry_visibility_packet: Mapping[str, Any] | None = None,
    static_section_registry_visibility_packet: Mapping[str, Any] | None = None,
    dashboard_status_index_registry_visibility_packet: Mapping[str, Any] | None = None,
    visibility_chain_summary_registry_visibility_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    display_visibility = _payload(display_registry_visibility_packet) or build_decision_policy_gate_dashboard_registry_visibility_packet()
    static_visibility = _payload(static_section_registry_visibility_packet) or build_decision_policy_gate_static_section_registry_visibility_packet()
    status_index_visibility = _payload(dashboard_status_index_registry_visibility_packet) or build_decision_policy_gate_dashboard_status_index_registry_visibility_packet()
    summary_visibility = _payload(visibility_chain_summary_registry_visibility_packet) or build_decision_policy_gate_visibility_chain_summary_registry_visibility_packet()

    components = (
        _component("decision_policy_gate_display_registry_visibility", display_visibility),
        _component("decision_policy_gate_static_section_registry_visibility", static_visibility),
        _component("decision_policy_gate_dashboard_status_index_registry_visibility", status_index_visibility),
        _component("decision_policy_gate_visibility_chain_summary_registry_visibility", summary_visibility),
    )
    visible_pages = tuple(dict.fromkeys(page for item in components for page in item["visible_pages"]))
    all_source_entries_available = all(bool(item["source_entry_available"]) for item in components)
    all_health_visible = all(bool(item["health_page_visible"]) for item in components)
    all_future_visible = all(bool(item["future_widget_page_visible"]) for item in components)
    all_not_runtime_loaded = all(bool(item["not_loaded_as_runtime_display_source"]) for item in components)
    completion_ready = all(bool(item["complete_for_read_only_visibility"]) for item in components)
    return {
        **DECISION_POLICY_GATE_VISIBILITY_COMPLETION_CHECKPOINT_CONTRACT,
        "checkpoint_components": CHECKPOINT_COMPONENT_KEYS,
        "components": components,
        "component_count": len(components),
        "all_source_entries_available": all_source_entries_available,
        "all_health_page_visible": all_health_visible,
        "all_future_widget_page_visible": all_future_visible,
        "all_not_loaded_as_runtime_display_source": all_not_runtime_loaded,
        "read_only_visibility_completion_ready": completion_ready,
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": all_health_visible,
        "future_widget_page_visible": all_future_visible,
        "display_packet_contract": dict(AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT),
        "display_registry_visibility_contract": dict(DECISION_POLICY_GATE_REGISTRY_VISIBILITY_CONTRACT),
        "static_section_registry_visibility_contract": dict(STATIC_SECTION_REGISTRY_VISIBILITY_CONTRACT),
        "dashboard_status_index_contract": dict(DECISION_POLICY_GATE_DASHBOARD_STATUS_INDEX_CONTRACT),
        "dashboard_status_index_registry_visibility_contract": dict(DASHBOARD_STATUS_INDEX_REGISTRY_VISIBILITY_CONTRACT),
        "visibility_chain_summary_contract": dict(DECISION_POLICY_GATE_VISIBILITY_CHAIN_SUMMARY_CONTRACT),
        "visibility_chain_summary_registry_visibility_contract": dict(VISIBILITY_CHAIN_SUMMARY_REGISTRY_VISIBILITY_CONTRACT),
        "not_loaded_as_runtime_display_source": True,
        "summary_line": (
            f"{CHECKPOINT_KEY}: components={len(components)} / "
            f"completion_ready={_bool_token(completion_ready)} / "
            f"health_visible={_bool_token(all_health_visible)} / "
            f"future_widget_visible={_bool_token(all_future_visible)} / "
            "read_only_visibility_completion_checkpoint"
        ),
    }
