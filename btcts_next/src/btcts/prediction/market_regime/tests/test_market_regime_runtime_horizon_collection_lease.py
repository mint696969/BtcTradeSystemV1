# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_lease.py
# desc: MR-F9.19L atomic single-process collection lease tests.

from __future__ import annotations

from pathlib import Path

import pytest

from btcts.prediction.market_regime.runtime_horizon_collection_contract import build_runtime_horizon_collection_plan
from btcts.prediction.market_regime.runtime_horizon_collection_lease import (
    acquire_runtime_horizon_collection_lease,
    heartbeat_runtime_horizon_collection_lease,
    read_runtime_horizon_collection_lease,
    recover_stale_runtime_horizon_collection_lease,
    release_runtime_horizon_collection_lease,
    runtime_horizon_collection_lease_path,
)


def _plan(tmp_path: Path):
    return build_runtime_horizon_collection_plan(
        source_root=tmp_path / "source",
        destination_root=tmp_path / "destination",
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:00:00Z",
    )


def test_atomic_acquire_and_duplicate_rejection(tmp_path) -> None:
    plan = _plan(tmp_path)
    first = acquire_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        acquired_at="2026-07-17T00:00:00Z",
        pid=123,
        lease_id="lease-a",
    )
    assert first["lease_id"] == "lease-a"
    assert runtime_horizon_collection_lease_path(tmp_path, plan=plan).exists()
    with pytest.raises(FileExistsError, match="already_held:lease-a:123"):
        acquire_runtime_horizon_collection_lease(
            tmp_path,
            plan=plan,
            acquired_at="2026-07-17T00:00:01Z",
            pid=124,
            lease_id="lease-b",
        )


def test_heartbeat_requires_same_lease_and_pid(tmp_path) -> None:
    plan = _plan(tmp_path)
    acquire_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        acquired_at="2026-07-17T00:00:00Z",
        pid=123,
        lease_id="lease-a",
    )
    updated = heartbeat_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        lease_id="lease-a",
        heartbeat_at="2026-07-17T00:01:00Z",
        pid=123,
    )
    assert updated["heartbeat_at"] == "2026-07-17T00:01:00Z"
    with pytest.raises(PermissionError, match="id_mismatch"):
        heartbeat_runtime_horizon_collection_lease(
            tmp_path,
            plan=plan,
            lease_id="lease-b",
            heartbeat_at="2026-07-17T00:02:00Z",
            pid=123,
        )
    with pytest.raises(PermissionError, match="pid_mismatch"):
        heartbeat_runtime_horizon_collection_lease(
            tmp_path,
            plan=plan,
            lease_id="lease-a",
            heartbeat_at="2026-07-17T00:02:00Z",
            pid=124,
        )


def test_release_is_owner_only_and_idempotent(tmp_path) -> None:
    plan = _plan(tmp_path)
    acquire_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        acquired_at="2026-07-17T00:00:00Z",
        pid=123,
        lease_id="lease-a",
    )
    with pytest.raises(PermissionError, match="id_mismatch"):
        release_runtime_horizon_collection_lease(
            tmp_path,
            plan=plan,
            lease_id="lease-b",
            pid=123,
        )
    released = release_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        lease_id="lease-a",
        pid=123,
    )
    assert released["already_released"] is False
    again = release_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        lease_id="lease-a",
        pid=123,
    )
    assert again["already_released"] is True


def test_stale_recovery_is_explicit_and_age_guarded(tmp_path) -> None:
    plan = _plan(tmp_path)
    acquire_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        acquired_at="2026-07-17T00:00:00Z",
        pid=123,
        lease_id="lease-a",
    )
    with pytest.raises(PermissionError, match="not_stale:60"):
        recover_stale_runtime_horizon_collection_lease(
            tmp_path,
            plan=plan,
            expected_lease_id="lease-a",
            observed_at="2026-07-17T00:01:00Z",
            minimum_stale_sec=120,
        )
    recovered = recover_stale_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        expected_lease_id="lease-a",
        observed_at="2026-07-17T00:02:00Z",
        minimum_stale_sec=120,
    )
    assert recovered["stale_age_sec"] == 120
    assert read_runtime_horizon_collection_lease(tmp_path, plan=plan) == {}


def test_stale_recovery_requires_expected_lease_id(tmp_path) -> None:
    plan = _plan(tmp_path)
    acquire_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        acquired_at="2026-07-17T00:00:00Z",
        pid=123,
        lease_id="lease-a",
    )
    with pytest.raises(PermissionError, match="expected_id_mismatch"):
        recover_stale_runtime_horizon_collection_lease(
            tmp_path,
            plan=plan,
            expected_lease_id="lease-b",
            observed_at="2026-07-17T00:10:00Z",
            minimum_stale_sec=120,
        )


def test_lease_safety_flags_remain_disabled(tmp_path) -> None:
    plan = _plan(tmp_path)
    lease = acquire_runtime_horizon_collection_lease(
        tmp_path,
        plan=plan,
        acquired_at="2026-07-17T00:00:00Z",
        pid=123,
        lease_id="lease-a",
    )
    for key in ("writer_registered", "scheduler_enabled", "detached_process_started", "writes_dhot"):
        assert lease[key] is False
