# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_signal_scoring_cp7.py
# desc: CP7 tests for market-regime signal-registry-v1 scoring and latest_read_model integration. Tmp fixtures only; no UI, scheduler, broker, AutoTrade, or ledger behavior.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime import FeatureGroup  # noqa: E402
from btcts.prediction.market_regime.features import build_market_regime_feature_bundle  # noqa: E402
from btcts.prediction.market_regime.signal_scoring import (  # noqa: E402
    MARKET_REGIME_SIGNAL_SCORING_VERSION,
    score_market_regime_signals,
)
from btcts.prediction.market_regime.sources import build_market_regime_source_snapshot  # noqa: E402
from btcts.prediction.market_regime.tools.write_latest import build_market_regime_latest_artifact_set  # noqa: E402


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _fixture_root(root: Path) -> None:
    forecast_path = root / "prediction/runs/2026-07-08/101500/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-08T10:15:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-08/101500/forecast_records.jsonl"},
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
                "false_break_count": 2,
                "volatility_compression_score": 0.20,
                "volatility_expansion_score": 0.10
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


def _bundle(root: Path):
    snapshot = build_market_regime_source_snapshot(root)
    return build_market_regime_feature_bundle(snapshot, generated_at="2026-07-08T10:15:02Z")


def test_cp7_signal_scoring_builds_explainable_votes(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    report = score_market_regime_signals(_bundle(tmp_path))
    assert report["ok"] is True
    assert report["signal_scoring_version"] == MARKET_REGIME_SIGNAL_SCORING_VERSION
    assert report["horizon_count"] == 8
    current = report["horizons"][0]
    vote_ids = {vote["signal_id"] for vote in current["signal_votes_top_n"]}
    assert {"absorption_score", "depth_imbalance", "orderflow_imbalance"} <= vote_ids
    assert current["source_family_scores"][FeatureGroup.LIQUIDITY.value] > 0
    assert current["regime_scores"]["RANGE"] > 0
    assert report["broker_private_api_allowed"] is False
    assert report["autotrade_trigger_allowed"] is False


def test_cp7_horizon_weights_change_family_influence(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    report = score_market_regime_signals(_bundle(tmp_path))
    by_key = {row["horizon_key"]: row for row in report["horizons"]}
    assert by_key["current"]["source_family_weights_used"]["liquidity"] == 1.0
    assert by_key["86400s"]["source_family_weights_used"]["liquidity"] == 0.05
    assert by_key["current"]["source_family_scores"]["liquidity"] > by_key["86400s"]["source_family_scores"]["liquidity"]
    assert by_key["86400s"]["source_family_weights_used"]["cross_venue"] == 0.80


def test_cp7_write_latest_read_model_contains_signal_report(tmp_path: Path) -> None:
    _fixture_root(tmp_path)
    artifacts = build_market_regime_latest_artifact_set(
        hot_root=tmp_path,
        generated_at="2026-07-08T10:16:00Z",
        run_id="market_regime_cp7_test",
    )
    read_model = artifacts["latest_read_model"]
    assert read_model["source_contribution_summary"]["signal_score_report"]["signal_scoring_version"] == MARKET_REGIME_SIGNAL_SCORING_VERSION
    first = read_model["horizons"][0]
    assert first["signal_votes_top_n"]
    assert first["source_family_scores"]
    assert first["regime_scores"]
    assert artifacts["latest_cards"]["compact_summary"]["signal_scoring_version"] == MARKET_REGIME_SIGNAL_SCORING_VERSION
    assert artifacts["latest_cards"]["compact_summary"]["signal_votes_available"] is True
