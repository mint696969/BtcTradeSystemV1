# path: ./tools/test_phase4a_prediction_system_ps_q19r_prediction_actual_market_review.py
# desc: Focused guard for PS-Q19R read-only prediction versus actual market review helper.

from __future__ import annotations

from datetime import datetime, timezone
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.review_prediction_vs_actual_market_ps_q19r import (  # noqa: E402
    DEFAULT_HORIZONS_SEC,
    MarketPoint,
    build_prediction_actual_market_review_packet,
    load_and_build_prediction_actual_market_review_packet,
)

SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q19R_PREDICTION_ACTUAL_MARKET_REVIEW_2026-06-25.md"
TOOL = REPO_ROOT / "tools/review_prediction_vs_actual_market_ps_q19r.py"

REQUIRED_MARKERS = (
    "ps_q19r_prediction_actual_market_review=true",
    "latest_prediction_vs_actual_market_review_helper_added=true",
    "reads_latest_prediction_artifact=true",
    "reads_market_overview_jsonl=true",
)

FALSE_BOUNDARIES = (
    "runtime_artifact_write_performed_by_review=false",
    "status_artifact_write_performed_by_review=false",
    "prediction_artifact_write_performed_by_review=false",
    "view_artifact_write_performed_by_review=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "would_send_to_broker=false",
)


def _payload() -> dict:
    return {
        "forecast_batch": {
            "generated_at": "2026-06-25T00:00:00Z",
            "records": [
                {"family": "trend_bias", "horizon_sec": 60, "primary_label": "long_bias", "confidence": "medium", "score": 0.6, "usable": True, "warnings": [], "drivers": ["unit"]},
                {"family": "market_regime", "horizon_sec": 60, "primary_label": "range_candidate", "confidence": "medium", "score": 0.5, "usable": True, "warnings": [], "drivers": ["unit"]},
                {"family": "reversal_zone", "horizon_sec": 300, "primary_label": "vwap_reversion_watch", "confidence": "low", "score": 0.4, "usable": True, "warnings": [], "drivers": ["unit"]},
            ],
        }
    }


def _points() -> list[MarketPoint]:
    return [
        MarketPoint(ts=datetime(2026, 6, 25, 0, 0, 0, tzinfo=timezone.utc), mid_price=100.0, best_bid=99.0, best_ask=101.0, spread=2.0, trust_state="trusted", continuity_state="continuous", interpretation_bucket="allow_structural_use"),
        MarketPoint(ts=datetime(2026, 6, 25, 0, 1, 0, tzinfo=timezone.utc), mid_price=100.10, best_bid=100.0, best_ask=100.2, spread=0.2, trust_state="trusted", continuity_state="continuous", interpretation_bucket="allow_structural_use"),
        MarketPoint(ts=datetime(2026, 6, 25, 0, 5, 0, tzinfo=timezone.utc), mid_price=100.11, best_bid=100.0, best_ask=100.2, spread=0.2, trust_state="trusted", continuity_state="continuous", interpretation_bucket="allow_structural_use"),
    ]


def test_spec_declares_read_only_review_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


def test_packet_compares_prediction_labels_to_realized_market_movement() -> None:
    packet = build_prediction_actual_market_review_packet(
        prediction_payload=_payload(),
        market_points=_points(),
        selected_horizons_sec=(60, 300),
        selected_families=("trend_bias", "market_regime", "reversal_zone"),
        direction_threshold_bps=2.0,
    )
    assert packet["ok"] is True
    assert packet["review_row_count"] == 3
    assert packet["actual_available_row_count"] == 3
    assert packet["actual_by_horizon"]["60"]["realized_direction"] == "up"
    rows = packet["review_rows"]
    assert any(row["family"] == "trend_bias" and row["alignment_hint"] == "direction_match" for row in rows)
    assert any(row["family"] == "market_regime" and row["alignment_hint"] == "range_or_neutral_broken" for row in rows)
    assert packet["scheduler_enabled"] is False
    assert packet["producer_enabled"] is False
    assert packet["warroom_ui_trigger_enabled"] is False
    assert packet["would_send_to_broker"] is False


def test_loader_reads_prediction_and_market_jsonl_from_paths(tmp_path: Path) -> None:
    root = tmp_path
    pred = root / "prediction/latest_prediction_system_result.json"
    pred.parent.mkdir(parents=True, exist_ok=True)
    pred.write_text(json.dumps(_payload()), encoding="utf-8")
    market = root / "market.jsonl"
    lines = [
        {"collector_ts": "2026-06-25T00:00:00Z", "mid_price": 100.0, "best_bid": 99.9, "best_ask": 100.1, "spread": 0.2, "trust_state": "trusted", "continuity_state": "continuous", "interpretation_bucket": "allow_structural_use"},
        {"collector_ts": "2026-06-25T00:01:00Z", "mid_price": 100.1, "best_bid": 100.0, "best_ask": 100.2, "spread": 0.2, "trust_state": "trusted", "continuity_state": "continuous", "interpretation_bucket": "allow_structural_use"},
        {"collector_ts": "2026-06-25T00:05:00Z", "mid_price": 100.11, "best_bid": 100.0, "best_ask": 100.2, "spread": 0.2, "trust_state": "trusted", "continuity_state": "continuous", "interpretation_bucket": "allow_structural_use"},
    ]
    market.write_text("\n".join(json.dumps(row) for row in lines) + "\n", encoding="utf-8")
    packet = load_and_build_prediction_actual_market_review_packet(
        root=str(root),
        prediction_path=str(pred),
        market_path=str(market),
        max_tail_bytes=4096,
        horizons_sec=(60, 300),
        families=("trend_bias", "market_regime", "reversal_zone"),
    )
    assert packet["ok"] is True
    assert packet["market_point_count_loaded"] == 3
    assert packet["review_row_count"] == 3



def test_untrusted_or_reanchor_actual_point_is_not_available() -> None:
    bad_points = [
        MarketPoint(ts=datetime(2026, 6, 25, 0, 0, 0, tzinfo=timezone.utc), mid_price=100.0, best_bid=99.0, best_ask=101.0, spread=2.0, trust_state="trusted", continuity_state="continuous", interpretation_bucket="allow_structural_use"),
        MarketPoint(ts=datetime(2026, 6, 25, 0, 1, 0, tzinfo=timezone.utc), mid_price=100.1, best_bid=100.2, best_ask=100.0, spread=-0.2, trust_state="quarantined", continuity_state="continuous", interpretation_bucket="reanchor_required"),
    ]
    packet = build_prediction_actual_market_review_packet(
        prediction_payload=_payload(),
        market_points=bad_points,
        selected_horizons_sec=(60,),
        selected_families=("trend_bias", "market_regime"),
    )
    assert packet["ok"] is True
    actual = packet["actual_by_horizon"]["60"]
    assert actual["available"] is False
    assert actual["actual_quality_ok"] is False
    assert "market_point_not_trusted" in actual["actual_quality_reasons"]
    assert "market_point_not_structural_use" in actual["actual_quality_reasons"]
    assert "market_point_negative_spread" in actual["actual_quality_reasons"]
    assert "market_point_crossed_book" in actual["actual_quality_reasons"]
    assert packet["actual_available_row_count"] == 0
    assert packet["alignment_summary"]["actual_unavailable"] == 2


def test_missing_market_points_blocks_review() -> None:
    packet = build_prediction_actual_market_review_packet(prediction_payload=_payload(), market_points=[])
    assert packet["ok"] is False
    assert "market_points_missing" in packet["blocked_reasons"]


def test_tool_has_no_write_or_execution_behavior() -> None:
    text = TOOL.read_text(encoding="utf-8")
    forbidden = (
        "append_jsonl(",
        "write_canonical(",
        "write_raw(",
        "place_order(",
        "send_order(",
        "would_send_to_broker: bool = True",
    )
    for token in forbidden:
        assert token not in text, token
    assert "runtime_artifact_write_performed_by_review" in text
    assert "read_only_review" in text


if __name__ == "__main__":
    test_spec_declares_read_only_review_boundaries()
    test_packet_compares_prediction_labels_to_realized_market_movement()
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as tmp:
        test_loader_reads_prediction_and_market_jsonl_from_paths(Path(tmp))
    test_untrusted_or_reanchor_actual_point_is_not_available()
    test_missing_market_points_blocks_review()
    test_tool_has_no_write_or_execution_behavior()
    print('{"ok": true}')
