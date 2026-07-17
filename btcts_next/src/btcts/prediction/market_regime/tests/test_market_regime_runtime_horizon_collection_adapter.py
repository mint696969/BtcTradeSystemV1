# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_runtime_horizon_collection_adapter.py
# desc: MR-F9.19L runtime-horizon collection adapter tests.

from __future__ import annotations

from pathlib import Path

import pytest

import btcts.prediction.market_regime.runtime_horizon_collection_adapter as module
from btcts.prediction.market_regime.runtime_horizon_collection_contract import build_runtime_horizon_collection_plan
from btcts.prediction.market_regime.runtime_horizon_collection_state import (
    advance_runtime_horizon_collection_state,
    build_initial_runtime_horizon_collection_state,
)


def _plan(tmp_path: Path, *, same_root: bool = False):
    source = tmp_path / "source"
    destination = source if same_root else tmp_path / "destination"
    return build_runtime_horizon_collection_plan(
        source_root=source,
        destination_root=destination,
        shadow_candidate_id="candidate",
        operator_id="mint",
        planned_start_utc="2026-07-17T00:00:00Z",
    )


def _running(plan):
    initial = build_initial_runtime_horizon_collection_state(plan=plan, created_at="2026-07-17T00:00:00Z")
    return advance_runtime_horizon_collection_state(
        plan=plan,
        previous=initial,
        event="START",
        observed_at="2026-07-17T00:00:01Z",
    )


def test_requires_explicit_collection_start_authorization(tmp_path) -> None:
    plan = _plan(tmp_path)
    with pytest.raises(PermissionError, match="start_authorization_required"):
        module.execute_runtime_horizon_collection_adapter_tick(
            tmp_path,
            plan=plan,
            state=_running(plan),
            observed_at="2026-07-17T00:01:01Z",
        )


def test_connects_fresh_preflight_readiness_and_writer_once(monkeypatch, tmp_path) -> None:
    plan = _plan(tmp_path)
    persistence_plan = {
        "prediction_origin": "2026-07-17T00:00:00Z",
        "run_id": "run-1",
        "write_order": [f"p-{i}.json" for i in range(8)] + ["manifest.json"],
        "manifest_relpath": "manifest.json",
    }
    calls = []

    def preflight(**kwargs):
        calls.append(("preflight", kwargs))
        return {"runtime_horizon_persistence_plan": persistence_plan}

    def readiness(**kwargs):
        calls.append(("readiness", kwargs))
        assert kwargs["preflight"]["hot_root"] == str(Path(plan["destination_root"]).resolve())
        return {"ready": True, "blockers": ()}

    def persist(root, **kwargs):
        calls.append(("writer", root, kwargs))
        return {"receipt": True}

    def tick(root, **kwargs):
        built = kwargs["preflight_builder"]()
        ready = kwargs["readiness_builder"](built)
        written = kwargs["writer"](built["runtime_horizon_persistence_plan"])
        assert ready["ready"] is True
        assert written["receipt"] is True
        return {
            "event": "WRITE_OK",
            "writer_invoked": True,
            "writes_dhot": False,
            "state": kwargs["state"],
        }

    monkeypatch.setattr(module, "build_shadow_runtime_preflight_once", preflight)
    monkeypatch.setattr(module, "build_runtime_horizon_write_readiness_report", readiness)
    monkeypatch.setattr(module, "persist_runtime_horizon_plan_once", persist)
    monkeypatch.setattr(module, "execute_runtime_horizon_collection_tick", tick)

    result = module.execute_runtime_horizon_collection_adapter_tick(
        tmp_path,
        plan=plan,
        state=_running(plan),
        observed_at="2026-07-17T00:01:01Z",
        collection_start_authorized=True,
    )
    assert [item[0] for item in calls] == ["preflight", "readiness", "writer"]
    assert calls[0][1]["generated_at"] == "2026-07-17T00:01:01Z"
    assert Path(calls[2][1]).resolve() == Path(plan["destination_root"]).resolve()
    assert calls[2][2]["enabled"] is True
    assert calls[2][2]["once"] is True
    assert result["writer_invoked"] is True
    assert result["writes_dhot"] is False


def test_same_source_and_destination_marks_actual_write_as_dhot(monkeypatch, tmp_path) -> None:
    plan = _plan(tmp_path, same_root=True)
    monkeypatch.setattr(
        module,
        "execute_runtime_horizon_collection_tick",
        lambda root, **kwargs: {
            "event": "WRITE_OK",
            "writer_invoked": True,
            "writes_dhot": True,
            "state": kwargs["state"],
        },
    )
    result = module.execute_runtime_horizon_collection_adapter_tick(
        tmp_path,
        plan=plan,
        state=_running(plan),
        observed_at="2026-07-17T00:01:01Z",
        collection_start_authorized=True,
    )
    assert result["writes_dhot"] is True


def test_skip_result_never_claims_dhot_write(monkeypatch, tmp_path) -> None:
    plan = _plan(tmp_path, same_root=True)
    monkeypatch.setattr(
        module,
        "execute_runtime_horizon_collection_tick",
        lambda root, **kwargs: {
            "event": "READINESS_SKIP",
            "writer_invoked": False,
            "writes_dhot": False,
            "state": kwargs["state"],
        },
    )
    result = module.execute_runtime_horizon_collection_adapter_tick(
        tmp_path,
        plan=plan,
        state=_running(plan),
        observed_at="2026-07-17T00:01:01Z",
        collection_start_authorized=True,
    )
    assert result["writes_dhot"] is False


def test_runtime_surfaces_remain_disabled(monkeypatch, tmp_path) -> None:
    plan = _plan(tmp_path)
    monkeypatch.setattr(
        module,
        "execute_runtime_horizon_collection_tick",
        lambda root, **kwargs: {
            "event": "READINESS_SKIP",
            "writer_invoked": False,
            "state": kwargs["state"],
        },
    )
    result = module.execute_runtime_horizon_collection_adapter_tick(
        tmp_path,
        plan=plan,
        state=_running(plan),
        observed_at="2026-07-17T00:01:01Z",
        collection_start_authorized=True,
    )
    for key in (
        "writer_registered",
        "scheduler_enabled",
        "producer_loop_enabled",
        "detached_process_started",
        "latest_pointer_created",
        "websocket_opened",
        "ui_inference_allowed",
        "ui_confidence_recalculation_allowed",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "order_submission_allowed",
    ):
        assert result[key] is False
