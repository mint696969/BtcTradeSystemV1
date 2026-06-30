# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_japanese_reading_layer_density_polish_q26b.py
# desc: PS-Q26B tests for compact Japanese density polish rows. Display-only; no trade guidance or execution.

from __future__ import annotations

from datetime import datetime
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_NOWCAST_JAPANESE_READING_DENSITY_POLISH_VERSION,
    build_warroom_live_market_nowcast_packet,
    build_warroom_live_nowcast_japanese_density_polish_packet,
    build_warroom_live_nowcast_operator_summary_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_JAPANESE_READING_DENSITY_POLISH_VERSION,
    build_latest_prediction_warroom_japanese_density_polish_packet,
    latest_prediction_warroom_display_rows,
    latest_prediction_warroom_horizon_expiry_packet,
    latest_prediction_warroom_operator_action_guidance_packet,
)


def test_q26b_nowcast_density_polish_is_compact_and_safe() -> None:
    packet = build_warroom_live_market_nowcast_packet(
        sources={
            "market_state": {"lane_state": "live", "last_best_bid": 100.0, "last_best_ask": 100.05, "last_spread": 0.05, "last_event_ts": "2026-06-30T00:00:00Z", "ts": "2026-06-30T00:00:00Z"},
            "health": {"ok": True, "status": "healthy", "ws_state": "LIVE", "ws_freshness": "LIVE", "gap_detected": False, "resync_active": False, "ts": "2026-06-30T00:00:00Z"},
            "daemon": {"mode": "RUNNING"},
            "executions": {"ts": "2026-06-30T00:00:00Z"},
        },
        now=datetime.fromisoformat("2026-06-30T00:00:03+00:00"),
    )
    summary = build_warroom_live_nowcast_operator_summary_packet(packet, lang="ja")
    polish = build_warroom_live_nowcast_japanese_density_polish_packet(packet, summary)
    assert polish["density_polish_version"] == WARROOM_LIVE_NOWCAST_JAPANESE_READING_DENSITY_POLISH_VERSION
    assert polish["operator_visible_compact_japanese_rows"] is True
    assert polish["compact_row_count"] == 5
    joined = "\n".join(str(row) for row in polish["compact_rows"])
    assert "いま読むべき結論" in joined
    assert "鮮度" in joined
    assert "売買指示ではありません" in joined
    assert polish["read_only"] is True
    assert polish["display_only"] is True
    assert polish["non_executing"] is True
    assert polish["trade_guidance_added"] is False
    assert polish["trade_signal_added"] is False
    assert polish["scheduler_enabled"] is False
    assert polish["producer_enabled"] is False
    assert polish["broker_private_api_allowed"] is False
    assert polish["would_send_to_broker"] is False


def test_q26b_prediction_density_polish_is_compact_and_safe() -> None:
    read_model = {
        "ok": True,
        "generated_at": "2026-06-30T00:00:00Z",
        "age_sec": 10,
        "freshness_state": "fresh",
        "selected_horizon_sec": [15, 60, 300, 900],
        "selected_records_by_horizon": {
            "15": [{"family": "trend_bias", "primary_label": "short_bias", "confidence": "medium", "score": 0.66, "warnings": [], "drivers": []}],
            "60": [{"family": "cross_venue_confirmation", "primary_label": "confirmed", "confidence": "high", "score": 0.7, "warnings": [], "drivers": []}],
            "300": [{"family": "market_regime", "primary_label": "range_candidate", "confidence": "medium", "score": 0.52, "warnings": [], "drivers": []}],
            "900": [{"family": "volatility_risk", "primary_label": "compression_watch", "confidence": "medium", "score": 0.58, "warnings": [], "drivers": []}],
        },
    }
    rows = latest_prediction_warroom_display_rows(read_model, lang="ja")
    expiry = latest_prediction_warroom_horizon_expiry_packet(read_model, lang="ja")
    guidance = latest_prediction_warroom_operator_action_guidance_packet({"horizon_expiry_packet": expiry, "freshness_state": "fresh", "age_sec": 10}, lang="ja")
    polish = build_latest_prediction_warroom_japanese_density_polish_packet(read_model, prediction_rows=rows, horizon_expiry_packet=expiry, operator_action_guidance_packet=guidance)
    assert polish["density_polish_version"] == WARROOM_PREDICTION_JAPANESE_READING_DENSITY_POLISH_VERSION
    assert polish["operator_visible_compact_japanese_rows"] is True
    assert polish["compact_row_count"] == 5
    joined = "\n".join(str(row) for row in polish["compact_rows"])
    assert "予測を読めるか" in joined
    assert "短期 15s/60s" in joined
    assert "売買指示ではありません" in joined
    assert polish["read_only"] is True
    assert polish["display_only"] is True
    assert polish["non_executing"] is True
    assert polish["trade_guidance_added"] is False
    assert polish["trade_signal_added"] is False
    assert polish["scheduler_enabled"] is False
    assert polish["producer_enabled"] is False
    assert polish["broker_private_api_allowed"] is False
    assert polish["would_send_to_broker"] is False
