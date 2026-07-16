# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_persistence_plan.py
# desc: MR-F9.19B build-only persistence ownership and atomic-write plan tests.

from __future__ import annotations

import copy
from types import MappingProxyType

import pytest

from btcts.prediction.market_regime.runtime_horizon_persistence_plan import (
    EXPECTED_HORIZONS,
    RUNTIME_HORIZON_NAMESPACE,
    build_runtime_horizon_persistence_plan,
)

ORIGIN = "2026-07-16T12:00:00Z"


def _artifact() -> dict:
    rows = []
    for horizon in EXPECTED_HORIZONS:
        rows.append({
            "horizon_sec": horizon,
            "trace_id": f"trace:{horizon}",
            "prediction_origin": ORIGIN,
            "status": "OBSERVED_ESTIMATE" if horizon == 0 else "FORECAST",
            "label": "RANGE",
            "source_timestamp": "2026-07-16T11:59:00Z",
            "source_currentness_verified": True,
            "source_freshness_state": "LIVE",
            "read_only": True,
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


def test_plan_owns_exactly_eight_immutable_horizon_artifacts_and_manifest() -> None:
    plan = build_runtime_horizon_persistence_plan(artifact=_artifact())
    assert plan["source_role"] == "hot_data_root"
    assert plan["namespace"] == RUNTIME_HORIZON_NAMESPACE
    assert plan["horizon_count"] == 8
    assert [row["horizon_sec"] for row in plan["horizon_artifacts"]] == list(EXPECTED_HORIZONS)
    assert len({row["artifact_relpath"] for row in plan["horizon_artifacts"]}) == 8
    assert all(f"horizon={row['horizon_sec']}.json" in row["artifact_relpath"] for row in plan["horizon_artifacts"])
    assert plan["manifest_relpath"].endswith("/manifest.json")
    assert plan["write_order"][-1] == plan["manifest_relpath"]
    assert len(plan["write_order"]) == 9


def test_plan_is_build_only_and_does_not_claim_latest_or_runtime_activation() -> None:
    plan = build_runtime_horizon_persistence_plan(artifact=_artifact())
    assert plan["disabled_by_default"] is True
    assert plan["writer_registered"] is False
    assert plan["would_write"] is False
    assert plan["latest_pointer_created"] is False
    assert plan["canonical_latest_replacement"] is False
    assert plan["scheduler_enabled"] is False
    assert plan["producer_loop_enabled"] is False
    assert plan["websocket_opened"] is False
    assert plan["order_submission_allowed"] is False
    assert plan["manifest_payload"]["latest_pointer_relpath"] is None


def test_atomic_contract_writes_manifest_last() -> None:
    plan = build_runtime_horizon_persistence_plan(artifact=_artifact())
    atomic = plan["atomic_write_contract"]
    assert atomic == {
        "lock_required": True,
        "lock_timeout_sec": 5.0,
        "stale_lock_sec": 60.0,
        "temporary_suffix": ".tmp",
        "replace_operation": "atomic_replace",
        "manifest_written_last": True,
    }


def test_plan_is_deterministic() -> None:
    first = build_runtime_horizon_persistence_plan(artifact=_artifact())
    second = build_runtime_horizon_persistence_plan(artifact=_artifact())
    assert first == second


def test_plan_rejects_missing_horizon_and_unsafe_boundary() -> None:
    missing = _artifact()
    missing["horizons"] = missing["horizons"][:-1]
    missing["horizon_count"] = 7
    with pytest.raises(ValueError, match="horizon_count_invalid"):
        build_runtime_horizon_persistence_plan(artifact=missing)

    unsafe = copy.deepcopy(_artifact())
    unsafe["safety"]["websocket_opened"] = True
    with pytest.raises(ValueError, match="safety_invalid:websocket_opened"):
        build_runtime_horizon_persistence_plan(artifact=unsafe)


def test_plan_rejects_trace_identity_and_origin_mismatch() -> None:
    duplicate = _artifact()
    duplicate["horizons"][1]["trace_id"] = duplicate["horizons"][0]["trace_id"]
    with pytest.raises(ValueError, match="trace_identity_invalid"):
        build_runtime_horizon_persistence_plan(artifact=duplicate)

    mismatch = _artifact()
    mismatch["horizons"][1]["prediction_origin"] = "2026-07-16T12:00:01Z"
    with pytest.raises(ValueError, match="origin_mismatch"):
        build_runtime_horizon_persistence_plan(artifact=mismatch)


def test_plan_accepts_recursive_mappingproxy_runtime_artifact() -> None:
    artifact = _artifact()
    proxied_rows = []
    for row in artifact["horizons"]:
        nested = dict(row)
        nested["metadata"] = MappingProxyType({
            "conditioning": MappingProxyType({
                "applied": True,
                "weights": (0.1, 0.2),
            })
        })
        proxied_rows.append(MappingProxyType(nested))
    proxied = MappingProxyType({
        **artifact,
        "horizons": tuple(proxied_rows),
        "safety": MappingProxyType(dict(artifact["safety"])),
    })

    plan = build_runtime_horizon_persistence_plan(artifact=proxied)

    assert plan["horizon_count"] == 8
    assert len(plan["horizon_artifacts"]) == 8
    assert plan["horizon_artifacts"][1]["payload"]["horizon"]["metadata"] == {
        "conditioning": {
            "applied": True,
            "weights": [0.1, 0.2],
        }
    }
    assert len(plan["horizon_artifacts"][1]["payload_sha256"]) == 64
