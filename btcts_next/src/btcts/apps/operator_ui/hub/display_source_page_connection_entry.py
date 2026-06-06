# path: ./btcts_next/src/btcts/apps/operator_ui/hub/display_source_page_connection_entry.py
# desc: Entry criteria for connecting dashboard hub display source panel to an existing page. No page/app routing mutation.

from __future__ import annotations

from btcts.apps.operator_ui.hub.display_source_registry import (
    DASHBOARD_HUB_PAGE_KEYS,
    PAGE_TO_CONSUMER_SCOPE,
)

DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT = {
    "entry_type": "dashboard_hub_display_source_page_connection_entry",
    "dashboard_role": "hub",
    "read_only_contract": True,
    "component_connection_planning": True,
    "not_app_py_wiring": True,
    "not_page_routing_mutation": True,
    "not_layout_decision": True,
    "not_runtime_wiring": True,
    "not_broker_or_order_wiring": True,
}

PREFERRED_INITIAL_PAGE = "health"
CONNECTABLE_PAGE_KEYS = ("collector", "health", "research")
PAGE_CONNECTION_REASONS = {
    "collector": "existing_live_dashboard_page_with_summary_source",
    "health": "existing_diagnostics_page_with_read_only_health_context",
    "research": "existing_future_widget_page_with_review_hint_context",
}


def dashboard_hub_display_source_page_connection_entry(
    *,
    preferred_page: str = PREFERRED_INITIAL_PAGE,
) -> dict:
    page_keys = tuple(str(key) for key in DASHBOARD_HUB_PAGE_KEYS)
    connectable = tuple(key for key in CONNECTABLE_PAGE_KEYS if key in page_keys)
    selected_page = preferred_page if preferred_page in connectable else (connectable[0] if connectable else "none")
    blocked_reasons: list[str] = []
    if not connectable:
        blocked_reasons.append("no_connectable_page_key")
    if selected_page == "none":
        blocked_reasons.append("selected_page_unavailable")
    page_connection_ready = not blocked_reasons
    return {
        **DASHBOARD_HUB_SOURCE_PAGE_CONNECTION_ENTRY_CONTRACT,
        "page_connection_ready": page_connection_ready,
        "selected_page_key": selected_page,
        "preferred_page_key": preferred_page,
        "connectable_page_keys": connectable,
        "all_dashboard_page_keys": page_keys,
        "consumer_scope": PAGE_TO_CONSUMER_SCOPE.get(selected_page, "none"),
        "connection_reason": PAGE_CONNECTION_REASONS.get(selected_page, "none"),
        "blocked_reasons": tuple(blocked_reasons),
        "allowed_next_surface": "existing_view_component_call" if page_connection_ready else "none",
        "app_py_wiring_allowed": False,
        "page_routing_mutation_allowed": False,
        "layout_decision_allowed": False,
        "runtime_wiring_allowed": False,
        "next_required_step": (
            "create_guarded_existing_view_component_insertion_slice" if page_connection_ready else "fix_page_connection_entry"
        ),
        "compact_line": (
            "dashboard_hub_source_page_connection="
            f"ready:{page_connection_ready};selected:{selected_page};"
            f"blocked:{','.join(blocked_reasons) or 'none'}"
        ),
    }
