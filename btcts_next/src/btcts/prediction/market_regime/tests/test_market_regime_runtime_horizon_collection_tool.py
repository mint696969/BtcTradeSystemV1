# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_tool.py
# desc: MR-F9.19N operator collection CLI prepare/status/stop/start argument-boundary tests.

from __future__ import annotations

import json
from pathlib import Path

import pytest

from btcts.prediction.market_regime.tools import runtime_horizon_collection as collection_tool
from btcts.prediction.market_regime.runtime_horizon_collection_state import (
    advance_runtime_horizon_collection_state,
    build_initial_runtime_horizon_collection_state,
    write_runtime_horizon_collection_state,
)
from btcts.prediction.market_regime.tools.runtime_horizon_collection import (
    authorization_file_path,
    main,
    plan_file_path,
    prepare_runtime_horizon_collection,
    status_runtime_horizon_collection,
    stop_runtime_horizon_collection,
)

DHOT = r"D:\btc_ts_hot"


def _prepared(tmp_path: Path):
    return prepare_runtime_horizon_collection(
        source_root=DHOT,
        destination_root=DHOT,
        control_root=tmp_path,
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T02:00:00Z",
        authorization_created_at="2026-07-17T01:59:00Z",
        ttl_sec=120,
    )


def test_prepare_persists_plan_and_read_only_authorization(tmp_path) -> None:
    result = _prepared(tmp_path)
    assert result["event"] == "PREPARED"
    assert result["collection_started"] is False
    assert result["writer_invoked"] is False
    plan_path = plan_file_path(tmp_path, result["collection_id"])
    auth_path = authorization_file_path(tmp_path, result["collection_id"])
    assert plan_path.exists()
    assert auth_path.exists()
    package = json.loads(auth_path.read_text(encoding="utf-8"))
    assert package["human_authorized"] is False
    assert package["writes_dhot"] is False


def test_status_without_state_or_lease_is_read_only(tmp_path) -> None:
    prepared = _prepared(tmp_path)
    result = status_runtime_horizon_collection(
        plan_path=prepared["plan_path"],
        control_root=tmp_path,
    )
    assert result["state_present"] is False
    assert result["lease_present"] is False
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False


def test_stop_sets_persisted_request_without_writer(tmp_path) -> None:
    prepared = _prepared(tmp_path)
    plan = json.loads(Path(prepared["plan_path"]).read_text(encoding="utf-8"))
    state = build_initial_runtime_horizon_collection_state(
        plan=plan,
        created_at="2026-07-17T01:59:00Z",
    )
    state = advance_runtime_horizon_collection_state(
        plan=plan,
        previous=state,
        event="START",
        observed_at="2026-07-17T02:00:00Z",
    )
    write_runtime_horizon_collection_state(tmp_path, plan=plan, state=state)
    result = stop_runtime_horizon_collection(
        plan_path=prepared["plan_path"],
        control_root=tmp_path,
        requested_at="2026-07-17T02:01:00Z",
    )
    assert result["stop_requested"] is True
    assert result["writer_invoked"] is False
    status = status_runtime_horizon_collection(
        plan_path=prepared["plan_path"],
        control_root=tmp_path,
    )
    assert status["state"]["stop_requested"] is True


def test_start_subcommand_requires_authorization_arguments(tmp_path) -> None:
    prepared = _prepared(tmp_path)
    with pytest.raises(SystemExit):
        main(["start", "--plan-path", prepared["plan_path"]])

def test_start_subcommand_passes_verified_inputs_to_start_wiring(tmp_path, monkeypatch) -> None:
    prepared = _prepared(tmp_path)
    package_path = authorization_file_path(tmp_path, prepared["collection_id"])
    package = json.loads(package_path.read_text(encoding="utf-8"))
    captured = {}

    def fake_start(control_root, **kwargs):
        captured["control_root"] = str(control_root)
        captured.update(kwargs)
        return {"event": "AUTHORIZED_FOREGROUND_START_RETURNED", "ok": True}

    monkeypatch.setattr(
        collection_tool,
        "run_authorized_runtime_horizon_collection_start",
        fake_start,
    )

    result = collection_tool.main(
        [
            "start",
            "--plan-path",
            prepared["plan_path"],
            "--authorization-package-path",
            str(package_path),
            "--authorization-text",
            package["expected_authorization_text"],
            "--control-root",
            str(tmp_path),
        ]
    )

    assert result == 0
    assert captured["control_root"] == str(tmp_path)
    assert captured["provided_authorization_text"] == package["expected_authorization_text"]
    assert captured["authorization_package"]["authorization_package_sha256"] == package["authorization_package_sha256"]
    assert captured["plan"]["collection_id"] == prepared["collection_id"]
    assert str(captured["expected_root"]) == DHOT
    assert callable(captured["now_provider"])
