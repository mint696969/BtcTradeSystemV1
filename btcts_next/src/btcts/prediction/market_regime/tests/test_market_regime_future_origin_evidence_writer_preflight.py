# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_writer_preflight.py
# desc: MR-F6.16 tests for explicit-candidate single-origin writer preflight without writes.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_origin_evidence_writer import build_origin_evidence_approval
from btcts.prediction.market_regime.future_origin_evidence_writer_preflight import build_origin_evidence_writer_preflight
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import build_market_regime_origin_feature_runtime_bundle
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.horizon_policy import build_default_horizon_policy

CANDIDATE_ID = "market_regime.origin_feature.shadow.ma_5_20.interquartile.v1"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _rows() -> tuple[dict[str, object], ...]:
    start = datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc)
    return tuple({"time_utc": _iso(start + timedelta(minutes=index)), "close": 100.0 + index} for index in range(60))


def _feature_bundle() -> MarketRegimeFeatureBundle:
    signals = (
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_generated_at", "2026-07-13T23:59:00Z", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 125.0, True),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 20.0, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "RANGE", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "session_context", "asia", True),
    )
    groups = (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.LIQUIDITY, FeatureGroup.SOURCE_QUALITY)
    coverage = tuple(SourceCoverage(group, True, FreshnessState.LIVE) for group in groups)
    return MarketRegimeFeatureBundle(generated_at="2026-07-14T00:00:00Z", signals=signals, coverage=coverage, source_snapshot_ok=True)


def _report() -> dict[str, object]:
    return {"market_regime_only": True, "horizons": [
        {"horizon_sec": item.horizon_sec, "horizon_key": item.horizon_key, "regime_scores": {"RANGE": 0.8, "UP_TREND": 0.2}}
        for item in build_default_horizon_policy().horizons if item.horizon_sec
    ]}


def _packet():
    bundle = _feature_bundle()
    report = _report()
    epoch = datetime.fromisoformat(bundle.generated_at.replace("Z", "+00:00")).timestamp()
    return build_market_regime_future_shadow_packet(
        feature_bundle=bundle,
        signal_score_report=report,
        origin_current_state=MarketRegimeCode.RANGE,
        origin_timestamp_epoch_sec=epoch,
        source_timestamp_epoch_sec=epoch - 60.0,
    )


def _runtime_bundle():
    return build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=_feature_bundle(),
        previous_current_state={"regime_code": "DOWN_TREND"},
        canonical_current_l4_candle_rows=_rows(),
        shadow_candidate_id=CANDIDATE_ID,
    )


def _approval():
    return build_origin_evidence_approval(
        approval_id="approval:mr-f6.16:fixture",
        operator_ids=("operator:fixture",),
        requested_at="2026-07-14T00:00:00Z",
        expires_at="2026-07-15T00:00:00Z",
        approved_writer_id="mr-f6-origin-writer",
        approved_writer_contract_version="writer.v1",
    )


def _build(**overrides: object):
    values = dict(
        packet=_packet(), signal_score_report=_report(), runtime_bundle=_runtime_bundle(),
        generated_at="2026-07-14T00:00:00Z", writer_id="mr-f6-origin-writer",
        writer_contract_version="writer.v1", executed_at="2026-07-14T01:00:00Z",
        approval=None,
    )
    values.update(overrides)
    return build_origin_evidence_writer_preflight(**values)


def test_without_approval_builds_immutable_plan_but_not_writer_preflight() -> None:
    result = _build()
    assert result["bundle_count"] == 7
    assert result["target_horizons_sec"] == (300, 900, 1800, 3600, 21600, 43200, 86400)
    assert result["single_origin_batch"] is True
    assert result["approval_present"] is False
    assert result["preflight_ready"] is False
    assert result["writer_preflight"] is None
    assert result["blockers"] == ("operator_approval_missing",)


def test_active_approval_runs_preflight_only_and_never_writes() -> None:
    result = _build(approval=_approval())
    assert result["preflight_ready"] is True
    assert result["writer_preflight"]["write_allowed"] is True
    assert result["writer_preflight"]["would_write"] is False
    assert result["preflight_only"] is True
    assert result["write_allowed"] is False
    assert result["would_write"] is False
    assert result["writer_invoked"] is False
    assert result["write_execution_performed"] is False
    assert result["writes_dhot"] is False
    assert result["counts_as_real_shadow_evidence"] is False


def test_forecast_and_origin_feature_parameter_identities_remain_separate() -> None:
    result = _build(approval=_approval())
    assert result["shadow_candidate_id"] == CANDIDATE_ID
    assert result["origin_feature_parameter_set_id"] == CANDIDATE_ID
    assert result["forecast_parameter_set_ids"]
    assert CANDIDATE_ID not in result["forecast_parameter_set_ids"]


def test_unready_or_tampered_runtime_bundle_fails_closed() -> None:
    runtime = dict(_runtime_bundle())
    runtime["runtime_source_ready"] = False
    with pytest.raises(ValueError, match="runtime_bundle_not_ready"):
        _build(runtime_bundle=runtime)

    runtime = dict(_runtime_bundle())
    runtime["parameter_set_id"] = "other"
    with pytest.raises(ValueError, match="candidate_parameter_identity_mismatch"):
        _build(runtime_bundle=runtime)


def test_runtime_bundle_must_match_packet_origin_and_snapshot() -> None:
    runtime = dict(_runtime_bundle())
    runtime["feature_bundle_generated_at"] = "2026-07-14T00:01:00Z"
    with pytest.raises(ValueError, match="runtime_origin_mismatch"):
        _build(runtime_bundle=runtime)

    runtime = dict(_runtime_bundle())
    runtime["feature_snapshot_ref"] = "market_regime_feature_snapshot:other"
    with pytest.raises(ValueError, match="runtime_snapshot_mismatch"):
        _build(runtime_bundle=runtime)


def test_packet_origin_must_equal_plan_generated_at() -> None:
    with pytest.raises(ValueError, match="generated_at_origin_mismatch"):
        _build(generated_at="2026-07-14T00:01:00Z")


def test_bad_approval_scope_or_window_fails_closed() -> None:
    approval = dict(_approval())
    approval["approved_writer_id"] = "other"
    with pytest.raises(PermissionError, match="approval_scope_mismatch"):
        _build(approval=approval)
    with pytest.raises(PermissionError, match="approval_not_active"):
        _build(approval=_approval(), executed_at="2026-07-15T00:00:00Z")


def test_bridge_exposes_no_write_or_scheduler_surface() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_writer_preflight as module
    assert not hasattr(module, "write_origin_evidence_once")
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
