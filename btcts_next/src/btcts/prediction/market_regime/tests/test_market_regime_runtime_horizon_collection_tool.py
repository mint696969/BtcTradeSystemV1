# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_tool.py
# desc: MR-F9.19M operator collection CLI prepare/status/stop tests; start remains fail-closed.

from __future__ import annotations

import json
from pathlib import Path

import pytest

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


def test_start_subcommand_is_fail_closed(tmp_path) -> None:
    prepared = _prepared(tmp_path)
    with pytest.raises(PermissionError, match="start_not_implemented"):
        main(["start", "--plan-path", prepared["plan_path"]])
