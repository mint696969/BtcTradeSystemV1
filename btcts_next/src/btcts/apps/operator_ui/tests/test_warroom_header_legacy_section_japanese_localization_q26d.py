# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_header_legacy_section_japanese_localization_q26d.py
# desc: PS-Q26D tests for WarRoom header and legacy/section Japanese localization. Display-only; no trade guidance or execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    WARROOM_HEADER_LEGACY_SECTION_JAPANESE_LOCALIZATION_VERSION,
    _q26d_prediction_observation_plain_text,
    _q26d_prediction_observation_quick_status_rows,
    build_warroom_q26d_header_legacy_section_localization_packet,
)
from btcts.apps.operator_ui.components.warroom_header import (  # noqa: E402
    WARROOM_HEADER_SOURCE_JAPANESE_LOCALIZATION_VERSION,
    _q26d_header_source_label,
    build_warroom_header_q26d_source_localization_packet,
)
from btcts.apps.operator_ui.prediction_warroom.texts.latest_prediction_display_texts import DISPLAY_TEXTS  # noqa: E402


def test_q26d_quick_status_rows_are_japanese_and_safe() -> None:
    packet = {
        "read_order": "quick_status_then_searchable_tokens_then_legacy_preflight_details",
        "q18aq_manual_resmoke_result": "pass",
        "q18aj_auto_refresh_enabled": True,
        "q18aj_refresh_heartbeat_utc": "2026-07-01T00:00:00Z",
        "q18ak_freshness_state": "unknown",
        "q18ak_safe_fallback_reason_codes": ["auto_refresh_source_packet_not_ok", "source_generated_at_missing"],
        "implementation_gate_review_result": "blocked_not_ready_to_enable",
        "latest_prediction_observation_status": "ready_for_operator_review",
    }
    rows = _q26d_prediction_observation_quick_status_rows(packet)
    joined = "\n".join(str(row) for row in rows)
    assert "確認項目" in joined
    assert "まず quick status" in joined
    assert "通過" in joined
    assert "自動更新元 packet が未OK" in joined
    assert "有効化は不可" in joined
    plain = _q26d_prediction_observation_plain_text(packet)
    assert "PS-Q18AU 予測最新 quick status" in plain
    assert "ready_for_operator_review" not in plain
    loc = build_warroom_q26d_header_legacy_section_localization_packet()
    assert loc["localization_version"] == WARROOM_HEADER_LEGACY_SECTION_JAPANESE_LOCALIZATION_VERSION
    assert loc["quick_status_japanese_localized"] is True
    assert loc["read_only"] is True
    assert loc["display_only"] is True
    assert loc["trade_guidance_added"] is False
    assert loc["broker_private_api_allowed"] is False
    assert loc["would_send_to_broker"] is False


def test_q26d_header_source_and_footer_are_localized_and_safe() -> None:
    assert _q26d_header_source_label("execution_market_live_canonical + research_experiment") == "実行市場live基準 + research補助"
    packet = build_warroom_header_q26d_source_localization_packet()
    assert packet["localization_version"] == WARROOM_HEADER_SOURCE_JAPANESE_LOCALIZATION_VERSION
    assert packet["header_source_label_japanese_localized"] is True
    assert packet["source_example"] == "実行市場live基準 + research補助"
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["trade_guidance_added"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False
    assert DISPLAY_TEXTS["ja"]["footer_token"] == "PS-Q19I 予測表示の日本語説明"
