# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_state.py
# desc: MR-F9.19L persistent collection state and stop-request tests.

from __future__ import annotations

import json
from pathlib import Path

import pytest

from btcts.prediction.market_regime.runtime_horizon_collection_contract import (
    build_runtime_horizon_collection_plan,
)
from btcts.prediction.market_regime.runtime_horizon_collection_state import (
    advance_runtime_horizon_collection_state,
    build_initial_runtime_horizon_collection_state,
    collection_state_paths,
    read_runtime_horizon_collection_state,
    validate_runtime_horizon_collection_state,
    write_runtime_horizon_collection_completion_receipt,
    write_runtime_horizon_collection_state,
    request_runtime_horizon_collection_stop,
)


def _plan(tmp_path: Path):
    return build_runtime_horizon_collection_plan(
        source_root=tmp_path / "source",
        destination_root=tmp_path / "destination",
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:00:00Z",
    )


def _initial(tmp_path: Path):
    return build_initial_runtime_horizon_collection_state(
        plan=_plan(tmp_path),
        created_at="2026-07-17T00:00:00Z",
    )


def test_initial_state_is_disabled_and_safe(tmp_path) -> None:
    state = _initial(tmp_path)
    assert state["status"] == "PLANNED"
    assert state["active"] is False
    assert state["iteration_count"] == 0
    assert state["written_origin_count"] == 0
    assert state["completed_prediction_origins"] == []
    for key in (
        "writer_registered",
        "scheduler_enabled",
        "producer_loop_enabled",
        "latest_pointer_created",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        assert state[key] is False


def test_atomic_state_and_progress_round_trip(tmp_path) -> None:
    plan = _plan(tmp_path)
    state = _initial(tmp_path)
    result = write_runtime_horizon_collection_state(tmp_path, plan=plan, state=state)
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False
    paths = collection_state_paths(tmp_path, plan)
    assert paths["state"].exists()
    assert paths["progress"].exists()
    assert not paths["state"].with_name("state.json.tmp").exists()
    assert read_runtime_horizon_collection_state(tmp_path, plan=plan) == state
    progress = json.loads(paths["progress"].read_text(encoding="utf-8"))
    assert progress["status"] == "PLANNED"
    assert progress["latest_pointer_created"] is False


def test_start_write_and_duplicate_origin_protection(tmp_path) -> None:
    plan = _plan(tmp_path)
    state = _initial(tmp_path)
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="WRITE_OK",
        observed_at="2026-07-17T00:01:01Z",
        prediction_origin="2026-07-17T00:00:00Z",
        closed_source_timestamp="2026-07-16T23:59:00Z",
        run_id="run-1",
    )
    assert state["written_origin_count"] == 1
    assert state["iteration_count"] == 1
    assert state["completed_prediction_origins"] == ["2026-07-17T00:00:00Z"]
    assert state["completed_closed_source_timestamps"] == ["2026-07-16T23:59:00Z"]
    with pytest.raises(ValueError, match="origin_already_completed"):
        advance_runtime_horizon_collection_state(
            plan=plan,
            previous=state,
            event="WRITE_OK",
            observed_at="2026-07-17T00:02:01Z",
            prediction_origin="2026-07-17T00:00:00Z",
            closed_source_timestamp="2026-07-16T23:59:00Z",
            run_id="run-2",
        )


def test_skip_counters_are_monotonic(tmp_path) -> None:
    plan = _plan(tmp_path)
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=_initial(tmp_path),
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="READINESS_SKIP",
        observed_at="2026-07-17T00:01:01Z",
        reason="source_not_current",
    )
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="DUPLICATE_ORIGIN_SKIP",
        observed_at="2026-07-17T00:02:01Z",
    )
    assert state["iteration_count"] == 2
    assert state["readiness_skip_count"] == 1
    assert state["duplicate_origin_skip_count"] == 1


def test_conflict_is_terminal_and_fail_closed(tmp_path) -> None:
    plan = _plan(tmp_path)
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=_initial(tmp_path),
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    failed = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="CONFLICT",
        observed_at="2026-07-17T00:01:01Z",
        reason="manifest_digest_conflict",
    )
    assert failed["status"] == "FAILED_CONFLICT"
    assert failed["active"] is False
    assert failed["error_count"] == 1
    with pytest.raises(ValueError, match="terminal"):
        advance_runtime_horizon_collection_state(
            plan=plan,
            previous=failed,
            event="START",
            observed_at="2026-07-17T00:02:01Z",
        )


def test_plan_or_state_tampering_is_rejected(tmp_path) -> None:
    plan = _plan(tmp_path)
    state = dict(_initial(tmp_path))
    state["plan_sha256"] = "bad"
    with pytest.raises(ValueError, match="plan_sha_mismatch"):
        validate_runtime_horizon_collection_state(plan=plan, state=state)

    state = dict(_initial(tmp_path))
    state["completed_prediction_origins"] = ["x", "x"]
    state["written_origin_count"] = 2
    with pytest.raises(ValueError, match="duplicate_origin"):
        validate_runtime_horizon_collection_state(plan=plan, state=state)


def test_completion_receipt_requires_completed_state(tmp_path) -> None:
    plan = _plan(tmp_path)
    state = _initial(tmp_path)
    with pytest.raises(ValueError, match="completion_state_required"):
        write_runtime_horizon_collection_completion_receipt(tmp_path, plan=plan, state=state)

    running = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    completed = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=running,
        event="COMPLETE",
        observed_at="2026-07-18T00:00:01Z",
    )
    result = write_runtime_horizon_collection_completion_receipt(
        tmp_path,
        plan=plan,
        state=completed,
    )
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False
    receipt = json.loads(collection_state_paths(tmp_path, plan)["completion_receipt"].read_text(encoding="utf-8"))
    assert receipt["collection_id"] == plan["collection_id"]
    assert receipt["latest_pointer_created"] is False


def test_restart_reads_same_persisted_completed_origins(tmp_path) -> None:
    plan = _plan(tmp_path)
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=_initial(tmp_path),
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="WRITE_OK",
        observed_at="2026-07-17T00:01:01Z",
        prediction_origin="2026-07-17T00:00:00Z",
        closed_source_timestamp="2026-07-16T23:59:00Z",
        run_id="run-1",
    )
    write_runtime_horizon_collection_state(tmp_path, plan=plan, state=state)
    restored = read_runtime_horizon_collection_state(tmp_path, plan=plan)
    assert restored["completed_prediction_origins"] == ["2026-07-17T00:00:00Z"]
    assert restored["written_origin_count"] == 1


def test_state_rejects_duplicate_closed_source(tmp_path) -> None:
    plan = _plan(tmp_path)
    state = dict(_initial(tmp_path))
    state["completed_prediction_origins"] = ["a", "b"]
    state["completed_closed_source_timestamps"] = ["x", "x"]
    state["written_origin_count"] = 2
    with pytest.raises(ValueError, match="duplicate_closed_source"):
        validate_runtime_horizon_collection_state(plan=plan, state=state)


def test_external_stop_request_is_persisted_atomically(tmp_path) -> None:
    plan = _plan(tmp_path)
    running = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=_initial(tmp_path),
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    write_runtime_horizon_collection_state(tmp_path, plan=plan, state=running)
    receipt = request_runtime_horizon_collection_stop(
        tmp_path,
        plan=plan,
        requested_at="2026-07-17T00:00:30Z",
    )
    assert receipt["ok"] is True
    assert receipt["stop_requested"] is True
    restored = read_runtime_horizon_collection_state(tmp_path, plan=plan)
    assert restored["stop_requested"] is True
    assert restored["updated_at"] == "2026-07-17T00:00:30Z"
