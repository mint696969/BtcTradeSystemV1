# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_audit_replay_evidence.py
# desc: MR-F6.23 audit/replay evidence hash-chain, replay, timing, and safety tests.

from __future__ import annotations

from types import MappingProxyType

import pytest

from btcts.prediction.market_regime.future_origin_evidence_audit_replay_evidence import (
    build_origin_evidence_audit_replay_evidence,
)
from btcts.prediction.market_regime.future_origin_evidence_recovery_resume_decision import (
    MARKET_REGIME_ORIGIN_EVIDENCE_RECOVERY_RESUME_DECISION_VERSION,
)

DECISION_HASH = "a" * 64


def _decision() -> dict[str, object]:
    return {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_RECOVERY_RESUME_DECISION_VERSION,
        "artifact_kind": "future_origin_evidence_recovery_resume_decision",
        "decision_id": f"origin-evidence-recovery-resume:{DECISION_HASH}",
        "decision_hash": DECISION_HASH,
        "receipt_hash": "b" * 64,
        "adapter_result_hash": "c" * 64,
        "execution_plan_hash": "d" * 64,
        "decided_at": "2026-07-14T01:35:00Z",
        "artifact_relpath": (
            "prediction/market_regime/future_origin_evidence/"
            "date=2026-07-14/batch-fixture.json"
        ),
        "dedupe_key": "fixture",
        "expected_artifact_hash": "e" * 64,
        "observed_artifact_hash": None,
        "destination_state": "absent",
        "recovery_disposition": "human_gated_resume_candidate",
        "blockers": (),
        "recovery_actions": (
            "reconfirm_human_gate",
            "rebuild_execution_context_from_bound_hashes",
            "reobserve_destination_before_any_execution",
        ),
        "failure_code": None,
        "failure_detail_hash": None,
        "automatic_retry_allowed": False,
        "resume_authorized_by_this_artifact": False,
        "conflicting_state_reclassified_as_absent": False,
        "inconsistent_state_reclassified_as_absent": False,
        "receipt_hash_preserved": True,
        "writer_write_function_imported": False,
        "writer_write_function_invoked": False,
        "writer_invoked": False,
        "execution_performed": False,
        "filesystem_read_performed": False,
        "filesystem_write_performed": False,
        "writes_dhot": False,
        "scheduler_enabled": False,
        "counts_as_real_shadow_evidence": False,
        "candidate_selection_performed": False,
        "live_parameter_apply_allowed": False,
        "auto_promotion_allowed": False,
        "canonical_replacement_allowed": False,
        "human_gate_required": True,
    }


def _evidence(**overrides: object) -> MappingProxyType:
    values = dict(
        recovery_decision=_decision(),
        recorded_at="2026-07-14T01:40:00Z",
        expected_recovery_decision_hash=DECISION_HASH,
        replay_source_id="replay:fixture",
    )
    values.update(overrides)
    return build_origin_evidence_audit_replay_evidence(**values)


def test_hash_chain_and_replay_manifest_are_bound() -> None:
    result = _evidence()
    manifest = result["replay_manifest"]
    assert result["recovery_decision_hash"] == DECISION_HASH
    assert result["execution_plan_hash"] == "d" * 64
    assert result["adapter_result_hash"] == "c" * 64
    assert result["receipt_hash"] == "b" * 64
    assert manifest["recovery_decision_hash"] == DECISION_HASH
    assert manifest["execution_plan_hash"] == "d" * 64
    assert manifest["adapter_result_hash"] == "c" * 64
    assert manifest["receipt_hash"] == "b" * 64
    assert manifest["destination_state"] == "absent"
    assert manifest["recovery_disposition"] == "human_gated_resume_candidate"


def test_failure_context_and_actions_are_preserved() -> None:
    decision = _decision()
    decision["failure_code"] = "writer_preflight_failed"
    decision["failure_detail_hash"] = "f" * 64
    decision["blockers"] = ("operator_review_required",)
    result = _evidence(recovery_decision=decision)
    manifest = result["replay_manifest"]
    assert manifest["failure_code"] == "writer_preflight_failed"
    assert manifest["failure_detail_hash"] == "f" * 64
    assert manifest["blockers"] == ("operator_review_required",)
    assert manifest["recovery_actions"] == (
        "reconfirm_human_gate",
        "rebuild_execution_context_from_bound_hashes",
        "reobserve_destination_before_any_execution",
    )


def test_external_decision_hash_and_decision_id_are_revalidated() -> None:
    with pytest.raises(PermissionError, match="external_decision_hash_mismatch"):
        _evidence(expected_recovery_decision_hash="f" * 64)

    bad = _decision()
    bad["decision_id"] = "other"
    with pytest.raises(ValueError, match="decision_id_mismatch"):
        _evidence(recovery_decision=bad)


def test_recorded_at_must_not_precede_decided_at() -> None:
    with pytest.raises(ValueError, match="before_decision"):
        _evidence(recorded_at="2026-07-14T01:34:59Z")
    with pytest.raises(ValueError, match="recorded_at_invalid"):
        _evidence(recorded_at="2026-07-14 01:40:00")


def test_replay_source_and_hash_fields_are_required() -> None:
    with pytest.raises(ValueError, match="source_id_missing"):
        _evidence(replay_source_id=" ")

    bad = _decision()
    bad["receipt_hash"] = "not-a-hash"
    with pytest.raises(ValueError, match="receipt_hash_invalid"):
        _evidence(recovery_decision=bad)

    bad = _decision()
    bad["expected_artifact_hash"] = "not-a-hash"
    with pytest.raises(ValueError, match="expected_artifact_hash_invalid"):
        _evidence(recovery_decision=bad)


def test_unsafe_decision_flags_fail_closed() -> None:
    bad = _decision()
    bad["writer_invoked"] = True
    with pytest.raises(ValueError, match="unsafe_decision_flag:writer_invoked"):
        _evidence(recovery_decision=bad)

    bad = _decision()
    bad["receipt_hash_preserved"] = False
    with pytest.raises(ValueError, match="receipt_hash_not_preserved"):
        _evidence(recovery_decision=bad)


def test_evidence_is_deterministic_and_immutable() -> None:
    first = _evidence()
    second = _evidence()
    assert first["evidence_id"] == second["evidence_id"]
    assert first["evidence_hash"] == second["evidence_hash"]
    assert first["replay_manifest_hash"] == second["replay_manifest_hash"]
    with pytest.raises(TypeError):
        first["replay_verification_only"] = False
    with pytest.raises(TypeError):
        first["replay_manifest"]["destination_state"] = "conflicting"


def test_replay_is_verification_only_and_nonexecuting() -> None:
    result = _evidence()
    assert result["replay_verification_only"] is True
    assert result["replay_reproduces_bound_identity"] is True
    assert result["replay_invokes_writer"] is False
    assert result["replay_reads_filesystem"] is False
    assert result["replay_writes_filesystem"] is False
    assert result["replay_writes_dhot"] is False
    assert result["replay_enables_scheduler"] is False
    assert result["replay_counts_as_real_shadow_evidence"] is False
    assert result["audit_evidence_is_authorization"] is False
    assert result["automatic_retry_allowed"] is False
    assert result["resume_authorized_by_this_artifact"] is False
    assert result["writer_invoked"] is False
    assert result["execution_performed"] is False
    assert result["filesystem_read_performed"] is False
    assert result["filesystem_write_performed"] is False
    assert result["writes_dhot"] is False
    assert result["scheduler_enabled"] is False


def test_manifest_hash_changes_with_replay_source_or_failure_context() -> None:
    first = _evidence()
    second = _evidence(replay_source_id="replay:other")
    assert first["replay_manifest_hash"] == second["replay_manifest_hash"]
    assert first["evidence_hash"] != second["evidence_hash"]

    decision = _decision()
    decision["failure_code"] = "x"
    decision["failure_detail_hash"] = "1" * 64
    third = _evidence(recovery_decision=decision)
    assert first["replay_manifest_hash"] != third["replay_manifest_hash"]


def test_module_exposes_no_writer_filesystem_cli_scheduler_or_replay_runner() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_audit_replay_evidence as module

    assert hasattr(module, "build_origin_evidence_audit_replay_evidence")
    assert not hasattr(module, "write_origin_evidence_once")
    assert not hasattr(module, "preflight_origin_evidence_write")
    assert not hasattr(module, "Path")
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
    assert not hasattr(module, "run_replay")
