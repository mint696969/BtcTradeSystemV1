# path: ./btcts_next/src/btcts/apps/operator_ui/hub/decision_policy_gate_visibility_chain_summary.py
# desc: Pure data read-only visibility chain summary for decision policy gate Operator/UI metadata. No UI implementation, commands, runtime payload loading, writes, mode apply, grants, or broker behavior.

from __future__ import annotations

from typing import Any, Mapping

from btcts.apps.operator_ui.components.ai_operator_display_sources import (
    load_operator_display_source_catalog,
)
from btcts.apps.operator_ui.components.autotrade_decision_ledger_policy_gate_display import (
    AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_dashboard_status_index import (
    DECISION_POLICY_GATE_DASHBOARD_STATUS_INDEX_CONTRACT,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_dashboard_status_index_registry_visibility import (
    build_decision_policy_gate_dashboard_status_index_registry_visibility_packet,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_static_section_model import (
    DECISION_POLICY_GATE_STATIC_SECTION_MODEL_CONTRACT,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_static_section_registry_visibility import (
    build_decision_policy_gate_static_section_registry_visibility_packet,
)
from btcts.apps.operator_ui.hub.decision_policy_gate_visibility import (
    build_decision_policy_gate_dashboard_registry_visibility_packet,
)

SUMMARY_KEY = "decision_policy_gate_read_only_visibility_chain_summary"
DISPLAY_SOURCE_KEY = "autotrade_decision_ledger_policy_gate_display"
STATIC_SECTION_SOURCE_KEY = "decision_policy_gate_static_section_model"
DASHBOARD_STATUS_INDEX_SOURCE_KEY = "decision_policy_gate_dashboard_status_index"

DECISION_POLICY_GATE_VISIBILITY_CHAIN_SUMMARY_CONTRACT = {
    "summary_key": SUMMARY_KEY,
    "summary_type": "decision_policy_gate_read_only_visibility_chain_summary_packet",
    "dashboard_role": "operator_ui_read_only_visibility_chain_summary",
    "read_only_contract": True,
    "non_executing": True,
    "data_model_only": True,
    "summary_only": True,
    "catalog_metadata_only": True,
    "visibility_summary_only": True,
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


def _entry(catalog: tuple[dict, ...], source_key: str) -> dict[str, Any]:
    for item in catalog:
        if isinstance(item, Mapping) and item.get("source_key") == source_key:
            return dict(item)
    return {}


def _bool_token(value: Any) -> str:
    return "true" if bool(value) else "false"


def _summary_item(component_key: str, *, catalog_entry: Mapping[str, Any], visibility_packet: Mapping[str, Any]) -> dict[str, Any]:
    visible_pages = tuple(str(item) for item in (visibility_packet.get("visible_pages") or ()) if item)
    return {
        "component_key": component_key,
        "catalog_entry_available": bool(catalog_entry),
        "visibility_packet_available": bool(visibility_packet),
        "source_entry_available": bool(visibility_packet.get("source_entry_available")),
        "source_key": catalog_entry.get("source_key") or visibility_packet.get("source_key"),
        "source_type": catalog_entry.get("source_type") or visibility_packet.get("source_type"),
        "visible_pages": visible_pages,
        "visible_page_count": len(visible_pages),
        "health_page_visible": bool(visibility_packet.get("health_page_visible")),
        "future_widget_page_visible": bool(visibility_packet.get("future_widget_page_visible")),
        "read_only_contract": True,
        "non_executing": True,
        "data_model_only": bool(catalog_entry.get("data_model_only", True)),
        "not_runtime_payload_loading": True,
        "not_runtime_wiring": True,
        "not_ui_rendering": True,
        "no_command_buttons": True,
    }


def build_decision_policy_gate_visibility_chain_summary_packet(
    catalog: tuple[dict, ...] | None = None,
    display_registry_visibility_packet: Mapping[str, Any] | None = None,
    static_section_registry_visibility_packet: Mapping[str, Any] | None = None,
    dashboard_status_index_registry_visibility_packet: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    catalog_payload = catalog or load_operator_display_source_catalog()
    display_visibility = dict(display_registry_visibility_packet) if isinstance(display_registry_visibility_packet, Mapping) else build_decision_policy_gate_dashboard_registry_visibility_packet()
    static_visibility = dict(static_section_registry_visibility_packet) if isinstance(static_section_registry_visibility_packet, Mapping) else build_decision_policy_gate_static_section_registry_visibility_packet()
    status_index_visibility = dict(dashboard_status_index_registry_visibility_packet) if isinstance(dashboard_status_index_registry_visibility_packet, Mapping) else build_decision_policy_gate_dashboard_status_index_registry_visibility_packet()

    display_entry = _entry(catalog_payload, DISPLAY_SOURCE_KEY)
    static_entry = _entry(catalog_payload, STATIC_SECTION_SOURCE_KEY)
    status_index_entry = _entry(catalog_payload, DASHBOARD_STATUS_INDEX_SOURCE_KEY)
    chain = (
        _summary_item("decision_policy_gate_display_registry_visibility", catalog_entry=display_entry, visibility_packet=display_visibility),
        _summary_item("decision_policy_gate_static_section_registry_visibility", catalog_entry=static_entry, visibility_packet=static_visibility),
        _summary_item("decision_policy_gate_dashboard_status_index_registry_visibility", catalog_entry=status_index_entry, visibility_packet=status_index_visibility),
    )
    all_visible_pages = tuple(dict.fromkeys(page for item in chain for page in item["visible_pages"]))
    chain_ready = all(item["catalog_entry_available"] and item["source_entry_available"] for item in chain)
    return {
        **DECISION_POLICY_GATE_VISIBILITY_CHAIN_SUMMARY_CONTRACT,
        "catalog_available": bool(catalog_payload),
        "chain": chain,
        "chain_component_count": len(chain),
        "chain_ready_for_read_only_visibility": bool(chain_ready),
        "visible_pages": all_visible_pages,
        "visible_page_count": len(all_visible_pages),
        "health_page_visible": all(bool(item["health_page_visible"]) for item in chain),
        "future_widget_page_visible": all(bool(item["future_widget_page_visible"]) for item in chain),
        "display_packet_contract": dict(AUTOTRADE_DECISION_LEDGER_POLICY_GATE_DISPLAY_CONTRACT),
        "static_section_model_contract": dict(DECISION_POLICY_GATE_STATIC_SECTION_MODEL_CONTRACT),
        "dashboard_status_index_contract": dict(DECISION_POLICY_GATE_DASHBOARD_STATUS_INDEX_CONTRACT),
        "not_loaded_as_runtime_display_source": True,
        "summary_line": (
            f"{SUMMARY_KEY}: components={len(chain)} / "
            f"chain_ready={_bool_token(chain_ready)} / "
            f"health_visible={_bool_token(all(bool(item['health_page_visible']) for item in chain))} / "
            f"future_widget_visible={_bool_token(all(bool(item['future_widget_page_visible']) for item in chain))} / "
            "read_only_visibility_summary"
        ),
    }
