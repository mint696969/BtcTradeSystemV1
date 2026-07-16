# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_write_authorization.py
# desc: MR-F9.19I read-only limited D-hot one-shot authorization-package tests.

from __future__ import annotations

import copy

import pytest

from btcts.prediction.market_regime.runtime_horizon_persistence_plan import (
    EXPECTED_HORIZONS,
    build_runtime_horizon_persistence_plan,
)
from btcts.prediction.market_regime.runtime_horizon_write_approval import (
    build_runtime_horizon_write_approval_token,
)
from btcts.prediction.market_regime.runtime_horizon_write_authorization import (
    build_runtime_horizon_write_authorization_package,
    validate_runtime_horizon_write_authorization_package,
)
from btcts.prediction.market_regime.runtime_horizon_write_readiness import (
    build_runtime_horizon_write_readiness_report,
)

ORIGIN = "2026-07-16T18:00:00Z"
CREATED = "2026-07-16T18:00:10Z"
DHOT = r"D:\btc_ts_hot"


def _inputs(tmp_path):
    rows = [
        {
            "horizon_sec": horizon,
            "trace_id": f"trace:{horizon}",
            "prediction_origin": ORIGIN,
            "source_timestamp": "2026-07-16T17:59:00Z",
            "source_currentness_verified": True,
            "source_freshness_state": "LIVE",
        }
        for horizon in EXPECTED_HORIZONS
    ]
    artifact = {
        "prediction_origin": ORIGIN,
        "horizon_count": 8,
        "horizons": rows,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "safety": {
            "writes_dhot": False,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "websocket_opened": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_submission_allowed": False,
            "canonical_replacement": False,
        },
    }
    plan = build_runtime_horizon_persistence_plan(artifact=artifact)
    preflight = {
        "hot_root": DHOT,
        "runtime_horizon_artifact": artifact,
        "runtime_horizon_artifact_built": True,
        "runtime_horizon_artifact_persisted": False,
        "runtime_horizon_persistence_plan": plan,
        "runtime_horizon_persistence_plan_built": True,
        "runtime_horizon_writer_registered": False,
        "writer_invoked": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "producer_loop_enabled": False,
        "broker_private_api_allowed": False,
        "autotrade_trigger_allowed": False,
        "order_submission_allowed": False,
        "auto_promotion_allowed": False,
        "live_parameter_apply_allowed": False,
    }
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            "btcts.prediction.market_regime.runtime_horizon_write_readiness._path_state",
            lambda path, expected: "missing",
        )
        readiness = build_runtime_horizon_write_readiness_report(
            preflight=preflight,
            destination_root=DHOT,
            operator_id="mint",
            enabled_acknowledged=True,
            once_acknowledged=True,
        )
    token = build_runtime_horizon_write_approval_token(
        readiness=readiness,
        plan=plan,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    return readiness, plan, token


def test_builds_exact_read_only_authorization_package(tmp_path) -> None:
    readiness, plan, token = _inputs(tmp_path)
    package = build_runtime_horizon_write_authorization_package(
        token=token,
        readiness=readiness,
        plan=plan,
        created_at=CREATED,
        ttl_sec=300,
        expected_dhot_root=DHOT,
    )
    validate_runtime_horizon_write_authorization_package(
        package=package,
        token=token,
        readiness=readiness,
        plan=plan,
        now="2026-07-16T18:04:59Z",
        expected_dhot_root=DHOT,
    )
    assert package["destination_root"].lower().endswith("btc_ts_hot")
    assert package["run_id"] == token["run_id"]
    assert package["origin_age_sec_at_package_creation"] == 10
    assert package["approval_token_sha256"] == token["approval_token_sha256"]
    assert len(package["artifact_bindings"]) == 8
    assert len(package["write_order"]) == 9
    assert package["write_order"][-1].endswith("/manifest.json")
    assert package["human_authorized"] is False
    assert package["awaiting_explicit_human_authorization"] is True
    assert package["writer_invoked"] is False
    assert package["writes_dhot"] is False
    assert len(package["expected_authorization_text_sha256"]) == 64
    assert len(package["authorization_package_sha256"]) == 64


def test_wrong_destination_and_invalid_ttl_are_rejected(tmp_path) -> None:
    readiness, plan, token = _inputs(tmp_path)

    wrong_readiness = copy.deepcopy(readiness)
    wrong_readiness["destination_root"] = str(tmp_path.resolve())
    wrong_token = build_runtime_horizon_write_approval_token(
        readiness=wrong_readiness,
        plan=plan,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    with pytest.raises(ValueError, match="destination_not_dhot"):
        build_runtime_horizon_write_authorization_package(
            token=wrong_token,
            readiness=wrong_readiness,
            plan=plan,
            created_at=CREATED,
            expected_dhot_root=DHOT,
        )

    with pytest.raises(ValueError, match="ttl_invalid"):
        build_runtime_horizon_write_authorization_package(
            token=token,
            readiness=readiness,
            plan=plan,
            created_at=CREATED,
            ttl_sec=301,
            expected_dhot_root=DHOT,
        )


def test_package_expires_and_is_not_valid_before_creation(tmp_path) -> None:
    readiness, plan, token = _inputs(tmp_path)
    package = build_runtime_horizon_write_authorization_package(
        token=token,
        readiness=readiness,
        plan=plan,
        created_at=CREATED,
        ttl_sec=300,
        expected_dhot_root=DHOT,
    )
    with pytest.raises(ValueError, match="not_yet_valid"):
        validate_runtime_horizon_write_authorization_package(
            package=package,
            token=token,
            readiness=readiness,
            plan=plan,
            now="2026-07-16T18:00:09Z",
            expected_dhot_root=DHOT,
        )
    with pytest.raises(PermissionError, match="expired"):
        validate_runtime_horizon_write_authorization_package(
            package=package,
            token=token,
            readiness=readiness,
            plan=plan,
            now="2026-07-16T18:05:11Z",
            expected_dhot_root=DHOT,
        )


def test_token_plan_or_package_change_is_rejected(tmp_path) -> None:
    readiness, plan, token = _inputs(tmp_path)
    package = build_runtime_horizon_write_authorization_package(
        token=token,
        readiness=readiness,
        plan=plan,
        created_at=CREATED,
        expected_dhot_root=DHOT,
    )
    changed_package = copy.deepcopy(package)
    changed_package["write_order"] = tuple(reversed(changed_package["write_order"]))
    with pytest.raises(ValueError, match="package_mismatch"):
        validate_runtime_horizon_write_authorization_package(
            package=changed_package,
            token=token,
            readiness=readiness,
            plan=plan,
            now=CREATED,
            expected_dhot_root=DHOT,
        )

    changed_token = copy.deepcopy(token)
    changed_token["approval_token_sha256"] = "0" * 64
    with pytest.raises(ValueError):
        validate_runtime_horizon_write_authorization_package(
            package=package,
            token=changed_token,
            readiness=readiness,
            plan=plan,
            now=CREATED,
            expected_dhot_root=DHOT,
        )


def test_package_has_no_writer_or_runtime_activation_surface(tmp_path) -> None:
    readiness, plan, token = _inputs(tmp_path)
    package = build_runtime_horizon_write_authorization_package(
        token=token,
        readiness=readiness,
        plan=plan,
        created_at=CREATED,
        expected_dhot_root=DHOT,
    )
    for key in (
        "writer_invoked",
        "writes_dhot",
        "writer_registered",
        "latest_pointer_created",
        "scheduler_enabled",
        "producer_loop_enabled",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        assert package[key] is False

def test_package_creation_is_bound_to_fresh_prediction_origin(tmp_path) -> None:
    readiness, plan, token = _inputs(tmp_path)

    with pytest.raises(ValueError, match="created_before_origin"):
        build_runtime_horizon_write_authorization_package(
            token=token,
            readiness=readiness,
            plan=plan,
            created_at="2026-07-16T17:59:59Z",
            expected_dhot_root=DHOT,
        )

    with pytest.raises(PermissionError, match="origin_too_old"):
        build_runtime_horizon_write_authorization_package(
            token=token,
            readiness=readiness,
            plan=plan,
            created_at="2026-07-16T18:05:01Z",
            expected_dhot_root=DHOT,
        )

    boundary = build_runtime_horizon_write_authorization_package(
        token=token,
        readiness=readiness,
        plan=plan,
        created_at="2026-07-16T18:05:00Z",
        expected_dhot_root=DHOT,
    )
    assert boundary["origin_age_sec_at_package_creation"] == 300
