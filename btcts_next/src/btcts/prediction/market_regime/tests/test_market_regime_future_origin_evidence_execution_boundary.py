# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_execution_boundary.py
# desc: MR-F6.18 tests for final pure authorization boundary without writer execution.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_origin_evidence_execution_boundary import build_origin_evidence_execution_boundary
from btcts.prediction.market_regime.future_origin_evidence_execution_request import OriginEvidenceExecutionReview, build_origin_evidence_execution_request
from btcts.prediction.market_regime.future_origin_evidence_writer import build_origin_evidence_approval
from btcts.prediction.market_regime.future_origin_evidence_writer_preflight import build_origin_evidence_writer_preflight
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import build_market_regime_origin_feature_runtime_bundle
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.horizon_policy import build_default_horizon_policy

CANDIDATE_ID = "market_regime.origin_feature.shadow.ma_5_20.interquartile.v1"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _request():
    generated_at = "2026-07-14T00:00:00Z"
    signals = (
        FeatureSignal(FeatureGroup.SOURCE_QUALITY, "current_l4_candle_window_generated_at", "2026-07-13T23:59:00Z", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_net_change_bps", 125.0, True),
        FeatureSignal(FeatureGroup.VOLATILITY, "current_l4_candle_realized_volatility_bps", 20.0, True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "current_l4_candle_regime_hint", "RANGE", True),
        FeatureSignal(FeatureGroup.PRICE_STRUCTURE, "session_context", "asia", True),
    )
    groups = (FeatureGroup.PRICE_STRUCTURE, FeatureGroup.VOLATILITY, FeatureGroup.LIQUIDITY, FeatureGroup.SOURCE_QUALITY)
    bundle = MarketRegimeFeatureBundle(
        generated_at=generated_at, signals=signals,
        coverage=tuple(SourceCoverage(group, True, FreshnessState.LIVE) for group in groups),
        source_snapshot_ok=True,
    )
    report = {"market_regime_only": True, "horizons": [
        {"horizon_sec": item.horizon_sec, "horizon_key": item.horizon_key, "regime_scores": {"RANGE": 0.8, "UP_TREND": 0.2}}
        for item in build_default_horizon_policy().horizons if item.horizon_sec
    ]}
    epoch = datetime.fromisoformat(generated_at.replace("Z", "+00:00")).timestamp()
    packet = build_market_regime_future_shadow_packet(
        feature_bundle=bundle, signal_score_report=report,
        origin_current_state=MarketRegimeCode.RANGE,
        origin_timestamp_epoch_sec=epoch, source_timestamp_epoch_sec=epoch - 60.0,
    )
    start = datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc)
    rows = tuple({"time_utc": _iso(start + timedelta(minutes=index)), "close": 100.0 + index} for index in range(60))
    runtime = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=bundle, previous_current_state={"regime_code": "DOWN_TREND"},
        canonical_current_l4_candle_rows=rows, shadow_candidate_id=CANDIDATE_ID,
    )
    approval = build_origin_evidence_approval(
        approval_id="approval:mr-f6.18:fixture", operator_ids=("operator:fixture",),
        requested_at="2026-07-14T00:00:00Z", expires_at="2026-07-15T00:00:00Z",
        approved_writer_id="mr-f6-origin-writer", approved_writer_contract_version="writer.v1",
    )
    preflight = build_origin_evidence_writer_preflight(
        packet=packet, signal_score_report=report, runtime_bundle=runtime,
        generated_at=generated_at, writer_id="mr-f6-origin-writer",
        writer_contract_version="writer.v1", executed_at="2026-07-14T01:00:00Z",
        approval=approval,
    )
    review = OriginEvidenceExecutionReview(
        reviewer_ids=("operator:mint",), reviewed_at="2026-07-14T01:05:00Z",
        preflight_reviewed=True, bundle_identity_reviewed=True,
        destination_reviewed=True, duplicate_prevention_reviewed=True,
        append_only_reviewed=True, canonical_isolation_reviewed=True,
        one_shot_scope_reviewed=True,
    )
    return build_origin_evidence_execution_request(
        preflight_artifact=preflight, review=review,
        requested_at="2026-07-14T01:10:00Z",
    )


def _boundary(**overrides: object):
    request = overrides.pop("execution_request", _request())
    values = dict(
        execution_request=request, evaluated_at="2026-07-14T01:15:00Z",
        destination_artifact_exists=False,
        destination_artifact_matches_request=False,
        expected_request_hash=request["request_hash"],
        expected_writer_id="mr-f6-origin-writer",
        expected_writer_contract_version="writer.v1",
        enabled_acknowledgement=False,
        once_acknowledgement=False,
    )
    values.update(overrides)
    return build_origin_evidence_execution_boundary(**values)


def test_acknowledgements_are_both_required() -> None:
    result = _boundary()
    assert result["authorization_ready_for_separate_writer_call"] is False
    assert "enabled_acknowledgement_missing" in result["blockers"]
    assert "once_acknowledgement_missing" in result["blockers"]
    assert _boundary(enabled_acknowledgement=True)["authorization_ready_for_separate_writer_call"] is False
    assert _boundary(once_acknowledgement=True)["authorization_ready_for_separate_writer_call"] is False


def test_complete_boundary_only_allows_separate_call_consideration() -> None:
    result = _boundary(enabled_acknowledgement=True, once_acknowledgement=True)
    assert result["authorization_ready_for_separate_writer_call"] is True
    assert result["decision"] == "separate_writer_call_may_be_considered"
    assert result["execution_authorized_by_this_artifact"] is False
    assert result["writer_imported"] is False
    assert result["writer_invoked"] is False
    assert result["execution_performed"] is False
    assert result["writes_dhot"] is False


def test_expired_approval_blocks_boundary() -> None:
    result = _boundary(
        evaluated_at="2026-07-15T00:00:00Z",
        enabled_acknowledgement=True,
        once_acknowledgement=True,
    )
    assert result["authorization_ready_for_separate_writer_call"] is False
    assert "approval_expired" in result["blockers"]


def test_destination_match_requires_existing_artifact() -> None:
    with pytest.raises(ValueError, match="destination_state_inconsistent"):
        _boundary(
            destination_artifact_exists=False,
            destination_artifact_matches_request=True,
            enabled_acknowledgement=True,
            once_acknowledgement=True,
        )


def test_existing_destination_is_terminal_or_conflict() -> None:
    duplicate = _boundary(
        destination_artifact_exists=True,
        destination_artifact_matches_request=True,
        enabled_acknowledgement=True,
        once_acknowledgement=True,
    )
    assert "destination_artifact_already_satisfied" in duplicate["blockers"]
    conflict = _boundary(
        destination_artifact_exists=True,
        destination_artifact_matches_request=False,
        enabled_acknowledgement=True,
        once_acknowledgement=True,
    )
    assert "destination_artifact_conflict" in conflict["blockers"]


def test_missing_or_non_mapping_review_fails_closed() -> None:
    request = dict(_request())
    request["review"] = None
    with pytest.raises(ValueError, match="review_missing"):
        _boundary(execution_request=request)


def test_temporal_order_is_revalidated_at_final_boundary() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_execution_boundary as module

    request = dict(_request())
    review = dict(request["review"])
    review["reviewed_at"] = "2026-07-14T00:59:59Z"
    request["review"] = review
    forged_hash = module._recompute_request_hash(request)
    request["request_hash"] = forged_hash
    request["request_id"] = f"origin-evidence-execution-request:{forged_hash}"
    with pytest.raises(ValueError, match="review_before_preflight"):
        _boundary(
            execution_request=request,
            expected_request_hash=forged_hash,
        )


def test_fully_rehashed_forgery_still_fails_external_hash_confirmation() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_execution_boundary as module

    original = _request()
    forged = dict(original)
    forged["dedupe_key"] = "forged"
    forged_hash = module._recompute_request_hash(forged)
    forged["request_hash"] = forged_hash
    forged["request_id"] = f"origin-evidence-execution-request:{forged_hash}"
    with pytest.raises(PermissionError, match="external_request_hash_mismatch"):
        _boundary(
            execution_request=forged,
            expected_request_hash=original["request_hash"],
        )


def test_writer_scope_requires_external_exact_match() -> None:
    with pytest.raises(PermissionError, match="writer_scope_mismatch"):
        _boundary(expected_writer_id="other")
    with pytest.raises(PermissionError, match="writer_scope_mismatch"):
        _boundary(expected_writer_contract_version="other")


def test_tampered_batch_contract_fails_hash_validation() -> None:
    request = dict(_request())
    request["write_plan_bundle_ids"] = tuple(reversed(request["write_plan_bundle_ids"]))
    with pytest.raises(ValueError, match="request_hash_mismatch"):
        _boundary(execution_request=request)

    request = dict(_request())
    request["target_horizons_sec"] = request["target_horizons_sec"][:-1]
    with pytest.raises(ValueError, match="request_hash_mismatch"):
        _boundary(execution_request=request)

    request = dict(_request())
    request["forecast_parameter_set_ids"] = ("tampered",)
    with pytest.raises(ValueError, match="request_hash_mismatch"):
        _boundary(execution_request=request)


def test_tampered_review_or_ready_state_fails_hash_validation() -> None:
    request = dict(_request())
    review = dict(request["review"])
    review["one_shot_scope_reviewed"] = False
    request["review"] = review
    with pytest.raises(ValueError, match="request_hash_mismatch"):
        _boundary(execution_request=request)

    request = dict(_request())
    request["request_ready_for_separate_execution"] = False
    with pytest.raises(ValueError, match="request_hash_mismatch"):
        _boundary(execution_request=request)

    request = dict(_request())
    request["blockers"] = ("tampered",)
    with pytest.raises(ValueError, match="request_hash_mismatch"):
        _boundary(execution_request=request)


def test_tampered_request_hash_fails_closed() -> None:
    request = dict(_request())
    request["dedupe_key"] = "other"
    with pytest.raises(ValueError, match="request_hash_mismatch"):
        _boundary(execution_request=request)


def test_boolean_inputs_are_strict() -> None:
    with pytest.raises(ValueError, match="boolean_invalid:enabled_acknowledgement"):
        _boundary(enabled_acknowledgement=1)


def test_module_exposes_no_writer_or_runtime_surface() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_execution_boundary as module
    assert not hasattr(module, "write_origin_evidence_once")
    assert not hasattr(module, "preflight_origin_evidence_write")
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
