# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_execution_request.py
# desc: MR-F6.17 tests for immutable human-reviewed one-shot request construction without execution.

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from btcts.prediction.market_regime.contracts import FeatureGroup, FreshnessState, MarketRegimeCode, SourceCoverage
from btcts.prediction.market_regime.features import FeatureSignal, MarketRegimeFeatureBundle
from btcts.prediction.market_regime.future_origin_evidence_execution_request import (
    OriginEvidenceExecutionReview,
    build_origin_evidence_execution_request,
)
from btcts.prediction.market_regime.future_origin_evidence_writer import build_origin_evidence_approval
from btcts.prediction.market_regime.future_origin_evidence_writer_preflight import build_origin_evidence_writer_preflight
from btcts.prediction.market_regime.future_origin_feature_runtime_bundle import build_market_regime_origin_feature_runtime_bundle
from btcts.prediction.market_regime.future_shadow_adapter import build_market_regime_future_shadow_packet
from btcts.prediction.market_regime.horizon_policy import build_default_horizon_policy

CANDIDATE_ID = "market_regime.origin_feature.shadow.ma_5_20.interquartile.v1"


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _feature_bundle() -> MarketRegimeFeatureBundle:
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


def _rows() -> tuple[dict[str, object], ...]:
    start = datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc)
    return tuple({"time_utc": _iso(start + timedelta(minutes=index)), "close": 100.0 + index} for index in range(60))


def _report() -> dict[str, object]:
    return {"market_regime_only": True, "horizons": [
        {"horizon_sec": item.horizon_sec, "horizon_key": item.horizon_key, "regime_scores": {"RANGE": 0.8, "UP_TREND": 0.2}}
        for item in build_default_horizon_policy().horizons if item.horizon_sec
    ]}


def _preflight():
    bundle = _feature_bundle()
    report = _report()
    epoch = datetime.fromisoformat(bundle.generated_at.replace("Z", "+00:00")).timestamp()
    packet = build_market_regime_future_shadow_packet(
        feature_bundle=bundle, signal_score_report=report,
        origin_current_state=MarketRegimeCode.RANGE,
        origin_timestamp_epoch_sec=epoch, source_timestamp_epoch_sec=epoch - 60.0,
    )
    runtime = build_market_regime_origin_feature_runtime_bundle(
        feature_bundle=bundle, previous_current_state={"regime_code": "DOWN_TREND"},
        canonical_current_l4_candle_rows=_rows(), shadow_candidate_id=CANDIDATE_ID,
    )
    approval = build_origin_evidence_approval(
        approval_id="approval:mr-f6.17:fixture", operator_ids=("operator:fixture",),
        requested_at="2026-07-14T00:00:00Z", expires_at="2026-07-15T00:00:00Z",
        approved_writer_id="mr-f6-origin-writer", approved_writer_contract_version="writer.v1",
    )
    return build_origin_evidence_writer_preflight(
        packet=packet, signal_score_report=report, runtime_bundle=runtime,
        generated_at=bundle.generated_at, writer_id="mr-f6-origin-writer",
        writer_contract_version="writer.v1", executed_at="2026-07-14T01:00:00Z",
        approval=approval,
    )


def _review(**overrides: object) -> OriginEvidenceExecutionReview:
    values = dict(
        reviewer_ids=("operator:mint",), reviewed_at="2026-07-14T01:05:00Z",
        preflight_reviewed=True, bundle_identity_reviewed=True,
        destination_reviewed=True, duplicate_prevention_reviewed=True,
        append_only_reviewed=True, canonical_isolation_reviewed=True,
        one_shot_scope_reviewed=True,
    )
    values.update(overrides)
    return OriginEvidenceExecutionReview(**values)


def test_complete_review_builds_immutable_request_without_authorizing_execution() -> None:
    result = build_origin_evidence_execution_request(
        preflight_artifact=_preflight(), review=_review(),
        requested_at="2026-07-14T01:10:00Z",
    )
    assert result["request_ready_for_separate_execution"] is True
    assert result["approval_requested_at"] == "2026-07-14T00:00:00Z"
    assert result["approval_expires_at"] == "2026-07-15T00:00:00Z"
    assert result["preflight_executed_at"] == "2026-07-14T01:00:00Z"
    assert result["one_shot_execution_requested"] is True
    assert result["execution_authorized_by_this_artifact"] is False
    assert result["enabled_acknowledgement_present"] is False
    assert result["once_acknowledgement_present"] is False
    assert result["writer_imported"] is False
    assert result["writer_invoked"] is False
    assert result["execution_performed"] is False
    assert result["writes_dhot"] is False


def test_request_identity_is_deterministic_and_bound_to_batch() -> None:
    first = build_origin_evidence_execution_request(
        preflight_artifact=_preflight(), review=_review(), requested_at="2026-07-14T01:10:00Z",
    )
    second = build_origin_evidence_execution_request(
        preflight_artifact=_preflight(), review=_review(), requested_at="2026-07-14T01:10:00Z",
    )
    assert first["request_id"] == second["request_id"]
    assert first["request_hash"] == second["request_hash"]
    assert first["schema_version"].endswith("mr_f6_17.v4")
    assert first["writer_id"] == "mr-f6-origin-writer"
    assert first["writer_contract_version"] == "writer.v1"
    assert set(first["bundle_ids"]) == set(first["write_plan_bundle_ids"])
    assert first["bundle_ids"] != first["write_plan_bundle_ids"]
    assert first["dedupe_key"]
    assert first["artifact_relpath"].endswith(f"batch-{first['dedupe_key']}.json")


def test_incomplete_review_remains_blocked() -> None:
    result = build_origin_evidence_execution_request(
        preflight_artifact=_preflight(),
        review=_review(one_shot_scope_reviewed=False),
        requested_at="2026-07-14T01:10:00Z",
    )
    assert result["request_ready_for_separate_execution"] is False
    assert result["one_shot_execution_requested"] is False
    assert result["blockers"] == ("human_review_incomplete",)


def test_request_time_must_be_inside_active_approval_window() -> None:
    with pytest.raises(PermissionError, match="approval_not_active"):
        build_origin_evidence_execution_request(
            preflight_artifact=_preflight(), review=_review(reviewed_at="2026-07-15T00:00:00Z"),
            requested_at="2026-07-15T00:00:00Z",
        )

    preflight = dict(_preflight())
    preflight["preflight_executed_at"] = "2026-07-15T00:00:00Z"
    with pytest.raises(ValueError, match="preflight_outside_approval_window"):
        build_origin_evidence_execution_request(
            preflight_artifact=preflight, review=_review(),
            requested_at="2026-07-14T01:10:00Z",
        )


def test_review_must_follow_preflight_and_be_inside_approval_window() -> None:
    with pytest.raises(ValueError, match="review_before_preflight"):
        build_origin_evidence_execution_request(
            preflight_artifact=_preflight(),
            review=_review(reviewed_at="2026-07-14T00:59:59Z"),
            requested_at="2026-07-14T01:10:00Z",
        )


def test_review_must_precede_request_and_flags_are_strict_bool() -> None:
    with pytest.raises(ValueError, match="review_after_request"):
        build_origin_evidence_execution_request(
            preflight_artifact=_preflight(), review=_review(reviewed_at="2026-07-14T01:11:00Z"),
            requested_at="2026-07-14T01:10:00Z",
        )
    with pytest.raises(ValueError, match="review_flag_invalid"):
        _review(preflight_reviewed=1)


def test_plan_bundle_identity_uses_set_equality_not_order_equality() -> None:
    preflight = _preflight()
    assert tuple(preflight["bundle_ids"]) != tuple(preflight["write_plan"]["bundle_ids"])
    result = build_origin_evidence_execution_request(
        preflight_artifact=preflight, review=_review(),
        requested_at="2026-07-14T01:10:00Z",
    )
    assert set(result["bundle_ids"]) == set(result["write_plan_bundle_ids"])


def test_tampered_preflight_or_plan_fails_closed() -> None:
    preflight = dict(_preflight())
    preflight["writes_dhot"] = True
    with pytest.raises(ValueError, match="unsafe_preflight_flag:writes_dhot"):
        build_origin_evidence_execution_request(
            preflight_artifact=preflight, review=_review(), requested_at="2026-07-14T01:10:00Z",
        )

    preflight = dict(_preflight())
    nested = dict(preflight["writer_preflight"])
    nested["dedupe_key"] = "other"
    preflight["writer_preflight"] = nested
    with pytest.raises(ValueError, match="dedupe_key_mismatch"):
        build_origin_evidence_execution_request(
            preflight_artifact=preflight, review=_review(), requested_at="2026-07-14T01:10:00Z",
        )


def test_module_exposes_no_writer_or_execution_surface() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_execution_request as module
    assert not hasattr(module, "write_origin_evidence_once")
    assert not hasattr(module, "preflight_origin_evidence_write")
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
