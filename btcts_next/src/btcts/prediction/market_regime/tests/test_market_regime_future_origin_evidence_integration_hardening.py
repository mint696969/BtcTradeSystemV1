# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_integration_hardening.py
# desc: MR-F6.24 end-to-end integration and hardening tests across the accepted non-executing contract chain.

from __future__ import annotations

from types import MappingProxyType

import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.future_forecast_contract import (
    FUTURE_MARKET_REGIME_HORIZONS_SEC,
)
from btcts.prediction.market_regime.future_mandatory_baseline_origin_evidence import (
    MarketRegimeOriginEvidence,
    build_market_regime_origin_evidence_bundle,
)
from btcts.prediction.market_regime.future_origin_evidence_audit_replay_evidence import (
    build_origin_evidence_audit_replay_evidence,
)
from btcts.prediction.market_regime.future_origin_evidence_dry_run_writer_adapter import (
    invoke_origin_evidence_writer_preflight_dry_run,
)
from btcts.prediction.market_regime.future_origin_evidence_duplicate_safe_receipt import (
    DESTINATION_STATE_ABSENT,
    DESTINATION_STATE_ALREADY_SATISFIED,
    build_origin_evidence_duplicate_safe_receipt,
)
from btcts.prediction.market_regime.future_origin_evidence_execution_boundary import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION,
)
from btcts.prediction.market_regime.future_origin_evidence_execution_plan import (
    build_origin_evidence_dry_run_execution_plan,
)
from btcts.prediction.market_regime.future_origin_evidence_execution_request import (
    MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION,
)
from btcts.prediction.market_regime.future_origin_evidence_recovery_resume_decision import (
    RECOVERY_DISPOSITION_HUMAN_GATED_RESUME_CANDIDATE,
    RECOVERY_DISPOSITION_TERMINAL_SUCCESS_EQUIVALENT,
    build_origin_evidence_recovery_resume_decision,
)
from btcts.prediction.market_regime.future_origin_evidence_writer import (
    MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
    build_origin_evidence_approval,
    build_origin_evidence_write_plan,
)

REQUEST_HASH = "a" * 64
EXPECTED_ARTIFACT_HASH = "f" * 64


def _bundles() -> tuple[MappingProxyType, ...]:
    result = []
    for horizon in FUTURE_MARKET_REGIME_HORIZONS_SEC:
        trace = f"trace:{horizon}"
        result.append(
            build_market_regime_origin_evidence_bundle(
                MarketRegimeOriginEvidence(
                    prediction_origin="2026-07-14T00:00:00Z",
                    prediction_origin_epoch_sec=1000.0,
                    source_timestamp="2026-07-13T23:59:59Z",
                    source_timestamp_epoch_sec=999.0,
                    target_horizon_sec=horizon,
                    trace_id=trace,
                    model_id="model.v1",
                    logic_version="logic.v1",
                    parameter_set_id=f"params.{horizon}.v1",
                    target_definition_version=f"market_regime_target.{horizon}s.v1",
                    feature_snapshot_ref=f"snapshot:{trace}",
                    current_state=MarketRegimeCode.RANGE,
                    previous_state=MarketRegimeCode.RANGE,
                    regime_scores={MarketRegimeCode.RANGE: 1.0},
                    recent_return=0.0,
                    fast_ma=100.0,
                    slow_ma=100.0,
                    realized_volatility=0.02,
                    low_volatility_threshold=0.01,
                    high_volatility_threshold=0.03,
                    current_forecast_label_selection=MarketRegimeCode.RANGE,
                )
            )
        )
    return tuple(result)


def _accepted_chain(*, destination_already_satisfied: bool = False):
    bundles = _bundles()
    writer_plan = build_origin_evidence_write_plan(
        generated_at="2026-07-14T00:00:00Z",
        writer_id="mr-f6-origin-writer",
        writer_contract_version="writer.v1",
        bundles=bundles,
        maximum_batch_rows=7,
    )
    approval = build_origin_evidence_approval(
        approval_id="approval:mr-f6.24:fixture",
        operator_ids=("operator:fixture",),
        requested_at="2026-07-14T00:00:00Z",
        expires_at="2026-07-15T00:00:00Z",
        approved_writer_id="mr-f6-origin-writer",
        approved_writer_contract_version="writer.v1",
    )
    bundle_ids = tuple(str(item["bundle_id"]) for item in bundles)
    relpath = (
        "prediction/market_regime/future_origin_evidence/"
        f"date={writer_plan['partition_key']}/batch-{writer_plan['dedupe_key']}.json"
    )
    request = {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_REQUEST_VERSION,
        "artifact_kind": "future_origin_evidence_one_shot_execution_request",
        "request_id": f"origin-evidence-execution-request:{REQUEST_HASH}",
        "request_hash": REQUEST_HASH,
        "writer_id": "mr-f6-origin-writer",
        "writer_contract_version": "writer.v1",
        "writer_contract_schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_WRITER_VERSION,
        "approval_id": approval["approval_id"],
        "approval_requested_at": approval["requested_at"],
        "approval_expires_at": approval["expires_at"],
        "artifact_relpath": relpath,
        "dedupe_key": writer_plan["dedupe_key"],
        "target_horizons_sec": FUTURE_MARKET_REGIME_HORIZONS_SEC,
        "bundle_ids": bundle_ids,
        "write_plan_bundle_ids": writer_plan["bundle_ids"],
        "forecast_parameter_set_ids": tuple(
            str(item["parameter_set_id"]) for item in bundles
        ),
    }
    boundary = {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_EXECUTION_BOUNDARY_VERSION,
        "artifact_kind": "future_origin_evidence_one_shot_execution_boundary",
        "request_id": request["request_id"],
        "request_hash": REQUEST_HASH,
        "expected_request_hash": REQUEST_HASH,
        "writer_id": "mr-f6-origin-writer",
        "writer_contract_version": "writer.v1",
        "evaluated_at": "2026-07-14T01:15:00Z",
        "approval_id": approval["approval_id"],
        "approval_requested_at": approval["requested_at"],
        "approval_expires_at": approval["expires_at"],
        "artifact_relpath": relpath,
        "dedupe_key": writer_plan["dedupe_key"],
        "bundle_ids": bundle_ids,
        "enabled_acknowledgement_present": True,
        "once_acknowledgement_present": True,
        "destination_artifact_exists": False,
        "destination_artifact_matches_request": False,
        "authorization_ready_for_separate_writer_call": True,
        "blockers": (),
        "decision": "separate_writer_call_may_be_considered",
        "execution_authorized_by_this_artifact": False,
        "writer_imported": False,
        "writer_invoked": False,
        "execution_performed": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "counts_as_real_shadow_evidence": False,
        "candidate_selection_performed": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
        "human_gate_required": True,
    }
    plan = build_origin_evidence_dry_run_execution_plan(
        execution_request=request,
        execution_boundary=boundary,
        planned_at="2026-07-14T01:20:00Z",
        expected_request_hash=REQUEST_HASH,
        expected_writer_id="mr-f6-origin-writer",
        expected_writer_contract_version="writer.v1",
    )
    adapter = invoke_origin_evidence_writer_preflight_dry_run(
        execution_plan=plan,
        writer_plan=writer_plan,
        approval=approval,
        bundles=bundles,
        executed_at="2026-07-14T01:25:00Z",
        expected_execution_plan_hash=plan["execution_plan_hash"],
        expected_writer_id="mr-f6-origin-writer",
        expected_writer_contract_version="writer.v1",
    )
    receipt = build_origin_evidence_duplicate_safe_receipt(
        adapter_result=adapter,
        observed_at="2026-07-14T01:30:00Z",
        destination_artifact_exists=destination_already_satisfied,
        destination_artifact_matches_expected=destination_already_satisfied,
        expected_adapter_result_hash=adapter["adapter_result_hash"],
        expected_artifact_hash=EXPECTED_ARTIFACT_HASH,
        observed_artifact_hash=(
            EXPECTED_ARTIFACT_HASH if destination_already_satisfied else None
        ),
    )
    decision = build_origin_evidence_recovery_resume_decision(
        receipt=receipt,
        decided_at="2026-07-14T01:35:00Z",
        expected_receipt_hash=receipt["receipt_hash"],
    )
    audit = build_origin_evidence_audit_replay_evidence(
        recovery_decision=decision,
        recorded_at="2026-07-14T01:40:00Z",
        expected_recovery_decision_hash=decision["decision_hash"],
        replay_source_id="replay:mr-f6.24:fixture",
    )
    return plan, adapter, receipt, decision, audit


def test_complete_hash_chain_is_preserved_end_to_end() -> None:
    plan, adapter, receipt, decision, audit = _accepted_chain()
    manifest = audit["replay_manifest"]

    assert adapter["execution_plan_hash"] == plan["execution_plan_hash"]
    assert receipt["adapter_result_hash"] == adapter["adapter_result_hash"]
    assert decision["receipt_hash"] == receipt["receipt_hash"]
    assert audit["recovery_decision_hash"] == decision["decision_hash"]
    assert manifest["execution_plan_hash"] == plan["execution_plan_hash"]
    assert manifest["adapter_result_hash"] == adapter["adapter_result_hash"]
    assert manifest["receipt_hash"] == receipt["receipt_hash"]
    assert manifest["recovery_decision_hash"] == decision["decision_hash"]


def test_path_dedupe_and_expected_artifact_identity_are_continuous() -> None:
    plan, adapter, receipt, decision, audit = _accepted_chain()
    manifest = audit["replay_manifest"]

    for artifact in (adapter, receipt, decision):
        assert artifact["artifact_relpath"] == plan["artifact_relpath"]
        assert artifact["dedupe_key"] == plan["dedupe_key"]
    assert manifest["artifact_relpath"] == plan["artifact_relpath"]
    assert manifest["dedupe_key"] == plan["dedupe_key"]
    assert manifest["expected_artifact_hash"] == EXPECTED_ARTIFACT_HASH


def test_absent_and_already_satisfied_states_remain_distinct() -> None:
    _, _, absent_receipt, absent_decision, absent_audit = _accepted_chain()
    _, _, satisfied_receipt, satisfied_decision, satisfied_audit = _accepted_chain(
        destination_already_satisfied=True
    )

    assert absent_receipt["destination_state"] == DESTINATION_STATE_ABSENT
    assert absent_decision["recovery_disposition"] == RECOVERY_DISPOSITION_HUMAN_GATED_RESUME_CANDIDATE
    assert absent_decision["resume_candidate"] is True

    assert satisfied_receipt["destination_state"] == DESTINATION_STATE_ALREADY_SATISFIED
    assert satisfied_decision["recovery_disposition"] == RECOVERY_DISPOSITION_TERMINAL_SUCCESS_EQUIVALENT
    assert satisfied_decision["resume_candidate"] is False
    assert satisfied_decision["terminal"] is True

    assert absent_audit["replay_manifest_hash"] != satisfied_audit["replay_manifest_hash"]


def test_all_stages_remain_immutable_and_nonexecuting() -> None:
    plan, adapter, receipt, decision, audit = _accepted_chain()
    for artifact in (plan, adapter, receipt, decision, audit):
        assert artifact["writer_invoked"] is False
        assert artifact["execution_performed"] is False
        assert artifact["writes_dhot"] is False
        assert artifact["scheduler_enabled"] is False
        assert artifact["counts_as_real_shadow_evidence"] is False
        assert artifact["live_parameter_apply_allowed"] is False
        assert artifact["auto_promotion_allowed"] is False
        assert artifact["canonical_replacement_allowed"] is False
        with pytest.raises(TypeError):
            artifact["writer_invoked"] = True

    assert adapter["filesystem_write_performed"] is False
    assert receipt["filesystem_read_performed"] is False
    assert receipt["filesystem_write_performed"] is False
    assert decision["automatic_retry_allowed"] is False
    assert decision["resume_authorized_by_this_artifact"] is False
    assert audit["replay_verification_only"] is True
    assert audit["replay_invokes_writer"] is False
    assert audit["replay_reads_filesystem"] is False
    assert audit["replay_writes_filesystem"] is False
    assert audit["replay_writes_dhot"] is False


def test_chain_is_deterministic_for_identical_inputs() -> None:
    first = _accepted_chain()
    second = _accepted_chain()
    keys = (
        "execution_plan_hash",
        "adapter_result_hash",
        "receipt_hash",
        "decision_hash",
        "evidence_hash",
    )
    for left, right, key in zip(first, second, keys):
        assert left[key] == right[key]


def test_tampering_at_each_external_hash_boundary_fails_closed() -> None:
    plan, adapter, receipt, decision, _ = _accepted_chain()

    with pytest.raises(PermissionError, match="external_adapter_hash_mismatch"):
        build_origin_evidence_duplicate_safe_receipt(
            adapter_result=adapter,
            observed_at="2026-07-14T01:30:00Z",
            destination_artifact_exists=False,
            destination_artifact_matches_expected=False,
            expected_adapter_result_hash="0" * 64,
            expected_artifact_hash=EXPECTED_ARTIFACT_HASH,
            observed_artifact_hash=None,
        )

    with pytest.raises(PermissionError, match="external_receipt_hash_mismatch"):
        build_origin_evidence_recovery_resume_decision(
            receipt=receipt,
            decided_at="2026-07-14T01:35:00Z",
            expected_receipt_hash="0" * 64,
        )

    with pytest.raises(PermissionError, match="external_decision_hash_mismatch"):
        build_origin_evidence_audit_replay_evidence(
            recovery_decision=decision,
            recorded_at="2026-07-14T01:40:00Z",
            expected_recovery_decision_hash="0" * 64,
            replay_source_id="replay:mr-f6.24:fixture",
        )

    assert plan["execution_plan_hash"] == adapter["execution_plan_hash"]


def test_public_modules_expose_no_hidden_execution_surfaces() -> None:
    modules = []
    from btcts.prediction.market_regime import future_origin_evidence_audit_replay_evidence as audit_module
    from btcts.prediction.market_regime import future_origin_evidence_duplicate_safe_receipt as receipt_module
    from btcts.prediction.market_regime import future_origin_evidence_execution_plan as plan_module
    from btcts.prediction.market_regime import future_origin_evidence_recovery_resume_decision as recovery_module

    modules.extend((plan_module, receipt_module, recovery_module, audit_module))
    for module in modules:
        assert not hasattr(module, "write_origin_evidence_once")
        assert not hasattr(module, "Path")
        assert not hasattr(module, "main")
        assert not hasattr(module, "register")
        assert not hasattr(module, "run_replay")
        assert not hasattr(module, "retry")
