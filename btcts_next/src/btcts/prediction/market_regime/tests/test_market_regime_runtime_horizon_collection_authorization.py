# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_authorization.py
# desc: MR-F9.19L bounded 24h collection start-authorization tests.

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from btcts.prediction.market_regime.runtime_horizon_collection_authorization import (
    build_runtime_horizon_collection_start_authorization_package,
    validate_runtime_horizon_collection_start_authorization_package,
)
from btcts.prediction.market_regime.runtime_horizon_collection_contract import (
    build_runtime_horizon_collection_plan,
)

DHOT = r"D:\btc_ts_hot"


def _plan(*, root: str = DHOT, start: str = "2026-07-17T02:00:00Z"):
    return build_runtime_horizon_collection_plan(
        source_root=root,
        destination_root=root,
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc=start,
    )


def test_builds_exact_collection_start_authorization() -> None:
    plan = _plan()
    package = build_runtime_horizon_collection_start_authorization_package(
        plan=plan,
        created_at="2026-07-17T01:59:00Z",
        expected_dhot_root=DHOT,
        ttl_sec=120,
    )
    validate_runtime_horizon_collection_start_authorization_package(
        package=package,
        plan=plan,
        now="2026-07-17T02:00:00Z",
        expected_dhot_root=DHOT,
    )
    assert package["collection_id"] == plan["collection_id"]
    assert package["plan_sha256"] == plan["plan_sha256"]
    assert package["duration_sec"] == 86400
    assert package["cadence_sec"] == 60
    assert package["lease_required"] is True
    assert package["manifest_recovery_required"] is True
    assert package["human_authorized"] is False
    assert len(package["authorization_package_sha256"]) == 64


def test_requires_same_dhot_source_and_destination(tmp_path) -> None:
    wrong = _plan(root=str(tmp_path))
    with pytest.raises(ValueError, match="root_not_dhot"):
        build_runtime_horizon_collection_start_authorization_package(
            plan=wrong,
            created_at="2026-07-17T01:59:00Z",
            expected_dhot_root=DHOT,
        )


def test_start_window_and_ttl_are_bounded() -> None:
    plan = _plan()
    with pytest.raises(ValueError, match="created_after_planned_start"):
        build_runtime_horizon_collection_start_authorization_package(
            plan=plan,
            created_at="2026-07-17T02:00:01Z",
            expected_dhot_root=DHOT,
        )
    with pytest.raises(ValueError, match="start_too_far"):
        build_runtime_horizon_collection_start_authorization_package(
            plan=plan,
            created_at="2026-07-17T01:54:59Z",
            expected_dhot_root=DHOT,
        )
    with pytest.raises(ValueError, match="expires_before_start"):
        build_runtime_horizon_collection_start_authorization_package(
            plan=plan,
            created_at="2026-07-17T01:59:00Z",
            expected_dhot_root=DHOT,
            ttl_sec=30,
        )


def test_package_tampering_and_expiry_are_rejected() -> None:
    plan = _plan()
    package = build_runtime_horizon_collection_start_authorization_package(
        plan=plan,
        created_at="2026-07-17T01:59:00Z",
        expected_dhot_root=DHOT,
        ttl_sec=120,
    )
    changed = copy.deepcopy(package)
    changed["cadence_sec"] = 30
    with pytest.raises(ValueError, match="package_mismatch"):
        validate_runtime_horizon_collection_start_authorization_package(
            package=changed,
            plan=plan,
            now="2026-07-17T02:00:00Z",
            expected_dhot_root=DHOT,
        )
    with pytest.raises(PermissionError, match="expired"):
        validate_runtime_horizon_collection_start_authorization_package(
            package=package,
            plan=plan,
            now="2026-07-17T02:01:01Z",
            expected_dhot_root=DHOT,
        )


def test_runtime_surfaces_remain_disabled() -> None:
    package = build_runtime_horizon_collection_start_authorization_package(
        plan=_plan(),
        created_at="2026-07-17T01:59:00Z",
        expected_dhot_root=DHOT,
    )
    for key in (
        "writer_invoked",
        "writes_dhot",
        "writer_registered",
        "latest_pointer_created",
        "scheduler_enabled",
        "detached_process_started",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        assert package[key] is False
