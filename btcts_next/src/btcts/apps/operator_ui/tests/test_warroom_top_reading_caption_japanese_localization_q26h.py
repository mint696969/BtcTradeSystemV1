# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_top_reading_caption_japanese_localization_q26h.py
# desc: PS-Q26H tests for WarRoom top reading caption and page-level token Japanese localization. Display-only; no execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_VERSION,
    _q26h_observation_plain_text,
    _q26h_observation_quick_status_rows,
    _warroom_reading_block_captions,
    build_warroom_q26h_top_reading_caption_japanese_localization_packet,
)


def _sample_packet() -> dict:
    return {
        "latest_prediction_observation_status": "ready_for_operator_review",
        "q18aq_manual_resmoke_result": "pass",
        "q18ak_freshness_state": "unknown",
        "q18ak_safe_fallback_reason_codes": ["source_generated_at_missing"],
        "q18aj_refresh_heartbeat_utc": "2026-07-01T00:00:00Z",
        "implementation_gate_review_result": "blocked_not_ready_to_enable",
        "read_order": "quick_status_then_searchable_tokens_then_legacy_preflight_details",
        "q18aj_auto_refresh_enabled": True,
    }


def test_q26h_reading_block_captions_are_japanese() -> None:
    captions = _warroom_reading_block_captions()
    joined = "\n".join(captions.values())
    assert "現在の市場summary" in joined
    assert "現在のactive event" in joined
    assert "予測はreview補助" in joined
    assert "operator review" in joined
    assert "read current regime" not in joined
    assert "read tactic stance" not in joined


def test_q26h_quick_status_plain_text_and_rows_are_japanese_and_safe() -> None:
    text = _q26h_observation_plain_text(_sample_packet())
    assert "PS-Q26H 予測最新ステータス" in text
    assert "安全fallback理由=生成時刻が欠落" in text
    assert "画面heartbeat=" in text
    assert "実render=なし" in text
    assert "AutoTrade=なし" in text
    assert "real_render=false" not in text
    assert "runtime binding=false" not in text
    assert "autotrade=false" not in text
    assert "broker=false" not in text
    rows = _q26h_observation_quick_status_rows(_sample_packet())
    joined = "\n".join(str(row) for row in rows)
    assert "画面heartbeat" in joined
    assert "実行挙動はありません" in joined
    assert "なし" in joined
    packet = build_warroom_q26h_top_reading_caption_japanese_localization_packet()
    assert packet["localization_version"] == WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_VERSION
    assert packet["reading_block_captions_japanese_localized"] is True
    assert packet["quick_status_plain_text_japanese_localized"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["trade_guidance_added"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False
