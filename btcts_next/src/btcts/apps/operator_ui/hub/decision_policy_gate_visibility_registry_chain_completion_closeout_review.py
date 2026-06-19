# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_closeout_review.py
# desc: Read-only closeout/continuation review packet for the decision policy gate registry visibility chain completion layers. Catalog/registry metadata only; no UI implementation, commands, runtime payload loading, final/chain/status/checkpoint builder execution, writes, mode apply, grants, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.ai_operator_display_sources import load_operator_display_source_catalog
from btcts.apps.operator_ui.components.operator_display_source_catalog import load_operator_dashboard_display_source_catalog
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_final_status_index import (
    DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_CONTRACT,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_final_status_index_registry_visibility import (
    VISIBILITY_REGISTRY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_REGISTRY_VISIBILITY_CONTRACT,
)
from btcts.apps.operator_ui.hub.display_source_registry import (
    display_source_keys_for_page,
    load_dashboard_hub_display_source_registry,
)

CLOSEOUT_REVIEW_KEY = "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review"
CLOSEOUT_REVIEW_TYPE = "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_packet"

CLOSEOUT_CATALOG_SOURCE_KEYS = (
    "autotrade_decision_ledger_policy_gate_display",
    "decision_policy_gate_static_section_model",
    "decision_policy_gate_dashboard_status_index",
    "decision_policy_gate_visibility_chain_summary",
    "decision_policy_gate_visibility_completion_checkpoint",
    "decision_policy_gate_visibility_completion_status_index",
    "decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion",
    "decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion_final_status_index",
)

CLOSEOUT_FINAL_LAYERS = (
    "decision_policy_gate_visibility_completion_status_index",
    "decision_policy_gate_visibility_completion_status_index_registry_visibility",
    "decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion",
    "decision_policy_gate_visibility_registry_chain_completion_registry_visibility",
    "decision_policy_gate_read_only_visibility_completion_status_index_registry_visibility_chain_completion_final_status_index",
    "decision_policy_gate_visibility_completion_status_index_registry_visibility_chain_completion_final_status_index",
    "decision_policy_gate_visibility_registry_chain_completion_final_status_index_registry_visibility",
)

DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CONTRACT = {
    "closeout_review_key": CLOSEOUT_REVIEW_KEY,
    "closeout_review_type": CLOSEOUT_REVIEW_TYPE,
    "dashboard_role": "operator_ui_read_only_visibility_registry_chain_completion_closeout_review",
    "read_only_contract": True,
    "non_executing": True,
    "data_model_only": True,
    "closeout_review_only": True,
    "continuation_review_only": True,
    "catalog_metadata_only": True,
    "registry_visibility_review_only": True,
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


def _entry_by_key(entries: tuple[dict[str, Any], ...], source_key: str) -> dict[str, Any]:
    for item in entries:
        if item.get("source_key") == source_key:
            return dict(item)
    return {}


def _source_review(source_key: str, entries: tuple[dict[str, Any], ...], health_keys: tuple[str, ...], logs_keys: tuple[str, ...]) -> dict[str, Any]:
    entry = _entry_by_key(entries, source_key)
    return {
        "source_key": source_key,
        "source_entry_available": bool(entry),
        "source_type": entry.get("source_type"),
        "consumer_scope": tuple(str(item) for item in (entry.get("consumer_scope") or ()) if item),
        "source_dependencies": tuple(str(item) for item in (entry.get("source_dependencies") or ()) if item),
        "health_page_visible": source_key in health_keys,
        "future_widget_page_visible": source_key in logs_keys,
        "read_only_contract": bool(entry.get("read_only_contract")),
        "data_model_only": bool(entry.get("data_model_only", True)),
        "not_runtime_payload_loading": bool(entry.get("not_runtime_payload_loading", True)),
        "not_runtime_wiring": bool(entry.get("not_runtime_wiring", True)),
        "not_ui_rendering": bool(entry.get("not_ui_rendering", True)),
        "no_command_buttons": bool(entry.get("no_command_buttons", True)),
        "command_buttons_allowed": bool(entry.get("command_buttons_allowed", False)),
        "forms_or_toggles_allowed": bool(entry.get("forms_or_toggles_allowed", False)),
        "runtime_wiring_allowed": bool(entry.get("runtime_wiring_allowed", False)),
        "ui_rendering_implementation_allowed": bool(entry.get("ui_rendering_implementation_allowed", False)),
        "decision_append_allowed": bool(entry.get("decision_append_allowed", False)),
        "live_shadow_behavior_change_allowed": bool(entry.get("live_shadow_behavior_change_allowed", False)),
        "persist_true_allowed": bool(entry.get("persist_true_allowed", False)),
        "would_append_shadow_decision": bool(entry.get("would_append_shadow_decision", False)),
        "would_apply_mode": bool(entry.get("would_apply_mode", False)),
        "would_execute_prearmed_grant": bool(entry.get("would_execute_prearmed_grant", False)),
        "would_write_runtime_artifact": bool(entry.get("would_write_runtime_artifact", False)),
        "would_write_preview_status_artifact": bool(entry.get("would_write_preview_status_artifact", False)),
        "would_send_to_broker": bool(entry.get("would_send_to_broker", False)),
    }


def build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_packet(
    ai_catalog: tuple[dict[str, Any], ...] | None = None,
    dashboard_catalog: Mapping[str, Any] | None = None,
    registry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    ai_entries = ai_catalog or load_operator_display_source_catalog()
    dashboard_payload = dashboard_catalog or load_operator_dashboard_display_source_catalog()
    dashboard_entries = tuple(dict(item) for item in (dashboard_payload.get("sources") or ()) if isinstance(item, Mapping))
    registry_payload = registry or load_dashboard_hub_display_source_registry()
    health_keys = display_source_keys_for_page("health", dict(registry_payload))
    logs_keys = display_source_keys_for_page("logs", dict(registry_payload))
    catalog_reviews = tuple(_source_review(source_key, ai_entries, health_keys, logs_keys) for source_key in CLOSEOUT_CATALOG_SOURCE_KEYS)
    dashboard_reviews = tuple(_source_review(source_key, dashboard_entries, health_keys, logs_keys) for source_key in CLOSEOUT_CATALOG_SOURCE_KEYS)
    safety_false_fields = (
        "command_buttons_allowed",
        "forms_or_toggles_allowed",
        "runtime_wiring_allowed",
        "ui_rendering_implementation_allowed",
        "decision_append_allowed",
        "live_shadow_behavior_change_allowed",
        "persist_true_allowed",
        "would_append_shadow_decision",
        "would_apply_mode",
        "would_execute_prearmed_grant",
        "would_write_runtime_artifact",
        "would_write_preview_status_artifact",
        "would_send_to_broker",
    )
    all_catalog_entries_available = all(item["source_entry_available"] for item in catalog_reviews)
    all_dashboard_entries_available = all(item["source_entry_available"] for item in dashboard_reviews)
    all_health_visible = all(item["health_page_visible"] for item in catalog_reviews)
    all_future_visible = all(item["future_widget_page_visible"] for item in catalog_reviews)
    all_read_only = all(item["read_only_contract"] for item in catalog_reviews)
    all_not_runtime = all(item["not_runtime_payload_loading"] and item["not_runtime_wiring"] and item["not_ui_rendering"] for item in catalog_reviews)
    all_safety_flags_false = all(not bool(item[field]) for item in catalog_reviews for field in safety_false_fields)
    closeout_complete = all((all_catalog_entries_available, all_dashboard_entries_available, all_health_visible, all_future_visible, all_read_only, all_not_runtime, all_safety_flags_false))
    return {
        **DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CONTRACT,
        "catalog_source_keys": CLOSEOUT_CATALOG_SOURCE_KEYS,
        "final_layer_markers": CLOSEOUT_FINAL_LAYERS,
        "catalog_reviews": catalog_reviews,
        "dashboard_catalog_reviews": dashboard_reviews,
        "catalog_source_count": len(CLOSEOUT_CATALOG_SOURCE_KEYS),
        "health_source_keys": health_keys,
        "future_widget_source_keys": logs_keys,
        "all_catalog_entries_available": all_catalog_entries_available,
        "all_dashboard_entries_available": all_dashboard_entries_available,
        "all_health_page_visible": all_health_visible,
        "all_future_widget_page_visible": all_future_visible,
        "all_read_only_contracts": all_read_only,
        "all_not_runtime_or_ui": all_not_runtime,
        "all_safety_flags_false": all_safety_flags_false,
        "closeout_review_completed": closeout_complete,
        "final_status_index_contract": dict(DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_CONTRACT),
        "final_status_index_registry_visibility_contract": dict(VISIBILITY_REGISTRY_CHAIN_COMPLETION_FINAL_STATUS_INDEX_REGISTRY_VISIBILITY_CONTRACT),
        "not_loaded_as_runtime_display_source": True,
        "next_safe_slice": "choose_next_from_room_truth_after_read_only_closeout_review",
        "summary_line": (
            f"{CLOSEOUT_REVIEW_KEY}: catalog_sources={len(CLOSEOUT_CATALOG_SOURCE_KEYS)} / "
            f"closeout_review_completed={'true' if closeout_complete else 'false'} / "
            "read_only_visibility_registry_chain_completion_closeout_review"
        ),
    }
