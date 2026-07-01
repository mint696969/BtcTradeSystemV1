# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_japanese_remaining_token_localization_q26c.py
# desc: PS-Q26C tests for remaining visible token localization. Display-only; no trade guidance or execution.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_NOWCAST_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION,
    build_warroom_live_nowcast_q26c_remaining_token_localization_packet,
    warroom_live_nowcast_q26c_localize_display_rows,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION,
    build_latest_prediction_warroom_q26c_remaining_token_localization_packet,
    latest_prediction_warroom_q26c_localize_display_rows,
)


def test_q26c_nowcast_detail_rows_get_japanese_columns_and_values() -> None:
    rows = [
        {"item": "current_state_score", "value": "14", "note": "weak_current_state"},
        {"layer": "foundation_integrity", "source": "collector_freshness", "role": "current-state trust gate", "status": "blocked", "reason": "freshness=stale_caution"},
    ]
    localized = warroom_live_nowcast_q26c_localize_display_rows(rows)
    joined = "\n".join(str(row) for row in localized)
    assert "項目" in joined
    assert "現在状態スコア" in joined
    assert "現在状態の土台が弱い" in joined
    assert "層" in joined
    assert "土台の健全性" in joined
    assert "Collector鮮度" in joined
    assert "古い/注意" in joined
    packet = build_warroom_live_nowcast_q26c_remaining_token_localization_packet()
    assert packet["remaining_token_localization_version"] == WARROOM_LIVE_NOWCAST_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION
    assert packet["operator_visible_localized_detail_tables"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    assert packet["trade_guidance_added"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False


def test_q26c_prediction_remaining_token_is_localized_and_safe() -> None:
    rows = [
        {"item": "prediction_tactical_readiness", "value": "prediction_rows_readable_as_current_artifact", "note": "short_horizon_expired_or_stale"},
        {"horizon": "15s", "family": "trend_bias", "label": "short_bias", "usable": "true"},
    ]
    localized = latest_prediction_warroom_q26c_localize_display_rows(rows)
    joined = "\n".join(str(row) for row in localized)
    assert "prediction_rows_readable_as_current_artifact" not in joined
    assert "予測表示: 現在artifactとして読める" in joined
    assert "短期は古い/弱い" in joined
    assert "分類" in joined
    assert "トレンド方向" in joined
    packet = build_latest_prediction_warroom_q26c_remaining_token_localization_packet()
    assert packet["remaining_token_localization_version"] == WARROOM_PREDICTION_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION
    assert packet["operator_visible_localized_detail_tables"] is True
    assert packet["read_only"] is True
    assert packet["display_only"] is True
    assert packet["non_executing"] is True
    assert packet["trade_guidance_added"] is False
    assert packet["broker_private_api_allowed"] is False
    assert packet["would_send_to_broker"] is False
