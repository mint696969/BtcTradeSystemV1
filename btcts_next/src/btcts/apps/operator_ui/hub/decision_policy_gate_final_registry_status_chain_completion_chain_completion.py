# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_final_registry_status_chain_completion_chain_completion.py
# desc: Read-only chain completion packet for completed decision policy gate final registry status chain completion registry visibility chain completion and registry visibility layers. Metadata aggregation only; no UI implementation, commands, runtime payload loading, legacy chain-completion/final-status-index/registry-visibility/closeout/chain/status/checkpoint builder execution, writes, mode apply, grants, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.hub.decision_policy_gate_final_registry_status_chain_completion_chain import (
    DECISION_POLICY_GATE_FINAL_REGISTRY_STATUS_CHAIN_COMPLETION_REGISTRY_VISIBILITY_CHAIN_COMPLETION_CONTRACT,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_final_registry_status_chain_completion_chain_visibility import (
    DECISION_POLICY_GATE_FINAL_REGISTRY_STATUS_CHAIN_COMPLETION_CHAIN_REGISTRY_VISIBILITY_CONTRACT,
    build_decision_policy_gate_final_registry_status_chain_completion_chain_registry_visibility_packet,
)

CHAIN_COMPLETION_KEY = "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion"
CHAIN_COMPLETION_TYPE = "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion_packet"
CHAIN_COMPLETION_SOURCE_KEY = "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion"
FINAL_COMPONENT_KEY = "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility"

CHAIN_COMPLETION_COMPONENT_KEYS = (
    CHAIN_COMPLETION_SOURCE_KEY,
    FINAL_COMPONENT_KEY,
)

DECISION_POLICY_GATE_FINAL_REGISTRY_STATUS_CHAIN_COMPLETION_CHAIN_REGISTRY_VISIBILITY_CHAIN_COMPLETION_CONTRACT = {
    "chain_completion_key": CHAIN_COMPLETION_KEY,
    "chain_completion_type": CHAIN_COMPLETION_TYPE,
    "dashboard_role": "operator_ui_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion",
    "read_only_contract": True,
    "non_executing": True,
    "data_model_only": True,
    "chain_completion_only": True,
    "registry_visibility_chain_completion_only": True,
    "final_status_index_registry_visibility_chain_completion_only": True,
    "final_registry_status_chain_completion_chain_registry_visibility_chain_completion_only": True,
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


def _false_flags(packet: Mapping[str, Any]) -> tuple[str, ...]:
    names = (
        "command_buttons_allowed", "forms_or_toggles_allowed", "runtime_wiring_allowed", "ui_rendering_implementation_allowed",
        "decision_append_allowed", "decision_ledger_integration_allowed", "live_shadow_behavior_change_allowed", "persist_true_allowed",
        "would_append_shadow_decision", "would_apply_mode", "would_execute_prearmed_grant", "would_write_runtime_artifact",
        "would_write_preview_status_artifact", "would_send_to_broker", "broker_execution_requested", "mode_apply_requested",
        "command_ledger_append_requested", "approval_append_requested",
    )
    return tuple(name for name in names if bool(packet.get(name)))


def _visible_pages(packet: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(str(item) for item in (packet.get("visible_pages") or ()) if item)


def _chain_completion_source_component(packet: Mapping[str, Any]) -> dict[str, Any]:
    entry = _payload(packet.get("source_entry"))
    visible_pages = _visible_pages(packet)
    ready = bool(entry) and bool(packet.get("health_page_visible")) and bool(packet.get("future_widget_page_visible")) and bool(packet.get("not_loaded_as_runtime_display_source", True)) and not _false_flags(entry)
    return {
        "component_key": CHAIN_COMPLETION_SOURCE_KEY,
        "component_type": "final_registry_status_chain_completion_registry_visibility_chain_completion_catalog_source_metadata",
        "source_entry_available": bool(entry),
        "source_key": entry.get("source_key"),
        "source_type": entry.get("source_type"),
        "chain_completion_module": entry.get("chain_completion_module"),
        "chain_completion_builder": entry.get("chain_completion_builder"),
        "source_dependencies": tuple(str(item) for item in (entry.get("source_dependencies") or ()) if item),
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": bool(packet.get("health_page_visible")),
        "future_widget_page_visible": bool(packet.get("future_widget_page_visible")),
        "not_loaded_as_runtime_display_source": bool(packet.get("not_loaded_as_runtime_display_source", True)),
        "read_only_contract": bool(entry.get("read_only_contract")),
        "non_executing": bool(entry.get("non_executing", True)),
        "data_model_only": bool(entry.get("data_model_only", True)),
        "chain_completion_only": bool(entry.get("chain_completion_only", True)),
        "registry_visibility_chain_completion_only": bool(entry.get("registry_visibility_chain_completion_only", True)),
        "final_status_index_registry_visibility_chain_completion_only": bool(entry.get("final_status_index_registry_visibility_chain_completion_only", True)),
        "not_runtime_payload_loading": bool(entry.get("not_runtime_payload_loading", True)),
        "not_runtime_wiring": bool(entry.get("not_runtime_wiring", True)),
        "not_ui_rendering": bool(entry.get("not_ui_rendering", True)),
        "no_command_buttons": bool(entry.get("no_command_buttons", True)),
        "safety_violations": _false_flags(entry),
        "ready_for_registry_visibility_chain_completion": ready,
    }


def _registry_visibility_component(packet: Mapping[str, Any]) -> dict[str, Any]:
    visible_pages = _visible_pages(packet)
    ready = bool(packet) and bool(packet.get("source_entry_available")) and bool(packet.get("health_page_visible")) and bool(packet.get("future_widget_page_visible")) and bool(packet.get("not_loaded_as_runtime_display_source", True)) and not _false_flags(packet)
    return {
        "component_key": FINAL_COMPONENT_KEY,
        "component_type": "final_registry_status_chain_completion_chain_registry_visibility_metadata",
        "visibility_packet_available": bool(packet),
        "visibility_packet_type": packet.get("visibility_packet_type"),
        "source_entry_available": bool(packet.get("source_entry_available")),
        "source_key": packet.get("source_key"),
        "source_type": packet.get("source_type"),
        "chain_completion_module": packet.get("chain_completion_module"),
        "chain_completion_builder": packet.get("chain_completion_builder"),
        "source_dependencies": tuple(str(item) for item in (packet.get("source_dependencies") or ()) if item),
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": bool(packet.get("health_page_visible")),
        "future_widget_page_visible": bool(packet.get("future_widget_page_visible")),
        "not_loaded_as_runtime_display_source": bool(packet.get("not_loaded_as_runtime_display_source", True)),
        "read_only_contract": bool(packet.get("read_only_contract")),
        "non_executing": bool(packet.get("non_executing", True)),
        "data_model_only": bool(packet.get("data_model_only", True)),
        "catalog_metadata_only": bool(packet.get("catalog_metadata_only", True)),
        "registry_visibility_only": bool(packet.get("registry_visibility_only", True)),
        "chain_completion_visibility_only": bool(packet.get("chain_completion_visibility_only", True)),
        "registry_visibility_chain_completion_visibility_only": bool(packet.get("registry_visibility_chain_completion_visibility_only", True)),
        "not_runtime_payload_loading": bool(packet.get("not_runtime_payload_loading", True)),
        "not_runtime_wiring": bool(packet.get("not_runtime_wiring", True)),
        "not_ui_rendering": bool(packet.get("not_ui_rendering", True)),
        "no_command_buttons": bool(packet.get("no_command_buttons", True)),
        "safety_violations": _false_flags(packet),
        "ready_for_registry_visibility_chain_completion": ready,
    }


def build_decision_policy_gate_final_registry_status_chain_completion_chain_registry_visibility_chain_completion_packet(
    final_registry_status_chain_completion_chain_registry_visibility_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    registry_visibility = _payload(final_registry_status_chain_completion_chain_registry_visibility_packet) or build_decision_policy_gate_final_registry_status_chain_completion_chain_registry_visibility_packet()
    components = (
        _chain_completion_source_component(registry_visibility),
        _registry_visibility_component(registry_visibility),
    )
    visible_pages = tuple(dict.fromkeys(page for component in components for page in component["visible_pages"]))
    ready = all(bool(component["ready_for_registry_visibility_chain_completion"]) for component in components)
    return {
        **DECISION_POLICY_GATE_FINAL_REGISTRY_STATUS_CHAIN_COMPLETION_CHAIN_REGISTRY_VISIBILITY_CHAIN_COMPLETION_CONTRACT,
        "chain_completion_components": CHAIN_COMPLETION_COMPONENT_KEYS,
        "components": components,
        "component_count": len(components),
        "final_component_key": FINAL_COMPONENT_KEY,
        "final_component_source_key": components[-1].get("source_key"),
        "final_component_visibility_packet_type": components[-1].get("visibility_packet_type"),
        "all_components_available": all(bool(component.get("source_entry_available") or component.get("visibility_packet_available")) for component in components),
        "all_health_page_visible": all(bool(component["health_page_visible"]) for component in components),
        "all_future_widget_page_visible": all(bool(component["future_widget_page_visible"]) for component in components),
        "all_not_loaded_as_runtime_display_source": all(bool(component["not_loaded_as_runtime_display_source"]) for component in components),
        "all_safety_flags_false": all(not tuple(component.get("safety_violations") or ()) for component in components),
        "registry_visibility_chain_completion_ready": ready,
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": all(bool(component["health_page_visible"]) for component in components),
        "future_widget_page_visible": all(bool(component["future_widget_page_visible"]) for component in components),
        "chain_completion_contract": dict(DECISION_POLICY_GATE_FINAL_REGISTRY_STATUS_CHAIN_COMPLETION_REGISTRY_VISIBILITY_CHAIN_COMPLETION_CONTRACT),
        "chain_completion_registry_visibility_contract": dict(DECISION_POLICY_GATE_FINAL_REGISTRY_STATUS_CHAIN_COMPLETION_CHAIN_REGISTRY_VISIBILITY_CONTRACT),
        "not_loaded_as_runtime_display_source": True,
        "summary_line": (
            f"{CHAIN_COMPLETION_KEY}: components={len(components)} / "
            f"registry_visibility_chain_completion_ready={_bool_token(ready)} / "
            f"final_component={FINAL_COMPONENT_KEY} / "
            "read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_final_status_index_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion_registry_visibility_chain_completion"
        ),
    }
