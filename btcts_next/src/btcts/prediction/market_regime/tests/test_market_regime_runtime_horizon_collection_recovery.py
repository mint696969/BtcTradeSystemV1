# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_recovery.py
# desc: MR-F9.19L read-only manifest recovery and state-merge tests.

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from btcts.prediction.market_regime.runtime_horizon_collection_contract import build_runtime_horizon_collection_plan
from btcts.prediction.market_regime.runtime_horizon_collection_recovery import (
    EXPECTED_HORIZONS,
    inspect_runtime_horizon_run_manifest,
    recover_runtime_horizon_collection_runs,
    merge_runtime_horizon_collection_recovery_into_state,
)
from btcts.prediction.market_regime.runtime_horizon_collection_state import (
    advance_runtime_horizon_collection_state,
    build_initial_runtime_horizon_collection_state,
)


def _canonical_digest(payload):
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _plan(tmp_path: Path):
    destination = tmp_path / "destination"
    return build_runtime_horizon_collection_plan(
        source_root=tmp_path / "source",
        destination_root=destination,
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:00:00Z",
    )


def _write_run(destination: Path, *, origin: str, run_id: str, closed_source: str):
    date = origin[:10]
    relbase = f"prediction/market_regime/runtime_horizons/date={date}/runs/{run_id}"
    refs = []
    for horizon in EXPECTED_HORIZONS:
        relpath = f"{relbase}/horizon={horizon}.json"
        payload = {
            "artifact_kind": "market_regime_runtime_horizon",
            "schema_version": "test",
            "prediction_family_id": "market_regime",
            "run_id": run_id,
            "prediction_origin": origin,
            "horizon_sec": horizon,
            "horizon": {
                "horizon_sec": horizon,
                "trace_id": f"trace-{horizon}",
                "source_timestamp": origin if horizon == 0 else closed_source,
            },
            "ui_inference_allowed": False,
            "ui_confidence_recalculation_allowed": False,
            "read_only": True,
            "non_executing": True,
        }
        path = destination / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        refs.append({
            "horizon_sec": horizon,
            "artifact_relpath": relpath,
            "trace_id": f"trace-{horizon}",
            "payload_sha256": _canonical_digest(payload),
        })
    manifest_relpath = f"{relbase}/manifest.json"
    manifest = {
        "artifact_kind": "market_regime_runtime_horizon_run_manifest",
        "prediction_family_id": "market_regime",
        "run_id": run_id,
        "prediction_origin": origin,
        "horizon_count": 8,
        "horizon_artifacts": refs,
        "latest_pointer_relpath": None,
        "canonical_latest_replacement": False,
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "read_only": True,
        "non_executing": True,
    }
    manifest_path = destination / manifest_relpath
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return manifest_path


def test_inspects_complete_run_and_recovers_closed_source(tmp_path) -> None:
    destination = tmp_path / "destination"
    manifest = _write_run(
        destination,
        origin="2026-07-17T00:01:05Z",
        run_id="run-1",
        closed_source="2026-07-17T00:00:00Z",
    )
    result = inspect_runtime_horizon_run_manifest(destination, manifest_path=manifest)
    assert result["run_id"] == "run-1"
    assert result["closed_source_timestamp"] == "2026-07-17T00:00:00Z"
    assert result["verified_horizon_count"] == 8
    assert result["json_file_count"] == 9
    assert result["payload_digests_verified"] is True
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False


def test_collection_recovery_filters_window_and_sorts(tmp_path) -> None:
    plan = _plan(tmp_path)
    destination = Path(plan["destination_root"])
    _write_run(destination, origin="2026-07-17T00:02:05Z", run_id="run-2", closed_source="2026-07-17T00:01:00Z")
    _write_run(destination, origin="2026-07-17T00:01:05Z", run_id="run-1", closed_source="2026-07-17T00:00:00Z")
    _write_run(destination, origin="2026-07-18T00:00:00Z", run_id="run-outside", closed_source="2026-07-17T23:59:00Z")
    report = recover_runtime_horizon_collection_runs(destination, plan=plan)
    assert report["manifest_scan_count"] == 3
    assert report["ignored_outside_window_count"] == 1
    assert report["recovered_run_count"] == 2
    assert report["closed_source_timestamps"] == [
        "2026-07-17T00:00:00Z",
        "2026-07-17T00:01:00Z",
    ]
    assert [item["run_id"] for item in report["recovered_runs"]] == ["run-1", "run-2"]


def test_same_closed_source_multiple_runs_is_conflict(tmp_path) -> None:
    plan = _plan(tmp_path)
    destination = Path(plan["destination_root"])
    _write_run(destination, origin="2026-07-17T00:01:05Z", run_id="run-1", closed_source="2026-07-17T00:00:00Z")
    _write_run(destination, origin="2026-07-17T00:01:30Z", run_id="run-2", closed_source="2026-07-17T00:00:00Z")
    with pytest.raises(ValueError, match="closed_source_conflict"):
        recover_runtime_horizon_collection_runs(destination, plan=plan)


def test_digest_tampering_is_rejected(tmp_path) -> None:
    destination = tmp_path / "destination"
    manifest = _write_run(destination, origin="2026-07-17T00:01:05Z", run_id="run-1", closed_source="2026-07-17T00:00:00Z")
    payload = destination / "prediction/market_regime/runtime_horizons/date=2026-07-17/runs/run-1/horizon=300.json"
    data = json.loads(payload.read_text(encoding="utf-8"))
    data["horizon"]["source_timestamp"] = "2026-07-17T00:02:00Z"
    payload.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="payload_digest_mismatch"):
        inspect_runtime_horizon_run_manifest(destination, manifest_path=manifest)


def test_inconsistent_future_source_identity_is_rejected(tmp_path) -> None:
    destination = tmp_path / "destination"
    manifest = _write_run(destination, origin="2026-07-17T00:01:05Z", run_id="run-1", closed_source="2026-07-17T00:00:00Z")
    manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    payload_path = destination / manifest_data["horizon_artifacts"][2]["artifact_relpath"]
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    payload["horizon"]["source_timestamp"] = "2026-07-17T00:01:00Z"
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    manifest_data["horizon_artifacts"][2]["payload_sha256"] = _canonical_digest(payload)
    manifest.write_text(json.dumps(manifest_data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="closed_source_identity_invalid"):
        inspect_runtime_horizon_run_manifest(destination, manifest_path=manifest)


def test_missing_payload_and_latest_pointer_are_rejected(tmp_path) -> None:
    destination = tmp_path / "destination"
    manifest = _write_run(destination, origin="2026-07-17T00:01:05Z", run_id="run-1", closed_source="2026-07-17T00:00:00Z")
    missing = destination / "prediction/market_regime/runtime_horizons/date=2026-07-17/runs/run-1/horizon=86400.json"
    missing.unlink()
    with pytest.raises(FileNotFoundError, match="artifact_missing"):
        inspect_runtime_horizon_run_manifest(destination, manifest_path=manifest)

    manifest = _write_run(destination, origin="2026-07-17T00:01:05Z", run_id="run-1", closed_source="2026-07-17T00:00:00Z")
    (manifest.parent / "latest.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="run_file_set_invalid|latest_pointer_exists"):
        inspect_runtime_horizon_run_manifest(destination, manifest_path=manifest)


def test_destination_must_match_plan(tmp_path) -> None:
    plan = _plan(tmp_path)
    with pytest.raises(ValueError, match="destination_mismatch"):
        recover_runtime_horizon_collection_runs(tmp_path / "other", plan=plan)


def test_recovery_report_merges_completed_runs_into_state_without_writer(tmp_path) -> None:
    plan = _plan(tmp_path)
    destination = Path(plan["destination_root"])
    _write_run(destination, origin="2026-07-17T00:01:05Z", run_id="run-1", closed_source="2026-07-17T00:00:00Z")
    report = recover_runtime_horizon_collection_runs(destination, plan=plan)
    initial = build_initial_runtime_horizon_collection_state(plan=plan, created_at="2026-07-17T00:00:00Z")
    running = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=initial,
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )
    merged = merge_runtime_horizon_collection_recovery_into_state(
        plan=plan,
        state=running,
        recovery_report=report,
        observed_at="2026-07-17T00:02:00Z",
    )
    assert merged["recovered_state_entry_count"] == 1
    assert merged["writer_invoked"] is False
    assert merged["writes_dhot"] is False
    state = merged["state"]
    assert state["completed_prediction_origins"] == ["2026-07-17T00:01:05Z"]
    assert state["completed_closed_source_timestamps"] == ["2026-07-17T00:00:00Z"]
    assert state["latest_run_id"] == "run-1"
