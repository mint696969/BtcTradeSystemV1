# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_contract.py
# desc: MR-F9.19L bounded 24h runtime-horizon collection contract tests.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from btcts.prediction.market_regime.runtime_horizon_collection_contract import (
    COLLECTION_CADENCE_SEC,
    COLLECTION_DURATION_SEC,
    MAX_COLLECTION_TICKS,
    build_runtime_horizon_collection_plan,
    validate_runtime_horizon_collection_plan,
)


def _build(tmp_path: Path):
    return build_runtime_horizon_collection_plan(
        source_root=tmp_path / "source",
        destination_root=tmp_path / "destination",
        shadow_candidate_id="market_regime.origin_feature.shadow.ma_5_20.interquartile.v1",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:00:00Z",
    )


def test_builds_exact_bounded_24h_plan(tmp_path) -> None:
    plan = _build(tmp_path)
    assert plan["duration_sec"] == COLLECTION_DURATION_SEC == 86_400
    assert plan["cadence_sec"] == COLLECTION_CADENCE_SEC == 60
    assert plan["expected_tick_count"] == 1_440
    assert plan["maximum_loop_iterations"] == MAX_COLLECTION_TICKS == 1_442
    assert plan["planned_start_utc"] == "2026-07-17T00:00:00Z"
    assert plan["planned_end_utc"] == "2026-07-18T00:00:00Z"
    assert plan["expected_horizon_count_per_origin"] == 8
    assert plan["expected_files_per_origin"] == 9
    assert plan["collection_id"].startswith("mr-f9-24h-")
    assert plan["state_relpath"].endswith("/state.json")
    assert plan["progress_relpath"].endswith("/progress.json")
    assert plan["completion_receipt_relpath"].endswith("/completion_receipt.json")
    validate_runtime_horizon_collection_plan(plan)


def test_plan_is_deterministic_for_same_identity(tmp_path) -> None:
    assert _build(tmp_path) == _build(tmp_path)


def test_identity_change_changes_collection_id(tmp_path) -> None:
    first = _build(tmp_path)
    second = build_runtime_horizon_collection_plan(
        source_root=tmp_path / "source",
        destination_root=tmp_path / "destination",
        shadow_candidate_id="market_regime.origin_feature.shadow.ma_5_20.interquartile.v1",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:01:00Z",
    )
    assert first["collection_id"] != second["collection_id"]


def test_duration_and_cadence_are_fixed(tmp_path) -> None:
    kwargs = dict(
        source_root=tmp_path / "source",
        destination_root=tmp_path / "destination",
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:00:00Z",
    )
    with pytest.raises(ValueError, match="duration_must_equal_86400"):
        build_runtime_horizon_collection_plan(**kwargs, duration_sec=60)
    with pytest.raises(ValueError, match="cadence_must_equal_60"):
        build_runtime_horizon_collection_plan(**kwargs, cadence_sec=300)


def test_requires_utc_timestamp_candidate_and_operator(tmp_path) -> None:
    base = dict(
        source_root=tmp_path / "source",
        destination_root=tmp_path / "destination",
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:00:00Z",
    )
    with pytest.raises(ValueError, match="timezone_required"):
        build_runtime_horizon_collection_plan(**{**base, "planned_start_utc": "2026-07-17T00:00:00"})
    with pytest.raises(ValueError, match="shadow_candidate_id_required"):
        build_runtime_horizon_collection_plan(**{**base, "shadow_candidate_id": " "})
    with pytest.raises(ValueError, match="operator_id_required"):
        build_runtime_horizon_collection_plan(**{**base, "operator_id": " "})


def test_safety_and_restart_policy_are_fail_closed(tmp_path) -> None:
    plan = _build(tmp_path)
    assert plan["origin_identity_policy"] == "one_origin_per_latest_closed_60s_candle"
    assert plan["duplicate_origin_policy"] == "skip_without_write"
    assert plan["readiness_failure_policy"] == "record_skip_and_continue"
    assert plan["destination_conflict_policy"] == "fail_closed_and_stop"
    assert plan["restart_policy"] == "resume_from_persisted_state_without_rewriting_completed_origins"
    assert plan["foreground_process_required"] is True
    assert plan["human_start_authorization_required"] is True
    assert plan["disabled_by_default"] is True
    for key in (
        "scheduler_registration_allowed",
        "latest_pointer_created",
        "writer_registered",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
        "auto_promotion_allowed",
        "live_parameter_apply_allowed",
        "collection_started",
        "collection_completed",
        "writer_invoked",
        "writes_dhot",
    ):
        assert plan[key] is False


def test_validation_rejects_any_mutation(tmp_path) -> None:
    plan = dict(_build(tmp_path))
    plan["cadence_sec"] = 120
    with pytest.raises(ValueError):
        validate_runtime_horizon_collection_plan(plan)


def test_input_datetime_is_normalized_to_utc(tmp_path) -> None:
    plan = build_runtime_horizon_collection_plan(
        source_root=tmp_path / "source",
        destination_root=tmp_path / "destination",
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T09:00:00+09:00",
    )
    assert plan["planned_start_utc"] == "2026-07-17T00:00:00Z"
