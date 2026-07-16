# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_write_readiness.py
# desc: MR-F9.19F build-only D-hot write-readiness report tests.

from __future__ import annotations

import copy
import json

import pytest

from btcts.prediction.market_regime.runtime_horizon_persistence_plan import (
    EXPECTED_HORIZONS,
    build_runtime_horizon_persistence_plan,
)
from btcts.prediction.market_regime.runtime_horizon_write_readiness import (
    build_runtime_horizon_write_readiness_report,
)

ORIGIN = "2026-07-16T16:00:00Z"


def _artifact() -> dict:
    rows = []
    for horizon in EXPECTED_HORIZONS:
        rows.append({
            "horizon_sec": horizon,
            "trace_id": f"trace:{horizon}",
            "prediction_origin": ORIGIN,
            "source_timestamp": "2026-07-16T15:59:00Z",
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


def _preflight(root) -> dict:
    artifact = _artifact()
    return {
        "hot_root": str(root),
        "runtime_horizon_artifact": artifact,
        "runtime_horizon_artifact_built": True,
        "runtime_horizon_artifact_persisted": False,
        "runtime_horizon_persistence_plan": build_runtime_horizon_persistence_plan(artifact=artifact),
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


def test_ready_when_sources_are_live_paths_missing_and_acknowledged(tmp_path) -> None:
    report = build_runtime_horizon_write_readiness_report(
        preflight=_preflight(tmp_path),
        destination_root=tmp_path,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    assert report["ready"] is True
    assert report["blockers"] == ()
    assert report["destination_state_counts"] == {"missing": 9, "duplicate": 0, "conflict": 0}
    assert report["manifest_written_last_planned"] is True
    assert report["build_only"] is True
    assert report["writer_invoked"] is False
    assert report["writes_dhot"] is False


def test_missing_acknowledgements_and_stale_sources_block_readiness(tmp_path) -> None:
    preflight = _preflight(tmp_path)
    preflight["runtime_horizon_artifact"]["horizons"][1]["source_currentness_verified"] = False
    preflight["runtime_horizon_artifact"]["horizons"][1]["source_freshness_state"] = "STALE_SOURCE_WINDOW"
    report = build_runtime_horizon_write_readiness_report(
        preflight=preflight,
        destination_root=tmp_path,
        operator_id="",
    )
    assert report["ready"] is False
    assert "operator_id_missing" in report["blockers"]
    assert "enabled_ack_missing" in report["blockers"]
    assert "once_ack_missing" in report["blockers"]
    assert "source_not_current:300" in report["blockers"]


def test_duplicate_and_conflict_states_are_read_only(tmp_path) -> None:
    preflight = _preflight(tmp_path)
    plan = preflight["runtime_horizon_persistence_plan"]
    first = plan["horizon_artifacts"][0]
    duplicate_path = tmp_path / first["artifact_relpath"]
    duplicate_path.parent.mkdir(parents=True, exist_ok=True)
    duplicate_path.write_text(
        json.dumps(first["payload"], ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    conflict = plan["horizon_artifacts"][1]
    conflict_path = tmp_path / conflict["artifact_relpath"]
    conflict_path.write_text("conflict\n", encoding="utf-8")

    report = build_runtime_horizon_write_readiness_report(
        preflight=preflight,
        destination_root=tmp_path,
        operator_id="mint",
        enabled_acknowledged=True,
        once_acknowledged=True,
    )
    assert report["ready"] is False
    assert report["destination_state_counts"] == {"missing": 7, "duplicate": 1, "conflict": 1}
    assert any(item.startswith("destination_conflict:") for item in report["blockers"])
    assert conflict_path.read_text(encoding="utf-8") == "conflict\n"


def test_destination_root_and_runtime_activation_fail_closed(tmp_path) -> None:
    preflight = _preflight(tmp_path)
    with pytest.raises(ValueError, match="destination_root_mismatch"):
        build_runtime_horizon_write_readiness_report(
            preflight=preflight,
            destination_root=tmp_path / "other",
            operator_id="mint",
            enabled_acknowledged=True,
            once_acknowledged=True,
        )

    unsafe = copy.deepcopy(preflight)
    unsafe["writes_dhot"] = True
    with pytest.raises(ValueError, match="preflight_safety_invalid:writes_dhot"):
        build_runtime_horizon_write_readiness_report(
            preflight=unsafe,
            destination_root=tmp_path,
            operator_id="mint",
            enabled_acknowledged=True,
            once_acknowledged=True,
        )


def test_report_has_no_write_or_runtime_activation_surface(tmp_path) -> None:
    report = build_runtime_horizon_write_readiness_report(
        preflight=_preflight(tmp_path),
        destination_root=tmp_path,
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
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        assert report[key] is False
