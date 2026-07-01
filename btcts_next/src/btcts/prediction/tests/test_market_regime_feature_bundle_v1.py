# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_feature_bundle_v1.py
# desc: PS-Q27I tests for market-regime feature bundle v1. Uses tmp_path source snapshots only; no real D-hot access.

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


def _build_fixture(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-01/170500/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:05:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/170500/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {
        "generated_at": "2026-07-01T17:05:00Z",
        "read_only": True,
        "non_executing": True,
    })
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "horizon_sec": 300, "primary_label": "range_candidate", "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 21600, "primary_label": "range_candidate", "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "ts": "2026-07-01T17:05:02Z",
        "lane_state": "live",
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9727585.0,
        "last_spread": -1479.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {
        "ts": "2026-07-01T17:05:02Z",
        "ok": True,
        "ws_state": "LIVE",
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {
        "ts": "2026-07-01T17:05:02Z",
        "ws_state": "LIVE",
        "trade_count": 20450,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def _bundle(root: Path):
    _build_fixture(root)
    snapshot = build_market_regime_source_snapshot(root)
    return build_market_regime_feature_bundle(snapshot, generated_at="2026-07-01T17:05:03Z")


def test_q27i_feature_bundle_builds_all_core_groups_from_snapshot(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    data = bundle.to_dict()
    groups = {item["feature_group"] for item in data["coverage"]}
    assert groups == {"price_structure", "volatility", "liquidity", "orderflow", "cross_venue", "source_quality"}
    assert data["source_snapshot_ok"] is True
    assert data["available_signal_count"] >= 10
    assert data["missing_sources"] == []
    assert data["safety"]["read_only"] is True
    assert data["safety"]["source_snapshot_input_only"] is True


def test_q27i_liquidity_and_orderflow_features_preserve_nowcast_values(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    liquidity = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.LIQUIDITY)}
    orderflow = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.ORDERFLOW)}
    assert liquidity["absolute_spread"].value == 1479.0
    assert liquidity["crossed_or_negative_spread"].value is True
    assert "negative_spread_seen" in liquidity["absolute_spread"].warnings
    assert orderflow["execution_trade_count"].value == 20450
    assert orderflow["executions_ws_live"].value is True


def test_q27i_price_volatility_cross_venue_features_use_market_regime_records(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    price = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.PRICE_STRUCTURE)}
    volatility = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.VOLATILITY)}
    cross = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.CROSS_VENUE)}
    assert price["market_regime_record_count"].value == 2
    assert price["market_regime_horizons_sec"].value == [300, 21600]
    assert price["latest_market_regime_label"].value == "range_candidate"
    assert volatility["volatility_state"].value == "normal"
    assert cross["cross_venue_agreement"].value == "aligned"


def test_q27i_missing_source_snapshot_degrades_without_exception(tmp_path: Path) -> None:
    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-01T17:05:03Z")
    data = bundle.to_dict()
    assert data["source_snapshot_ok"] is False
    assert "latest_manifest" in data["missing_sources"]
    assert "collector_market_state" in data["missing_sources"]
    source_quality = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.SOURCE_QUALITY)}
    assert source_quality["missing_source_count"].value >= 1
    assert source_quality["source_quality_score"].value < 1.0


def test_q27i_feature_bundle_safety_flags_remain_false(tmp_path: Path) -> None:
    bundle = _bundle(tmp_path)
    safety = bundle.to_dict()["safety"]
    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "scheduler_enabled",
        "producer_enabled",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ledger_append_allowed",
        "mode_apply_allowed",
        "parameter_apply_allowed",
        "would_send_to_broker",
    ):
        assert safety[key] is False


def test_q27i_feature_modules_do_not_import_ui_or_runtime_paths() -> None:
    package_root = Path(__file__).resolve().parents[1] / "market_regime"
    forbidden = ("import streamlit", "from streamlit", "runtime_root(", "send_to_broker(", "append_ledger(", "ledger.append(", "open(\"D:")
    for path in list((package_root / "features").glob("*.py")):
        text = path.read_text(encoding="utf-8-sig")
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"
