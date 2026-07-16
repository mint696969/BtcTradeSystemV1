# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_write_approval.py
# desc: MR-F9.19G build-only approval token binding tests.

from __future__ import annotations

import copy
import hashlib
import json

import pytest

from btcts.prediction.market_regime.runtime_horizon_persistence_plan import (
    EXPECTED_HORIZONS,
    build_runtime_horizon_persistence_plan,
)
from btcts.prediction.market_regime.runtime_horizon_write_approval import (
    build_runtime_horizon_write_approval_token,
    validate_runtime_horizon_write_approval_token,
)
from btcts.prediction.market_regime.runtime_horizon_write_readiness import (
    build_runtime_horizon_write_readiness_report,
)

ORIGIN = "2026-07-16T16:30:00Z"


def _payload_digest(value: dict) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _artifact() -> dict:
    rows = []
    for horizon in EXPECTED_HORIZONS:
        rows.append({
            "horizon_sec": horizon,
            "trace_id": f"trace:{horizon}",
            "prediction_origin": ORIGIN,
            "source_timestamp": "2026-07-16T16:29:00Z",
            "source_currentness_verified": True,
            "source_freshness_state": "LIVE",
        })
    return {
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


def _inputs(tmp_path):
    artifact = _artifact()
    plan = build_runtime_horizon_persistence_plan(artifact=artifact)
    preflight = {
        "hot_root": str(tmp_path),
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
    readiness = build_runtime_horizon_write_readiness_report(
        preflight=preflight,
        destination_root=tmp_path,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    return readiness, plan


def test_builds_and_validates_exact_build_only_approval_token(tmp_path) -> None:
    readiness, plan = _inputs(tmp_path)
    token = build_runtime_horizon_write_approval_token(
        readiness=readiness,
        plan=plan,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    validate_runtime_horizon_write_approval_token(
        token=token,
        readiness=readiness,
        plan=plan,
    )
    assert token["run_id"] == plan["run_id"]
    assert token["prediction_origin"] == ORIGIN
    assert len(token["artifact_bindings"]) == 8
    assert len(token["write_order"]) == 9
    assert token["write_order"][-1].endswith("/manifest.json")
    assert len(token["readiness_sha256"]) == 64
    assert len(token["approval_token_sha256"]) == 64
    assert token["build_only"] is True
    assert token["writer_invoked"] is False
    assert token["writes_dhot"] is False


def test_acknowledgements_and_operator_are_required(tmp_path) -> None:
    readiness, plan = _inputs(tmp_path)
    with pytest.raises(ValueError, match="operator_missing"):
        build_runtime_horizon_write_approval_token(
            readiness=readiness, plan=plan, operator_id=""
        )
    with pytest.raises(PermissionError, match="enabled_ack_required"):
        build_runtime_horizon_write_approval_token(
            readiness=readiness, plan=plan, operator_id="mint"
        )
    with pytest.raises(PermissionError, match="once_ack_required"):
        build_runtime_horizon_write_approval_token(
            readiness=readiness, plan=plan, operator_id="mint", enabled_acknowledged=True
        )


def test_readiness_run_path_and_digest_changes_invalidate_token(tmp_path) -> None:
    readiness, plan = _inputs(tmp_path)
    token = build_runtime_horizon_write_approval_token(
        readiness=readiness,
        plan=plan,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    cases = []
    changed_readiness = copy.deepcopy(readiness)
    changed_readiness["run_id"] = "run-other"
    cases.append((changed_readiness, plan))
    changed_readiness = copy.deepcopy(readiness)
    changed_readiness["destination_checks"][0]["artifact_relpath"] += ".other"
    cases.append((changed_readiness, plan))
    changed_plan = copy.deepcopy(plan)
    changed_plan["horizon_artifacts"][0]["payload_sha256"] = "0" * 64
    cases.append((readiness, changed_plan))

    for changed_ready, changed_plan in cases:
        with pytest.raises(ValueError):
            validate_runtime_horizon_write_approval_token(
                token=token,
                readiness=changed_ready,
                plan=changed_plan,
            )


def test_not_ready_or_conflicted_readiness_is_rejected(tmp_path) -> None:
    readiness, plan = _inputs(tmp_path)
    blocked = copy.deepcopy(readiness)
    blocked["ready"] = False
    blocked["blockers"] = ("source_not_current:300",)
    with pytest.raises(ValueError, match="readiness_not_ready"):
        build_runtime_horizon_write_approval_token(
            readiness=blocked,
            plan=plan,
            operator_id="mint",
            enabled_acknowledged=True,
            once_acknowledged=True,
        )


def test_token_has_no_write_or_runtime_activation_surface(tmp_path) -> None:
    readiness, plan = _inputs(tmp_path)
    token = build_runtime_horizon_write_approval_token(
        readiness=readiness,
        plan=plan,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
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
        "order_submission_allowed",
    ):
        assert token[key] is False


def test_payload_or_manifest_content_change_with_stale_digest_is_rejected(tmp_path) -> None:
    readiness, plan = _inputs(tmp_path)

    changed_plan = copy.deepcopy(plan)
    changed_plan["horizon_artifacts"][0]["payload"]["trace_id"] = "trace:tampered"
    with pytest.raises(ValueError, match="artifact_digest_mismatch"):
        build_runtime_horizon_write_approval_token(
            readiness=readiness,
            plan=changed_plan,
            operator_id="mint",
            enabled_acknowledged=True,
            once_acknowledged=True,
        )

    changed_plan = copy.deepcopy(plan)
    changed_plan["manifest_payload"]["run_id"] = "run-tampered"
    with pytest.raises(ValueError, match="manifest_digest_mismatch"):
        build_runtime_horizon_write_approval_token(
            readiness=readiness,
            plan=changed_plan,
            operator_id="mint",
            enabled_acknowledged=True,
            once_acknowledged=True,
        )


def test_manifest_semantic_binding_rejects_rehashed_mismatched_artifact_list(tmp_path) -> None:
    readiness, plan = _inputs(tmp_path)
    changed_plan = copy.deepcopy(plan)
    changed_plan["manifest_payload"]["horizon_artifacts"][0]["trace_id"] = "trace:other"
    changed_plan["manifest_payload_sha256"] = _payload_digest(changed_plan["manifest_payload"])

    with pytest.raises(ValueError, match="manifest_artifact_bindings_mismatch"):
        build_runtime_horizon_write_approval_token(
            readiness=readiness,
            plan=changed_plan,
            operator_id="mint",
            enabled_acknowledged=True,
            once_acknowledged=True,
        )


def test_plan_runtime_safety_activation_is_rejected(tmp_path) -> None:
    readiness, plan = _inputs(tmp_path)
    changed_plan = copy.deepcopy(plan)
    changed_plan["producer_loop_enabled"] = True

    with pytest.raises(ValueError, match="plan_safety_invalid:producer_loop_enabled"):
        build_runtime_horizon_write_approval_token(
            readiness=readiness,
            plan=changed_plan,
            operator_id="mint",
            enabled_acknowledged=True,
            once_acknowledged=True,
        )
