# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_quick_status_panel_extraction_q26r.py
# desc: PS-Q26R tests for quick-status panel extraction with warroom_page compatibility wrappers. Display-only; no runtime writes or execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels import warroom_latest_prediction_quick_status_panel as panel  # noqa: E402
from btcts.apps.operator_ui.views import warroom_page  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_latest_prediction_quick_status_panel.py"


def test_q26r_quick_status_panel_exports_safe_packet_and_keeps_legacy_wrapper() -> None:
    q18aj = {
        "auto_refresh_enabled": True,
        "fragment_refresh_enabled": True,
        "broad_page_reload_disabled": True,
        "refresh_heartbeat_utc": "2026-07-01T00:00:00Z",
    }
    q18ak = {
        "freshness_state": "unknown",
        "safe_fallback_reason_codes": ["source_generated_at_missing"],
        "observed_now_utc": "2026-07-01T00:00:00Z",
        "source_age_sec": None,
    }
    from_panel = panel._prediction_warroom_latest_prediction_observation_cleanup_summary_packet(
        q18aj_packet=q18aj,
        q18ak_packet=q18ak,
    )
    from_page = warroom_page._prediction_warroom_latest_prediction_observation_cleanup_summary_packet(
        q18aj_packet=q18aj,
        q18ak_packet=q18ak,
    )
    assert from_page == from_panel
    assert from_panel["ok"] is True
    assert from_panel["observation_cleanup_state"] == "operator_quick_status_visible_display_only"
    assert from_panel["real_rendering_enabled"] is False
    assert from_panel["component_runtime_binding_allowed"] is False
    assert from_panel["runtime_artifact_write_allowed"] is False
    assert from_panel["status_artifact_write_allowed"] is False
    assert from_panel["ledger_append_allowed"] is False
    assert from_panel["autotrade_trigger_allowed"] is False
    assert from_panel["broker_private_api_allowed"] is False
    assert from_panel["would_send_to_broker"] is False


def test_q26r_warroom_page_is_thin_wrapper_and_panel_holds_implementation() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert "from btcts.apps.operator_ui.prediction_warroom.panels import warroom_latest_prediction_quick_status_panel as quick_status_panel" in page_text
    assert "PS-Q26R compatibility wrappers" in page_text
    assert "q18aj = q18aj_packet if isinstance" not in page_text
    assert "q18aj = q18aj_packet if isinstance" in panel_text
    assert "WARROOM_LATEST_PREDICTION_QUICK_STATUS_PANEL_VERSION" in panel_text
    assert "PS_Q18AU_OBSERVATION_QUICK_STATUS" in page_text
    assert "Prediction WarRoom latest summary observation quick status" in page_text
    assert "def _prediction_warroom_latest_prediction_observation_cleanup_summary_packet" in page_text
    assert "def _render_prediction_warroom_latest_prediction_observation_cleanup_summary_section" in page_text
    assert "quick_status_panel._render_prediction_warroom_latest_prediction_observation_cleanup_summary_section" in page_text
