# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_persistence.py
# desc: MR-F9.19C once-only atomic writer tests against temporary roots only.

from __future__ import annotations

import copy
import json

import pytest

from btcts.prediction.market_regime.runtime_horizon_persistence import (
    persist_runtime_horizon_plan_once,
)
from btcts.prediction.market_regime.runtime_horizon_persistence_plan import (
    EXPECTED_HORIZONS,
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


def _plan() -> dict:
    return dict(build_runtime_horizon_persistence_plan(artifact=_artifact()))


def test_writer_is_disabled_by_default_and_requires_once_ack(tmp_path) -> None:
    plan = _plan()
    with pytest.raises(PermissionError, match="disabled_by_default"):
        persist_runtime_horizon_plan_once(tmp_path, plan=plan)
    with pytest.raises(PermissionError, match="once_ack_required"):
        persist_runtime_horizon_plan_once(tmp_path, plan=plan, enabled=True)
    with pytest.raises(ValueError, match="flags_invalid"):
        persist_runtime_horizon_plan_once(tmp_path, plan=plan, enabled=1, once=True)


def test_writer_persists_eight_artifacts_then_manifest_and_is_idempotent(tmp_path) -> None:
    plan = _plan()
    first = persist_runtime_horizon_plan_once(
        tmp_path, plan=plan, enabled=True, once=True
    )
    assert first["written"] is True
    assert first["written_count"] == 9
    assert first["duplicate_count"] == 0
    assert first["written_paths"][-1] == plan["manifest_relpath"]
    assert first["manifest_written_last"] is True
    assert first["latest_pointer_created"] is False
    assert first["writer_registered"] is False
    assert first["producer_loop_enabled"] is False
    assert first["websocket_opened"] is False

    for item in plan["horizon_artifacts"]:
        path = tmp_path / item["artifact_relpath"]
        assert path.exists()
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["horizon_sec"] == item["horizon_sec"]
    assert (tmp_path / plan["manifest_relpath"]).exists()

    second = persist_runtime_horizon_plan_once(
        tmp_path, plan=plan, enabled=True, once=True
    )
    assert second["written"] is False
    assert second["duplicate"] is True
    assert second["written_count"] == 0
    assert second["duplicate_count"] == 9


def test_writer_resumes_missing_horizon_and_rewrites_manifest_last(tmp_path) -> None:
    plan = _plan()
    persist_runtime_horizon_plan_once(tmp_path, plan=plan, enabled=True, once=True)
    missing = plan["horizon_artifacts"][3]["artifact_relpath"]
    (tmp_path / missing).unlink()
    (tmp_path / plan["manifest_relpath"]).unlink()

    result = persist_runtime_horizon_plan_once(
        tmp_path, plan=plan, enabled=True, once=True
    )
    assert result["written_paths"] == (missing, plan["manifest_relpath"])
    assert result["manifest_written_last"] is True
    assert result["duplicate_count"] == 7


def test_writer_detects_all_conflicts_before_writing_any_missing_path(tmp_path) -> None:
    plan = _plan()
    first = plan["horizon_artifacts"][0]["artifact_relpath"]
    second = plan["horizon_artifacts"][1]["artifact_relpath"]
    first_path = tmp_path / first
    first_path.parent.mkdir(parents=True, exist_ok=True)
    first_path.write_text("conflict\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="existing_conflict"):
        persist_runtime_horizon_plan_once(
            tmp_path, plan=plan, enabled=True, once=True
        )

    assert not (tmp_path / second).exists()
    assert not (tmp_path / plan["manifest_relpath"]).exists()


def test_writer_rejects_tampered_digest_manifest_refs_and_path_escape(tmp_path) -> None:
    plan = _plan()

    bad_digest = copy.deepcopy(plan)
    bad_digest["horizon_artifacts"][0]["payload_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="payload_digest_mismatch"):
        persist_runtime_horizon_plan_once(
            tmp_path, plan=bad_digest, enabled=True, once=True
        )

    bad_refs = copy.deepcopy(plan)
    bad_refs["manifest_payload"]["horizon_artifacts"][0]["trace_id"] = "tampered"
    with pytest.raises(ValueError, match="manifest_refs_mismatch"):
        persist_runtime_horizon_plan_once(
            tmp_path, plan=bad_refs, enabled=True, once=True
        )

    escaped = copy.deepcopy(plan)
    escaped["manifest_relpath"] = (
        "prediction/market_regime/runtime_horizons/date=2026-07-16/../../escape.json"
    )
    with pytest.raises(ValueError, match="relpath_invalid"):
        persist_runtime_horizon_plan_once(
            tmp_path, plan=escaped, enabled=True, once=True
        )


def test_writer_rejects_runtime_activation_tampering(tmp_path) -> None:
    for key in (
        "writer_registered",
        "producer_loop_enabled",
        "scheduler_enabled",
        "websocket_opened",
        "order_submission_allowed",
    ):
        plan = _plan()
        plan[key] = True
        with pytest.raises(ValueError, match=f"plan_safety_invalid:{key}"):
            persist_runtime_horizon_plan_once(
                tmp_path, plan=plan, enabled=True, once=True
            )
