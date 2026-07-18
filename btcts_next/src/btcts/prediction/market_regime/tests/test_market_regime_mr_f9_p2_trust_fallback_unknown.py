# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_mr_f9_p2_trust_fallback_unknown.py
# desc: MR-F9 P2 integration guards for fallback truth, UNKNOWN/prematurity preservation, and non-promoting trust semantics.

from __future__ import annotations

import hashlib
import json
from copy import deepcopy

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_baseline_model import (
    FutureBaselineEvidence,
    forecast_future_market_regime_baseline,
)
from btcts.prediction.market_regime.future_execution_evidence import (
    FutureInferenceMode,
    build_market_regime_future_execution_evidence,
)
from btcts.prediction.market_regime.future_shadow_outcome import (
    FutureShadowOutcomeEvidence,
    FutureShadowOutcomeStatus,
    resolve_market_regime_future_shadow_outcome,
)
from btcts.prediction.market_regime.future_trace_identity import (
    build_market_regime_future_trace_identity,
)
from btcts.prediction.market_regime.runtime_horizon_read_model import (
    project_market_regime_runtime_horizons_to_read_model,
)

HORIZONS = (0, 300, 900, 1800, 3600, 21600, 43200, 86400)
ORIGIN = "2026-07-18T00:00:00Z"
RUN_ID = "run-mr-f9-p2"


def _forecast(*, horizon: int = 900):
    return forecast_future_market_regime_baseline(
        FutureBaselineEvidence(
            origin_timestamp=ORIGIN,
            origin_current_state=MarketRegimeCode.RANGE,
            target_horizon_sec=horizon,
            feature_snapshot_ref="snapshot:mr-f9-p2",
            regime_scores={
                MarketRegimeCode.BREAKOUT: 0.61,
                MarketRegimeCode.RANGE: 0.39,
            },
            available_feature_families=(
                "price_structure",
                "volatility",
                "liquidity",
                "microprice",
                "source_quality",
                "session_context",
            ),
            source_timestamp_epoch_sec=100.0,
            origin_timestamp_epoch_sec=102.0,
        )
    )


def _digest(payload: dict) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _runtime_fixture() -> tuple[dict, dict[str, dict]]:
    payloads: dict[str, dict] = {}
    artifacts: list[dict] = []
    for sec in HORIZONS:
        relpath = f"prediction/market_regime/runtime_horizons/p2/horizon={sec}.json"
        is_fallback = sec == 900
        is_current = sec == 0
        payload = {
            "schema_version": "prediction.market_regime.runtime_horizon_persistence_plan.mr_f9_19b.v1",
            "artifact_kind": "market_regime_runtime_horizon",
            "prediction_family_id": "market_regime",
            "prediction_origin": ORIGIN,
            "run_id": RUN_ID,
            "horizon_sec": sec,
            "read_only": True,
            "non_executing": True,
            "ui_inference_allowed": False,
            "ui_confidence_recalculation_allowed": False,
            "horizon": {
                "horizon_key": "current" if is_current else f"{sec}s",
                "horizon_sec": sec,
                "prediction_origin": ORIGIN,
                "trace_id": f"trace:p2:{sec}",
                "label": "RANGE" if is_current else "UNKNOWN",
                "status": "OBSERVED_ESTIMATE" if is_current else "ABSTAIN",
                "abstained": not is_current,
                "abstain_reason": "" if is_current else "prematurity_or_unavailable",
                "inference_mode": "FALLBACK" if is_fallback else "FULL_INFERENCE",
                "model_id": f"model-{sec}",
                "logic_version": f"logic-{sec}",
                "parameter_set_id": f"params-{sec}",
                "target_definition_version": f"target-{sec}",
                "display_confidence_percent": None,
                "calibrated_probability_claim": False,
                "confidence_semantics": "not_promoted_for_runtime_display",
                "source_kind": "fixture_source",
                "source_timestamp": "2026-07-17T23:58:00Z",
                "source_age_sec": 120,
                "source_freshness_state": "STALE" if is_fallback else "LIVE",
                "fallback_used": is_fallback,
                "fallback_reason": "forecast_records_stale" if is_fallback else "",
                "fallback_source_ref": "compat:l4" if is_fallback else "",
                "warnings": [],
                "invalidation_conditions": [],
                "metadata": {"blockers": []},
                "read_only": True,
            },
        }
        payloads[relpath] = payload
        artifacts.append(
            {
                "artifact_relpath": relpath,
                "horizon_sec": sec,
                "payload_sha256": _digest(payload),
                "trace_id": f"trace:p2:{sec}",
            }
        )

    manifest = {
        "schema_version": "prediction.market_regime.runtime_horizon_persistence_plan.mr_f9_19b.v1",
        "artifact_kind": "market_regime_runtime_horizon_run_manifest",
        "prediction_family_id": "market_regime",
        "prediction_origin": ORIGIN,
        "run_id": RUN_ID,
        "horizon_count": 8,
        "horizon_artifacts": artifacts,
        "latest_pointer_relpath": None,
        "read_only": True,
        "non_executing": True,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
    }
    return manifest, payloads


def test_fallback_truth_requires_reason_and_source_and_is_non_promoting() -> None:
    forecast = _forecast()
    evidence = build_market_regime_future_execution_evidence(
        forecast,
        inference_mode=FutureInferenceMode.FALLBACK,
        source_freshness_state="STALE",
        source_age_sec=120.0,
        fallback_reason="forecast_records_stale",
        fallback_source_ref="compat:l4",
    )
    payload = evidence.to_dict()

    assert payload["fallback_used"] is True
    assert payload["fallback_reason"] == "forecast_records_stale"
    assert payload["fallback_source_ref"] == "compat:l4"
    assert payload["trace_id"] == build_market_regime_future_trace_identity(forecast).trace_id
    assert payload["source_freshness_state"] == "STALE"
    assert payload["calculation_fingerprint"].startswith(
        "market_regime_future_calculation:"
    )
    assert payload["parameter_auto_promotion_allowed"] is False
    assert payload["live_parameter_apply_allowed"] is False


@pytest.mark.parametrize(
    ("reason", "source_ref", "error"),
    (
        ("", "compat:l4", "fallback_reason_required"),
        ("forecast_records_stale", "", "fallback_source_ref_required"),
    ),
)
def test_fallback_missing_truth_fields_fails_closed(
    reason: str,
    source_ref: str,
    error: str,
) -> None:
    with pytest.raises(ValueError, match=error):
        build_market_regime_future_execution_evidence(
            _forecast(),
            inference_mode=FutureInferenceMode.FALLBACK,
            source_freshness_state="STALE",
            source_age_sec=120.0,
            fallback_reason=reason,
            fallback_source_ref=source_ref,
        )


def test_prematurity_missing_observation_and_unknown_remain_unresolved() -> None:
    trace = build_market_regime_future_trace_identity(_forecast(horizon=300))

    premature = resolve_market_regime_future_shadow_outcome(
        trace=trace,
        evidence=FutureShadowOutcomeEvidence(
            resolved_at="2026-07-18T00:04:59Z",
            observation_available=False,
        ),
    )
    missing = resolve_market_regime_future_shadow_outcome(
        trace=trace,
        evidence=FutureShadowOutcomeEvidence(
            resolved_at="2026-07-18T00:06:00Z",
            observation_available=False,
        ),
    )
    unknown = resolve_market_regime_future_shadow_outcome(
        trace=trace,
        evidence=FutureShadowOutcomeEvidence(
            resolved_at="2026-07-18T00:06:00Z",
            observation_available=True,
            observed_at="2026-07-18T00:05:30Z",
            observed_future_state=MarketRegimeCode.UNKNOWN,
            observation_source_ref="observation:test",
        ),
    )

    assert premature.status is FutureShadowOutcomeStatus.UNRESOLVED
    assert premature.reason == "target_horizon_not_expired"
    assert missing.status is FutureShadowOutcomeStatus.UNRESOLVED
    assert missing.reason == "observation_unavailable"
    assert unknown.status is FutureShadowOutcomeStatus.UNRESOLVED
    assert unknown.reason == "observed_future_state_unknown"
    assert unknown.observed_future_state is MarketRegimeCode.UNKNOWN


def test_read_model_preserves_unknown_and_fallback_truth_without_recalculation() -> None:
    manifest, payloads = _runtime_fixture()
    model = project_market_regime_runtime_horizons_to_read_model(
        manifest=manifest,
        payloads_by_relpath=payloads,
    )

    rows = {int(row["horizon_sec"]): row for row in model["horizon_rows"]}
    fallback = rows[900]

    assert fallback["primary_label"] == "UNKNOWN"
    assert fallback["confidence_percent"] == 0
    assert fallback["confidence_kind"] == "unavailable_not_promoted"
    assert fallback["freshness_state"] == "STALE"
    assert fallback["family_payload"]["fallback_used"] is True
    assert fallback["family_payload"]["fallback_reason"] == (
        "forecast_records_stale"
    )
    assert fallback["trace_refs"][0]["trace_id"] == "trace:p2:900"
    assert model["projection"]["prediction_invoked"] is False
    assert model["projection"]["classifier_invoked"] is False
    assert model["projection"]["confidence_recalculated"] is False
    assert model["projection"]["source_merge_performed"] is False
    assert model["projection"]["writes_dhot"] is False


def test_read_model_digest_tamper_fails_closed() -> None:
    manifest, payloads = _runtime_fixture()
    relpath = manifest["horizon_artifacts"][2]["artifact_relpath"]
    tampered = deepcopy(payloads)
    tampered[relpath]["horizon"]["fallback_reason"] = "hidden"

    with pytest.raises(ValueError, match="runtime_horizon_payload_digest_mismatch"):
        project_market_regime_runtime_horizons_to_read_model(
            manifest=manifest,
            payloads_by_relpath=tampered,
        )
