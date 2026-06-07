# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_operator_display_source_catalog.py
# desc: Verify operator dashboard display source catalog is hub-friendly, read-only, and layout-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.operator_display_source_catalog import (  # noqa: E402
    OPERATOR_DASHBOARD_HUB_CONTRACT,
    load_operator_dashboard_display_source_catalog,
    select_display_sources_for_consumer,
)


def main() -> int:
    assert OPERATOR_DASHBOARD_HUB_CONTRACT["dashboard_role"] == "hub"
    assert OPERATOR_DASHBOARD_HUB_CONTRACT["current_tab_layout_is_temporary"] is True
    assert OPERATOR_DASHBOARD_HUB_CONTRACT["widget_reusable"] is True
    assert OPERATOR_DASHBOARD_HUB_CONTRACT["layout_decision_free"] is True
    assert OPERATOR_DASHBOARD_HUB_CONTRACT["read_only_contract"] is True
    assert OPERATOR_DASHBOARD_HUB_CONTRACT["not_runtime_wiring"] is True
    assert OPERATOR_DASHBOARD_HUB_CONTRACT["not_ui_rendering"] is True

    catalog = load_operator_dashboard_display_source_catalog()
    assert catalog["catalog_type"] == "operator_dashboard_display_source_catalog"
    assert catalog["dashboard_role"] == "hub"
    assert catalog["source_count"] == len(catalog["sources"])
    assert catalog["source_keys"] == tuple(item["source_key"] for item in catalog["sources"])
    assert "review_hint_display" in catalog["source_keys"]
    assert "hot_cold_duplicate_safe_dataset_view_model" in catalog["source_keys"]
    assert "source_catalog" not in catalog["source_keys"]
    origins = {item["source_origin"] for item in catalog["sources"]}
    assert "ai_operator_display_sources" in origins
    assert "hot_cold_display_sources" in origins
    assert all(
        item["source_origin"] in {"ai_operator_display_sources", "hot_cold_display_sources"}
        for item in catalog["sources"]
    )
    assert all(item["read_only_contract"] is True for item in catalog["sources"])
    assert all(item["widget_reusable"] is True for item in catalog["sources"])
    assert all(item["layout_decision_free"] is True for item in catalog["sources"])
    assert all(item["not_runtime_wiring"] is True for item in catalog["sources"])
    assert all(item["not_ui_rendering"] is True for item in catalog["sources"])

    ai_sources = select_display_sources_for_consumer("ai_tab", catalog)
    assert ai_sources
    assert {item["source_key"] for item in ai_sources} >= {
        "prediction_widget",
        "tactic_context",
        "review_hint_context",
        "review_hint_display",
    }

    health_sources = select_display_sources_for_consumer("health_tab", catalog)
    assert any(item["source_key"] == "hot_cold_duplicate_safe_dataset_view_model" for item in health_sources)

    future_sources = select_display_sources_for_consumer("some_future_tab", catalog)
    assert future_sources
    assert all("future_widget" in item["consumer_scope"] for item in future_sources)

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
