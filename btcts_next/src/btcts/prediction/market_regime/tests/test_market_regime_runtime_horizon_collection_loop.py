# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_loop.py
# desc: MR-F9.19L restart-safe foreground collection loop tests.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from btcts.prediction.market_regime.runtime_horizon_collection_contract import build_runtime_horizon_collection_plan
from btcts.prediction.market_regime.runtime_horizon_collection_loop import run_runtime_horizon_collection_foreground_loop
from btcts.prediction.market_regime.runtime_horizon_collection_lease import (
    acquire_runtime_horizon_collection_lease,
    read_runtime_horizon_collection_lease,
)
from btcts.prediction.market_regime.runtime_horizon_collection_state import (
    advance_runtime_horizon_collection_state,
    build_initial_runtime_horizon_collection_state,
    collection_state_paths,
    read_runtime_horizon_collection_state,
    write_runtime_horizon_collection_state,
    request_runtime_horizon_collection_stop,
)


def _dt(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def _plan(tmp_path: Path, start="2026-07-17T00:00:00Z"):
    return build_runtime_horizon_collection_plan(
        source_root=tmp_path / "source",
        destination_root=tmp_path / "destination",
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc=start,
    )


def test_completes_at_planned_end_without_tick(tmp_path) -> None:
    plan = _plan(tmp_path)
    times = iter([_dt("2026-07-18T00:00:00Z"), _dt("2026-07-18T00:00:00Z")])
    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=lambda state, observed_at: (_ for _ in ()).throw(AssertionError("tick must not run")),
        now_provider=lambda: next(times),
        sleep_fn=lambda seconds: None,
    )
    assert result["ok"] is True
    assert result["stop_reason"] == "planned_end_reached"
    assert result["loop_iterations"] == 0
    assert result["state"]["status"] == "COMPLETED"
    assert collection_state_paths(tmp_path, plan)["completion_receipt"].exists()


def test_one_tick_then_completion(tmp_path) -> None:
    plan = _plan(tmp_path)
    times = iter([
        _dt("2026-07-17T00:00:00Z"),
        _dt("2026-07-17T00:00:01Z"),
        _dt("2026-07-18T00:00:00Z"),
    ])
    sleeps = []

    def tick(state, observed_at):
        next_state = advance_runtime_horizon_collection_state(
            plan=plan,
            previous=state,
            event="READINESS_SKIP",
            observed_at=observed_at,
            reason="source_not_current",
        )
        write_runtime_horizon_collection_state(tmp_path, plan=plan, state=next_state)
        return {"event": "READINESS_SKIP", "state": next_state, "writer_invoked": False}

    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=tick,
        now_provider=lambda: next(times),
        sleep_fn=sleeps.append,
    )
    assert result["ok"] is True
    assert result["loop_iterations"] == 1
    assert sleeps == [60.0]
    assert result["state"]["readiness_skip_count"] == 1


def test_restart_resumes_persisted_running_state(tmp_path) -> None:
    plan = _plan(tmp_path)
    initial = build_initial_runtime_horizon_collection_state(plan=plan, created_at="2026-07-17T00:00:00Z")
    running = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=initial,
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    previous = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=running,
        event="READINESS_SKIP",
        observed_at="2026-07-17T00:01:01Z",
    )
    write_runtime_horizon_collection_state(tmp_path, plan=plan, state=previous)
    times = iter([_dt("2026-07-18T00:00:00Z")])
    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=lambda state, observed_at: (_ for _ in ()).throw(AssertionError("tick must not run")),
        now_provider=lambda: next(times),
        sleep_fn=lambda seconds: None,
    )
    assert result["state"]["iteration_count"] == 1
    assert result["state"]["readiness_skip_count"] == 1
    assert result["state"]["status"] == "COMPLETED"


def test_persisted_paused_state_resumes_then_stops_on_request(tmp_path) -> None:
    plan = _plan(tmp_path)
    initial = build_initial_runtime_horizon_collection_state(plan=plan, created_at="2026-07-17T00:00:00Z")
    running = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=initial,
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    paused = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=running,
        event="PAUSE",
        observed_at="2026-07-17T00:00:02Z",
    )
    paused = {**paused, "stop_requested": True}
    write_runtime_horizon_collection_state(tmp_path, plan=plan, state=paused)
    times = iter([_dt("2026-07-17T00:00:03Z"), _dt("2026-07-17T00:00:03Z")])
    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=lambda state, observed_at: (_ for _ in ()).throw(AssertionError("tick must not run")),
        now_provider=lambda: next(times),
        sleep_fn=lambda seconds: None,
    )
    assert result["stop_reason"] == "stop_requested"
    assert result["state"]["status"] == "PAUSED"
    assert result["state"]["active"] is False


def test_tick_exception_fails_closed_and_persists(tmp_path) -> None:
    plan = _plan(tmp_path)
    times = iter([
        _dt("2026-07-17T00:00:00Z"),
        _dt("2026-07-17T00:00:01Z"),
        _dt("2026-07-17T00:00:01Z"),
    ])
    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=lambda state, observed_at: (_ for _ in ()).throw(RuntimeError("boom")),
        now_provider=lambda: next(times),
        sleep_fn=lambda seconds: None,
    )
    assert result["ok"] is False
    assert result["stop_reason"] == "tick_exception"
    assert result["state"]["status"] == "FAILED_CONTRACT"
    assert "RuntimeError:boom" in result["state"]["last_error"]
    restored = read_runtime_horizon_collection_state(tmp_path, plan=plan)
    assert restored["status"] == "FAILED_CONTRACT"


def test_terminal_state_is_not_restarted(tmp_path) -> None:
    plan = _plan(tmp_path)
    initial = build_initial_runtime_horizon_collection_state(plan=plan, created_at="2026-07-17T00:00:00Z")
    running = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=initial,
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    completed = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=running,
        event="COMPLETE",
        observed_at="2026-07-18T00:00:00Z",
    )
    write_runtime_horizon_collection_state(tmp_path, plan=plan, state=completed)
    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=lambda state, observed_at: (_ for _ in ()).throw(AssertionError("tick must not run")),
        now_provider=lambda: (_ for _ in ()).throw(AssertionError("clock must not run")),
        sleep_fn=lambda seconds: None,
    )
    assert result["event"] == "ALREADY_TERMINAL"
    assert result["ok"] is True


def test_safety_flags_remain_disabled(tmp_path) -> None:
    plan = _plan(tmp_path)
    times = iter([_dt("2026-07-18T00:00:00Z"), _dt("2026-07-18T00:00:00Z")])
    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=lambda state, observed_at: {},
        now_provider=lambda: next(times),
        sleep_fn=lambda seconds: None,
    )
    for key in (
        "writer_registered",
        "scheduler_enabled",
        "detached_process_started",
        "latest_pointer_created",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        assert result[key] is False


def test_loop_reloads_external_stop_request_before_next_tick(tmp_path) -> None:
    plan = _plan(tmp_path)
    times = iter([
        _dt("2026-07-17T00:00:00Z"),
        _dt("2026-07-17T00:00:01Z"),
        _dt("2026-07-17T00:01:01Z"),
    ])
    tick_count = 0

    def tick(state, observed_at):
        nonlocal tick_count
        tick_count += 1
        next_state = advance_runtime_horizon_collection_state(
            plan=plan,
            previous=state,
            event="READINESS_SKIP",
            observed_at=observed_at,
            reason="source_not_current",
        )
        write_runtime_horizon_collection_state(tmp_path, plan=plan, state=next_state)
        return {"event": "READINESS_SKIP", "state": next_state, "writer_invoked": False}

    def sleep(_seconds):
        request_runtime_horizon_collection_stop(
            tmp_path,
            plan=plan,
            requested_at="2026-07-17T00:00:30Z",
        )

    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=tick,
        now_provider=lambda: next(times),
        sleep_fn=sleep,
    )
    assert tick_count == 1
    assert result["stop_reason"] == "stop_requested"
    assert result["state"]["status"] == "PAUSED"
    assert result["state"]["active"] is False


def test_lease_required_rejects_duplicate_before_tick(tmp_path) -> None:
    plan = _plan(tmp_path)
    acquire_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        acquired_at="2026-07-17T00:00:00Z",
        pid=123,
        lease_id="held",
    )
    with pytest.raises(FileExistsError, match="already_held"):
        run_runtime_horizon_collection_foreground_loop(
            tmp_path,
            plan=plan,
            tick_executor=lambda state, observed_at: pytest.fail("tick must not run"),
            now_provider=lambda: _dt("2026-07-17T00:00:01Z"),
            sleep_fn=lambda seconds: None,
            lease_required=True,
            lease_id="second",
            lease_pid=124,
        )


def test_lease_is_released_on_planned_completion(tmp_path) -> None:
    plan = _plan(tmp_path)
    times = iter([
        _dt("2026-07-17T00:00:00Z"),
        _dt("2026-07-18T00:00:00Z"),
    ])
    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=lambda state, observed_at: pytest.fail("tick must not run"),
        now_provider=lambda: next(times),
        sleep_fn=lambda seconds: None,
        lease_required=True,
        lease_id="lease-a",
        lease_pid=123,
    )
    assert result["lease_acquired"] is True
    assert result["lease_released"] is True
    assert read_runtime_horizon_collection_lease(tmp_path, plan=plan) == {}


def test_lease_is_released_after_tick_exception(tmp_path) -> None:
    plan = _plan(tmp_path)
    times = iter([
        _dt("2026-07-17T00:00:00Z"),
        _dt("2026-07-17T00:00:01Z"),
    ])
    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=lambda state, observed_at: (_ for _ in ()).throw(RuntimeError("boom")),
        now_provider=lambda: next(times),
        sleep_fn=lambda seconds: None,
        lease_required=True,
        lease_id="lease-a",
        lease_pid=123,
    )
    assert result["stop_reason"] == "tick_exception"
    assert result["state"]["status"] == "FAILED_CONTRACT"
    assert result["lease_acquired"] is True
    assert result["lease_released"] is True
    assert read_runtime_horizon_collection_lease(tmp_path, plan=plan) == {}


def test_anchored_cadence_waits_for_start_and_avoids_drift(tmp_path) -> None:
    plan = _plan(tmp_path, start="2026-07-17T00:01:00Z")
    times = iter([
        _dt("2026-07-17T00:00:50Z"),
        _dt("2026-07-17T00:00:50Z"),
        _dt("2026-07-17T00:01:00Z"),
        _dt("2026-07-17T00:01:03Z"),
        _dt("2026-07-17T00:01:07Z"),
        _dt("2026-07-18T00:01:00Z"),
    ])
    sleeps = []

    def tick(state, observed_at):
        next_state = advance_runtime_horizon_collection_state(
            plan=plan,
            previous=state,
            event="READINESS_SKIP",
            observed_at=observed_at,
            reason="source_not_current",
        )
        write_runtime_horizon_collection_state(tmp_path, plan=plan, state=next_state)
        return {"event": "READINESS_SKIP", "state": next_state, "writer_invoked": False}

    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=tick,
        now_provider=lambda: next(times),
        sleep_fn=sleeps.append,
        cadence_anchored=True,
    )
    assert result["ok"] is True
    assert result["cadence_anchored"] is True
    assert sleeps == [10.0, 53.0]


def test_anchored_cadence_sleep_is_bounded_by_end(tmp_path) -> None:
    plan = _plan(tmp_path, start="2026-07-16T00:00:30Z")
    times = iter([
        _dt("2026-07-17T00:00:00Z"),
        _dt("2026-07-17T00:00:00Z"),
        _dt("2026-07-17T00:00:00Z"),
        _dt("2026-07-17T00:00:01Z"),
        _dt("2026-07-17T00:00:10Z"),
        _dt("2026-07-17T00:00:30Z"),
    ])
    sleeps = []

    def tick(state, observed_at):
        next_state = advance_runtime_horizon_collection_state(
            plan=plan,
            previous=state,
            event="READINESS_SKIP",
            observed_at=observed_at,
            reason="source_not_current",
        )
        write_runtime_horizon_collection_state(tmp_path, plan=plan, state=next_state)
        return {"event": "READINESS_SKIP", "state": next_state, "writer_invoked": False}

    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=tick,
        now_provider=lambda: next(times),
        sleep_fn=sleeps.append,
        cadence_anchored=True,
    )
    assert result["stop_reason"] == "planned_end_reached"
    assert sleeps == [20.0]

def test_preacquired_lease_is_verified_and_released(tmp_path) -> None:
    plan = _plan(tmp_path)
    lease = acquire_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        acquired_at="2026-07-17T00:00:00Z",
        pid=123,
        lease_id="lease-a",
    )
    times = iter([_dt("2026-07-18T00:00:00Z")])
    result = run_runtime_horizon_collection_foreground_loop(
        tmp_path,
        plan=plan,
        tick_executor=lambda state, observed_at: pytest.fail("tick must not run"),
        now_provider=lambda: next(times),
        sleep_fn=lambda seconds: None,
        lease_required=True,
        lease_id="lease-a",
        lease_pid=123,
        preacquired_lease=lease,
    )
    assert result["stop_reason"] == "planned_end_reached"
    assert result["lease_acquired"] is True
    assert result["lease_released"] is True
    assert read_runtime_horizon_collection_lease(tmp_path, plan=plan) == {}
