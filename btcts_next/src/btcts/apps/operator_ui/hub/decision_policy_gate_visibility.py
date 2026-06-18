# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility.py
# desc: Read-only dashboard registry visibility packet for the decision ledger policy gate display source. No UI rendering, commands, runtime wiring, decision append, mode apply, grants, writes, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.hub.display_source_registry import (
    display_source_keys_for_page,
    load_dashboard_hub_display_source_registry,
)

DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY = "autotrade_decision_ledger_policy_gate_display"
DECISION_POLICY_GATE_DISPLAY_SOURCE_TYPE = "autotrade_decision_ledger_policy_gate_display_packet"

DECISION_POLICY_GATE_REGISTRY_VISIBILITY_CONTRACT = {
    "visibility_packet_type": "decision_policy_gate_dashboard_registry_visibility",
    "source_key": DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY,
    "source_type": DECISION_POLICY_GATE_DISPLAY_SOURCE_TYPE,
    "dashboard_role": "operator_ui_dashboard_registry_visibility",
    "read_only_contract": True,
    "non_executing": True,
    "widget_reusable": True,
    "layout_decision_free": True,
    "not_runtime_wiring": True,
    "not_ui_rendering": True,
    "no_command_buttons": True,
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


def _source_entry(registry: Mapping[str, Any], source_key: str) -> dict[str, Any]:
    catalog = registry.get("source_catalog") or {}
    sources = catalog.get("sources") or () if isinstance(catalog, Mapping) else ()
    for item in sources:
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
                "not_runtime_wiring": True,
                "not_ui_rendering": True,
                "no_command_buttons": True,
            }
        )
    return tuple(out)


def visible_pages_for_decision_policy_gate(registry: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    payload = registry or load_dashboard_hub_display_source_registry()
    return tuple(
        str(item.get("page_key"))
        for item in _page_visibility(payload, DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY)
        if item.get("visible") and item.get("page_key")
    )


def build_decision_policy_gate_dashboard_registry_visibility_packet(
    registry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = registry or load_dashboard_hub_display_source_registry()
    source_entry = _source_entry(payload, DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY)
    page_visibility = _page_visibility(payload, DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY)
    visible_pages = tuple(str(item.get("page_key")) for item in page_visibility if item.get("visible") and item.get("page_key"))
    page_key_map = {
        "health": display_source_keys_for_page("health", dict(payload)),
        "logs": display_source_keys_for_page("logs", dict(payload)),
    }
    return {
        **DECISION_POLICY_GATE_REGISTRY_VISIBILITY_CONTRACT,
        "registry_available": bool(payload),
        "source_entry_available": bool(source_entry),
        "source_entry": source_entry,
        "page_visibility": page_visibility,
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY in page_key_map["health"],
        "future_widget_page_visible": DECISION_POLICY_GATE_DISPLAY_SOURCE_KEY in page_key_map["logs"],
        "display_source_keys_for_page": page_key_map,
    }
