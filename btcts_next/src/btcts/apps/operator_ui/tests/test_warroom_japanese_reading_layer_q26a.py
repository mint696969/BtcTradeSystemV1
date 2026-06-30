# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_japanese_reading_layer_q26a.py
# desc: PS-Q26A tests for Japanese operator reading rows on WarRoom nowcast and prediction display. Display-only; no writes/execution.

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_NOWCAST_JAPANESE_READING_LAYER_VERSION,
    build_warroom_live_market_nowcast_packet,
    build_warroom_live_nowcast_japanese_reading_layer_packet,
    build_warroom_live_nowcast_operator_summary_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_JAPANESE_READING_LAYER_VERSION,
    build_latest_prediction_warroom_japanese_reading_layer_packet,
    latest_prediction_warroom_display_rows,
    latest_prediction_warroom_horizon_expiry_packet,
    latest_prediction_warroom_operator_action_guidance_packet,
)


def test_q26a_nowcast_japanese_reading_layer_is_display_only() -> None:
    packet = build_warroom_live_market_nowcast_packet(
        sources={
            "market_state": {"lane_state": "live", "last_best_bid": 100.0, "last_best_ask": 101.0, "last_spread": 1.0, "last_event_ts": "2026-06-30T00:00:00Z", "ts": "2026-06-30T00:00:00Z"},
            "health": {"ok": True, "status": "healthy", "ws_state": "LIVE", "ws_freshness": "LIVE", "gap_detected": False, "resync_active": False, "ts": "2026-06-30T00:00:00Z"},
            "daemon": {"mode": "RUNNING"},
            "executions": {"ts": "2026-06-30T00:00:00Z"},
        },
        now=datetime.fromisoformat("2026-06-30T00:00:03+00:00"),
    )
    summary = build_warroom_live_nowcast_operator_summary_packet(packet, lang="ja")
    layer = build_warroom_live_nowcast_japanese_reading_layer_packet(packet, summary)
    assert layer["japanese_reading_layer_version"] == WARROOM_LIVE_NOWCAST_JAPANESE_READING_LAYER_VERSION
    assert layer["operator_visible_japanese_rows"] is True
    assert layer["row_count"] >= 5
    joined = "\n".join(str(row) for row in layer["rows"])
    assert "現在状態" in joined
    assert "売買指示ではありません" in joined or "売買" in joined
    assert layer["read_only"] is True
    assert layer["non_executing"] is True
    assert layer["display_only"] is True
    assert layer["scheduler_enabled"] is False
    assert layer["producer_enabled"] is False
    assert layer["broker_private_api_allowed"] is False
    assert layer["would_send_to_broker"] is False


def test_q26a_prediction_japanese_reading_layer_is_display_only() -> None:
    read_model = {
        "ok": True,
        "generated_at": "2026-06-30T00:00:00Z",
        "age_sec": 20,
        "freshness_state": "fresh",
        "selected_horizon_sec": [15, 60, 300, 900],
        "selected_records_by_horizon": {
            "15": [{"family": "trend_bias", "primary_label": "short_bias", "confidence": "medium", "score": 0.66, "warnings": [], "drivers": []}],
            "60": [{"family": "cross_venue_confirmation", "primary_label": "confirmed", "confidence": "high", "score": 0.7, "warnings": [], "drivers": []}],
            "300": [{"family": "market_regime", "primary_label": "range_candidate", "confidence": "medium", "score": 0.52, "warnings": [], "drivers": []}],
            "900": [{"family": "volatility_risk", "primary_label": "compression_watch", "confidence": "medium", "score": 0.58, "warnings": [], "drivers": []}],
        },
    }
    prediction_rows = latest_prediction_warroom_display_rows(read_model, lang="ja")
    expiry = latest_prediction_warroom_horizon_expiry_packet(read_model, lang="ja")
    guidance = latest_prediction_warroom_operator_action_guidance_packet({"horizon_expiry_packet": expiry, "freshness_state": "fresh", "age_sec": 20}, lang="ja")
    layer = build_latest_prediction_warroom_japanese_reading_layer_packet(read_model, prediction_rows=prediction_rows, horizon_expiry_packet=expiry, operator_action_guidance_packet=guidance)
    assert layer["japanese_reading_layer_version"] == WARROOM_PREDICTION_JAPANESE_READING_LAYER_VERSION
    assert layer["operator_visible_japanese_rows"] is True
    assert layer["row_count"] >= 5
    joined = "\n".join(str(row) for row in layer["rows"])
    assert "予測データ鮮度" in joined
    assert "短期 15s / 60s" in joined
    assert "売買指示" in joined or "operator review" in joined
    assert layer["read_only"] is True
    assert layer["non_executing"] is True
    assert layer["display_only"] is True
    assert layer["scheduler_enabled"] is False
    assert layer["producer_enabled"] is False
    assert layer["broker_private_api_allowed"] is False
    assert layer["would_send_to_broker"] is False
