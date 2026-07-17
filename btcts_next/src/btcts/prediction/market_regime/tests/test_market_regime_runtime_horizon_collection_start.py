# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_start.py
# desc: MR-F9.19N exact-human-authorized foreground start wiring tests.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from btcts.prediction.market_regime.runtime_horizon_collection_authorization import (
    build_runtime_horizon_collection_start_authorization_package,
)
from btcts.prediction.market_regime.runtime_horizon_collection_contract import (
    build_runtime_horizon_collection_plan,
)
from btcts.prediction.market_regime.runtime_horizon_collection_lease import (
    read_runtime_horizon_collection_lease,
)
from btcts.prediction.market_regime.runtime_horizon_collection_start import (
    run_authorized_runtime_horizon_collection_start,
)
from btcts.prediction.market_regime.runtime_horizon_collection_state import (
    read_runtime_horizon_collection_state,
)


def _dt(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def _prepared(tmp_path: Path):
    root = tmp_path / "dhot"
    plan = build_runtime_horizon_collection_plan(
        source_root=root,
        destination_root=root,
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:01:00Z",
    )
    package = build_runtime_horizon_collection_start_authorization_package(
        plan=plan,
        created_at="2026-07-17T00:00:30Z",
        expected_dhot_root=root,
        ttl_sec=120,
    )
    return root, plan, package


def test_exact_text_root_and_ttl_fail_before_loop(tmp_path) -> None:
    root, plan, package = _prepared(tmp_path)
    fail_loop = lambda *args, **kwargs: pytest.fail("loop must not run")
    with pytest.raises(PermissionError, match="exact_authorization_text_mismatch"):
        run_authorized_runtime_horizon_collection_start(
            root,
            plan=plan,
            authorization_package=package,
            provided_authorization_text="wrong",
            expected_root=root,
            now_provider=lambda: _dt("2026-07-17T00:01:00Z"),
            loop_runner=fail_loop,
        )
    with pytest.raises(PermissionError, match="root_binding_mismatch"):
        run_authorized_runtime_horizon_collection_start(
            root,
            plan=plan,
            authorization_package=package,
            provided_authorization_text=package["expected_authorization_text"],
            expected_root=tmp_path / "other",
            now_provider=lambda: _dt("2026-07-17T00:01:00Z"),
            loop_runner=fail_loop,
        )
    with pytest.raises(PermissionError, match="expired"):
        run_authorized_runtime_horizon_collection_start(
            root,
            plan=plan,
            authorization_package=package,
            provided_authorization_text=package["expected_authorization_text"],
            expected_root=root,
            now_provider=lambda: _dt("2026-07-17T00:02:31Z"),
            loop_runner=fail_loop,
        )


def test_lease_and_recovered_planned_state_exist_before_loop(tmp_path) -> None:
    root, plan, package = _prepared(tmp_path)
    observed = {}

    def fake_loop(control_root, **kwargs):
        observed.update(kwargs)
        state = read_runtime_horizon_collection_state(root, plan=plan)
        lease = read_runtime_horizon_collection_lease(root, plan=plan)
        assert state["status"] == "PLANNED"
        assert state["active"] is False
        assert lease["lease_id"] == "lease-a"
        return {
            "ok": False,
            "stop_reason": "test_return",
            "state": state,
            "lease_acquired": True,
            "lease_released": False,
        }

    result = run_authorized_runtime_horizon_collection_start(
        root,
        plan=plan,
        authorization_package=package,
        provided_authorization_text=package["expected_authorization_text"],
        expected_root=root,
        now_provider=lambda: _dt("2026-07-17T00:00:45Z"),
        pid=123,
        lease_id="lease-a",
        loop_runner=fake_loop,
    )
    assert observed["lease_required"] is True
    assert observed["cadence_anchored"] is True
    assert observed["preacquired_lease"]["lease_id"] == "lease-a"
    assert result["authorization_verified"] is True
    assert result["recovery_completed_before_loop"] is True
    assert result["recovered_state_persisted_before_loop"] is True
    assert result["scheduler_enabled"] is False
    assert result["order_submission_allowed"] is False


def test_duplicate_lease_rejects_second_start_before_loop(tmp_path) -> None:
    root, plan, package = _prepared(tmp_path)
    kwargs = {
        "plan": plan,
        "authorization_package": package,
        "provided_authorization_text": package["expected_authorization_text"],
        "expected_root": root,
        "now_provider": lambda: _dt("2026-07-17T00:01:00Z"),
        "pid": 123,
        "lease_id": "lease-a",
        "loop_runner": lambda *args, **kwargs: {"ok": False, "state": {}},
    }
    run_authorized_runtime_horizon_collection_start(root, **kwargs)
    with pytest.raises(FileExistsError, match="already_held"):
        run_authorized_runtime_horizon_collection_start(root, **kwargs)

def test_preloop_failure_releases_newly_acquired_lease(tmp_path) -> None:
    root, plan, package = _prepared(tmp_path)
    from btcts.prediction.market_regime.runtime_horizon_collection_state import (
        advance_runtime_horizon_collection_state,
        build_initial_runtime_horizon_collection_state,
        write_runtime_horizon_collection_state,
    )

    initial = build_initial_runtime_horizon_collection_state(
        plan=plan,
        created_at="2026-07-17T00:00:00Z",
    )
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
        observed_at="2026-07-18T00:01:00Z",
    )
    write_runtime_horizon_collection_state(root, plan=plan, state=completed)

    with pytest.raises(PermissionError, match="terminal_state"):
        run_authorized_runtime_horizon_collection_start(
            root,
            plan=plan,
            authorization_package=package,
            provided_authorization_text=package["expected_authorization_text"],
            expected_root=root,
            now_provider=lambda: _dt("2026-07-17T00:01:00Z"),
            pid=123,
            lease_id="lease-a",
            loop_runner=lambda *args, **kwargs: pytest.fail("loop must not run"),
        )
    assert read_runtime_horizon_collection_lease(root, plan=plan) == {}

def test_loop_runner_exception_releases_preacquired_lease(tmp_path) -> None:
    root, plan, package = _prepared(tmp_path)

    def fail_loop(*args, **kwargs):
        assert read_runtime_horizon_collection_lease(root, plan=plan)["lease_id"] == "lease-a"
        raise RuntimeError("loop exploded")

    with pytest.raises(RuntimeError, match="loop exploded"):
        run_authorized_runtime_horizon_collection_start(
            root,
            plan=plan,
            authorization_package=package,
            provided_authorization_text=package["expected_authorization_text"],
            expected_root=root,
            now_provider=lambda: _dt("2026-07-17T00:00:45Z"),
            pid=123,
            lease_id="lease-a",
            loop_runner=fail_loop,
        )

    assert read_runtime_horizon_collection_lease(root, plan=plan) == {}


def test_default_loop_waits_until_planned_start_before_running(tmp_path) -> None:
    root, plan, package = _prepared(tmp_path)
    times = iter(
        [
            _dt("2026-07-17T00:00:30Z"),
            _dt("2026-07-17T00:00:30Z"),
            _dt("2026-07-17T00:01:00Z"),
            _dt("2026-07-18T00:01:00Z"),
        ]
    )
    sleeps = []

    result = run_authorized_runtime_horizon_collection_start(
        root,
        plan=plan,
        authorization_package=package,
        provided_authorization_text=package["expected_authorization_text"],
        expected_root=root,
        now_provider=lambda: next(times),
        sleep_fn=lambda seconds: sleeps.append(seconds),
        pid=123,
        lease_id="lease-a",
    )

    assert sleeps == [30.0]
    assert result["stop_reason"] == "planned_end_reached"
    assert result["state"]["status"] == "COMPLETED"
    assert result["lease_released"] is True
