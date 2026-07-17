# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_tick.py
# desc: MR-F9.19L one-tick collection execution and deduplication tests.

from __future__ import annotations

import json
from pathlib import Path

import pytest

from btcts.prediction.market_regime.runtime_horizon_collection_contract import build_runtime_horizon_collection_plan
from btcts.prediction.market_regime.runtime_horizon_collection_state import (
    advance_runtime_horizon_collection_state,
    build_initial_runtime_horizon_collection_state,
    collection_state_paths,
)
from btcts.prediction.market_regime.runtime_horizon_collection_tick import execute_runtime_horizon_collection_tick


def _plan(tmp_path: Path):
    return build_runtime_horizon_collection_plan(
        source_root=tmp_path / "source",
        destination_root=tmp_path / "destination",
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:00:00Z",
    )


def _running(tmp_path: Path):
    plan = _plan(tmp_path)
    initial = build_initial_runtime_horizon_collection_state(plan=plan, created_at="2026-07-17T00:00:00Z")
    return plan, advance_runtime_horizon_collection_state(
        plan=plan,
        previous=initial,
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )


def _persistence_plan(origin="2026-07-17T00:00:00Z", run_id="run-1"):
    paths = [f"artifact-{index}.json" for index in range(8)] + ["manifest.json"]
    return {"prediction_origin": origin, "run_id": run_id, "write_order": paths, "manifest_relpath": "manifest.json"}


def _preflight(plan=None):
    return {
        "runtime_horizon_artifact": {
            "horizons": [
                {"horizon_sec": 0, "source_timestamp": "2026-07-17T00:00:00Z"},
                {"horizon_sec": 300, "source_timestamp": "2026-07-16T23:59:00Z"},
                {"horizon_sec": 900, "source_timestamp": "2026-07-16T23:59:00Z"},
            ]
        },
        "runtime_horizon_persistence_plan": plan or _persistence_plan(),
        "runtime_horizon_writer_registered": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
    }


def _write_result(plan=None):
    plan = plan or _persistence_plan()
    return {
        "written_paths": tuple(plan["write_order"]),
        "duplicate_paths": (),
        "written_count": 9,
        "duplicate_count": 0,
        "manifest_relpath": plan["manifest_relpath"],
        "manifest_written_last": True,
        "latest_pointer_created": False,
        "writer_registered": False,
        "producer_loop_enabled": False,
        "scheduler_enabled": False,
        "websocket_opened": False,
        "order_submission_allowed": False,
    }


def test_requires_running_state(tmp_path) -> None:
    plan = _plan(tmp_path)
    state = build_initial_runtime_horizon_collection_state(plan=plan)
    with pytest.raises(PermissionError, match="running_state_required"):
        execute_runtime_horizon_collection_tick(
            tmp_path,
            plan=plan,
            state=state,
            observed_at="2026-07-17T00:01:01Z",
            preflight_builder=lambda: _preflight(),
            readiness_builder=lambda preflight: {"ready": True, "blockers": ()},
            writer=lambda persistence_plan: _write_result(persistence_plan),
        )


def test_duplicate_origin_skips_before_readiness_and_writer(tmp_path) -> None:
    plan, state = _running(tmp_path)
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="WRITE_OK",
        observed_at="2026-07-17T00:01:01Z",
        prediction_origin="2026-07-17T00:00:00Z",
        closed_source_timestamp="2026-07-16T23:59:00Z",
        run_id="run-old",
    )
    calls = {"readiness": 0, "writer": 0}
    result = execute_runtime_horizon_collection_tick(
        tmp_path,
        plan=plan,
        state=state,
        observed_at="2026-07-17T00:02:01Z",
        preflight_builder=lambda: _preflight(),
        readiness_builder=lambda preflight: calls.__setitem__("readiness", calls["readiness"] + 1),
        writer=lambda persistence_plan: calls.__setitem__("writer", calls["writer"] + 1),
    )
    assert result["event"] == "DUPLICATE_ORIGIN_SKIP"
    assert calls == {"readiness": 0, "writer": 0}
    assert result["state"]["duplicate_origin_skip_count"] == 1


def test_readiness_failure_skips_without_writer(tmp_path) -> None:
    plan, state = _running(tmp_path)
    calls = {"writer": 0}
    result = execute_runtime_horizon_collection_tick(
        tmp_path,
        plan=plan,
        state=state,
        observed_at="2026-07-17T00:01:01Z",
        preflight_builder=lambda: _preflight(),
        readiness_builder=lambda preflight: {"ready": False, "blockers": ("source_not_current:300",)},
        writer=lambda persistence_plan: calls.__setitem__("writer", 1),
    )
    assert result["event"] == "READINESS_SKIP"
    assert result["writer_invoked"] is False
    assert calls["writer"] == 0
    assert result["state"]["readiness_skip_count"] == 1


def test_destination_conflict_is_terminal_without_writer(tmp_path) -> None:
    plan, state = _running(tmp_path)
    result = execute_runtime_horizon_collection_tick(
        tmp_path,
        plan=plan,
        state=state,
        observed_at="2026-07-17T00:01:01Z",
        preflight_builder=lambda: _preflight(),
        readiness_builder=lambda preflight: {"ready": False, "blockers": ("destination_conflict:manifest.json",)},
        writer=lambda persistence_plan: pytest.fail("writer must not run"),
    )
    assert result["event"] == "CONFLICT"
    assert result["state"]["status"] == "FAILED_CONFLICT"
    assert result["state"]["active"] is False


def test_ready_tick_writes_once_and_persists_state(tmp_path) -> None:
    plan, state = _running(tmp_path)
    calls = {"writer": 0}
    persistence = _persistence_plan()

    def writer(received):
        calls["writer"] += 1
        assert received is persistence
        return _write_result(received)

    result = execute_runtime_horizon_collection_tick(
        tmp_path,
        plan=plan,
        state=state,
        observed_at="2026-07-17T00:01:01Z",
        preflight_builder=lambda: _preflight(persistence),
        readiness_builder=lambda preflight: {"ready": True, "blockers": ()},
        writer=writer,
    )
    assert result["event"] == "WRITE_OK"
    assert result["writer_invoked"] is True
    assert calls["writer"] == 1
    assert result["state"]["written_origin_count"] == 1
    paths = collection_state_paths(tmp_path, plan)
    state_file = json.loads(paths["state"].read_text(encoding="utf-8"))
    assert state_file["completed_prediction_origins"] == ["2026-07-17T00:00:00Z"]


def test_mixed_written_and_duplicate_receipt_is_accepted(tmp_path) -> None:
    plan, state = _running(tmp_path)
    persistence = _persistence_plan()
    result = _write_result(persistence)
    result.update({
        "written_paths": tuple(persistence["write_order"][:4]),
        "duplicate_paths": tuple(persistence["write_order"][4:]),
        "written_count": 4,
        "duplicate_count": 5,
        "manifest_written_last": True,
    })
    output = execute_runtime_horizon_collection_tick(
        tmp_path,
        plan=plan,
        state=state,
        observed_at="2026-07-17T00:01:01Z",
        preflight_builder=lambda: _preflight(persistence),
        readiness_builder=lambda preflight: {"ready": True, "blockers": ()},
        writer=lambda received: result,
    )
    assert output["event"] == "WRITE_OK"


def test_invalid_receipt_never_advances_state(tmp_path) -> None:
    plan, state = _running(tmp_path)
    bad = _write_result()
    bad["manifest_relpath"] = "wrong.json"
    with pytest.raises(ValueError, match="manifest_receipt_mismatch"):
        execute_runtime_horizon_collection_tick(
            tmp_path,
            plan=plan,
            state=state,
            observed_at="2026-07-17T00:01:01Z",
            preflight_builder=lambda: _preflight(),
            readiness_builder=lambda preflight: {"ready": True, "blockers": ()},
            writer=lambda persistence_plan: bad,
        )
    assert not collection_state_paths(tmp_path, plan)["state"].exists()


def test_preflight_safety_violation_rejected_before_readiness(tmp_path) -> None:
    plan, state = _running(tmp_path)
    preflight = dict(_preflight())
    preflight["scheduler_enabled"] = True
    with pytest.raises(ValueError, match="preflight_safety_invalid:scheduler_enabled"):
        execute_runtime_horizon_collection_tick(
            tmp_path,
            plan=plan,
            state=state,
            observed_at="2026-07-17T00:01:01Z",
            preflight_builder=lambda: preflight,
            readiness_builder=lambda value: pytest.fail("readiness must not run"),
            writer=lambda value: pytest.fail("writer must not run"),
        )


def test_closed_source_duplicate_skips_even_with_new_prediction_origin(tmp_path) -> None:
    plan, state = _running(tmp_path)
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="WRITE_OK",
        observed_at="2026-07-17T00:01:01Z",
        prediction_origin="2026-07-17T00:00:00Z",
        closed_source_timestamp="2026-07-16T23:59:00Z",
        run_id="run-old",
    )
    preflight = _preflight(_persistence_plan(origin="2026-07-17T00:00:30Z", run_id="run-new"))
    result = execute_runtime_horizon_collection_tick(
        tmp_path,
        plan=plan,
        state=state,
        observed_at="2026-07-17T00:02:01Z",
        preflight_builder=lambda: preflight,
        readiness_builder=lambda value: pytest.fail("readiness must not run"),
        writer=lambda value: pytest.fail("writer must not run"),
    )
    assert result["event"] == "DUPLICATE_ORIGIN_SKIP"
    assert result["closed_source_timestamp"] == "2026-07-16T23:59:00Z"
    assert result["writer_invoked"] is False
