# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_top_bar_placeholder_status_polish_q29j.py
# desc: PS-Q29J guards for WarRoom v2 top-bar placeholder status polish.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.top_bar import (  # noqa: E402
    WARROOM_V2_TOP_BAR_RENDERER_VERSION,
    build_warroom_v2_top_bar_renderer_packet,
)
from btcts.apps.operator_ui.prediction_warroom.v2 import build_warroom_v2_placeholder_read_models_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
TOP_BAR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2/top_bar.py"
PLACEHOLDERS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/placeholder_read_models.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29J_WARROOM_V2_TOP_BAR_PLACEHOLDER_STATUS_POLISH_2026-07-02.md"


def _top_models() -> list[dict]:
    packet = build_warroom_v2_placeholder_read_models_packet(generated_at="2026-07-02T07:20:00Z")
    return [model for model in packet["read_models"] if model["payload"].get("zone") == "top"]


def test_q29j_top_read_models_have_status_payloads() -> None:
    models = _top_models()
    assert [model["widget_id"] for model in models] == ["current_state_mini_bar", "safety_mini_bar", "alert_summary"]
    for model in models:
        payload = model["payload"]
        assert payload["status_source"] == "placeholder_read_model"
        assert payload["state_label"] == "未接続"
        assert payload["status_badge"] == "NO_DATA"
        assert payload["status_summary"]
        assert payload["status_lines"]
        assert payload["placeholder_only"] is True
        assert payload["runtime_connected"] is False
        assert payload["push_connected"] is False


def test_q29j_top_bar_renderer_packet_is_display_only() -> None:
    packet = build_warroom_v2_top_bar_renderer_packet(_top_models())
    assert packet["renderer_version"] == WARROOM_V2_TOP_BAR_RENDERER_VERSION
    assert packet["top_bar_placeholder_status_polish"] is True
    assert packet["display_only"] is True
    assert packet["placeholder_only"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["would_send_to_broker"] is False
    assert packet["widget_ids"] == ["current_state_mini_bar", "safety_mini_bar", "alert_summary"]


def test_q29j_top_bar_files_are_small_and_side_effect_free() -> None:
    forbidden = (
        "D:" + "\\",
        "E:" + "\\",
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
        "websocket.",
        "sse.",
    )
    for path in (TOP_BAR, PLACEHOLDERS):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220
        for token in forbidden:
            assert token not in text


def test_q29j_no_route_or_legacy_warroom_change() -> None:
    app_text = APP.read_text(encoding="utf-8-sig")
    legacy_text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert '("warroom_v2", get_text(lang, "page_warroom"), warroom_v2_page)' in app_text
    assert 'LEGACY_PAGE_KEY_REDIRECTS = {' in app_text
    assert '"warroom": "warroom_v2"' in app_text
    assert "top_bar_placeholder_status" not in legacy_text
    assert "prediction_warroom.v2.push_widgets" in legacy_text
    assert "ensure_warroom_push_widget_live_observation_runtime" in legacy_text
    assert "apply_warroom_push_widget_rt_live_receiver_bridge_to_session_state" in legacy_text
    assert "warroom_v2_page" not in legacy_text
    assert "build_warroom_v2_shell_preview_packet" not in legacy_text
    assert "classify_market_regime_feature_bundle(" not in legacy_text
    assert "send_to_broker(" not in legacy_text
    assert "autotrade_trigger_allowed = True" not in legacy_text


def test_q29j_doc_records_top_bar_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "top_widgets=現在状態,安全境界,アラート" in text
    assert "status_source=placeholder_read_model" in text
    assert "runtime_connected=false" in text
    assert "not_connecting_dhot=true" in text
    assert "not_changing_legacy_warroom=true" in text
