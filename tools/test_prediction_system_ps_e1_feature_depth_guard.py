# path: ./tools/test_prediction_system_ps_e1_feature_depth_guard.py
# desc: Focused guard for PS-E1 feature-depth contracts.

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "btcts_next" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

FEATURE_DEPTH = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "feature_depth.py"
INIT = ROOT / "btcts_next" / "src" / "btcts" / "prediction" / "__init__.py"
DOC = ROOT / "docs" / "strategy" / "PREDICTION_SYSTEM_PS_E1_FEATURE_DEPTH_PLAN_BTC_BITFLYER_2026-06-19.md"


def test_static_boundaries_and_contract_markers() -> None:
    text = FEATURE_DEPTH.read_text(encoding="utf-8") + "\n" + INIT.read_text(encoding="utf-8") + "\n" + DOC.read_text(encoding="utf-8")
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
    assert "FeatureDepthSnapshot" in text
    assert "OrderBookFeatureSummary" in text
    assert "TradeFlowFeatureSummary" in text
    assert "build_feature_depth_snapshot" in text
    assert "primary_direction_owner=False" in text
    assert "usable_for_primary_short_horizon=False" in text


def test_feature_depth_snapshot_from_provided_inputs_context_only() -> None:
    from btcts.prediction import SourceTrustState, assess_source_quality, build_feature_depth_snapshot, build_provider_reliability_registry

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    q = {
        "bf_fx_board": assess_source_quality(source_id="bf_fx_board", source_family="bitflyer_fx_public_board", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
        "bf_fx_trades": assess_source_quality(source_id="bf_fx_trades", source_family="bitflyer_fx_public_trades", latest_event_ts=now.isoformat().replace("+00:00", "Z"), now=now, trust_state=SourceTrustState.TRUSTED),
    }
    registry = build_provider_reliability_registry(source_quality_by_id=q, observed_source_ids=("bf_fx_board", "bf_fx_trades"), now=now)
    snapshot = build_feature_depth_snapshot(
        orderbook_snapshots=(
            {"source_id": "bf_fx_board", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "event_ts": now.isoformat().replace("+00:00", "Z"), "bid_price": 10000000, "ask_price": 10001000, "bid_depth": 3.0, "ask_depth": 2.5, "imbalance_ratio": 0.09},
        ),
        tradeflow_windows=(
            {"source_id": "bf_fx_trades", "venue": "bitFlyer", "symbol": "FX_BTC_JPY", "event_ts": now.isoformat().replace("+00:00", "Z"), "buy_volume": 3.2, "sell_volume": 2.8, "aggressive_buy_volume": 1.4, "aggressive_sell_volume": 1.0, "trade_count": 120},
        ),
        provider_reliability_registry=registry,
        now=now,
    )
    data = snapshot.to_dict()
    assert data["feature_depth_state"] in {"usable_context", "warning_context"}
    assert data["context_only"] is True
    assert data["primary_direction_owner"] is False
    assert data["usable_for_primary_short_horizon"] is False
    assert data["read_only"] is True
    assert data["non_executing"] is True
    assert data["would_collect_public_source"] is False
    assert data["would_write_runtime_artifact"] is False
    assert data["would_send_to_broker"] is False
    assert data["broker_execution_requested"] is False
    assert data["mode_apply_requested"] is False
    assert data["command_ledger_append_requested"] is False
    assert data["orderbook"]["average_spread_bps"] is not None
    assert data["tradeflow"]["buy_sell_imbalance_ratio"] is not None
    assert data["input_refs"]


def test_feature_depth_missing_inputs_safe_unavailable() -> None:
    from btcts.prediction import build_feature_depth_snapshot

    now = datetime(2026, 6, 19, 0, 0, 0, tzinfo=timezone.utc)
    snapshot = build_feature_depth_snapshot(now=now)
    data = snapshot.to_dict()
    assert data["feature_depth_state"] == "unavailable"
    assert data["context_only"] is True
    assert data["primary_direction_owner"] is False
    assert data["usable_for_primary_short_horizon"] is False
    assert "orderbook_feature_depth_missing" in data["blockers"]
    assert "tradeflow_feature_depth_missing" in data["blockers"]
    assert data["read_only"] is True
    assert data["non_executing"] is True


def main() -> int:
    test_static_boundaries_and_contract_markers()
    test_feature_depth_snapshot_from_provided_inputs_context_only()
    test_feature_depth_missing_inputs_safe_unavailable()
    print("[OK] Prediction System PS-E1 feature depth guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
