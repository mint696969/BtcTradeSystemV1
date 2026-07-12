# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_regime_classifier_v1.py
# desc: PS-Q27J tests for pure market-regime classifier v1. Uses tmp_path snapshots only; no real D-hot access.

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime import FeatureGroup, MarketRegimeCode, TacticalHint  # noqa: E402
from btcts.prediction.market_regime.features import build_market_regime_feature_bundle  # noqa: E402
from btcts.prediction.market_regime.inference import classify_market_regime_feature_bundle  # noqa: E402
from btcts.prediction.market_regime.sources import build_market_regime_source_snapshot  # noqa: E402


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n", encoding="utf-8")


def _build_fixture(root: Path, *, label: str = "range_candidate", spread: float = -1479.0) -> None:
    forecast_path = root / "prediction/runs/2026-07-01/171500/forecast_records.jsonl"
    _write_json(root / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:15:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/171500/forecast_records.jsonl"},
    })
    _write_json(root / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "horizon_sec": 300, "primary_label": label, "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 21600, "primary_label": label, "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(root / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9727585.0,
        "last_spread": spread,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(root / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(root / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})


def _packet(root: Path, *, label: str = "range_candidate", spread: float = -1479.0):
    _build_fixture(root, label=label, spread=spread)
    snapshot = build_market_regime_source_snapshot(root)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-01T17:15:02Z")
    return classify_market_regime_feature_bundle(bundle, generated_at="2026-07-01T17:15:03Z")


def test_q27j_classifier_emits_all_canonical_horizons(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    data = packet.to_dict()
    assert data["logic_version"] == "prediction.market_regime.regime_classifier.ps_q27z.v3"
    assert data["horizons_present_sec"] == [0, 300, 900, 1800, 3600, 21600, 43200, 86400]
    assert [item["horizon_label"] for item in data["predictions"]] == ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]
    assert data["safety"]["read_only"] is True
    assert data["safety"]["would_send_to_broker"] is False


def test_q27j_range_candidate_maps_to_range_with_no_new_entry_on_negative_spread(tmp_path: Path) -> None:
    packet = _packet(tmp_path, label="range_candidate", spread=-1479.0)
    by_horizon = {row.horizon_sec: row for row in packet.predictions}
    current = by_horizon[0]
    forecast = by_horizon[300]
    assert current.regime_code == MarketRegimeCode.UNKNOWN
    assert current.diagnostic_record["future_forecast_label_used_for_current"] is False
    assert forecast.regime_code == MarketRegimeCode.RANGE
    assert forecast.tactical_hint == TacticalHint.NO_NEW_ENTRY
    assert forecast.evidence_quality.value in {"PARTIAL", "WEAK"}
    assert "negative_spread_seen" in forecast.warnings
    assert forecast.confidence_percent >= 50
    assert forecast.safety.would_send_to_broker is False


def test_q27j_trend_candidate_maps_to_up_trend_when_spread_safe(tmp_path: Path) -> None:
    packet = _packet(tmp_path, label="trend_candidate", spread=1200.0)
    by_horizon = {row.horizon_sec: row for row in packet.predictions}
    current = by_horizon[0]
    forecast = by_horizon[300]
    assert current.regime_code == MarketRegimeCode.UNKNOWN
    assert current.diagnostic_record["future_forecast_label_used_for_current"] is False
    assert forecast.regime_code == MarketRegimeCode.UP_TREND
    assert forecast.tactical_hint == TacticalHint.TREND_FOLLOW_WATCH
    assert "negative_spread_seen" not in forecast.warnings
    assert forecast.confidence_percent >= 60


def test_q27j_missing_sources_degrade_to_unknown_without_exception(tmp_path: Path) -> None:
    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-01T17:15:02Z")
    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-01T17:15:03Z")
    assert packet.predictions
    assert {prediction.regime_code for prediction in packet.predictions} == {MarketRegimeCode.UNKNOWN}
    assert {prediction.tactical_hint for prediction in packet.predictions} == {TacticalHint.UNKNOWN_HOLD}
    assert "latest_manifest" in packet.missing_sources
    assert "source_snapshot_not_ok" in packet.warnings


def test_q27j_packet_preserves_feature_coverage_and_diagnostics(tmp_path: Path) -> None:
    packet = _packet(tmp_path, label="range_candidate", spread=1200.0)
    assert {coverage.feature_group for coverage in packet.source_coverage} >= {FeatureGroup.PRICE_STRUCTURE, FeatureGroup.LIQUIDITY, FeatureGroup.SOURCE_QUALITY}
    first = packet.predictions[0]
    assert first.diagnostic_record["classifier_version"] == "prediction.market_regime.regime_classifier.ps_q27z.v3"
    assert first.diagnostic_record["source_snapshot_input_only"] is True
    assert first.diagnostic_record["execution_enabled"] is False
    assert first.diagnostic_record["runtime_write_requested"] is False


def test_q27w_classifier_uses_horizon_specific_forecast_labels(tmp_path: Path) -> None:
    forecast_path = tmp_path / "prediction/runs/2026-07-01/172500/forecast_records.jsonl"
    _write_json(tmp_path / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:25:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/172500/forecast_records.jsonl"},
    })
    _write_json(tmp_path / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "horizon_sec": 300, "primary_label": "trend_candidate", "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 900, "primary_label": "range_candidate", "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
        {"family": "market_regime", "horizon_sec": 21600, "primary_label": "breakout_candidate", "values": {"volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9730264.0,
        "last_spread": 1200.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(tmp_path / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})

    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-01T17:25:02Z")
    price_signals = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.PRICE_STRUCTURE)}
    assert price_signals["market_regime_labels_by_horizon_sec"].value == {
        "300": "trend_candidate",
        "900": "range_candidate",
        "21600": "breakout_candidate",
    }

    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-01T17:25:03Z")
    by_horizon = {prediction.horizon_sec: prediction for prediction in packet.predictions}
    assert by_horizon[0].regime_code == MarketRegimeCode.UNKNOWN
    assert by_horizon[0].diagnostic_record["label_selection_reason"] == "current_state_estimator_unavailable"
    assert by_horizon[0].diagnostic_record["future_forecast_label_used_for_current"] is False
    assert by_horizon[300].regime_code == MarketRegimeCode.UP_TREND
    assert by_horizon[300].diagnostic_record["selected_forecast_horizon_sec"] == 300
    assert by_horizon[900].regime_code == MarketRegimeCode.RANGE
    assert by_horizon[900].diagnostic_record["selected_forecast_horizon_sec"] == 900
    assert by_horizon[21600].regime_code == MarketRegimeCode.BREAKOUT
    assert by_horizon[21600].diagnostic_record["selected_forecast_label"] == "breakout_candidate"
    missing_horizon = by_horizon[1800]
    assert missing_horizon.regime_code == MarketRegimeCode.UNKNOWN
    assert missing_horizon.confidence_percent == 15
    assert missing_horizon.freshness_state.value == "STALE"
    assert missing_horizon.evidence_quality.value == "MISSING"
    assert missing_horizon.diagnostic_record["selected_label"] == ""
    assert missing_horizon.diagnostic_record["selected_label_source"] == "none"
    assert missing_horizon.diagnostic_record["label_selection_reason"] == "forecast_horizon_label_missing"
    assert all(prediction.diagnostic_record["horizon_specific_classifier"] is True for prediction in packet.predictions)


def test_q27y_classifier_calibrates_confidence_from_selected_forecast_metrics(tmp_path: Path) -> None:
    forecast_path = tmp_path / "prediction/runs/2026-07-01/173500/forecast_records.jsonl"
    _write_json(tmp_path / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:35:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/173500/forecast_records.jsonl"},
    })
    _write_json(tmp_path / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {
            "family": "market_regime",
            "horizon_sec": 300,
            "primary_label": "range_candidate",
            "score": 0.20,
            "values_snapshot": {"estimated_signal_strength_percent": 20, "estimated_reference_hit_rate_percent": 30, "volatility_state": "normal", "cross_venue_agreement": "aligned"},
        },
        {
            "family": "market_regime",
            "horizon_sec": 900,
            "primary_label": "range_candidate",
            "score": 0.90,
            "values_snapshot": {"estimated_signal_strength_percent": 85, "estimated_reference_hit_rate_percent": 80, "volatility_state": "normal", "cross_venue_agreement": "aligned"},
        },
    ])
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9730264.0,
        "last_spread": 1200.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(tmp_path / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})

    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-01T17:35:02Z")
    price_signals = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.PRICE_STRUCTURE)}
    assert price_signals["market_regime_scores_by_horizon_sec"].value == {"300": 0.2, "900": 0.9}
    assert price_signals["market_regime_signal_strength_percent_by_horizon_sec"].value == {"300": 20.0, "900": 85.0}
    assert price_signals["market_regime_reference_hit_rate_percent_by_horizon_sec"].value == {"300": 30.0, "900": 80.0}

    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-01T17:35:03Z")
    by_horizon = {prediction.horizon_sec: prediction for prediction in packet.predictions}
    assert by_horizon[300].confidence_percent < by_horizon[900].confidence_percent
    assert by_horizon[0].confidence_percent == 15
    assert by_horizon[0].diagnostic_record["future_forecast_label_used_for_current"] is False
    assert by_horizon[300].diagnostic_record["selected_forecast_score"] == 0.2
    assert by_horizon[900].diagnostic_record["selected_signal_strength_percent"] == 85.0
    assert by_horizon[900].diagnostic_record["selected_reference_hit_rate_percent"] == 80.0
    assert by_horizon[300].diagnostic_record["confidence_calibrated_from_forecast_metric"] is True
    assert packet.logic_version == "prediction.market_regime.regime_classifier.ps_q27z.v3"


def test_q27z_classifier_calibrates_evidence_quality_from_selected_forecast_metrics(tmp_path: Path) -> None:
    forecast_path = tmp_path / "prediction/runs/2026-07-01/174000/forecast_records.jsonl"
    _write_json(tmp_path / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:40:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/174000/forecast_records.jsonl"},
    })
    _write_json(tmp_path / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {
            "family": "market_regime",
            "horizon_sec": 300,
            "primary_label": "range_candidate",
            "score": 0.20,
            "values_snapshot": {"estimated_signal_strength_percent": 20, "estimated_reference_hit_rate_percent": 30, "volatility_state": "normal", "cross_venue_agreement": "aligned"},
        },
        {
            "family": "market_regime",
            "horizon_sec": 900,
            "primary_label": "range_candidate",
            "score": 0.92,
            "values_snapshot": {"estimated_signal_strength_percent": 90, "estimated_reference_hit_rate_percent": 85, "volatility_state": "normal", "cross_venue_agreement": "aligned"},
        },
    ])
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9730264.0,
        "last_spread": 1200.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(tmp_path / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})

    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-01T17:40:02Z")
    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-01T17:40:03Z")
    by_horizon = {prediction.horizon_sec: prediction for prediction in packet.predictions}
    assert by_horizon[300].evidence_quality.value == "WEAK"
    assert by_horizon[900].evidence_quality.value == "STRONG"
    assert by_horizon[300].diagnostic_record["selected_evidence_quality_reason"] == "forecast_metric_weak"
    assert by_horizon[900].diagnostic_record["selected_evidence_quality_reason"] == "forecast_metric_strong"
    assert by_horizon[900].diagnostic_record["evidence_quality_calibrated_from_forecast_metric"] is True
    assert packet.logic_version == "prediction.market_regime.regime_classifier.ps_q27z.v3"


def test_q27j_classifier_safety_flags_remain_false(tmp_path: Path) -> None:
    packet = _packet(tmp_path)
    safety = packet.to_dict()["safety"]
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


def test_q27j_inference_modules_do_not_import_ui_or_runtime_paths() -> None:
    package_root = Path(__file__).resolve().parents[1] / "market_regime"
    forbidden = ("import streamlit", "from streamlit", "runtime_root(", "send_to_broker(", "append_ledger(", "ledger.append(", "open(\"D:")
    for path in list((package_root / "inference").glob("*.py")):
        text = path.read_text(encoding="utf-8-sig")
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_mr_a1_stale_forecast_records_are_blocked_by_currentness_gate(tmp_path: Path) -> None:
    forecast_path = tmp_path / "prediction/runs/2026-07-01/171500/forecast_records.jsonl"
    _write_json(tmp_path / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:15:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/171500/forecast_records.jsonl"},
    })
    _write_json(tmp_path / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "generated_at": "2026-07-01T17:15:00Z", "horizon_sec": 300, "primary_label": "trend_candidate", "score": 0.95, "values_snapshot": {"estimated_signal_strength_percent": 95, "estimated_reference_hit_rate_percent": 90, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 9729064.0,
        "last_best_ask": 9730264.0,
        "last_spread": 1200.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(tmp_path / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})

    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-08T17:15:02Z")
    source_quality = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.SOURCE_QUALITY)}
    assert source_quality["forecast_records_current_enough"].value is False
    assert "forecast_records_stale" in bundle.warnings
    coverage_by_group = {coverage.feature_group: coverage for coverage in bundle.coverage}
    assert coverage_by_group[FeatureGroup.PRICE_STRUCTURE].freshness_state.value == "STALE"
    assert coverage_by_group[FeatureGroup.VOLATILITY].freshness_state.value == "STALE"
    assert coverage_by_group[FeatureGroup.CROSS_VENUE].freshness_state.value == "STALE"

    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-08T17:15:03Z")
    first = packet.predictions[0]
    assert first.regime_code == MarketRegimeCode.UNKNOWN
    assert first.freshness_state.value == "STALE"
    assert first.confidence_percent == 15
    assert "forecast_records_stale" in first.warnings
    assert first.diagnostic_record["forecast_records_currentness_gate_applied"] is True
    assert first.diagnostic_record["selected_forecast_label"] == ""
    assert first.diagnostic_record["label_selection_reason"] == "current_state_estimator_unavailable"
    assert first.diagnostic_record["future_forecast_label_used_for_current"] is False
    price = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.PRICE_STRUCTURE)}
    # MR_A4_COVERAGE_IGNORES_THRESHOLD_METADATA_2026_07_09
    # Threshold metadata may be present without a live current-L4 candle window.
    assert "current_l4_candle_threshold_set_id" in price
    assert price["current_l4_candle_threshold_set_id"].available is True
    assert price["current_l4_candle_window_available"].value is False
    assert coverage_by_group[FeatureGroup.PRICE_STRUCTURE].freshness_state.value == "STALE"


def _write_warroom_candles(root: Path, rows: list[dict]) -> None:
    base = root / "data/derived/warroom/candles/exchange=bitflyer/symbol=FX_BTC_JPY/timeframe=60s"
    base.mkdir(parents=True, exist_ok=True)
    (base / "closed.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n", encoding="utf-8")
    forming = dict(rows[-1])
    forming["candle_status"] = "forming"
    (base / "forming.json").write_text(json.dumps(forming, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (base / "meta.json").write_text(json.dumps({"ok": True, "timeframe_sec": 60, "closed_count": len(rows), "end_ts_utc": rows[-1]["time_utc"], "read_only_source": True, "broker_send_enabled": False}, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def test_mr_a2_stale_forecast_can_fallback_to_current_l4_candle_window(tmp_path: Path) -> None:
    forecast_path = tmp_path / "prediction/runs/2026-07-01/171500/forecast_records.jsonl"
    _write_json(tmp_path / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:15:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": "prediction/runs/2026-07-01/171500/forecast_records.jsonl"},
    })
    _write_json(tmp_path / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "generated_at": "2026-07-01T17:15:00Z", "horizon_sec": 300, "primary_label": "range_candidate", "score": 0.95, "values_snapshot": {"estimated_signal_strength_percent": 95, "estimated_reference_hit_rate_percent": 90, "volatility_state": "normal", "cross_venue_agreement": "aligned"}},
    ])
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 10000000.0,
        "last_best_ask": 10001000.0,
        "last_spread": 1000.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(tmp_path / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE", "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 20450, "read_only": True, "would_send_to_broker": False})
    _write_json(tmp_path / "state/collector_vnext/unified_daemon_status.json", {"read_only": True, "would_send_to_broker": False})
    _write_warroom_candles(tmp_path, [
        {"time": 1783539000, "time_utc": "2026-07-08T19:30:00Z", "open": 100.0, "high": 101.0, "low": 99.8, "close": 100.5, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60, "candle_status": "closed"},
        {"time": 1783539060, "time_utc": "2026-07-08T19:31:00Z", "open": 100.5, "high": 103.0, "low": 100.4, "close": 102.8, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60, "candle_status": "closed"},
        {"time": 1783539120, "time_utc": "2026-07-08T19:32:00Z", "open": 102.8, "high": 105.0, "low": 102.7, "close": 104.9, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60, "candle_status": "closed"},
    ])

    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-08T19:32:30Z")
    source_quality = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.SOURCE_QUALITY)}
    price = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.PRICE_STRUCTURE)}
    assert source_quality["forecast_records_current_enough"].value is False
    assert source_quality["current_l4_candle_window_current_enough"].value is True
    assert price["current_l4_candle_regime_hint"].value == "UP_TREND"

    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-08T19:32:31Z")
    first = packet.predictions[0]
    assert first.regime_code == MarketRegimeCode.UP_TREND
    assert first.freshness_state.value == "LIVE"
    assert 35 < first.confidence_percent <= 65
    assert first.evidence_quality.value == "PARTIAL"
    assert first.diagnostic_record["selected_evidence_quality_reason"] == "current_l4_fallback_uncalibrated_partial"
    coverage_by_group = {coverage.feature_group: coverage for coverage in bundle.coverage}
    assert coverage_by_group[FeatureGroup.PRICE_STRUCTURE].freshness_state.value == "LIVE"
    assert coverage_by_group[FeatureGroup.VOLATILITY].freshness_state.value == "LIVE"
    assert source_quality["current_l4_candle_window_current_enough"].value is True
    assert first.diagnostic_record["forecast_records_currentness_gate_applied"] is True
    assert first.diagnostic_record["current_l4_candle_window_current_enough"] is True
    assert first.diagnostic_record["current_l4_candle_window_fallback_used"] is False
    assert first.diagnostic_record["current_state_estimator_used"] is True
    assert first.diagnostic_record["label_selection_reason"] == "mr_f4_transition_policy"
    assert first.diagnostic_record["current_state_canonical_selection_reason"].startswith(
        "mr_f4_transition_policy_"
    )
    assert first.diagnostic_record["selected_label"] == "UP_TREND"
    assert first.diagnostic_record["selected_label_source"] == "current_state_estimator"
    assert first.diagnostic_record["selected_forecast_label"] == ""
    assert first.diagnostic_record["selected_l4_candle_regime_hint"] == "UP_TREND"
    evidence = first.diagnostic_record["current_l4_candle_evidence"]
    assert evidence["raw_candle_payload_included"] is False
    assert evidence["window_current_enough"] is True
    assert evidence["window_available"] is True
    assert evidence["regime_hint"] == "UP_TREND"
    assert evidence["net_change_bps"] > 0
    assert evidence["range_bps"] > 0
    assert evidence["realized_volatility_bps"] is not None
    assert evidence["source_refs"]

def test_mr_vs4_stale_forecast_and_stale_l4_ignore_negative_spread_for_regime(tmp_path: Path) -> None:
    _build_fixture(tmp_path, label="trend_candidate", spread=-1479.0)
    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(
        snapshot, generated_at="2026-07-10T09:15:00Z"
    )

    packet = classify_market_regime_feature_bundle(
        bundle, generated_at="2026-07-10T09:15:01Z"
    )

    assert {prediction.regime_code for prediction in packet.predictions} == {
        MarketRegimeCode.UNKNOWN
    }
    assert {prediction.confidence_percent for prediction in packet.predictions} == {15}
    assert {prediction.freshness_state.value for prediction in packet.predictions} == {
        "STALE"
    }
    assert {prediction.tactical_hint for prediction in packet.predictions} == {
        TacticalHint.NO_NEW_ENTRY
    }
    for prediction in packet.predictions:
        assert "negative_spread_seen" in prediction.warnings
        assert prediction.diagnostic_record["selected_label"] == ""
        expected_reason = (
            "current_state_estimator_unavailable"
            if prediction.horizon_sec == 0
            else "forecast_records_stale_blocked"
        )
        assert prediction.diagnostic_record["label_selection_reason"] == expected_reason
        assert prediction.diagnostic_record["forecast_records_current_enough"] is False
        assert (
            prediction.diagnostic_record["current_l4_candle_window_current_enough"]
            is False
        )

def test_mr_vs4_fresh_l4_is_live_only_for_applicable_short_horizons(tmp_path: Path) -> None:
    forecast_path = tmp_path / "prediction/runs/2026-07-01/171500/forecast_records.jsonl"
    _write_json(tmp_path / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-01T17:15:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": str(forecast_path.relative_to(tmp_path)).replace("\\", "/")},
    })
    _write_json(tmp_path / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {"family": "market_regime", "generated_at": "2026-07-01T17:15:00Z", "horizon_sec": 300, "primary_label": "range_candidate"},
    ])
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY", "last_best_bid": 10000000.0,
        "last_best_ask": 10001000.0, "last_spread": 1000.0,
        "read_only": True, "would_send_to_broker": False,
    })
    _write_json(tmp_path / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE"})
    _write_json(tmp_path / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 10})
    _write_json(tmp_path / "state/collector_vnext/unified_daemon_status.json", {"read_only": True})
    _write_warroom_candles(tmp_path, [
        {"time": 1783539000, "time_utc": "2026-07-08T19:30:00Z", "open": 100.0, "high": 101.0, "low": 99.8, "close": 100.5, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60, "candle_status": "closed"},
        {"time": 1783539060, "time_utc": "2026-07-08T19:31:00Z", "open": 100.5, "high": 103.0, "low": 100.4, "close": 102.8, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60, "candle_status": "closed"},
        {"time": 1783539120, "time_utc": "2026-07-08T19:32:00Z", "open": 102.8, "high": 105.0, "low": 102.7, "close": 104.9, "volume": 1.0, "trade_count": 10, "timeframe_sec": 60, "candle_status": "closed"},
    ])

    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-08T19:32:30Z")
    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-08T19:32:31Z")
    by_horizon = {row.horizon_sec: row for row in packet.predictions}

    current = by_horizon[0]
    assert current.freshness_state.value == "LIVE"
    assert current.regime_code != MarketRegimeCode.UNKNOWN
    assert current.evidence_quality.value in {"PARTIAL", "WEAK"}
    assert "current_state_estimator_used" in current.warnings
    assert "current_l4_candle_window_fallback_used" not in current.warnings

    for horizon_sec in (300, 900, 1800, 3600):
        row = by_horizon[horizon_sec]
        assert row.freshness_state.value == "LIVE"
        assert row.regime_code != MarketRegimeCode.UNKNOWN
        assert row.evidence_quality.value in {"PARTIAL", "WEAK"}
        assert "current_l4_candle_window_fallback_used" in row.warnings

    for horizon_sec in (21600, 43200, 86400):
        row = by_horizon[horizon_sec]
        assert row.regime_code == MarketRegimeCode.UNKNOWN
        assert row.confidence_percent == 15
        assert row.freshness_state.value == "STALE"
        assert row.evidence_quality.value == "MISSING"
        assert row.diagnostic_record["selected_evidence_quality_reason"] == "no_current_evidence_for_horizon"
        assert "current_l4_candle_window_fallback_used" not in row.warnings
        assert "current_l4_candle_window_not_applicable_to_horizon" in row.warnings

def test_mr_vs4_missing_exact_forecast_horizon_fails_closed_without_cross_horizon_label_reuse(tmp_path: Path) -> None:
    forecast_path = tmp_path / "prediction/runs/2026-07-10/120000/forecast_records.jsonl"
    _write_json(tmp_path / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-10T12:00:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": str(forecast_path.relative_to(tmp_path)).replace("\\", "/")},
    })
    _write_json(tmp_path / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {
            "family": "market_regime",
            "generated_at": "2026-07-10T12:00:00Z",
            "horizon_sec": 300,
            "primary_label": "range_candidate",
        },
    ])
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 10000000.0,
        "last_best_ask": 10001000.0,
        "last_spread": 1000.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(tmp_path / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE"})
    _write_json(tmp_path / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 10})
    _write_json(tmp_path / "state/collector_vnext/unified_daemon_status.json", {"read_only": True})

    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-10T12:00:30Z")
    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-10T12:00:31Z")
    by_horizon = {row.horizon_sec: row for row in packet.predictions}

    assert by_horizon[0].regime_code == MarketRegimeCode.UNKNOWN
    assert by_horizon[0].freshness_state.value == "STALE"
    assert by_horizon[0].diagnostic_record["label_selection_reason"] == "current_state_estimator_unavailable"
    assert by_horizon[0].diagnostic_record["future_forecast_label_used_for_current"] is False
    assert by_horizon[300].regime_code == MarketRegimeCode.RANGE
    assert by_horizon[300].freshness_state.value == "LIVE"

    for horizon_sec in (900, 1800, 3600, 21600, 43200, 86400):
        row = by_horizon[horizon_sec]
        assert row.regime_code == MarketRegimeCode.UNKNOWN
        assert row.confidence_percent == 15
        assert row.freshness_state.value == "STALE"
        assert row.evidence_quality.value == "MISSING"
        assert row.diagnostic_record["selected_label"] == ""
        assert row.diagnostic_record["selected_label_source"] == "none"
        assert row.diagnostic_record["label_selection_reason"] == "forecast_horizon_label_missing"

def test_mr_vs4_blocked_forecast_record_is_not_accepted_as_horizon_label(tmp_path: Path) -> None:
    forecast_path = tmp_path / "prediction/runs/2026-07-10/120000/forecast_records.jsonl"
    _write_json(tmp_path / "prediction/latest_manifest.json", {
        "generated_at": "2026-07-10T12:00:00Z",
        "legacy_latest_path": "prediction/latest_prediction_system_result.json",
        "sidecars": {"forecast_records": str(forecast_path.relative_to(tmp_path)).replace("\\", "/")},
    })
    _write_json(tmp_path / "prediction/latest_prediction_system_result.json", {"read_only": True, "non_executing": True})
    _write_jsonl(forecast_path, [
        {
            "family": "market_regime",
            "generated_at": "2026-07-10T12:00:00Z",
            "horizon_sec": 21600,
            "primary_label": "range_candidate",
            "confidence": "unknown",
            "score": None,
            "usable": False,
            "blockers": ["insufficient_exact_horizon_candles"],
            "values_snapshot": {
                "technical_candle_count": 1,
                "technical_source_id": "ohlcv_6h",
            },
        },
    ])
    _write_json(tmp_path / "state/collector_vnext/unified_market_state_status.json", {
        "last_symbol_raw": "FX_BTC_JPY",
        "last_best_bid": 10000000.0,
        "last_best_ask": 10001000.0,
        "last_spread": 1000.0,
        "read_only": True,
        "would_send_to_broker": False,
    })
    _write_json(tmp_path / "state/collector_vnext/unified_health.json", {"ok": True, "ws_state": "LIVE"})
    _write_json(tmp_path / "state/collector_vnext/unified_executions_status.json", {"ws_state": "LIVE", "trade_count": 10})
    _write_json(tmp_path / "state/collector_vnext/unified_daemon_status.json", {"read_only": True})

    snapshot = build_market_regime_source_snapshot(tmp_path)
    bundle = build_market_regime_feature_bundle(snapshot, generated_at="2026-07-10T12:00:30Z")
    price_signals = {signal.name: signal for signal in bundle.signals_by_group(FeatureGroup.PRICE_STRUCTURE)}
    assert price_signals["market_regime_record_count"].value == 1
    assert price_signals["market_regime_usable_record_count"].value == 0
    assert price_signals["market_regime_labels_by_horizon_sec"].value == {}

    packet = classify_market_regime_feature_bundle(bundle, generated_at="2026-07-10T12:00:31Z")
    row = {prediction.horizon_sec: prediction for prediction in packet.predictions}[21600]
    assert row.regime_code == MarketRegimeCode.UNKNOWN
    assert row.confidence_percent == 15
    assert row.freshness_state.value == "STALE"
    assert row.evidence_quality.value == "MISSING"
    assert row.diagnostic_record["label_selection_reason"] == "forecast_horizon_label_missing"

def test_mr_f3_current_diagnostic_surfaces_observed_and_eligible_rankings(tmp_path: Path) -> None:
    packet = _packet(tmp_path, label="range_candidate", spread=1200.0)
    current = next(row for row in packet.predictions if row.horizon_sec == 0)
    diagnostic = current.diagnostic_record
    assert "current_state_eligible_top_candidate" in diagnostic
    assert "current_state_eligible_top_candidate_score" in diagnostic
    assert "current_state_eligible_runner_up_candidate" in diagnostic
    assert "current_state_eligible_candidate_score_margin" in diagnostic
    assert "current_state_label_selection_eligible_candidates" in diagnostic
    assert "current_state_label_selection_ineligible_candidates" in diagnostic
    assert "current_state_label_selection_readiness_blockers" in diagnostic
    assert diagnostic["current_state_scoring_label_selection_enabled"] is False
    assert "current_state_shadow_recommended_regime_code" in diagnostic
    assert diagnostic["current_state_shadow_recommendation_enabled"] is False
    assert diagnostic["current_state_shadow_recommendation_applied_to_selected_label"] is False
    assert "current_state_canonical_selection_reason" in diagnostic
    assert "current_state_transition_policy_canonical_application_enabled" in diagnostic
    assert "current_state_transition_policy_applied_to_selected_label" in diagnostic
    assert "current_state_transition_policy_legacy_fallback_used" in diagnostic
    assert "current_state_transition_policy_previous_regime_held" in diagnostic
    assert "current_state_shadow_transition_policy_version" in diagnostic
    assert "current_state_shadow_transition_decision" in diagnostic
    assert isinstance(diagnostic["current_state_shadow_transition_blockers"], list)
    assert diagnostic["current_state_shadow_transition_observation_only"] is True
    assert diagnostic["current_state_shadow_transition_applied_to_selected_label"] is False
    assert diagnostic["future_forecast_label_used_for_current"] is False
