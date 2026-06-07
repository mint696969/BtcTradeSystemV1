# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_dashboard_hub_display_source_health_page_insertion.py
# desc: Verify dashboard hub source panel is inserted into Health page only, without app.py/sidebar/runtime wiring.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
_REPO_ROOT = Path(__file__).resolve().parents[6]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.components.slot_definitions import (  # noqa: E402
    health_widget_ids,
    health_widget_slot,
    health_widget_zone_ids,
)
from btcts.apps.operator_ui.hub.display_source_page_connection_entry import (  # noqa: E402
    dashboard_hub_display_source_page_connection_entry,
)


def main() -> int:
    health_page = _REPO_ROOT / "btcts_next" / "src" / "btcts" / "apps" / "operator_ui" / "views" / "health_page.py"
    app_py = _REPO_ROOT / "btcts_next" / "src" / "btcts" / "apps" / "operator_ui" / "app.py"

    health_text = health_page.read_text(encoding="utf-8")
    app_text = app_py.read_text(encoding="utf-8")

    entry = dashboard_hub_display_source_page_connection_entry()
    assert entry["page_connection_ready"] is True
    assert entry["selected_page_key"] == "health"
    assert entry["allowed_next_surface"] == "existing_view_component_call"

    assert "render_dashboard_hub_display_source_panel" in health_text
    assert "health_widget_slot(\"dashboard_hub_source_panel\")" in health_text
    assert "def _render_dashboard_hub_source_panel_section() -> None:" in health_text
    assert health_text.count("render_dashboard_hub_display_source_panel()") == 1
    assert "dashboard_hub_source_panel" not in app_text
    assert "render_dashboard_hub_display_source_panel" not in app_text

    assert "dashboard_hub_source_panel" in health_widget_ids()
    assert "detail" in health_widget_zone_ids()
    slot = health_widget_slot("dashboard_hub_source_panel")
    assert slot["page_id"] == "health"
    assert slot["zone_id"] == "detail"
    assert slot["widget_id"] == "dashboard_hub_source_panel"
    assert slot["refresh_mode"] == "poll_normal"
    assert slot["priority"] == 118
    assert slot["tone"] == "neutral"

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
