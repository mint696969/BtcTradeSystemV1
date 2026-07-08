# path: ./btcts_next/src/btcts/prediction/tests/test_market_regime_latest_artifact_contract.py
# desc: CP3 tests for market-regime latest artifact contracts. Pure contracts only; no UI render, filesystem write, scheduler, broker, or AutoTrade behavior.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.prediction.market_regime import (  # noqa: E402
    EvidenceQuality,
    FreshnessState,
    MarketRegimeCode,
    MarketRegimePrediction,
    MarketRegimePredictionPacket,
    TacticalHint,
)
from btcts.prediction.market_regime.artifact_contracts import (  # noqa: E402
    LATEST_CARDS_JSON_RELPATH,
    LATEST_JSON_RELPATH,
    LATEST_READ_MODEL_JSON_RELPATH,
    MARKET_REGIME_LATEST_CARDS_SCHEMA_VERSION,
    STATUS_JSON_RELPATH,
    artifact_relative_paths,
    build_market_regime_latest_artifact,
    build_market_regime_latest_cards_artifact,
    build_market_regime_latest_read_model_artifact,
    build_market_regime_run_manifest_artifact,
    build_market_regime_status_artifact,
    validate_market_regime_latest_cards_artifact,
)


def _prediction_packet() -> MarketRegimePredictionPacket:
    prediction = MarketRegimePrediction(
        horizon_label="15分後",
        horizon_sec=900,
        regime_code=MarketRegimeCode.RANGE,
        confidence_percent=70,
        evidence_quality=EvidenceQuality.PARTIAL,
        freshness_state=FreshnessState.LIVE,
        tactical_hint=TacticalHint.RANGE_TACTIC,
        drivers=("price_in_range", "mean_reversion_to_vwap"),
        warnings=("sell_pressure_conflict",),
        invalidation_hints=("range_low_break_with_volume",),
        parameter_set_id="market_regime.pset.test.v1",
    )
    return MarketRegimePredictionPacket(
        generated_at="2026-07-08T08:30:00Z",
        predictions=(prediction,),
        parameter_set_id="market_regime.pset.test.v1",
    )


def _card() -> dict:
    return {
        "horizon": "15分後",
        "regime_code": "RANGE",
        "regime_label": "レンジ",
        "confidence_percent": 70,
        "freshness_badge": "LIVE",
        "evidence_quality": "PARTIAL",
        "short_tag_label": "方向感なし",
        "detail": {
            "reason_lines": ["price_in_range", "mean_reversion_to_vwap"],
            "warning_lines": ["sell_pressure_conflict"],
            "source_lines": ["candle_structure", "trend_structure"],
        },
    }


def test_cp3_artifact_relative_paths_are_stable() -> None:
    paths = artifact_relative_paths()
    assert paths["latest_json"] == LATEST_JSON_RELPATH == "prediction/market_regime/latest.json"
    assert paths["latest_cards_json"] == LATEST_CARDS_JSON_RELPATH == "prediction/market_regime/latest_cards.json"
    assert paths["latest_read_model_json"] == LATEST_READ_MODEL_JSON_RELPATH == "prediction/market_regime/latest_read_model.json"
    assert paths["status_json"] == STATUS_JSON_RELPATH == "prediction/market_regime/status.json"


def test_cp3_latest_cards_artifact_contract_validates_fixture() -> None:
    artifact = build_market_regime_latest_cards_artifact(
        generated_at="2026-07-08T08:30:00Z",
        run_id="market_regime_20260708T083000Z_test",
        prediction_id="prediction_test_001",
        parameter_set_id="market_regime.pset.test.v1",
        cards=[_card()],
        source_refs={"candles": {"relpath": "data/derived/warroom/plain_candles/latest.jsonl", "start_ts": "2026-07-08T08:15:00Z", "end_ts": "2026-07-08T08:30:00Z"}},
        compact_summary={"top_driver": "price_in_range"},
    )
    assert artifact["schema_version"] == MARKET_REGIME_LATEST_CARDS_SCHEMA_VERSION
    assert artifact["artifact_kind"] == "latest_cards"
    assert artifact["prediction_family_id"] == "market_regime"
    assert artifact["horizon_count"] == 1
    assert artifact["cards"][0]["confidence_percent"] == 70
    assert artifact["source_refs"]["candles"]["relpath"].endswith("latest.jsonl")
    result = validate_market_regime_latest_cards_artifact(artifact)
    assert result == {"ok": True, "validator_version": result["validator_version"], "failure_count": 0, "failures": [], "card_count": 1}


def test_cp3_latest_cards_validation_rejects_raw_payload_and_unsafe_flags() -> None:
    artifact = build_market_regime_latest_cards_artifact(
        generated_at="2026-07-08T08:30:00Z",
        run_id="market_regime_20260708T083000Z_test",
        cards=[_card()],
    )
    artifact["raw_orderbook"] = {"bids": []}
    artifact["safety"]["broker_private_api_allowed"] = True
    result = validate_market_regime_latest_cards_artifact(artifact)
    assert result["ok"] is False
    assert "forbidden_raw_payload_key_present" in result["failures"]
    assert "safety_broker_private_api_allowed_not_false" in result["failures"]


def test_cp3_latest_and_read_model_and_status_are_non_executing() -> None:
    packet = _prediction_packet()
    latest = build_market_regime_latest_artifact(packet=packet, run_id="market_regime_20260708T083000Z_test")
    read_model = build_market_regime_latest_read_model_artifact(
        generated_at=packet.generated_at,
        run_id="market_regime_20260708T083000Z_test",
        horizons=[{"horizon": "15分後", "drivers": ["price_in_range"], "conflicts": ["sell_pressure_conflict"], "invalidation": ["range_low_break_with_volume"]}],
    )
    status = build_market_regime_status_artifact(generated_at=packet.generated_at, status="latest_ready", latest_run_id="market_regime_20260708T083000Z_test")
    manifest = build_market_regime_run_manifest_artifact(generated_at=packet.generated_at, run_id="market_regime_20260708T083000Z_test")

    for artifact in (latest, read_model, status, manifest):
        assert artifact["prediction_family_id"] == "market_regime"
        assert artifact["safety"]["read_only"] is True
        assert artifact["safety"]["broker_private_api_allowed"] is False
        assert artifact["safety"]["autotrade_trigger_allowed"] is False
        assert artifact["safety"]["ledger_append_allowed"] is False
        assert artifact["safety"]["would_send_to_broker"] is False

    assert latest["refs"]["latest_cards_json"] == "prediction/market_regime/latest_cards.json"
    assert "not win rate" in read_model["explanation_note"]
    assert status["latest_cards_available"] is True
    assert manifest["refs"]["status_json"] == "prediction/market_regime/status.json"
