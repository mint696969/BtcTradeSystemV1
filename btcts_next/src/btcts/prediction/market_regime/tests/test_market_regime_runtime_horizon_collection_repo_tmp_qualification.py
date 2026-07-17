# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_repo_tmp_qualification.py
# desc: MR-F9.19O production-path repository-tmp qualification through CLI/start/lease/recovery/loop/tick/state.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import btcts.prediction.market_regime.runtime_horizon_collection_start as start_module
from btcts.prediction.market_regime.runtime_horizon_collection_authorization import (
    build_runtime_horizon_collection_start_authorization_package,
)
from btcts.prediction.market_regime.runtime_horizon_collection_contract import (
    build_runtime_horizon_collection_plan,
)
from btcts.prediction.market_regime.runtime_horizon_collection_lease import (
    acquire_runtime_horizon_collection_lease,
    read_runtime_horizon_collection_lease,
    recover_stale_runtime_horizon_collection_lease,
)
from btcts.prediction.market_regime.runtime_horizon_collection_recovery import EXPECTED_HORIZONS
from btcts.prediction.market_regime.runtime_horizon_collection_state import (
    collection_state_paths,
    request_runtime_horizon_collection_stop,
)
from btcts.prediction.market_regime.runtime_horizon_collection_tick import (
    execute_runtime_horizon_collection_tick,
)
from btcts.prediction.market_regime.tools import runtime_horizon_collection as collection_tool


def _dt(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


class _Clock:
    def __init__(self, *values: str) -> None:
        self._values = iter(_dt(value) for value in values)
        self._last = _dt(values[-1])

    def __call__(self) -> datetime:
        try:
            self._last = next(self._values)
        except StopIteration:
            pass
        return self._last


def _canonical_digest(payload) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _prepared(root: Path):
    plan = build_runtime_horizon_collection_plan(
        source_root=root,
        destination_root=root,
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:00:00Z",
    )
    package = build_runtime_horizon_collection_start_authorization_package(
        plan=plan,
        created_at="2026-07-16T23:59:00Z",
        expected_dhot_root=root,
        ttl_sec=300,
    )
    plan_path = collection_tool.plan_file_path(root, plan["collection_id"])
    auth_path = collection_tool.authorization_file_path(root, plan["collection_id"])
    collection_tool._atomic_write_json(plan_path, plan)
    collection_tool._atomic_write_json(auth_path, package)
    return plan, package, plan_path, auth_path


def _persistence_plan(origin: str, run_id: str):
    date = origin[:10]
    base = f"prediction/market_regime/runtime_horizons/date={date}/runs/{run_id}"
    write_order = [f"{base}/horizon={horizon}.json" for horizon in EXPECTED_HORIZONS]
    manifest_relpath = f"{base}/manifest.json"
    return {
        "prediction_origin": origin,
        "run_id": run_id,
        "write_order": write_order + [manifest_relpath],
        "manifest_relpath": manifest_relpath,
    }


def _write_run(destination: Path, persistence_plan, closed_source: str):
    origin = persistence_plan["prediction_origin"]
    run_id = persistence_plan["run_id"]
    refs = []
    for horizon, relpath in zip(EXPECTED_HORIZONS, persistence_plan["write_order"][:8]):
        payload = {
            "artifact_kind": "market_regime_runtime_horizon",
            "schema_version": "mr_f9_19o_test",
            "prediction_family_id": "market_regime",
            "run_id": run_id,
            "prediction_origin": origin,
            "horizon_sec": horizon,
            "horizon": {
                "horizon_sec": horizon,
                "trace_id": f"trace-{run_id}-{horizon}",
                "source_timestamp": origin if horizon == 0 else closed_source,
            },
            "ui_inference_allowed": False,
            "ui_confidence_recalculation_allowed": False,
            "read_only": True,
            "non_executing": True,
        }
        path = destination / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        refs.append(
            {
                "horizon_sec": horizon,
                "artifact_relpath": relpath,
                "trace_id": payload["horizon"]["trace_id"],
                "payload_sha256": _canonical_digest(payload),
            }
        )
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
    manifest_path = destination / persistence_plan["manifest_relpath"]
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return {
        "written_paths": tuple(persistence_plan["write_order"]),
        "duplicate_paths": (),
        "written_count": 9,
        "duplicate_count": 0,
        "manifest_relpath": persistence_plan["manifest_relpath"],
        "manifest_written_last": True,
        "latest_pointer_created": False,
        "writer_registered": False,
        "producer_loop_enabled": False,
        "scheduler_enabled": False,
        "websocket_opened": False,
        "order_submission_allowed": False,
    }


def _install_repo_tmp_adapter(monkeypatch, root: Path, *, stop_after_first_write: bool = False):
    closed_source = "2026-07-16T23:59:00Z"
    counters = {"writer": 0, "tick": 0}

    def adapter(state_root, *, plan, state, observed_at, collection_start_authorized=False):
        assert collection_start_authorized is True
        counters["tick"] += 1
        run_id = "run-" + observed_at.replace(":", "").replace("-", "")
        persistence = _persistence_plan(observed_at, run_id)
        horizons = [
            {
                "horizon_sec": horizon,
                "source_timestamp": observed_at if horizon == 0 else closed_source,
            }
            for horizon in EXPECTED_HORIZONS
        ]
        preflight = {
            "runtime_horizon_artifact": {"horizons": horizons},
            "runtime_horizon_persistence_plan": persistence,
            "runtime_horizon_writer_registered": False,
            "writer_invoked": False,
            "writes_dhot": False,
            "scheduler_enabled": False,
            "producer_loop_enabled": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "order_submission_allowed": False,
        }

        def writer(received):
            counters["writer"] += 1
            return _write_run(root, received, closed_source)

        result = execute_runtime_horizon_collection_tick(
            state_root,
            plan=plan,
            state=state,
            observed_at=observed_at,
            preflight_builder=lambda: preflight,
            readiness_builder=lambda value: {"ready": True, "blockers": ()},
            writer=writer,
        )
        if stop_after_first_write and counters["writer"] == 1:
            request_runtime_horizon_collection_stop(
                state_root,
                plan=plan,
                requested_at=observed_at,
            )
        return result

    monkeypatch.setattr(start_module, "execute_runtime_horizon_collection_adapter_tick", adapter)
    return counters


def _start_args(plan_path: Path, auth_path: Path, package, root: Path):
    return [
        "start",
        "--plan-path",
        str(plan_path),
        "--authorization-package-path",
        str(auth_path),
        "--authorization-text",
        package["expected_authorization_text"],
        "--control-root",
        str(root),
    ]


def test_cli_first_write_duplicate_skip_and_planned_end(monkeypatch, tmp_path, capsys) -> None:
    root = tmp_path / "repo_tmp"
    plan, package, plan_path, auth_path = _prepared(root)
    counters = _install_repo_tmp_adapter(monkeypatch, root)
    clock = _Clock(
        "2026-07-17T00:00:00Z",
        "2026-07-17T00:00:00Z",
        "2026-07-17T00:00:00Z",
        "2026-07-17T00:00:01Z",
        "2026-07-17T00:00:01Z",
        "2026-07-17T00:01:01Z",
        "2026-07-17T00:01:01Z",
        "2026-07-18T00:00:00Z",
    )
    assert collection_tool.main(
        _start_args(plan_path, auth_path, package, root),
        expected_root=root,
        now_provider=clock,
        sleep_fn=lambda seconds: None,
    ) == 0
    result = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert result["stop_reason"] == "planned_end_reached"
    assert result["state"]["written_origin_count"] == 1
    assert result["state"]["duplicate_origin_skip_count"] == 1
    assert counters == {"writer": 1, "tick": 2}
    assert result["lease_released"] is True
    assert read_runtime_horizon_collection_lease(root, plan=plan) == {}


def test_stop_resume_and_state_loss_manifest_recovery(monkeypatch, tmp_path, capsys) -> None:
    root = tmp_path / "repo_tmp"
    plan, package, plan_path, auth_path = _prepared(root)
    first = _install_repo_tmp_adapter(monkeypatch, root, stop_after_first_write=True)
    first_clock = _Clock(
        "2026-07-17T00:00:00Z",
        "2026-07-17T00:00:00Z",
        "2026-07-17T00:00:00Z",
        "2026-07-17T00:00:01Z",
        "2026-07-17T00:00:01Z",
        "2026-07-17T00:00:02Z",
    )
    collection_tool.main(
        _start_args(plan_path, auth_path, package, root),
        expected_root=root,
        now_provider=first_clock,
        sleep_fn=lambda seconds: None,
    )
    first_result = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert first_result["stop_reason"] == "stop_requested"
    assert first == {"writer": 1, "tick": 1}
    state_path = collection_state_paths(root, plan)["state"]
    state_path.unlink()

    second = _install_repo_tmp_adapter(monkeypatch, root)
    second_clock = _Clock(
        "2026-07-17T00:02:00Z",
        "2026-07-17T00:02:00Z",
        "2026-07-17T00:02:01Z",
        "2026-07-18T00:00:00Z",
    )
    collection_tool.main(
        _start_args(plan_path, auth_path, package, root),
        expected_root=root,
        now_provider=second_clock,
        sleep_fn=lambda seconds: None,
    )
    second_result = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert second_result["recovered_state_entry_count"] == 1
    assert second_result["state"]["written_origin_count"] == 1
    assert second_result["state"]["duplicate_origin_skip_count"] == 1
    assert second == {"writer": 0, "tick": 1}
    assert second_result["stop_reason"] == "planned_end_reached"


def test_duplicate_lease_and_explicit_stale_recovery(tmp_path) -> None:
    root = tmp_path / "repo_tmp"
    plan, package, plan_path, auth_path = _prepared(root)
    acquire_runtime_horizon_collection_lease(
        root,
        plan=plan,
        acquired_at="2026-07-17T00:00:00Z",
        pid=123,
        lease_id="lease-a",
    )
    with pytest.raises(FileExistsError, match="already_held"):
        collection_tool.main(
            _start_args(plan_path, auth_path, package, root),
            expected_root=root,
            now_provider=lambda: _dt("2026-07-17T00:01:00Z"),
            sleep_fn=lambda seconds: None,
        )
    recovered = recover_stale_runtime_horizon_collection_lease(
        root,
        plan=plan,
        expected_lease_id="lease-a",
        observed_at="2026-07-17T00:02:00Z",
        minimum_stale_sec=120,
    )
    assert recovered["stale_age_sec"] == 120
    assert read_runtime_horizon_collection_lease(root, plan=plan) == {}


def test_recovery_conflict_fails_closed_and_releases_start_lease(tmp_path) -> None:
    root = tmp_path / "repo_tmp"
    plan, package, plan_path, auth_path = _prepared(root)
    _write_run(root, _persistence_plan("2026-07-17T00:01:00Z", "run-a"), "2026-07-17T00:00:00Z")
    _write_run(root, _persistence_plan("2026-07-17T00:01:30Z", "run-b"), "2026-07-17T00:00:00Z")
    with pytest.raises(ValueError, match="closed_source_conflict"):
        collection_tool.main(
            _start_args(plan_path, auth_path, package, root),
            expected_root=root,
            now_provider=lambda: _dt("2026-07-17T00:02:00Z"),
            sleep_fn=lambda seconds: None,
        )
    assert read_runtime_horizon_collection_lease(root, plan=plan) == {}
