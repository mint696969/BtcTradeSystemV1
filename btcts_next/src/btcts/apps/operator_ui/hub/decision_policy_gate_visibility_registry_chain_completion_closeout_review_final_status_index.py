# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_closeout_review_final_status_index.py
# desc: Final pure data read-only status index for completed decision policy gate closeout review and closeout review registry visibility layers. Registry-visibility metadata aggregation only; no UI implementation, commands, runtime payload loading, closeout/final/chain/status/checkpoint builder execution, writes, mode apply, grants, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_closeout_review import (
    DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CONTRACT,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_closeout_review_registry_visibility import (
    VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_REGISTRY_VISIBILITY_CONTRACT,
    build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_registry_visibility_packet,
)

CLOSEOUT_REVIEW_FINAL_STATUS_INDEX_KEY = "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_final_status_index"
CLOSEOUT_REVIEW_FINAL_STATUS_INDEX_TYPE = "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_final_status_index_packet"
CLOSEOUT_REVIEW_SOURCE_KEY = "decision_policy_gate_visibility_registry_chain_completion_closeout_review"
FINAL_COMPONENT_KEY = "decision_policy_gate_visibility_registry_chain_completion_closeout_review_registry_visibility"

CLOSEOUT_REVIEW_FINAL_STATUS_INDEX_COMPONENT_KEYS = (
    CLOSEOUT_REVIEW_SOURCE_KEY,
    FINAL_COMPONENT_KEY,
)

DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_FINAL_STATUS_INDEX_CONTRACT = {
    "final_status_index_key": CLOSEOUT_REVIEW_FINAL_STATUS_INDEX_KEY,
    "final_status_index_type": CLOSEOUT_REVIEW_FINAL_STATUS_INDEX_TYPE,
    "dashboard_role": "operator_ui_read_only_visibility_registry_chain_completion_closeout_review_final_status_index",
    "read_only_contract": True,
    "non_executing": True,
    "data_model_only": True,
    "status_index_only": True,
    "final_status_index_only": True,
    "closeout_review_final_status_index_only": True,
    "registry_visibility_chain_completion_closeout_review_final_status_index_only": True,
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
        "command_buttons_allowed",
        "forms_or_toggles_allowed",
        "runtime_wiring_allowed",
        "ui_rendering_implementation_allowed",
        "decision_append_allowed",
        "decision_ledger_integration_allowed",
        "live_shadow_behavior_change_allowed",
        "persist_true_allowed",
        "would_append_shadow_decision",
        "would_apply_mode",
        "would_execute_prearmed_grant",
        "would_write_runtime_artifact",
        "would_write_preview_status_artifact",
        "would_send_to_broker",
    )
    return tuple(name for name in names if bool(packet.get(name)))


def _source_component(packet: Mapping[str, Any]) -> dict[str, Any]:
    entry = _payload(packet.get("source_entry"))
    visible_pages = tuple(str(item) for item in (packet.get("visible_pages") or ()) if item)
    ready = bool(entry) and bool(packet.get("health_page_visible")) and bool(packet.get("future_widget_page_visible")) and bool(packet.get("not_loaded_as_runtime_display_source", True)) and not _false_flags(entry)
    return {
        "component_key": CLOSEOUT_REVIEW_SOURCE_KEY,
        "component_type": "closeout_review_catalog_source_metadata",
        "source_entry_available": bool(entry),
        "source_key": entry.get("source_key"),
        "source_type": entry.get("source_type"),
        "closeout_review_module": entry.get("closeout_review_module"),
        "closeout_review_builder": entry.get("closeout_review_builder"),
        "source_dependencies": tuple(str(item) for item in (entry.get("source_dependencies") or ()) if item),
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": bool(packet.get("health_page_visible")),
        "future_widget_page_visible": bool(packet.get("future_widget_page_visible")),
        "not_loaded_as_runtime_display_source": bool(packet.get("not_loaded_as_runtime_display_source", True)),
        "read_only_contract": bool(entry.get("read_only_contract")),
        "non_executing": bool(entry.get("non_executing", True)),
        "data_model_only": bool(entry.get("data_model_only", True)),
        "closeout_review_only": bool(entry.get("closeout_review_only", True)),
        "continuation_review_only": bool(entry.get("continuation_review_only", True)),
        "catalog_metadata_only": bool(entry.get("catalog_metadata_only", True)),
        "not_runtime_payload_loading": bool(entry.get("not_runtime_payload_loading", True)),
        "not_runtime_wiring": bool(entry.get("not_runtime_wiring", True)),
        "not_ui_rendering": bool(entry.get("not_ui_rendering", True)),
        "no_command_buttons": bool(entry.get("no_command_buttons", True)),
        "safety_violations": _false_flags(entry),
        "ready_for_closeout_review_final_status_index": ready,
    }


def _registry_visibility_component(packet: Mapping[str, Any]) -> dict[str, Any]:
    visible_pages = tuple(str(item) for item in (packet.get("visible_pages") or ()) if item)
    ready = bool(packet) and bool(packet.get("source_entry_available")) and bool(packet.get("health_page_visible")) and bool(packet.get("future_widget_page_visible")) and bool(packet.get("not_loaded_as_runtime_display_source", True)) and not _false_flags(packet)
    return {
        "component_key": FINAL_COMPONENT_KEY,
        "component_type": "closeout_review_registry_visibility_metadata",
        "visibility_packet_available": bool(packet),
        "visibility_packet_type": packet.get("visibility_packet_type"),
        "source_entry_available": bool(packet.get("source_entry_available")),
        "source_key": packet.get("source_key"),
        "source_type": packet.get("source_type"),
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
        "not_runtime_payload_loading": bool(packet.get("not_runtime_payload_loading", True)),
        "not_runtime_wiring": bool(packet.get("not_runtime_wiring", True)),
        "not_ui_rendering": bool(packet.get("not_ui_rendering", True)),
        "no_command_buttons": bool(packet.get("no_command_buttons", True)),
        "safety_violations": _false_flags(packet),
        "ready_for_closeout_review_final_status_index": ready,
    }


def build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_final_status_index_packet(
    closeout_review_registry_visibility_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    registry_visibility = _payload(closeout_review_registry_visibility_packet) or build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_registry_visibility_packet()
    components = (
        _source_component(registry_visibility),
        _registry_visibility_component(registry_visibility),
    )
    visible_pages = tuple(dict.fromkeys(page for item in components for page in item["visible_pages"]))
    final_status_index_ready = all(bool(item["ready_for_closeout_review_final_status_index"]) for item in components)
    return {
        **DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_FINAL_STATUS_INDEX_CONTRACT,
        "final_status_index_components": CLOSEOUT_REVIEW_FINAL_STATUS_INDEX_COMPONENT_KEYS,
        "components": components,
        "component_count": len(components),
        "final_component_key": FINAL_COMPONENT_KEY,
        "final_component_source_key": components[-1].get("source_key"),
        "final_component_visibility_packet_type": components[-1].get("visibility_packet_type"),
        "all_components_available": all(bool(item.get("source_entry_available") or item.get("visibility_packet_available")) for item in components),
        "all_health_page_visible": all(bool(item["health_page_visible"]) for item in components),
        "all_future_widget_page_visible": all(bool(item["future_widget_page_visible"]) for item in components),
        "all_not_loaded_as_runtime_display_source": all(bool(item["not_loaded_as_runtime_display_source"]) for item in components),
        "all_safety_flags_false": all(not tuple(item.get("safety_violations") or ()) for item in components),
        "closeout_review_final_status_index_ready": final_status_index_ready,
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": all(bool(item["health_page_visible"]) for item in components),
        "future_widget_page_visible": all(bool(item["future_widget_page_visible"]) for item in components),
        "closeout_review_contract": dict(DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CONTRACT),
        "closeout_review_registry_visibility_contract": dict(VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_REGISTRY_VISIBILITY_CONTRACT),
        "not_loaded_as_runtime_display_source": True,
        "summary_line": (
            f"{CLOSEOUT_REVIEW_FINAL_STATUS_INDEX_KEY}: components={len(components)} / "
            f"closeout_review_final_status_index_ready={_bool_token(final_status_index_ready)} / "
            f"final_component={FINAL_COMPONENT_KEY} / "
            "read_only_visibility_registry_chain_completion_closeout_review_final_status_index"
        ),
    }
