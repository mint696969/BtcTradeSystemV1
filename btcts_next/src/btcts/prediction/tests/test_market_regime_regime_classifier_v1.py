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
    assert data["logic_version"] == "prediction.market_regime.regime_classifier.ps_q27j.v1"
    assert data["horizons_present_sec"] == [0, 300, 900, 1800, 3600, 21600, 43200, 86400]
    assert [item["horizon_label"] for item in data["predictions"]] == ["現在", "5分後", "15分後", "30分後", "60分後", "6時間後", "12時間後", "24時間後"]
    assert data["safety"]["read_only"] is True
    assert data["safety"]["would_send_to_broker"] is False


def test_q27j_range_candidate_maps_to_range_with_no_new_entry_on_negative_spread(tmp_path: Path) -> None:
    packet = _packet(tmp_path, label="range_candidate", spread=-1479.0)
    first = packet.predictions[0]
    assert first.regime_code == MarketRegimeCode.RANGE
    assert first.tactical_hint == TacticalHint.NO_NEW_ENTRY
    assert first.evidence_quality.value in {"PARTIAL", "WEAK"}
    assert "negative_spread_seen" in first.warnings
    assert first.confidence_percent >= 50
    assert first.safety.would_send_to_broker is False


def test_q27j_trend_candidate_maps_to_up_trend_when_spread_safe(tmp_path: Path) -> None:
    packet = _packet(tmp_path, label="trend_candidate", spread=1200.0)
    first = packet.predictions[0]
    assert first.regime_code == MarketRegimeCode.UP_TREND
    assert first.tactical_hint == TacticalHint.TREND_FOLLOW_WATCH
    assert "negative_spread_seen" not in first.warnings
    assert first.confidence_percent >= 60


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
    assert first.diagnostic_record["classifier_version"] == "prediction.market_regime.regime_classifier.ps_q27j.v1"
    assert first.diagnostic_record["source_snapshot_input_only"] is True
    assert first.diagnostic_record["execution_enabled"] is False
    assert first.diagnostic_record["runtime_write_requested"] is False


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
