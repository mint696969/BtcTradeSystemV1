# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary_registry_visibility.py
# desc: Read-only registry visibility packet for the decision policy gate closeout review chain closeout summary catalog entry. Catalog/registry metadata only; no UI implementation, commands, runtime payload loading, chain-closeout-summary/final/closeout/chain/status/checkpoint builder execution, writes, mode apply, grants, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.operator_display_source_catalog import load_operator_dashboard_display_source_catalog
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary import (
    DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_CONTRACT,
)
from btcts.apps.operator_ui.hub.display_source_registry import (
    display_source_keys_for_page,
    load_dashboard_hub_display_source_registry,
)

VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_SOURCE_KEY = "decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary"
VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_SOURCE_TYPE = "decision_policy_gate_read_only_visibility_registry_chain_completion_closeout_review_chain_closeout_summary_packet"

VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_REGISTRY_VISIBILITY_CONTRACT = {
    "visibility_packet_type": "decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary_registry_visibility",
    "source_key": VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_SOURCE_KEY,
    "source_type": VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_SOURCE_TYPE,
    "dashboard_role": "operator_ui_visibility_registry_chain_completion_closeout_review_chain_closeout_summary_registry_visibility",
    "read_only_contract": True,
    "non_executing": True,
    "data_model_only": True,
    "catalog_metadata_only": True,
    "registry_visibility_only": True,
    "chain_closeout_summary_visibility_only": True,
    "closeout_review_chain_closeout_summary_visibility_only": True,
    "registry_chain_completion_closeout_review_chain_closeout_summary_visibility_only": True,
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


def _source_entry(catalog: Mapping[str, Any], source_key: str) -> dict[str, Any]:
    for item in catalog.get("sources") or ():
        if isinstance(item, Mapping) and item.get("source_key") == source_key:
            return dict(item)
    return {}


def _page_visibility(registry: Mapping[str, Any], source_key: str) -> tuple[dict[str, Any], ...]:
    out: list[dict[str, Any]] = []
    for entry in registry.get("page_entries") or ():
        if not isinstance(entry, Mapping):
            continue
        keys = tuple(str(item) for item in (entry.get("source_keys") or ()) if item)
        out.append(
            {
                "page_key": entry.get("page_key"),
                "consumer_scope": entry.get("consumer_scope"),
                "visible": source_key in keys,
                "source_count": int(entry.get("source_count") or 0),
                "read_only_contract": True,
                "data_model_only": True,
                "registry_visibility_only": True,
                "not_runtime_payload_loading": True,
                "not_runtime_wiring": True,
                "not_ui_rendering": True,
                "no_command_buttons": True,
            }
        )
    return tuple(out)


def visible_pages_for_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary(
    registry: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    payload = registry or load_dashboard_hub_display_source_registry()
    return tuple(
        str(item.get("page_key"))
        for item in _page_visibility(payload, VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_SOURCE_KEY)
        if item.get("visible") and item.get("page_key")
    )


def build_decision_policy_gate_visibility_registry_chain_completion_closeout_review_chain_closeout_summary_registry_visibility_packet(
    catalog: Mapping[str, Any] | None = None,
    registry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    catalog_payload = catalog or load_operator_dashboard_display_source_catalog()
    registry_payload = registry or load_dashboard_hub_display_source_registry()
    source_entry = _source_entry(catalog_payload, VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_SOURCE_KEY)
    page_visibility = _page_visibility(registry_payload, VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_SOURCE_KEY)
    visible_pages = tuple(str(item.get("page_key")) for item in page_visibility if item.get("visible") and item.get("page_key"))
    page_key_map = {
        "health": display_source_keys_for_page("health", dict(registry_payload)),
        "logs": display_source_keys_for_page("logs", dict(registry_payload)),
    }
    return {
        **VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_REGISTRY_VISIBILITY_CONTRACT,
        "catalog_available": bool(catalog_payload),
        "registry_available": bool(registry_payload),
        "source_entry_available": bool(source_entry),
        "source_entry": source_entry,
        "chain_closeout_summary_module": source_entry.get("chain_closeout_summary_module"),
        "chain_closeout_summary_builder": source_entry.get("chain_closeout_summary_builder"),
        "source_dependencies": tuple(str(item) for item in (source_entry.get("source_dependencies") or ()) if item),
        "chain_closeout_summary_contract": dict(DECISION_POLICY_GATE_VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_CONTRACT),
        "page_visibility": page_visibility,
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_SOURCE_KEY in page_key_map["health"],
        "future_widget_page_visible": VISIBILITY_REGISTRY_CHAIN_COMPLETION_CLOSEOUT_REVIEW_CHAIN_CLOSEOUT_SUMMARY_SOURCE_KEY in page_key_map["logs"],
        "display_source_keys_for_page": page_key_map,
        "not_loaded_as_runtime_display_source": True,
    }
