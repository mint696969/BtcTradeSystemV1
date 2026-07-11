# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_q18aj_q18ak_legacy_panel_japanese_localization_q26g.py
# desc: PS-Q26G tests for Q18AJ/Q18AK legacy panel visible Japanese localization. Display-only; legacy searchable tokens are preserved.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (  # noqa: E402
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_JAPANESE_LOCALIZATION_VERSION,
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
    build_latest_prediction_summary_widget_q18aj_japanese_localization_packet,
    latest_prediction_summary_widget_q18aj_searchable_plain_text,
    latest_prediction_summary_widget_q18aj_visible_display_rows,
    latest_prediction_summary_widget_q18aj_visible_plain_text,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (  # noqa: E402
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_JAPANESE_LOCALIZATION_VERSION,
    build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet,
    build_latest_prediction_summary_widget_q18ak_japanese_localization_packet,
    latest_prediction_summary_widget_q18ak_searchable_plain_text,
    latest_prediction_summary_widget_q18ak_visible_display_rows,
    latest_prediction_summary_widget_q18ak_visible_plain_text,
)



def _q26g_stale_q18aj_source_packet() -> dict[str, object]:
    return {
        "ok": True,
        "component_source_generated_at": "2026-06-24T03:00:00Z",
        "auto_refresh_enabled": True,
        "fragment_slot_refresh_path_enabled": True,
        "partial_update_enabled": True,
        "broad_page_reload_disabled": True,
        "refresh_mode": "poll_normal",
        "refresh_interval_sec": 5,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "ledger_append_allowed": False,
    }

def test_q26g_q18aj_visible_text_localized_but_legacy_searchable_preserved() -> None:
    packet = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet()
    legacy = latest_prediction_summary_widget_q18aj_searchable_plain_text(packet)
    assert "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT" in legacy
    assert "autotrade=false" in legacy
    visible = latest_prediction_summary_widget_q18aj_visible_plain_text(packet)
    assert "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT" not in visible
    assert "autotrade=false" not in visible
    assert "broker=false" not in visible
    assert "自動更新" in visible
    assert "広域ページreload=なし" in visible
    assert "AutoTrade=なし" in visible
    rows = latest_prediction_summary_widget_q18aj_visible_display_rows(packet)
    joined = "\n".join(str(row) for row in rows)
    assert "確認項目" in joined
    assert "見るポイント" in joined
    assert "AutoTrade triggerとbroker/private API（売買接続）は無効です。" in joined
    loc = build_latest_prediction_summary_widget_q18aj_japanese_localization_packet()
    assert loc["localization_version"] == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_JAPANESE_LOCALIZATION_VERSION
    assert loc["legacy_searchable_plain_text_preserved"] is True
    assert loc["read_only"] is True
    assert loc["display_only"] is True
    assert loc["trade_guidance_added"] is False
    assert loc["broker_private_api_allowed"] is False
    assert loc["would_send_to_broker"] is False


def test_q26g_q18ak_visible_text_localized_but_legacy_searchable_preserved() -> None:
    packet = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        supplied_q18aj_bounded_auto_refresh_packet=_q26g_stale_q18aj_source_packet(),
        now_utc="2026-06-24T04:57:45Z",
    )
    legacy = latest_prediction_summary_widget_q18ak_searchable_plain_text(packet)
    assert "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS" in legacy
    assert "safe_fallback_reason_codes=source_generated_at_stale" in legacy
    visible = latest_prediction_summary_widget_q18ak_visible_plain_text(packet)
    assert "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS" not in visible
    assert "autotrade=false" not in visible
    assert "broker=false" not in visible
    assert "writes=false" not in visible
    assert "鮮度" in visible
    assert "fallback理由" in visible
    assert "生成時刻が古い" in visible
    assert "AutoTrade=なし" in visible
    rows = latest_prediction_summary_widget_q18ak_visible_display_rows(packet)
    joined = "\n".join(str(row) for row in rows)
    assert "確認項目" in joined
    assert "fallback理由" in joined
    assert "実行挙動はありません" in joined
    loc = build_latest_prediction_summary_widget_q18ak_japanese_localization_packet()
    assert loc["localization_version"] == LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_JAPANESE_LOCALIZATION_VERSION
    assert loc["legacy_searchable_plain_text_preserved"] is True
    assert loc["read_only"] is True
    assert loc["display_only"] is True
    assert loc["trade_guidance_added"] is False
    assert loc["broker_private_api_allowed"] is False
    assert loc["would_send_to_broker"] is False
