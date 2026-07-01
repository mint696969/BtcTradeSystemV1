# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_telemetry_footer_detail_note_localization_q26e.py
# desc: PS-Q26E tests for telemetry footer and detail-note Japanese localization. Display-only; no trade guidance or execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION,
    build_latest_prediction_warroom_q26e_telemetry_footer_detail_note_localization_packet,
    latest_prediction_warroom_q26e_telemetry_footer_text,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_NOWCAST_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION,
    build_warroom_live_nowcast_q26e_telemetry_footer_detail_note_localization_packet,
    warroom_live_nowcast_q26e_localize_display_rows,
    warroom_live_nowcast_q26e_telemetry_footer_text,
)


def test_q26e_prediction_footer_is_japanese_and_safe() -> None:
    text = latest_prediction_warroom_q26e_telemetry_footer_text({"freshness_state": "fresh", "prediction_row_count": 24, "generated_at": "2026-07-01T00:00:00Z"}, lang="ja")
    assert "表示言語=ja" in text
    assert "表示専用" in text
    assert "AutoTrade=なし" in text
    assert "broker=なし" in text
    assert "view_artifact_write_allowed=false" not in text
    packet = build_latest_prediction_warroom_q26e_telemetry_footer_detail_note_localization_packet()
    assert packet["localization_version"] == WARROOM_PREDICTION_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    assert packet["trade_guidance_added"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q26e_nowcast_footer_and_notes_are_japanese_and_safe() -> None:
    text = warroom_live_nowcast_q26e_telemetry_footer_text({"current_state_summary": "current_market_state_live_observable", "nowcast_freshness_state": "live", "market_event_age_sec": 0, "spread_bps": 1.2})
    assert "読み取り専用=はい" in text
    assert "AutoTrade=なし" in text
    assert "broker=なし" in text
    rows = warroom_live_nowcast_q26e_localize_display_rows([{"item": "source_layering_version", "value": "v", "note": "display-only current-state layer"}, {"item": "operator_instruction", "value": "x", "note": "not a trade instruction"}])
    joined = "\n".join(str(row) for row in rows)
    assert "表示専用の現在状態レイヤー" in joined
    assert "売買指示ではありません" in joined
    packet = build_warroom_live_nowcast_q26e_telemetry_footer_detail_note_localization_packet()
    assert packet["localization_version"] == WARROOM_LIVE_NOWCAST_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    assert packet["trade_guidance_added"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False
