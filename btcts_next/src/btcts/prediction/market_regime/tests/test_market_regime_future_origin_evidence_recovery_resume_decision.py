# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_future_origin_evidence_recovery_resume_decision.py
# desc: MR-F6.22 recovery/resume decision state, hash, timing, and safety tests.

from __future__ import annotations

from types import MappingProxyType

import pytest

from btcts.prediction.market_regime.future_origin_evidence_duplicate_safe_receipt import (
    DESTINATION_STATE_ABSENT,
    DESTINATION_STATE_ALREADY_SATISFIED,
    DESTINATION_STATE_CONFLICTING,
    DESTINATION_STATE_INCONSISTENT,
    MARKET_REGIME_ORIGIN_EVIDENCE_DUPLICATE_SAFE_RECEIPT_VERSION,
)
from btcts.prediction.market_regime.future_origin_evidence_recovery_resume_decision import (
    RECOVERY_DISPOSITION_HUMAN_GATED_RESUME_CANDIDATE,
    RECOVERY_DISPOSITION_REOBSERVATION_REQUIRED,
    RECOVERY_DISPOSITION_TERMINAL_CONFLICT_BLOCKED,
    RECOVERY_DISPOSITION_TERMINAL_SUCCESS_EQUIVALENT,
    build_origin_evidence_recovery_resume_decision,
)

RECEIPT_HASH = "a" * 64


def _receipt(
    destination_state: str = DESTINATION_STATE_ABSENT,
    *,
    blockers: tuple[str, ...] = (),
) -> dict[str, object]:
    observed_hash = None
    if destination_state == DESTINATION_STATE_ALREADY_SATISFIED:
        observed_hash = "b" * 64
        blockers = blockers or ("destination_artifact_already_satisfied",)
    elif destination_state == DESTINATION_STATE_CONFLICTING:
        observed_hash = "c" * 64
        blockers = blockers or ("destination_artifact_conflict",)
    elif destination_state == DESTINATION_STATE_INCONSISTENT:
        blockers = blockers or ("destination_artifact_hash_missing",)

    return {
        "schema_version": MARKET_REGIME_ORIGIN_EVIDENCE_DUPLICATE_SAFE_RECEIPT_VERSION,
        "artifact_kind": "future_origin_evidence_duplicate_safe_receipt",
        "receipt_id": f"origin-evidence-duplicate-safe-receipt:{RECEIPT_HASH}",
        "receipt_hash": RECEIPT_HASH,
        "adapter_result_hash": "d" * 64,
        "execution_plan_hash": "e" * 64,
        "observed_at": "2026-07-14T01:30:00Z",
        "artifact_relpath": (
            "prediction/market_regime/future_origin_evidence/"
            "date=2026-07-14/batch-fixture.json"
        ),
        "dedupe_key": "fixture",
        "expected_artifact_hash": "b" * 64,
        "observed_artifact_hash": observed_hash,
        "destination_state": destination_state,
        "blockers": blockers,
        "receipt_is_authorization": False,
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


def _decision(**overrides: object) -> MappingProxyType:
    values = dict(
        receipt=_receipt(),
        decided_at="2026-07-14T01:35:00Z",
        expected_receipt_hash=RECEIPT_HASH,
        failure_code=None,
        failure_detail_hash=None,
    )
    values.update(overrides)
    return build_origin_evidence_recovery_resume_decision(**values)


def test_absent_is_only_human_gated_resume_candidate() -> None:
    result = _decision()
    assert result["destination_state"] == DESTINATION_STATE_ABSENT
    assert result["recovery_disposition"] == RECOVERY_DISPOSITION_HUMAN_GATED_RESUME_CANDIDATE
    assert result["resume_candidate"] is True
    assert result["terminal"] is False
    assert result["recovery_actions"] == (
        "reconfirm_human_gate",
        "rebuild_execution_context_from_bound_hashes",
        "reobserve_destination_before_any_execution",
    )
    assert result["resume_authorized_by_this_artifact"] is False


def test_already_satisfied_is_terminal_success_equivalent() -> None:
    result = _decision(receipt=_receipt(DESTINATION_STATE_ALREADY_SATISFIED))
    assert result["recovery_disposition"] == RECOVERY_DISPOSITION_TERMINAL_SUCCESS_EQUIVALENT
    assert result["resume_candidate"] is False
    assert result["terminal"] is True
    assert result["recovery_actions"] == ("return_existing_duplicate_safe_receipt",)
    assert "destination_artifact_already_satisfied" in result["blockers"]


def test_conflicting_is_terminal_blocked_and_never_reclassified() -> None:
    result = _decision(receipt=_receipt(DESTINATION_STATE_CONFLICTING))
    assert result["recovery_disposition"] == RECOVERY_DISPOSITION_TERMINAL_CONFLICT_BLOCKED
    assert result["resume_candidate"] is False
    assert result["terminal"] is True
    assert result["conflicting_state_reclassified_as_absent"] is False
    assert result["recovery_actions"] == ("explicit_conflict_resolution_required",)


def test_inconsistent_requires_reobservation_and_never_reclassified() -> None:
    result = _decision(receipt=_receipt(DESTINATION_STATE_INCONSISTENT))
    assert result["recovery_disposition"] == RECOVERY_DISPOSITION_REOBSERVATION_REQUIRED
    assert result["resume_candidate"] is False
    assert result["terminal"] is False
    assert result["inconsistent_state_reclassified_as_absent"] is False
    assert result["recovery_actions"] == (
        "repair_or_replace_observation_source",
        "reobserve_destination",
        "build_new_duplicate_safe_receipt",
    )


def test_receipt_blockers_are_preserved_without_duplication() -> None:
    receipt = _receipt(
        DESTINATION_STATE_CONFLICTING,
        blockers=("destination_artifact_conflict", "operator_review_required"),
    )
    result = _decision(receipt=receipt)
    assert result["blockers"] == (
        "destination_artifact_conflict",
        "operator_review_required",
    )


def test_external_receipt_hash_and_receipt_id_are_revalidated() -> None:
    with pytest.raises(PermissionError, match="external_receipt_hash_mismatch"):
        _decision(expected_receipt_hash="f" * 64)

    bad = _receipt()
    bad["receipt_id"] = "other"
    with pytest.raises(ValueError, match="receipt_id_mismatch"):
        _decision(receipt=bad)


def test_decision_time_must_not_precede_receipt_observation() -> None:
    with pytest.raises(ValueError, match="before_receipt_observation"):
        _decision(decided_at="2026-07-14T01:29:59Z")
    with pytest.raises(ValueError, match="decided_at_invalid"):
        _decision(decided_at="2026-07-14 01:35:00")


def test_failure_context_is_bound_and_validated() -> None:
    first = _decision(
        failure_code="writer_preflight_failed",
        failure_detail_hash="1" * 64,
    )
    second = _decision(
        failure_code="writer_preflight_failed",
        failure_detail_hash="2" * 64,
    )
    assert first["failure_code"] == "writer_preflight_failed"
    assert first["decision_hash"] != second["decision_hash"]

    with pytest.raises(ValueError, match="failure_code_invalid"):
        _decision(failure_code=" ")
    with pytest.raises(ValueError, match="failure_detail_hash_invalid"):
        _decision(failure_code="x", failure_detail_hash="not-a-hash")
    with pytest.raises(ValueError, match="failure_detail_without_code"):
        _decision(failure_detail_hash="1" * 64)


def test_unsafe_receipt_flags_fail_closed() -> None:
    bad = _receipt()
    bad["writer_invoked"] = True
    with pytest.raises(ValueError, match="unsafe_receipt_flag:writer_invoked"):
        _decision(receipt=bad)

    bad = _receipt()
    bad["receipt_is_authorization"] = True
    with pytest.raises(ValueError, match="receipt_authorization_invalid"):
        _decision(receipt=bad)


def test_decision_is_deterministic_immutable_and_nonexecuting() -> None:
    first = _decision()
    second = _decision()
    assert first["decision_id"] == second["decision_id"]
    assert first["decision_hash"] == second["decision_hash"]
    assert first["receipt_hash_preserved"] is True
    assert first["automatic_retry_allowed"] is False
    assert first["resume_authorized_by_this_artifact"] is False
    assert first["writer_invoked"] is False
    assert first["execution_performed"] is False
    assert first["filesystem_read_performed"] is False
    assert first["filesystem_write_performed"] is False
    assert first["writes_dhot"] is False
    assert first["scheduler_enabled"] is False
    with pytest.raises(TypeError):
        first["resume_candidate"] = False


def test_module_exposes_no_writer_filesystem_cli_scheduler_or_retry_surface() -> None:
    import btcts.prediction.market_regime.future_origin_evidence_recovery_resume_decision as module

    assert hasattr(module, "build_origin_evidence_recovery_resume_decision")
    assert not hasattr(module, "write_origin_evidence_once")
    assert not hasattr(module, "preflight_origin_evidence_write")
    assert not hasattr(module, "Path")
    assert not hasattr(module, "main")
    assert not hasattr(module, "register")
    assert not hasattr(module, "retry")
