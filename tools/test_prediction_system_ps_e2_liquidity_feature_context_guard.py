# path: ./tools/test_prediction_system_ps_e2_liquidity_feature_context_guard.py
# desc: Focused guard for PS-E2 liquidity feature-depth context-only integration.

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

RULE = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "rule_based_v0.py"
SYSTEM = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "system.py"
FEATURE_DEPTH = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "feature_depth.py"


def _rows(now: datetime) -> list[dict[str, object]]:
    base = now - timedelta(minutes=29)
    return [
        {
            "event_ts": (base + timedelta(minutes=idx)).isoformat().replace("+00:00", "Z"),
            "price": 10_000_000 + idx * 900,
            "size": 0.2,
        }
        for idx in range(30)
    ]


def _venue_snapshots(now: datetime) -> list[dict[str, object]]:
    ts = now.isoformat().replace("+00:00", "Z")
    return [
        {"source_id": "bf_spot", "venue": "bitFlyer", "symbol": "BTC_JPY", "price": 10_000_000, "event_ts": ts, "market_role": "bitflyer_spot"},
        {"source_id": "bf_fx", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "price": 10_005_000, "event_ts": ts, "market_role": "bitflyer_fx"},
    ]


def _feature_depth(now: datetime):
    from btcts.prediction import SourceTrustState, assess_source_quality, build_feature_depth_snapshot, build_provider_reliability_registry

    q = {
        "bf_fx_board": assess_source_quality(source_id="bf_fx_board", source_family="bitflyer_fx_public_board", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
        "bf_fx_trades": assess_source_quality(source_id="bf_fx_trades", source_family="bitflyer_fx_public_trades", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
    }
    registry = build_provider_reliability_registry(source_quality_by_id=q, observed_source_ids=("bf_fx_board", "bf_fx_trades"), now=now)
    return build_feature_depth_snapshot(
        orderbook_snapshots=(
            {"source_id": "bf_fx_board", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "event_ts": now.isoformat().replace("+00:00", "Z"), "bid_price": 10_000_000, "ask_price": 10_001_500, "bid_depth": 4.0, "ask_depth": 3.5, "imbalance_ratio": 0.12},
        ),
        tradeflow_windows=(
            {"source_id": "bf_fx_trades", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "event_ts": now.isoformat().replace("+00:00", "Z"), "buy_volume": 4.0, "sell_volume": 2.5, "aggressive_buy_volume": 1.5, "aggressive_sell_volume": 0.9, "trade_count": 180},
        ),
        provider_reliability_registry=registry,
        now=now,
    )


def test_static_boundaries_and_ps_e2_markers() -> None:
    text = RULE.read_text(encoding="utf-8") + "\n" + SYSTEM.read_text(encoding="utf-8") + "\n" + FEATURE_DEPTH.read_text(encoding="utf-8")
    forbidden = [
        "btcts.autotrade",
        "btcts.collector_vnext",
        "append_decision_jsonl",
        "send_order",
        "place_order",
        "private_api",
        "requests.get",
        "urllib.request",
        "would_apply_mode: bool = True",
        "would_send_to_broker: bool = True",
    ]
    hits = [item for item in forbidden if item in text]
    assert not hits, hits
    assert "_apply_liquidity_feature_depth_context" in text
    assert "feature_depth_snapshot" in text
    assert "ps_e2.v1" in text


def test_rule_based_liquidity_accepts_feature_depth_context_only() -> None:
    from btcts.prediction import PredictionFamily, build_rule_based_v0_outputs

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    outputs = build_rule_based_v0_outputs(feature_depth_snapshot=_feature_depth(now), horizon_sec=300, now=now)
    liquidity = next(item for item in outputs if item.family == PredictionFamily.LIQUIDITY_EXECUTION_QUALITY)
    data = liquidity.to_dict()
    context = data["values"]["feature_depth_context"]
    assert context["version"] == "ps_e2.v1"
    assert context["context_only"] is True
    assert context["primary_direction_owner"] is False
    assert context["usable_for_primary_short_horizon"] is False
    assert context["orderbook_average_spread_bps"] is not None
    assert "liquidity_feature_depth_context_supplied" in data["drivers"]
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def test_prediction_system_passes_feature_depth_to_liquidity_only_as_context() -> None:
    from btcts.prediction import HorizonGroup, build_prediction_system_result

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    result = build_prediction_system_result(
        rows=_rows(now),
        venue_snapshots=_venue_snapshots(now),
        feature_depth_snapshot=_feature_depth(now),
        requested_horizon_groups=(HorizonGroup.SHORT_HORIZON,),
        now=now,
    )
    data = result.to_dict()
    liquidity_outputs = [item for item in data["outputs"] if item["family"] == "liquidity_execution_quality"]
    assert len(data["outputs"]) == 33
    assert data["forecast_batch"]["record_count"] == 33
    assert len(liquidity_outputs) == 3
    assert all(item["values"]["feature_depth_context"]["version"] == "ps_e2.v1" for item in liquidity_outputs)
    assert all(item["values"]["feature_depth_context"]["primary_direction_owner"] is False for item in liquidity_outputs)
    assert all(item["values"]["feature_depth_context"]["usable_for_primary_short_horizon"] is False for item in liquidity_outputs)
    assert data["system_input"]["feature_snapshot"]["feature_depth_snapshot_supplied"] is True
    assert data["gpt_review_digest"]["liquidity_feature_depth_context_version"] == "ps_e2.v1"
    assert data["gpt_review_digest"]["feature_depth_context_only"] is True
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False


def main() -> int:
    test_static_boundaries_and_ps_e2_markers()
    test_rule_based_liquidity_accepts_feature_depth_context_only()
    test_prediction_system_passes_feature_depth_to_liquidity_only_as_context()
    print("[OK] Prediction System PS-E2 liquidity feature-depth context guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
