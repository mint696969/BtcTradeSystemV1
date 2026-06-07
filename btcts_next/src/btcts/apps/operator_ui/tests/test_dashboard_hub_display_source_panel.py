# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_panel.py
# desc: Verify dashboard hub display source panel helper stays component-only and app.py-free.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

PANEL_SOURCE = (Path(__file__).resolve().parents[4] / "btcts" / "apps" / "operator_ui" / "components" / "dashboard_hub_source_panel.py").read_text(encoding="utf-8")

from btcts.apps.operator_ui.components.dashboard_hub_source_panel import (  # noqa: E402
    DASHBOARD_HUB_SOURCE_PANEL_CONTRACT,
    _rows_for_table,
    _status_tone,
)


def main() -> int:
    assert DASHBOARD_HUB_SOURCE_PANEL_CONTRACT["panel_type"] == "dashboard_hub_display_source_panel"
    assert DASHBOARD_HUB_SOURCE_PANEL_CONTRACT["streamlit_rendering"] is True
    assert DASHBOARD_HUB_SOURCE_PANEL_CONTRACT["component_only_rendering"] is True
    assert DASHBOARD_HUB_SOURCE_PANEL_CONTRACT["not_app_py_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_PANEL_CONTRACT["not_page_routing"] is True
    assert DASHBOARD_HUB_SOURCE_PANEL_CONTRACT["not_runtime_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_PANEL_CONTRACT["not_broker_or_order_wiring"] is True
    assert DASHBOARD_HUB_SOURCE_PANEL_CONTRACT["read_only_contract"] is True

    assert _status_tone("ready") == "primary"
    assert _status_tone("blocked") == "danger"
    assert _status_tone("unknown") == "danger"

    hot_cold_rows = _rows_for_table(
        (
            {"label": "hot_cold_status", "value": "catalog_ready_payload_not_opened"},
            {"label": "hot_cold_payload_loader", "value": "not_opened"},
        )
    )
    assert hot_cold_rows == [
        {"label": "hot_cold_status", "value": "catalog_ready_payload_not_opened"},
        {"label": "hot_cold_payload_loader", "value": "not_opened"},
    ]

    rows = _rows_for_table(
        (
            {"label": "status", "value": "ready"},
            {"label": "sources", "value": 5},
            {"label": None, "value": None},
            "skip-me",
        )
    )
    assert rows == [
        {"label": "status", "value": "ready"},
        {"label": "sources", "value": "5"},
        {"label": "", "value": ""},
    ]

    source = PANEL_SOURCE
    assert "hot_cold_row_count" in source
    assert "hot_cold_status_label" in source
    assert "hot_cold_metadata_detail_status" in source
    assert "hot_cold_rows_present" in source
    assert "hot_cold_status:" in source

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
