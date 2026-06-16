# path: ./btcts_next/src/btcts/autotrade/tests/test_parameter_bundle_shadow_cycle_wiring.py
# desc: Guards shadow cycle runtime parameter bundle loading and decision rationale identity wiring.

from __future__ import annotations

from btcts.autotrade.config import initial_parameter_bundle_v0_1
from btcts.autotrade.config.bundle_lifecycle import parameter_bundle_json_path
from btcts.autotrade.config.models import ParameterSetBundleRegistry
from btcts.autotrade.config.registry import write_bundle_registry, write_parameter_bundle
from btcts.autotrade.shadow_cycle import run_shadow_cycle_once


def test_shadow_cycle_blocks_when_requested_runtime_bundle_is_missing(tmp_path) -> None:
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    write_bundle_registry(
        registry_path,
        ParameterSetBundleRegistry(active_shadow_bundle_id="pb_missing"),
    )

    result = run_shadow_cycle_once(
        load_runtime_parameter_bundle=True,
        parameter_bundle_registry_path=registry_path,
        persist=False,
    )

    data = result.to_dict()
    assert result.appended is False
    assert result.result.snapshot_id is None
    assert "parameter_bundle_file_missing" in result.blocked_by
    assert "parameter_bundle_runtime_load_failed" in result.blocked_by
    assert result.parameter_bundle_load is not None
    assert data["parameter_bundle_load"]["bundle_id"] == "pb_missing"
    assert data["parameter_bundle_load"]["would_send_to_broker"] is False
    assert data["would_send_to_broker"] is False


def test_shadow_cycle_loads_runtime_bundle_before_market_state_lookup(monkeypatch, tmp_path) -> None:
    bundle = initial_parameter_bundle_v0_1()
    registry_path = tmp_path / "parameter_sets" / "registry.json"
    bundle_path = parameter_bundle_json_path(registry_path.parent, bundle.parameter_bundle_id)

    write_bundle_registry(
        registry_path,
        ParameterSetBundleRegistry(active_shadow_bundle_id=bundle.parameter_bundle_id),
    )
    write_parameter_bundle(bundle_path, bundle)

    calls = {}

    def fake_run_latest_market_state_shadow_decision(**kwargs):
        calls.update(kwargs)

        class FakeResult:
            snapshot_id = "snap_fake"
            forecast_id = "fc_fake"
            decision_id = "dec_fake"
            candidate_action = "WAIT"
            risk_allowed = False
            appended = False
            ledger_path = tmp_path / "shadow_decisions.jsonl"
            blocked_by = ()
            would_send_to_broker = False
            decision = None
            diagnostics = None

            def to_dict(self):
                return {
                    "snapshot_id": self.snapshot_id,
                    "forecast_id": self.forecast_id,
                    "decision_id": self.decision_id,
                    "candidate_action": self.candidate_action,
                    "risk_allowed": self.risk_allowed,
                    "appended": self.appended,
                    "ledger_path": str(self.ledger_path),
                    "blocked_by": [],
                    "would_send_to_broker": False,
                    "decision": None,
                    "diagnostics": None,
                }

        return FakeResult()

    monkeypatch.setattr(
        "btcts.autotrade.shadow_cycle.run_latest_market_state_shadow_decision",
        fake_run_latest_market_state_shadow_decision,
    )

    result = run_shadow_cycle_once(
        load_runtime_parameter_bundle=True,
        parameter_bundle_registry_path=registry_path,
        persist=False,
    )

    data = result.to_dict()
    assert result.result.snapshot_id == "snap_fake"
    assert result.parameter_bundle_load is not None
    assert result.parameter_bundle_load.found is True
    assert calls["parameter_set"].parameter_set_id == bundle.trade_parameter_set_id
    assert calls["parameter_bundle"].parameter_bundle_id == bundle.parameter_bundle_id
    assert data["parameter_bundle_load"]["bundle_id"] == bundle.parameter_bundle_id
    assert data["parameter_bundle_load"]["bundle"]["regime_parameter_set"]["kind"] == "regime"
    assert data["would_send_to_broker"] is False


def test_shadow_cycle_explicit_parameter_bundle_takes_precedence(monkeypatch) -> None:
    bundle = initial_parameter_bundle_v0_1()
    calls = {}

    def fake_run_latest_market_state_shadow_decision(**kwargs):
        calls.update(kwargs)

        class FakeResult:
            snapshot_id = "snap_explicit"
            forecast_id = None
            decision_id = None
            candidate_action = None
            risk_allowed = False
            appended = False
            ledger_path = None
            blocked_by = ()
            would_send_to_broker = False
            decision = None
            diagnostics = None

            def to_dict(self):
                return {
                    "snapshot_id": self.snapshot_id,
                    "forecast_id": self.forecast_id,
                    "decision_id": self.decision_id,
                    "candidate_action": self.candidate_action,
                    "risk_allowed": self.risk_allowed,
                    "appended": self.appended,
                    "ledger_path": self.ledger_path,
                    "blocked_by": [],
                    "would_send_to_broker": False,
                    "decision": None,
                    "diagnostics": None,
                }

        return FakeResult()

    monkeypatch.setattr(
        "btcts.autotrade.shadow_cycle.run_latest_market_state_shadow_decision",
        fake_run_latest_market_state_shadow_decision,
    )

    result = run_shadow_cycle_once(
        parameter_bundle=bundle,
        load_runtime_parameter_bundle=True,
        parameter_bundle_registry_path=None,
        persist=False,
    )

    assert result.parameter_bundle_load is None
    assert result.result.snapshot_id == "snap_explicit"
    assert calls["parameter_set"].parameter_set_id == bundle.trade_parameter_set_id
    assert calls["parameter_bundle"].parameter_bundle_id == bundle.parameter_bundle_id
