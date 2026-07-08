# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_feature_expansion_cp6.py
# desc: CP6 tests for market-regime liquidity/orderbook history, orderflow, and confirmed technical-structure feature expansion. Pure tmp fixtures only.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime import FeatureGroup  # noqa: E402
from btcts.prediction.market_regime.features import build_market_regime_feature_bundle  # noqa: E402
from btcts.prediction.market_regime.sources import build_market_regime_source_snapshot  # noqa: E402


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _fixture_root(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-08/094500/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-08T09:45:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-08/094500/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {
            "family": "market_regime",
            "horizon_sec": 900,
            "primary_label": "range_candidate",
            "score": 0.82,
            "values_snapshot": {
                "estimated_signal_strength_percent": 75,
                "estimated_reference_hit_rate_percent": 68,
                "volatility_state": "normal",
                "cross_venue_agreement": "aligned",
                "range_high": 9800000,
                "range_low": 9700000,
                "vwap": 9750000,
                "ma_slope": -0.12,
                "atr": 18000,
                "realized_volatility": 0.018,
                "price_position_in_range": 0.54,
                "break_hold_count": 1,
                "false_break_count": 2
            },
        }
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9749000.0,
        "last_best_ask": 9751000.0,
        "last_spread": 2000.0,
        "bid_depth_size": 18.0,
        "ask_depth_size": 12.0,
        "microprice": 9750200.0,
        "liquidity_replenishment_score": 0.72,
        "liquidity_disappearance_score": 0.21,
        "absorption_score": 0.63,
        "spread_change_bps_1m": -1.5,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {
        "ws_state": "LIVE",
        "trade_count": 20450,
        "aggressive_buy_volume": 8.5,
        "aggressive_sell_volume": 4.0,
        "cvd": 3.25,
        "large_trade_count": 5,
        "volume_acceleration": 1.4,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def _signals_by_name(root: Path, group: FeatureGroup) -> dict[str, object]:
    snapshot = build_market_regime_source_snapshot(root)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-08T09:45:02Z")
    return {signal.name: signal for signal in bundle.signals_by_group(group)}


def test_cp6_liquidity_orderbook_transition_signals_are_available(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    signals = _signals_by_name(tmp_path, FeatureGroup.LIQUIDITY)
    assert signals["mid_price"].value == 9750000.0
    assert round(signals["spread_bps"].value, 4) == round(2000.0 / 9750000.0 * 10000.0, 4)
    assert signals["depth_imbalance"].value == 0.2
    assert signals["microprice"].value == 9750200.0
    assert signals["microprice_bias_bps"].value > 0
    assert signals["liquidity_replenishment_score"].value == 0.72
    assert signals["liquidity_disappearance_score"].value == 0.21
    assert signals["absorption_score"].value == 0.63
    assert signals["spread_change_bps_1m"].value == -1.5


def test_cp6_orderflow_expansion_signals_are_available(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    signals = _signals_by_name(tmp_path, FeatureGroup.ORDERFLOW)
    assert signals["aggressive_buy_volume"].value == 8.5
    assert signals["aggressive_sell_volume"].value == 4.0
    assert signals["orderflow_imbalance"].value == 0.36
    assert signals["cvd"].value == 3.25
    assert signals["large_trade_count"].value == 5
    assert signals["volume_acceleration"].value == 1.4


def test_cp6_confirmed_technical_structure_signals_are_available(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    signals = _signals_by_name(tmp_path, FeatureGroup.PRICE_STRUCTURE)
    assert signals["range_high"].value == 9800000.0
    assert signals["range_low"].value == 9700000.0
    assert signals["vwap"].value == 9750000.0
    assert signals["ma_slope"].value == -0.12
    assert signals["price_position_in_range"].value == 0.54
    assert signals["break_hold_count"].value == 1
    assert signals["false_break_count"].value == 2
    assert signals["confirmed_technical_structure_available"].value is True


def test_cp6_volatility_numeric_signals_are_available(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    signals = _signals_by_name(tmp_path, FeatureGroup.VOLATILITY)
    assert signals["atr"].value == 18000.0
    assert signals["realized_volatility"].value == 0.018
    assert signals["volatility_state"].value == "normal"
