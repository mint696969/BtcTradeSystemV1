# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_shadow_runtime_execution_once.py
# desc: MR-F9.14 guards for read-only one-shot preflight plus explicit observations to execution evidence JSON.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import build_market_regime_origin_feature_runtime_bundle
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.future_shadow_runtime_preflight_bridge import build_future_shadow_runtime_preflight_report
from btcts.prediction.market_regime.horizon_policy import build_default_horizon_policy
from btcts.prediction.market_regime.tools.shadow_runtime_execution_once import (
    build_shadow_runtime_execution_once_report,
    main,
)

CANDIDATE_ID = "market_regime.origin_feature.shadow.ma_5_20.interquartile.v1"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _rows() -> tuple[dict[str, object], ...]:
    start = datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc)
    return tuple({"time_utc": _iso(start + timedelta(minutes=index)), "close": 100.0 + index} for index in range(60))


def _bundle() -> MarketRegimeFeatureBundle:
    signals = (
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_generated_at", "2026-07-13T23:59:00Z", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 125.0, True),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 20.0, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "RANGE", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "session_context", "asia", True),
    )
    groups = (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.LIQUIDITY, FeatureGroup.SOURCE_QUALITY)
    return MarketRegimeFeatureBundle(
        generated_at="2026-07-14T00:00:00Z",
        signals=signals,
        coverage=tuple(SourceCoverage(group, True, FreshnessState.LIVE) for group in groups),
        source_snapshot_ok=True,
    )


def _report() -> dict[str, object]:
    return {"market_regime_only": True, "horizons": [
        {"horizon_sec": item.horizon_sec, "horizon_key": item.horizon_key, "regime_scores": {"RANGE": 0.8, "UP_TREND": 0.2}}
        for item in build_default_horizon_policy().horizons if item.horizon_sec
    ]}


def _preflight():
    bundle = _bundle()
    report = _report()
    epoch = datetime.fromisoformat(bundle.generated_at.replace("Z", "+00:00")).timestamp()
    packet = build_market_regime_future_shadow_packet(
        feature_bundle=bundle,
        signal_score_report=report,
        origin_current_state=MarketRegimeCode.RANGE,
        origin_timestamp_epoch_sec=epoch,
        source_timestamp_epoch_sec=epoch - 60.0,
    )
    runtime = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=bundle,
        previous_current_state={"regime_code": "DOWN_TREND"},
        canonical_current_l4_candle_rows=_rows(),
        shadow_candidate_id=CANDIDATE_ID,
    )
    return build_future_shadow_runtime_preflight_report(packet=packet, signal_score_report=report, runtime_bundle=runtime)


def _observation_payload(preflight=None):
    report = _preflight() if preflight is None else preflight
    rows = []
    for pair in report["pairs"]:
        for forecast in pair["forecasts"]:
            abstain = forecast["forecast_status"] == "ABSTAIN"
            rows.append({
                "trace_id": forecast["trace_id"],
                "prediction_origin": forecast["origin_timestamp"],
                "feature_snapshot_ref": forecast["feature_snapshot_ref"],
                "target_horizon_sec": forecast["target_horizon_sec"],
                "parameter_set_id": forecast["parameter_set_id"],
                "inference_mode": "ABSTAINED_WITHOUT_INFERENCE" if abstain else "FULL_INFERENCE",
                "raw_output_semantics": "UNSPECIFIED" if abstain else "SCORE",
                "source_freshness_state": "FRESH",
                "source_age_sec": 60.0,
                "fallback_reason": "",
                "fallback_source_ref": "",
            })
    return {"artifact_kind": "future_shadow_execution_observation_batch", "rows": rows}


def test_builds_execution_once_result_from_direct_preflight() -> None:
    preflight = _preflight()
    result = build_shadow_runtime_execution_once_report(
        preflight_payload=preflight,
        observation_payload=_observation_payload(preflight),
    )
    assert result["pair_count"] == 7
    assert result["trace_count"] == 14
    assert result["evidence_count"] == 14
    assert result["fact_build_report"]["trace_count"] == 14
    assert result["execution_report"]["evidence_count"] == 14
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False


def test_fact_dataclasses_are_converted_to_json_native_dicts() -> None:
    preflight = _preflight()
    result = build_shadow_runtime_execution_once_report(
        preflight_payload=preflight,
        observation_payload=_observation_payload(preflight),
    )
    facts = result["fact_build_report"]["facts_by_trace_id"]
    assert len(facts) == 14
    first = next(iter(facts.values()))
    assert isinstance(first, dict)
    assert first["inference_mode"] in {
        "FULL_INFERENCE",
        "ABSTAINED_WITHOUT_INFERENCE",
    }
    assert first["raw_output_semantics"] in {"SCORE", "UNSPECIFIED"}
    assert first["source_freshness_state"] == "FRESH"


def test_accepts_wrapped_mr_f8_once_result() -> None:
    preflight = _preflight()
    wrapped = {
        "artifact_kind": "mr_f8_runtime_preflight_once_result",
        "preflight_report": preflight,
    }
    result = build_shadow_runtime_execution_once_report(
        preflight_payload=wrapped,
        observation_payload=_observation_payload(preflight),
    )
    assert result["prediction_origin"] == preflight["prediction_origin"]
    assert result["feature_snapshot_ref"] == preflight["feature_snapshot_ref"]


def test_observation_kind_and_enum_values_fail_closed() -> None:
    preflight = _preflight()
    with pytest.raises(ValueError, match="observation_kind_invalid"):
        build_shadow_runtime_execution_once_report(
            preflight_payload=preflight,
            observation_payload={"artifact_kind": "wrong", "rows": []},
        )

    payload = _observation_payload(preflight)
    payload["rows"][0]["inference_mode"] = "UNKNOWN"
    with pytest.raises(ValueError, match="inference_mode_invalid"):
        build_shadow_runtime_execution_once_report(
            preflight_payload=preflight,
            observation_payload=payload,
        )


def test_explicit_identity_mismatch_is_rejected_by_fact_builder() -> None:
    preflight = _preflight()
    payload = _observation_payload(preflight)
    payload["rows"][0]["parameter_set_id"] = "candidate:tampered"
    with pytest.raises(ValueError, match="observation_identity_mismatch"):
        build_shadow_runtime_execution_once_report(
            preflight_payload=preflight,
            observation_payload=payload,
        )


def test_main_requires_preflight_acknowledgement() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--preflight-json", "a.json", "--observations-json", "b.json"])
    assert exc.value.code == 2


def test_result_is_json_native_and_never_enables_runtime_paths() -> None:
    preflight = _preflight()
    result = build_shadow_runtime_execution_once_report(
        preflight_payload=preflight,
        observation_payload=_observation_payload(preflight),
    )
    assert isinstance(result["fact_build_report"], dict)
    assert isinstance(result["execution_report"], dict)
    assert result["preflight_only"] is True
    assert result["writes_repository"] is False
    assert result["scheduler_enabled"] is False
    assert result["producer_loop_enabled"] is False
    assert result["broker_private_api_allowed"] is False
    assert result["autotrade_trigger_allowed"] is False
    assert result["order_submission_allowed"] is False
    assert result["auto_promotion_allowed"] is False
    assert result["live_parameter_apply_allowed"] is False
